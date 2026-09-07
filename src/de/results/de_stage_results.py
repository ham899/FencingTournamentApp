from dataclasses import dataclass, field, InitVar

from de.de_bracket import DEBracket
from de.results.de_entry_result import DEEntryResult, DEEntryStatus
from entities.tournament_entry import TournamentEntry


@dataclass(slots=True)
class _DEEntryResultState:
    """
    Hold mutable state while calculating a DE entry result.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose result is being calculated.
    bracket_seed : int
        The entry's one-based starting seed within the DE bracket.
    round_reached : int, default=1
        The one-based number of the furthest DE round reached.
    status : DEEntryStatus, default=`DEEntryStatus.ACTIVE`
        The entry's current participation status.
    place : int | None, default=`None`
        The entry's confirmed finishing place, or `None` if its exact place has not yet been determined.
    """
    entry: TournamentEntry
    bracket_seed: int
    round_reached: int = field(default=1, init=False)
    status: DEEntryStatus = field(default=DEEntryStatus.ACTIVE, init=False)
    place: int | None = field(default=None, init=False)


@dataclass(frozen=True, slots=True)
class DEStageResults:
    """
    Represent a fixed snapshot of every entry's results in a DE stage.

    The snapshot is calculated from the supplied bracket's current state.

    The calculated fields cannot be reassigned after initialization.

    Parameters
    ----------
    bracket : DEBracket
        The bracket from which to calculate the result snapshot.

    Attributes
    ----------
    entry_results : tuple[DEEntryResult, ...]
        The calculated entry result snapshots in result order.
    """
    bracket: InitVar[DEBracket]
    entry_results: tuple[DEEntryResult, ...] = field(init=False)


    # --- Initialization and Validation ---
    def __post_init__(self, bracket: DEBracket) -> None:
        """
        Validate the bracket and calculate the DE stage result snapshot.

        Parameters
        ----------
        bracket : DEBracket
            The bracket from which to calculate the results.

        Raises
        ------
        TypeError
            If `bracket` is not a `DEBracket`.
        """
        if not isinstance(bracket, DEBracket):
            raise TypeError(f'Bracket must be a DEBracket - got {type(bracket).__name__}')

        object.__setattr__(self, 'entry_results', self._calculate_stage_results(bracket))


    # --- Helper Methods ---
    def _initialize_entry_states(self, bracket: DEBracket) -> dict[int, _DEEntryResultState]:
        """
        Create the initial mutable result state for every bracket entry.

        Parameters
        ----------
        bracket : DEBracket
            The bracket containing the entries and their initial tableau order.

        Returns
        -------
        dict[int, _DEEntryResultState]
            A mapping from each tournament entry ID to its initialized result state.

        Raises
        ------
        ValueError
            If the number of bracket entries does not agree with the number of occupied seed positions.
        """
        round_one_seed_order: tuple[int, ...] = bracket.round_one_seed_order

        occupied_seed_order = (seed for seed in round_one_seed_order if seed <= bracket.num_entries)

        return {
            entry.id: _DEEntryResultState(
                entry=entry, 
                bracket_seed=bracket_seed
            )
            for entry, bracket_seed in zip(
                bracket.entries, 
                occupied_seed_order, 
                strict=True
            )
        }
    
    def _update_entry_states(self, bracket: DEBracket, entry_states_by_id: dict[int, _DEEntryResultState]) -> None:
        """
        Update entry result states from the bracket's current state.

        The bracket is examined round by round. 
        Entries appearing in later rounds have their furthest round reached updated, 
        losers of completed matchups are marked as eliminated, 
        and the winner of a completed final is marked as the stage winner.

        Parameters
        ----------
        bracket : DEBracket
            The bracket whose current state is being examined.
        entry_states_by_id : dict[int, _DEEntryResultState]
            The mutable result states keyed by tournament entry ID.
        """
        for de_round in bracket.rounds:
            for matchup in de_round.matchups:
                # Case 1: Matchup is a BYE
                if matchup.is_bye():
                    continue

                # Case 2: Matchup is completed
                elif matchup.is_complete():
                    if matchup.round_number != 1:
                        entry_states_by_id[matchup.loser.id].round_reached = matchup.round_number
                    
                    entry_states_by_id[matchup.loser.id].status = DEEntryStatus.ELIMINATED

                    # Case 2.1: Matchup was the final
                    if matchup.round_number == bracket.num_rounds:
                        entry_states_by_id[matchup.winner.id].round_reached = matchup.round_number
                        entry_states_by_id[matchup.winner.id].status = DEEntryStatus.WINNER

                # Case 3: Matchup is ready but incomplete
                elif matchup.has_both_entries() and matchup.is_incomplete():
                    for entry in (matchup.entry1, matchup.entry2):
                        if matchup.round_number != 1:
                            entry_states_by_id[entry.id].round_reached = matchup.round_number

                # Case 4: Matchup is undetermined with one entry
                elif matchup.has_exactly_one_entry():
                    if matchup.has_entry_at(0):
                        entry_states_by_id[matchup.entry1.id].round_reached = matchup.round_number
                    else:
                        entry_states_by_id[matchup.entry2.id].round_reached = matchup.round_number

                # Case 5: Matchup is undetermined with no entries
                elif matchup.has_no_entries():
                    continue

    def _order_entry_states(self, entry_states_by_id: dict[int, _DEEntryResultState]) -> tuple[_DEEntryResultState, ...]:
        """
        Arrange the entry states in current result order.

        Entries are ordered first by the furthest round reached, then by participation status, then by bracket seed.

        Parameters
        ----------
        entry_states_by_id : dict[int, _DEEntryResultState]
            The mutable result states keyed by tournament entry ID.

        Returns
        -------
        tuple[_DEEntryResultState, ...]
            The entry result states in current result order.
        """
        status_rank = {
            DEEntryStatus.WINNER: 0,
            DEEntryStatus.ACTIVE: 1,
            DEEntryStatus.ELIMINATED: 2
        }

        return tuple(
            sorted(
                entry_states_by_id.values(),
                key=lambda entry_state: (-entry_state.round_reached, status_rank[entry_state.status], entry_state.bracket_seed)
            )
        )

    def _assign_confirmed_places(self, bracket: DEBracket, ordered_entry_states: tuple[_DEEntryResultState, ...]) -> None:
        """
        Assign confirmed finishing places where possible.

        **Note:** Active entries and entries eliminated during an incomplete round keep a place of `None`.

        Parameters
        ----------
        bracket : DEBracket
            The bracket whose progress determines which places are confirmed.
        ordered_entry_states : tuple[_DEEntryResultState, ...]
            The mutable entry states in result order.
        """
        for place, entry_state in enumerate(ordered_entry_states, start=1):
            if entry_state.status == DEEntryStatus.WINNER:
                entry_state.place = 1

            elif entry_state.status == DEEntryStatus.ELIMINATED and (
                bracket.current_round_number is None or 
                entry_state.round_reached < bracket.current_round_number):
                entry_state.place = place

    def _calculate_stage_results(self, bracket: DEBracket) -> tuple[DEEntryResult, ...]:
        """
        Calculate the DE entry result snapshots in result order.

        Parameters
        ----------
        bracket : DEBracket
            The bracket from which to calculate the result snapshot.

        Returns
        -------
        tuple[DEEntryResult, ...]
            The calculated entry result snapshots in result order.
        """
        # Step 1: Initialize the result state for each entry
        entry_states_by_id = self._initialize_entry_states(bracket)
        
        # Step 2: Update the states from the bracket
        self._update_entry_states(bracket, entry_states_by_id)

        # Step 3: Order the entry states
        ordered_entry_states = self._order_entry_states(entry_states_by_id)

        # Step 4: Assign confirmed places
        self._assign_confirmed_places(bracket, ordered_entry_states)

        # Step 5: Create the immutable entry result snapshots
        return tuple(
            DEEntryResult(
                entry=entry_state.entry,
                stage_number=bracket.stage_number,
                bracket_seed=entry_state.bracket_seed,
                round_reached=entry_state.round_reached,
                place=entry_state.place,
                status=entry_state.status
            )
            for entry_state in ordered_entry_states
        )
