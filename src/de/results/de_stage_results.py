from dataclasses import dataclass, field, InitVar

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.results.de_bracket_results import DEBracketResults
from de.results.de_entry_result import DEEntryResult, DEEntryStatus
from de.results.de_entry_stage_result import DEEntryStageResult
from entities import SeededEntry
from tournament.results.stage import StageEntryStatus, StageResults


@dataclass(frozen=True, slots=True)
class DEStageResults(StageResults):
    """
    Represent an immutable snapshot of a direct-elimination stage's results.

    Combine main-bracket results with optional fifth-to-eighth-place consolation results and 
    expose the shared stage result interface.
    Bracket calculations determine placements and inherited ties; 
    this class resolves stage placements, orders entries, and assigns stage result fields.

    Stage status follows the main bracket: its winner and active entries remain ACTIVE, 
    while its eliminated entries are ELIMINATED. 
    Consolation determines the current order and stage places of its participants. 
    Their stage status continues to follow the main bracket.

    The supplied brackets and seeded-entry tuple are used only during initialization and are not stored. 
    Individual result snapshots retain references to their tournament entries.

    Parameters
    ----------
    stage_number : int
        The stage's one-based position within its tournament.
    seeded_entries : tuple[SeededEntry, ...]
        Seeded entries for exactly the main-bracket participants, including their previous-stage placements. 
        Relevant entries are selected for the consolation calculation. 
        Each bracket's seed order must satisfy the incoming-ranking requirements of DEBracketResults.
    main_bracket : DEBracket
        The MAIN bracket belonging to this stage.
    consolation_bracket : DEBracket | None, default=None
        An optional CONSOLATION bracket determining stage places 5-8.
        Its participants must belong to the main bracket and share its tournament and stage. 
        The caller must supply the appropriate fifth-to-eighth-place participants; 
        subset validation alone does not establish their eligibility for those places.

    Attributes
    ----------
    stage_number : int
        The stage's one-based position within its tournament.
    ranked_results : tuple[DEEntryStageResult, ...]
        One result per main-bracket entry in current stage ranking order. 
        Entries follow main-bracket order, 
        with consolation participants ordered by their consolation standings starting at position 5.
        Each entry has a unique, one-based position. Its place is ``None`` until confirmed. 
        Multiple entries may share a confirmed place.

    Notes
    -----
    A confirmed consolation place becomes a stage place by adding four.
    Entries sharing a confirmed stage place have ``is_tie=True``.
    Entries awaiting a place have ``is_tie=None``.
    Advancing entries in a stopped main bracket remain ACTIVE with unresolved places.
    """
    seeded_entries: InitVar[tuple[SeededEntry, ...]]
    main_bracket: InitVar[DEBracket]
    consolation_bracket: InitVar[DEBracket | None] = None
    _ranked_results: tuple[DEEntryStageResult, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self, seeded_entries: tuple[SeededEntry, ...], main_bracket: DEBracket, consolation_bracket: DEBracket | None) -> None:
        """
        Validate the inputs and calculate the stage result snapshot.

        Parameters
        ----------
        seeded_entries : tuple[SeededEntry, ...]
            Main-bracket participants and their previous-stage placements.
        main_bracket : DEBracket
            The main bracket whose results define stage participation status.
        consolation_bracket : DEBracket | None
            The optional bracket determining stage places 5-8.

        Raises
        ------
        TypeError
            If the stage number has an invalid type, a bracket has an invalid type, 
            or seeded entries fail the type checks in `DEBracketResults`.
        ValueError
            If the stage number is not positive, bracket roles or stage numbers are inconsistent, 
            the brackets have different tournament IDs, consolation entries are not a subset of main-bracket entries, 
            seeded entries fail the value checks in `DEBracketResults`, 
            or if the consolation entry IDs differ from the IDs in the corresponding slice of the main-bracket standings.
        """
        # 1. Validate inputs
        location = self.__class__.__name__
        super(DEStageResults, self).__post_init__()
        self._validate_main_bracket(main_bracket, location)

        if consolation_bracket is not None:
            self._validate_consolation_bracket(consolation_bracket, main_bracket, location)

        # 2. Calculate the main-bracket result snapshot
        main_bracket_results = DEBracketResults(main_bracket, seeded_entries)

        # 3. Calculate the optional consolation snapshot
        consolation_results = None

        if consolation_bracket is not None:
            consolation_entry_ids: set[int] = set(entry.id for entry in consolation_bracket.entries)

            consolation_seeded_entries = tuple(
                seeded_entry for seeded_entry in seeded_entries if seeded_entry.entry.id in consolation_entry_ids
            )

            consolation_results = DEBracketResults(consolation_bracket, consolation_seeded_entries)

        # 4. Convert every entry into a stage result, with or without consolation information
        ranked_results = self._calculate_stage_entry_results(main_bracket_results, consolation_results)

        object.__setattr__(self, '_ranked_results', ranked_results)


    # --- Properties ---
    @property
    def ranked_results(self) -> tuple[DEEntryStageResult, ...]:
        """Return the entry results in stage ranking order."""
        return self._ranked_results


    # --- Helper Methods ---
    def _calculate_stage_entry_results(self, main_bracket_results: DEBracketResults, 
            consolation_results: DEBracketResults | None) -> tuple[DEEntryStageResult, ...]:
        """
        Combine main and consolation bracket results into stage standings.

        Start with the main bracket's ranking order and placements. 
        When a consolation bracket exists, 
        its entries occupy the rows immediately after the four main-bracket semifinalists. 
        Only those rows follow the consolation bracket's ranking order.

        A confirmed consolation place is offset by four to obtain the stage place. 
        An unresolved place remains ``None``. 
        For example, if the seventh-place bout finishes before the fifth-place bout, 
        the two consolation finalists still occupy positions 5 and 6, 
        with their places unresolved.

        Stage status comes from the main bracket. 
        ``WINNER`` and ``ACTIVE`` map to stage ``ACTIVE``, and ``ELIMINATED`` maps to stage ``ELIMINATED``. 
        Entries sharing a confirmed stage place are tied. Entries with an unresolved place have ``is_tie=None``.

        Parameters
        ----------
        main_bracket_results : DEBracketResults
            The ranked main-bracket results for all stage participants.
        consolation_results : DEBracketResults | None
            The ranked consolation results, if available. 
            Their entries must match the main-bracket entries in the rows they replace.

        Returns
        -------
        tuple[DEEntryStageResult, ...]
            One result per entry in current stage ranking order.
            `position` is the one-based row in the standings, 
            and `place` is the confirmed finishing place, if available.

        Raises
        ------
        ValueError
            If the consolation entry IDs differ from the IDs in the corresponding slice of the main-bracket standings.
        """
        # Use main-bracket order and places as the starting standings
        ranked_main_results = main_bracket_results.ranked_results
        results_with_stage_places = [(result, result.place) for result in ranked_main_results]

        if consolation_results is not None:
            ranked_consolation_results = consolation_results.ranked_results

            # Consolation starts after the four main-bracket semifinalists
            num_main_semifinalists: int = 4
            consolation_slice: slice = slice(num_main_semifinalists, num_main_semifinalists + len(ranked_consolation_results))

            main_results_by_entry_id: dict[int, DEEntryResult] = {
                result.entry.id: result for result in ranked_main_results[consolation_slice]
            }

            consolation_entry_ids: set[int] = {result.entry.id for result in ranked_consolation_results}

            # Require the same entries so the replacement cannot duplicate or drop a fencer
            if main_results_by_entry_id.keys() != consolation_entry_ids:
                raise ValueError(
                    'Consolation entries must match the main-bracket entries whose stage positions are being replaced'
                )

            # Follow consolation order and keep each fencer's main result for stage status
            consolation_rows: list[tuple[DEEntryResult, int | None]] = []
            for consolation_result in ranked_consolation_results:
                main_result = main_results_by_entry_id[consolation_result.entry.id]
                consolation_place = consolation_result.place
                stage_place = None if consolation_place is None else consolation_place + num_main_semifinalists
                consolation_rows.append((main_result, stage_place))

            results_with_stage_places[consolation_slice] = consolation_rows

        # Count confirmed places after the merge to identify stage ties
        stage_place_counts: dict[int, int] = {}
        for _, stage_place in results_with_stage_places:
            if stage_place is not None:
                stage_place_counts[stage_place] = stage_place_counts.get(stage_place, 0) + 1

        # Assign live positions from the combined row order
        stage_results: list[DEEntryStageResult] = []
        for position, (main_result, stage_place) in enumerate(results_with_stage_places, start=1):
            if main_result.status is DEEntryStatus.ELIMINATED:
                stage_status = StageEntryStatus.ELIMINATED
            else:
                stage_status = StageEntryStatus.ACTIVE

            is_tie = None if stage_place is None else stage_place_counts[stage_place] > 1

            stage_results.append(
                DEEntryStageResult(
                    entry=main_result.entry,
                    stage_number=self.stage_number,
                    status=stage_status,
                    position=position,
                    place=stage_place,
                    is_tie=is_tie
                )
            )

        return tuple(stage_results)


    # --- Validation Helper Methods ---
    def _validate_main_bracket(self, main_bracket: DEBracket, location: str) -> None:
        """
        Validate the main bracket's type, role, and stage number.

        Parameters
        ----------
        main_bracket : DEBracket
            The proposed main bracket for this result snapshot.
        location : str
            The calling class or method name used in error messages.

        Raises
        ------
        TypeError
            If main_bracket is not a DEBracket.
        ValueError
            If the bracket does not have the MAIN role or its stage number differs from this snapshot's stage number.
        """
        if not isinstance(main_bracket, DEBracket):
            raise TypeError(
                f'Main bracket must be a DEBracket in {location} - got {type(main_bracket).__name__}'
            )

        if main_bracket.bracket_role != DEBracketRole.MAIN:
            raise ValueError(f'Main bracket must have the MAIN bracket role in {location}')

        if main_bracket.stage_number != self.stage_number:
            raise ValueError(
                f'Main bracket must belong to stage {self.stage_number} in {location}'
                f' - got stage {main_bracket.stage_number}'
            )

    def _validate_consolation_bracket(self, consolation_bracket: DEBracket, main_bracket: DEBracket, location: str) -> None:
        """
        Validate a supplied consolation bracket against the main bracket.

        Call only when a consolation bracket is supplied. 
        Check its type, role, tournament, stage, and participant membership. 
        These checks do not verify that its participants are specifically the main-bracket quarterfinal losers.

        Parameters
        ----------
        consolation_bracket : DEBracket
            The proposed bracket for stage places 5-8.
        main_bracket : DEBracket
            The validated main bracket defining tournament, stage, and membership.
        location : str
            The calling class or method name used in error messages.

        Raises
        ------
        TypeError
            If consolation_bracket is not a DEBracket.
        ValueError
            If the bracket does not have the CONSOLATION role, 
            belongs to a different tournament or stage, 
            or contains entries outside the main bracket.
        """
        if not isinstance(consolation_bracket, DEBracket):
            raise TypeError(
                f'Consolation bracket must be either None or a DEBracket in {location} - got {type(consolation_bracket).__name__}'
            )

        if consolation_bracket.bracket_role != DEBracketRole.CONSOLATION:
            raise ValueError(
                f'Consolation bracket must have the CONSOLATION bracket role in {location}'
            )

        if consolation_bracket.tournament_id != main_bracket.tournament_id:
            raise ValueError(
                f'The consolation bracket and main bracket must have the same tournament ID in {location}'
            )

        if consolation_bracket.stage_number != main_bracket.stage_number:
            raise ValueError(
                f'The consolation bracket and main bracket must have the same stage number in {location}'
            )

        main_entry_ids = {entry.id for entry in main_bracket.entries}
        consolation_entry_ids = {entry.id for entry in consolation_bracket.entries}

        if not consolation_entry_ids <= main_entry_ids:
            raise ValueError(
                f'The entries in the consolation bracket must be a subset of the entries in the main bracket in {location}'
            )
