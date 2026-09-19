from dataclasses import dataclass, field, replace, InitVar

from de.de_bracket import DEBracket
from de.results.de_bracket_results import DEBracketResults
from de.results.de_entry_result import DEEntryResult, DEEntryStatus


@dataclass(frozen=True, slots=True)
class DEStageResults:
    """
    Represent a snapshot of the DE stage results.

    Parameters
    ----------
    main_bracket : DEBracket
        The main bracket of the stage from which to calculate the results.
    consolation_bracket : DEBracket | None
        The consolation bracket to finalize the places between 5th and 8th.

    Attributes
    ----------
    entry_results : tuple[DEEntryResult, ...]
        The combined entry result snapshots in current result order.
        Seeds, rounds reached, and statuses describe the main bracket;
        places account for the consolation bracket when provided.
    """
    main_bracket: InitVar[DEBracket]
    consolation_bracket: InitVar[DEBracket | None] = None
    entry_results: tuple[DEEntryResult, ...] = field(init=False)

    def __post_init__(self, main_bracket: DEBracket, consolation_bracket: DEBracket | None) -> None:
        """
        Validate the bracket types and calculate the stage result snapshot.

        Raises
        ------
        TypeError
            If main_bracket is not a DEBracket, or consolation_bracket is neither None nor a DEBracket.
        """
        # Validate inputs
        location = 'DEStageResults'
        if not isinstance(main_bracket, DEBracket):
            raise TypeError(f'Main bracket must be a DEBracket in {location} - got {type(main_bracket).__name__}')

        if consolation_bracket is not None and not isinstance(consolation_bracket, DEBracket):
            raise TypeError(f'Consolation bracket must be either None or a DEBracket in {location} - got {type(consolation_bracket).__name__}')

        # Calculate the main-bracket result snapshot
        main_bracket_results = DEBracketResults(main_bracket)

        if consolation_bracket is None:
            entry_results = main_bracket_results.entry_results

        # Otherwise, calculate the consolation results and combine both snapshots
        else:
            consolation_results = DEBracketResults(consolation_bracket)

            entry_results = self._combine_main_and_consolation_bracket_results(
                main_bracket_results=main_bracket_results, 
                consolation_results=consolation_results
            )

        object.__setattr__(self, 'entry_results', entry_results)


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
        consolation_results_by_id: dict[int, DEEntryResult] = {result.entry.id: result for result in consolation_results.entry_results}
        
        new_entry_results: list[DEEntryResult] = []

        for entry_result in main_bracket_results.entry_results:
            consolation_result = consolation_results_by_id.get(entry_result.entry.id)

            if consolation_result is None:
                new_entry_results.append(entry_result)
                continue

            stage_place = (consolation_result.place + 4 if consolation_result.place is not None else None)

            # Create a new entry snapshot with the updated stage place
            new_entry_results.append(replace(entry_result, place=stage_place))

        status_rank = {DEEntryStatus.WINNER: 0, DEEntryStatus.ACTIVE: 1, DEEntryStatus.ELIMINATED: 2}

        new_entry_results.sort(
            key=lambda result: (
                -result.round_reached, 
                status_rank[result.status], 
                result.place if result.place is not None else float('inf'),
                result.bracket_seed
            )
        )

        return tuple(new_entry_results)
