from dataclasses import dataclass, field, replace, InitVar

import validation

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.results.de_bracket_results import DEBracketResults
from de.results.de_entry_result import DEEntryResult, DEEntryStatus
from entities.tournament_entry import TournamentEntry


@dataclass(frozen=True, slots=True)
class DEStageResults:
    """
    Represent a snapshot of the DE stage results.

    The supplied brackets are used only during initialization and are not stored. 
    Individual result snapshots retain references to their tournament entries.

    Parameters
    ----------
    stage_number : int
        The one-based position of the stage within the tournament the snapshot is representing.
    main_bracket : DEBracket
        The main bracket of the stage from which to calculate the results.
    consolation_bracket : DEBracket | None
        The consolation bracket to finalize the places between 5th and 8th.

    Attributes
    ----------
    stage_number : int
        The one-based position of the stage within the tournament the snapshot is representing.
    ranked_results : tuple[DEEntryResult, ...]
        The entry snapshots ordered by descending round reached,
        participation status (winner, active, eliminated),
        ascending confirmed place, and ascending bracket seed.
        Within the same round and status, unresolved places follow confirmed places.
        Seeds, rounds reached, and statuses describe the main bracket.
        Places account for the consolation bracket when provided.
    """
    stage_number: int
    main_bracket: InitVar[DEBracket]
    consolation_bracket: InitVar[DEBracket | None] = None
    ranked_results: tuple[DEEntryResult, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self, main_bracket: DEBracket, consolation_bracket: DEBracket | None) -> None:
        """
        Validate the bracket types and calculate the stage result snapshot.

        Raises
        ------
        TypeError
            If the stage number is not an integer, if ``main_bracket`` is not a ``DEBracket``, 
            or ``consolation_bracket`` is neither ``None`` nor a ``DEBracket``.
        ValueError
            If the stage number is not positive, 
            if ``main_bracket`` does not have the ``DEBracketRole.MAIN`` role, 
            if the main bracket's stage number does not match the supplied ``stage_number``,
            if the consolation bracket does not have the ``DEBracketRole.CONSOLATION`` role, 
            the brackets do not belong to the same tournament or stage, 
            or the consolation entries are not a subset of the main-bracket entries.
        """
        # Validate inputs
        location = 'DEStageResults'

        validation.validate_positive_int(self.stage_number, 'Stage number', location)

        if not isinstance(main_bracket, DEBracket):
            raise TypeError(f'Main bracket must be a DEBracket in {location} - got {type(main_bracket).__name__}')
        
        if main_bracket.bracket_role != DEBracketRole.MAIN:
            raise ValueError(f'Main bracket must have the MAIN bracket role in {location}')

        if main_bracket.stage_number != self.stage_number:
            raise ValueError(
                f'Main bracket must belong to stage {self.stage_number} in {location} - got stage {main_bracket.stage_number}'
            )

        if consolation_bracket is not None:
            if not isinstance(consolation_bracket, DEBracket):
                raise TypeError(
                    f'Consolation bracket must be either None or a DEBracket in {location} - got {type(consolation_bracket).__name__}'
                )

            if consolation_bracket.bracket_role != DEBracketRole.CONSOLATION:
                raise ValueError(f'Consolation bracket must have the CONSOLATION bracket role in {location}')

            if consolation_bracket.tournament_id != main_bracket.tournament_id:
                raise ValueError(f'The consolation bracket and main bracket must have the same tournament ID in {location}')

            if consolation_bracket.stage_number != main_bracket.stage_number:
                raise ValueError(f'The consolation bracket and main bracket must have the same stage number in {location}')

            main_entry_ids = {entry.id for entry in main_bracket.entries}
            consolation_entry_ids = {entry.id for entry in consolation_bracket.entries}

            if not consolation_entry_ids <= main_entry_ids:
                raise ValueError(
                    f'The entries in the consolation bracket must be a subset of the entries in the main bracket in {location}'
                )

        # Calculate the main-bracket result snapshot
        main_bracket_results = DEBracketResults(main_bracket)

        if consolation_bracket is None:
            ranked_results = main_bracket_results.ranked_results

        # Otherwise, calculate the consolation results and combine both snapshots
        else:
            consolation_results = DEBracketResults(consolation_bracket)

            ranked_results = self._combine_main_and_consolation_bracket_results(
                main_bracket_results=main_bracket_results, 
                consolation_results=consolation_results
            )

        object.__setattr__(self, 'ranked_results', ranked_results)


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the represented entries."""
        return self.ranked_results[0].tournament_id

    @property
    def num_entries(self) -> int:
        """Return the number of represented entries."""
        return len(self.ranked_results)

    @property
    def ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the tournament entries in the same order as ``ranked_results``."""
        return tuple(result.entry for result in self.ranked_results)

    @property
    def ranked_names(self) -> tuple[str, ...]:
        """Return the entry display names in the same order as ``ranked_results``."""
        return tuple(result.display_name for result in self.ranked_results)


    # --- Helper Methods ---
    def _combine_main_and_consolation_bracket_results(
            self, main_bracket_results: DEBracketResults, consolation_results: DEBracketResults) -> tuple[DEEntryResult, ...]:
        """
        Combine main-bracket results with fifth-to-eighth-place results.

        Consolation places 1-4 become stage places 5-8. Entries whose
        consolation places are unresolved receive a stage place of None.
        Entries outside the consolation bracket retain their main-bracket results.

        Main-bracket seeds, rounds reached, and statuses are preserved.

        Parameters
        ----------
        main_bracket_results : DEBracketResults
            The main-bracket result snapshot.
        consolation_results : DEBracketResults
            The result snapshot for the bracket determining places 5-8.

        Returns
        -------
        tuple[DEEntryResult, ...]
            The combined snapshots ordered by descending main-bracket round reached, 
            status (winner, active, eliminated), ascending place, and ascending main-bracket seed. 
            Unresolved places sort after confirmed places within the same round and status group.
        """
        consolation_results_by_id: dict[int, DEEntryResult] = {result.entry.id: result for result in consolation_results.ranked_results}

        new_ranked_results: list[DEEntryResult] = []

        for entry_result in main_bracket_results.ranked_results:
            consolation_result = consolation_results_by_id.get(entry_result.entry.id)

            if consolation_result is None:
                new_ranked_results.append(entry_result)
                continue

            stage_place = (consolation_result.place + 4 if consolation_result.place is not None else None)

            # Create a new entry snapshot with the updated stage place
            new_ranked_results.append(replace(entry_result, place=stage_place))

        status_rank = {DEEntryStatus.WINNER: 0, DEEntryStatus.ACTIVE: 1, DEEntryStatus.ELIMINATED: 2}

        new_ranked_results.sort(
            key=lambda result: (
                -result.round_reached, 
                status_rank[result.status], 
                result.place if result.place is not None else float('inf'),
                result.bracket_seed
            )
        )

        return tuple(new_ranked_results)
