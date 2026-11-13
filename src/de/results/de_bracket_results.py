from dataclasses import dataclass, field, InitVar

import validation

from de.de_bracket import DEBracket
from de.results.de_entry_result import DEEntryResult, DEEntryStatus
from entities.seeded_entry import SeededEntry
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
    previous_place : int | None
        The entry's one-based finishing place in the previous stage of the tournament.
        None if no previous placement is available.
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
    previous_place: int | None
    round_reached: int = field(default=1, init=False)
    status: DEEntryStatus = field(default=DEEntryStatus.ACTIVE, init=False)
    place: int | None = field(default=None, init=False)


@dataclass(frozen=True, slots=True)
class DEBracketResults:
    """
    Represent a fixed snapshot of every entry's results in a DE bracket.

    Results are calculated from the bracket's current state, 
    including its optional third-place matchup. 
    Equal non-None previous placements preserve ties among entries eliminated in the same round, 
    unless a placement match separates them. 

    Third-place participants remain eliminated from contention to win this bracket. 
    Their places remain unconfirmed until that matchup is complete.

    A stopped bracket has no winner. Entries that reach its stopping round remain active with no confirmed place. 
    Once the stopped bracket is complete, these active entries represent its advancing entries.

    The bracket and seeded-entry tuple are used only during initialization and are not stored. 
    Result snapshots retain references to tournament entries; the calculated result fields cannot be reassigned.

    Parameters
    ----------
    bracket : DEBracket
        The bracket from which to calculate the snapshot. 
        Its seed order must preserve the incoming ranking so that 
        incoming ties are consecutive within each elimination group. 
        This ordering requirement is assumed, rather than validated here.
    seeded_entries : tuple[SeededEntry, ...]
        Previous-stage placement information for exactly the bracket's entries,
        with unique entry IDs and the same tournament ID as the bracket.
        Tuple order does not matter. Bracket seeds are derived from the bracket,
        not from the seed values in this tuple. For a consolation bracket,
        supply only its participants, retaining their previous-stage placements.

    Attributes
    ----------
    ranked_results : tuple[DEEntryResult, ...]
        Entry snapshots ordered by descending round reached, status (winner, active, eliminated), 
        ascending confirmed place, and ascending bracket seed. 
        Within the same round and status, unresolved places follow confirmed places. 
        Tied entries retain their bracket-seed order.
    """
    bracket: InitVar[DEBracket]
    seeded_entries: InitVar[tuple[SeededEntry, ...]]
    _ranked_results: tuple[DEEntryResult, ...] = field(init=False)


    # --- Initialization and Validation ---
    def __post_init__(self, bracket: DEBracket, seeded_entries: tuple[SeededEntry, ...]) -> None:
        """
        Validate the inputs and calculate the bracket result snapshot.

        Parameters
        ----------
        bracket : DEBracket
            The bracket whose current state is represented.
        seeded_entries : tuple[SeededEntry, ...]
            The bracket participants and their previous-stage placements.

        Raises
        ------
        TypeError
            If bracket is not a DEBracket, seeded_entries is not a tuple,
            an item is not a SeededEntry holding a TournamentEntry,
            a seed is not an integer, or a previous place is neither an integer nor None.
        ValueError
            If a seed or supplied previous place is not positive, entry IDs are duplicated, 
            tournament IDs differ, or the supplied entry IDs do not match the bracket participants exactly.
        """
        location = self.__class__.__name__

        if not isinstance(bracket, DEBracket):
            raise TypeError(
                f'Bracket must be a DEBracket in {location} - got {type(bracket).__name__}'
            )

        self._validate_seeded_entries(seeded_entries, bracket, location)

        seeded_entry_lookup = {seeded_entry.entry.id: seeded_entry for seeded_entry in seeded_entries}

        object.__setattr__(self, '_ranked_results', self._calculate_ranked_results(bracket, seeded_entry_lookup))


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the represented entries."""
        return self._ranked_results[0].tournament_id

    @property
    def stage_number(self) -> int:
        """Return the stage number shared by the entry results."""
        return self._ranked_results[0].stage_number

    @property
    def num_entries(self) -> int:
        """Return the number of represented entries."""
        return len(self._ranked_results)

    @property
    def ranked_results(self) -> tuple[DEEntryResult, ...]:
        """Return the immutable entry snapshots in bracket ranking order."""
        return self._ranked_results

    @property
    def ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the tournament entries in the same order as ``ranked_results``."""
        return tuple(result.entry for result in self._ranked_results)

    @property
    def ranked_names(self) -> tuple[str, ...]:
        """Return the entry display names in the same order as ``ranked_results``."""
        return tuple(result.display_name for result in self._ranked_results)


    # --- Helper Methods ---
    def _initialize_entry_states(self, bracket: DEBracket, seeded_entry_lookup: dict[int, SeededEntry]) -> dict[int, _DEEntryResultState]:
        """
        Create the initial mutable result state for every bracket entry.

        Bracket seeds are derived from the occupied first-round seed positions;
        previous placements are taken from the supplied lookup.

        Parameters
        ----------
        bracket : DEBracket
            The bracket containing the entries and their initial tableau order.
        seeded_entry_lookup : dict[int, SeededEntry]
            Validated seeded entries keyed by tournament entry ID, providing previous-stage placements.

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
                bracket_seed=bracket_seed, 
                previous_place=seeded_entry_lookup[entry.id].previous_place
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
        Assign confirmed finishing places from the bracket state.

        Winners receive first place. 
        Active entries and eliminated entries whose elimination round is not yet confirmed retain a place of None.
        An elimination is confirmed when the bracket has no current round or the entry was eliminated before the current round.

        Confirmed eliminated entries with the same non-None previous placement and elimination round share a place. 

        Among entries eliminated in the same round, entries with equal previous placements must appear consecutively in the ordered results.

        Places assigned to third-place participants are temporary and are subsequently overridden by _apply_third_place_result().

        Parameters
        ----------
        bracket : DEBracket
            The bracket whose progress determines which places are confirmed.
        ordered_entry_states : tuple[_DEEntryResultState, ...]
            The mutable entry states in result order.
        """
        previous_state: _DEEntryResultState | None = None

        for position, entry_state in enumerate(ordered_entry_states, start=1):
            elimination_is_confirmed = (
                entry_state.status is DEEntryStatus.ELIMINATED
                and (bracket.current_round_number is None or entry_state.round_reached < bracket.current_round_number)
            )

            # Case 1: The bracket winner always finishes first
            if entry_state.status is DEEntryStatus.WINNER:
                entry_state.place = 1

            # Case 2: An eliminated entry's finishing place is confirmed
            elif elimination_is_confirmed:
                ties_with_previous = (
                    previous_state is not None
                    and entry_state.previous_place is not None
                    and entry_state.previous_place == previous_state.previous_place
                    and entry_state.round_reached == previous_state.round_reached
                    and previous_state.status is DEEntryStatus.ELIMINATED
                )

                if ties_with_previous:
                    entry_state.place = previous_state.place
                else:
                    entry_state.place = position

            # Case 3: The entry's finishing place is still unresolved
            else:
                entry_state.place = None

            previous_state = entry_state

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

    def _calculate_ranked_results(self, bracket: DEBracket, seeded_entry_lookup: dict[int, SeededEntry]) -> tuple[DEEntryResult, ...]:
        """
        Calculate the DE entry result snapshots in result order.

        Parameters
        ----------
        bracket : DEBracket
            The bracket from which to calculate the result snapshot.
        seeded_entry_lookup : dict[int, SeededEntry]
            Validated seeded entries keyed by tournament entry ID, providing previous-stage placements.

        Returns
        -------
        tuple[DEEntryResult, ...]
            The calculated entry result snapshots in result order.
        """
        # Step 1: Initialize the result state for each entry
        entry_states_by_id = self._initialize_entry_states(bracket, seeded_entry_lookup)
        
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
                previous_place=entry_state.previous_place,
                round_reached=entry_state.round_reached,
                place=entry_state.place,
                status=entry_state.status
            )
            for entry_state in ordered_entry_states
        )

    # --- Validation Helper Methods ---
    def _validate_seeded_entries(self, seeded_entries: tuple[SeededEntry, ...],  bracket: DEBracket, location: str) -> None:
        """
        Validate seeded-entry types, values, and bracket membership.

        Parameters
        ----------
        seeded_entries : tuple[SeededEntry, ...]
            Entries supplying previous-stage placements for this bracket.
        bracket : DEBracket
            The bracket defining the required participants and tournament.
        location : str
            The calling class or method name used in validation messages.

        Raises
        ------
        TypeError
            If the collection is not a tuple, an item is not a SeededEntry holding a TournamentEntry, 
            a seed is not an integer, or a previous place is neither an integer nor None.
        ValueError
            If a seed or supplied previous place is not positive, tournament IDs differ, 
            entry IDs are duplicated, or the supplied entry IDs do not match the bracket participants exactly.

        Notes
        -----
        Consistency between previous placements and bracket seed order is a caller responsibility.
        """
        if not isinstance(seeded_entries, tuple):
            raise TypeError(f'Seeded entries must be held in a tuple - got {type(seeded_entries).__name__}')

        tournament_id: int | None = None
        for i, seeded_entry in enumerate(seeded_entries):
            item_name: str = f'seeded entry at index {i}'

            if not isinstance(seeded_entry, SeededEntry):
                raise TypeError(f'Item at index {i} is not a SeededEntry - got {type(seeded_entry).__name__}')

            if not isinstance(seeded_entry.entry, TournamentEntry):
                raise TypeError(
                    f'{item_name.capitalize()} holds an entry that is not a TournamentEntry - got {type(seeded_entry.entry).__name__}'
                )

            validation.validate_positive_int(seeded_entry.seed, f'Seed of {item_name}', location)
            validation.validate_optional_positive_int(seeded_entry.previous_place, f'Previous place of {item_name}', location)

            if tournament_id is None:
                tournament_id = seeded_entry.entry.tournament_id

                if tournament_id != bracket.tournament_id:
                    raise ValueError(
                        f'The seeded entries and the bracket must share a tournament ID - '
                        f'tournament ID = {tournament_id} and bracket ID = {bracket.tournament_id}'
                    )

            if seeded_entry.entry.tournament_id != tournament_id:
                raise ValueError(f'{item_name.capitalize()} does not share a tournament ID with the first seeded entry')

        # Use sets to check for unique entry IDs and to verify that the seeded entries match the bracket entries exactly
        entry_ids: tuple[int, ...] = tuple(seeded_entry.entry.id for seeded_entry in seeded_entries)

        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError(
                f'Seeded entries must have unique entry IDs in {location}'
            )

        bracket_entry_ids = {entry.id for entry in bracket.entries}

        if set(entry_ids) != bracket_entry_ids:
            raise ValueError(
                f'Seeded entries must match the bracket entries exactly in {location}'
            )
