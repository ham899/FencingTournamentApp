from dataclasses import dataclass, field, InitVar

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.results.de_bracket_results import DEBracketResults
from de.results.de_entry_result import DEEntryResult, DEEntryStatus
from de.results.de_entry_stage_result import DEEntryStageResult
from entities.seeded_entry import SeededEntry
from tournament.results.stage.stage_results import StageResults
from tournament.results.stage.stage_entry_result import StageEntryStatus


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
    Consolation affects placement only and does not restore eligibility to advance from the stage.

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
        One result per main-bracket entry, ordered by descending main-bracket round reached, 
        main-bracket status (winner, active, eliminated), ascending confirmed stage place, 
        and ascending main-bracket seed.
        Within the same round and status, unresolved places follow confirmed places. 
        Positions are unique, one-based indices in this snapshot; 
        they may change in subsequent snapshots as matches are completed.
        Places may be shared or unresolved. An unresolved place has is_tie=None.

    Notes
    -----
    Consolation places are offset by four, preserving any shared placements.
    Progress within unfinished consolation rounds does not independently control the stage ordering. 
    A stopped main bracket's advancing entries remain ACTIVE with unresolved places, as supplied by DEBracketResults.
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
            or seeded entries fail the type checks in DEBracketResults.
        ValueError
            If the stage number is not positive, bracket roles or stage numbers are inconsistent, 
            the brackets have different tournament IDs, consolation entries are not a subset of main-bracket entries,
            or seeded entries fail the value checks in DEBracketResults.
        """
        # 1. Validate inputs
        location = self.__class__.__name__

        super(DEStageResults, self).__post_init__()

        self._validate_main_bracket(main_bracket, location)

        if consolation_bracket is not None:
            self._validate_consolation_bracket(consolation_bracket, main_bracket, location)

        # 2. Calculate the main-bracket result snapshot
        main_bracket_results = DEBracketResults(
            bracket=main_bracket,
            seeded_entries=seeded_entries
        )

        # 3. Calculate the optional consolation snapshot
        consolation_results = None

        if consolation_bracket is not None:
            consolation_entry_ids = {entry.id for entry in consolation_bracket.entries}

            consolation_seeded_entries = tuple(
                seeded_entry for seeded_entry in seeded_entries if seeded_entry.entry.id in consolation_entry_ids
            )

            consolation_results = DEBracketResults(
                bracket=consolation_bracket,
                seeded_entries=consolation_seeded_entries
            )

        # 4. Convert every entry into a stage result, with or without consolation information
        ranked_results = self._calculate_stage_entry_results(
            main_bracket_results=main_bracket_results,
            consolation_results=consolation_results
        )

        object.__setattr__(self, '_ranked_results', ranked_results)


    # --- Properties ---
    @property
    def ranked_results(self) -> tuple[DEEntryStageResult, ...]:
        """Return the entry results in stage ranking order."""
        return self._ranked_results


    # --- Helper Methods ---
    def _calculate_stage_entry_results(
            self, 
            main_bracket_results: DEBracketResults, 
            consolation_results: DEBracketResults | None) -> tuple[DEEntryStageResult, ...]:
        """
        Resolve bracket placements and construct ordered stage entry results.

        Entries outside consolation retain their main-bracket places. 
        For consolation participants, confirmed consolation places are increased by four; 
        unresolved consolation places produce unresolved stage places.

        Order entries using main-bracket round reached and status, resolved stage place, and main-bracket seed. 
        Assign unique positions after sorting.
        Map main-bracket WINNER and ACTIVE to stage ACTIVE, and main-bracket ELIMINATED to stage ELIMINATED. 
        Count equal confirmed stage places to identify ties; unresolved places receive is_tie=None.

        Parameters
        ----------
        main_bracket_results : DEBracketResults
            The snapshot containing every stage participant's main-bracket result.
        consolation_results : DEBracketResults | None
            Optional snapshot used to resolve stage places 5-8.

        Returns
        -------
        tuple[DEEntryStageResult, ...]
            Stage results in current ranking order, with one result per entry.
            Position represents current ordering rather than a confirmed place.
        """
        consolation_results_by_entry_id: dict[int, DEEntryResult] = {}

        if consolation_results is not None:
            consolation_results_by_entry_id = {result.entry.id: result for result in consolation_results.ranked_results}

        # Step 1: Resolve stage places while retaining main-bracket information
        results_with_places: list[tuple[DEEntryResult, int | None]] = []

        for main_result in main_bracket_results.ranked_results:
            consolation_result = consolation_results_by_entry_id.get(main_result.entry.id)

            if consolation_result is None:
                stage_place = main_result.place
            elif consolation_result.place is None:
                stage_place = None
            else:
                stage_place = consolation_result.place + 4

            results_with_places.append((main_result, stage_place))


        # Step 2: Establish the combined ordering before assigning positions
        status_rank = {DEEntryStatus.WINNER: 0, DEEntryStatus.ACTIVE: 1, DEEntryStatus.ELIMINATED: 2}
        
        results_with_places.sort(
            key=lambda result: (
                -result[0].round_reached,
                status_rank[result[0].status],
                result[1] if result[1] is not None else float('inf'),
                result[0].bracket_seed
            )
        )


        # Step 3: Count confirmed placements to identify ties
        place_counts: dict[int, int] = {}

        for _, place in results_with_places:
            if place is not None:
                place_counts[place] = place_counts.get(place, 0) + 1


        # Step 4: Translate each bracket result into the shared stage interface
        stage_results: list[DEEntryStageResult] = []

        for position, (main_result, stage_place) in enumerate(results_with_places, start=1):
            if main_result.status is DEEntryStatus.ELIMINATED:
                stage_status = StageEntryStatus.ELIMINATED
            else:
                stage_status = StageEntryStatus.ACTIVE
            
            if stage_place is None:
                is_tie = None
            else:
                is_tie = place_counts[stage_place] > 1

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
