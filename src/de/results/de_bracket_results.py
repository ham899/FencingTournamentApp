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
        The one-based number of the furthest bracket round reached.
        Participation in the separate third-place matchup does not change this value.
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
class DEBracketResults:
    """
    Represent a fixed snapshot of every entry's results in a DE bracket.

    The snapshot is calculated from the supplied bracket's current state,
    including its optional third-place matchup.

    Third-place participants remain eliminated from championship contention.
    Their exact places remain unconfirmed until the third-place matchup is complete.

    A stopped bracket has no winner. 
    Entries that reach its stopping round remain active and have no confirmed place, 
    while eliminated entries are ordered after them. 
    Once the bracket is complete, those active entries represent its advancing entries.

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
        Validate the bracket and calculate the DE bracket result snapshot.

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

        object.__setattr__(self, 'entry_results', self._calculate_bracket_results(bracket))


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
        Update entry result states from the bracket rounds.

        Entries appearing in later rounds have their furthest round reached updated,
        losers of completed matchups are marked as eliminated,
        and the winner of a completed final is marked as the bracket winner.

        The separate third-place matchup is handled by _apply_third_place_result().

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

        Entries are ordered by furthest bracket round reached, 
        participation status (with winners before active entries before eliminated entries), 
        confirmed place, and lastly, bracket seed.

        Within the same round and status, entries with confirmed places precede those whose places are None.

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
                key=lambda entry_state: (
                    -entry_state.round_reached, 
                    status_rank[entry_state.status], 
                    # Within the same round and status, sort unknown places after known places
                    entry_state.place if entry_state.place is not None else float('inf'),
                    entry_state.bracket_seed
                )
            )
        )

    def _assign_confirmed_places(self, bracket: DEBracket, ordered_entry_states: tuple[_DEEntryResultState, ...]) -> None:
        """
        Assign finishing places from the bracket state.

        Active entries retain a place of ``None``. 
        In a stopped bracket, this includes entries that have reached the stopping round and 
        qualified to advance.
        Eliminated entries receive a place only after all bracket rounds up to 
        and including their elimination round are complete.

        Places assigned to third-place participants are temporary here.

        Parameters
        ----------
        bracket : DEBracket
            The bracket whose progress determines which places are confirmed.
        ordered_entry_states : tuple[_DEEntryResultState, ...]
            The mutable entry states in result order.
        """
        for place, entry_state in enumerate(ordered_entry_states, start=1):
            if entry_state.status is DEEntryStatus.WINNER:
                entry_state.place = 1

            elif entry_state.status is DEEntryStatus.ELIMINATED and (
                bracket.current_round_number is None or 
                entry_state.round_reached < bracket.current_round_number):
                entry_state.place = place

    def _apply_third_place_result(self, bracket: DEBracket, entry_states_by_id: dict[int, _DEEntryResultState]) -> None:
        """
        Override bracket places using the optional third-place matchup.

        Do nothing when the third-place matchup is disabled.
        Otherwise, clear any places assigned to its current participants.
        If the matchup is complete, assign its winner third place and its loser fourth place.

        Participation status and furthest bracket round reached are unchanged.

        Parameters
        ----------
        bracket : DEBracket
            The bracket containing the optional third-place matchup.
        entry_states_by_id : dict[int, _DEEntryResultState]
            The mutable result states keyed by tournament entry ID.
        """
        third_place_matchup = bracket.third_place_matchup

        # Do nothing when the third-place matchup is disabled
        if third_place_matchup is None:
            return
        
        # Exact places remain unknown until the third-place matchup is complete
        for entry in (third_place_matchup.entry1, third_place_matchup.entry2):
            if entry is not None:
                entry_states_by_id[entry.id].place = None
            
        # Override seed-based placement with the deciding matchup's result
        if third_place_matchup.is_complete():
            entry_states_by_id[third_place_matchup.winner.id].place = 3
            entry_states_by_id[third_place_matchup.loser.id].place = 4

    def _calculate_bracket_results(self, bracket: DEBracket) -> tuple[DEEntryResult, ...]:
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

        # Step 3: Order the entry states for bracket place assignment
        ordered_entry_states = self._order_entry_states(entry_states_by_id)

        # Step 4: Assign places from the bracket's state
        self._assign_confirmed_places(bracket, ordered_entry_states)

        # Step 5: Apply the third-place match result if applicable
        self._apply_third_place_result(bracket, entry_states_by_id)

        # Step 6: Update the ordering using the confirmed places
        ordered_entry_states = self._order_entry_states(entry_states_by_id)

        # Step 7: Create the immutable entry result snapshots
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
