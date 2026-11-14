import datetime as dt

from dataclasses import dataclass, field, InitVar
from math import floor
from zoneinfo import ZoneInfo

import validation

from de.de_stage import DEStage
from de.results.de_stage_results import DEStageResults
from entities import Fencer, SeededEntry, TournamentEntry
from poules.poule_stage import PouleStage
from poules.results.poule_stage_results import PouleStageResults
from tournament.configs import DEConfig, PouleConfig, TournamentConfig
from tournament.results.stage import StageEntryStatus, StageResults
from tournament.results.tournament_results import TournamentResults
from tournament.tournament_stage import TournamentStage


@dataclass(eq=False)
class Tournament:
    """
    Represent a fencing club tournament and coordinate its configured stages.

    Fencers are supplied in initial seed order. 
    Initialization creates their tournament entries and the first configured stage. 
    Later stages are created explicitly as the tournament advances.

    Parameters
    ----------
    id : int
        The tournament's unique identifier. 
    fencers : tuple[Fencer, ...]
        At least two distinct fencers in initial seed order, with the highest-seeded fencer first. 
        Used during initialization only.
    config : TournamentConfig
        The tournament's stage sequence and settings.
    name : str | None, optional
        An optional descriptive name for the tournament.
    random_seed : int | None, optional
        A non-negative seed passed to stages that use randomization.
        Defaults to None.
    date : datetime.datetime, optional
        The tournament's date and time. 
        Defaults to the current time in America/Vancouver.

    Attributes
    ----------
    initial_seeded_entries : tuple[SeededEntry, ...]
        All tournament entries in initial seed order. 
        These seeds are retained as the tournament advances; 
        each stage maintains its own seeding.
    stages : list[TournamentStage]
        The stages created so far, in tournament order. 
    """
    id: int
    fencers: InitVar[tuple[Fencer, ...]]
    config: TournamentConfig

    name: str | None = None
    random_seed: int | None = None
    date: dt.datetime = field(default_factory=lambda: dt.datetime.now(ZoneInfo('America/Vancouver')))

    initial_seeded_entries: tuple[SeededEntry, ...] = field(init=False)
    stages: list[TournamentStage] = field(init=False, default_factory=list)


    # --- Initialization and Validation ---
    def __post_init__(self, fencers: tuple[Fencer, ...]) -> None:
        """
        Validate inputs, create the initial entries, and create the first stage.

        Raises
        ------
        TypeError
            If an input has an invalid type.
        ValueError
            If an input value is invalid, fewer than two fencers are supplied, fencer IDs are repeated, 
            or if the configured stage sequence fails the conservative participant-count check.
        """
        location = self.__class__.__name__

        # Validate the input parameters
        validation.validate_positive_int(self.id, 'Tournament ID', location)
        self._validate_fencers(fencers, location)
        self._validate_config(self.config, location)
        validation.validate_optional_string(self.name, 'Tournament name', location)
        self._validate_date(self.date, location)
        validation.validate_optional_non_negative_int(self.random_seed, 'Random seed', location)

        # Validate participant counts throughout the configured stage sequence
        self._validate_participant_flow(len(fencers), location)

        # Create the tournament entries in initial seed order
        self.initial_seeded_entries = self._create_seeded_entries(fencers)

        # Create the first configured stage
        self.stages.append(self._create_stage(stage_index=0, seeded_entries=self.initial_seeded_entries))


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return an identifying label containing the tournament ID."""
        return f'Tournament {self.id}'

    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """
        Return all tournament entries in initial seed order.

        Includes entries that have been eliminated or have not advanced to later stages.
        """
        return tuple(seeded_entry.entry for seeded_entry in self.initial_seeded_entries)

    @property
    def num_entries(self) -> int:
        """Return the total number of entries in the tournament, including eliminated entries."""
        return len(self.initial_seeded_entries)

    @property
    def num_stages(self) -> int:
        """Return the total number of planned, configured stages for the tournament."""
        return len(self.config.stage_configs)

    @property
    def current_stage_number(self) -> int | None:
        """Return the one-based current stage number, or None if complete."""
        return None if self.is_complete() else len(self.stages)

    @property
    def current_stage_index(self) -> int | None:
        """Return the zero-based current stage index, or None if complete."""
        stage_number = self.current_stage_number
        return None if stage_number is None else stage_number - 1

    @property
    def current_stage(self) -> TournamentStage | None:
        """Return the current stage, or None if the tournament is complete."""
        stage_index = self.current_stage_index
        return None if stage_index is None else self.stages[stage_index]


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """Compare tournaments by ID; return NotImplemented for other types."""
        if not isinstance(other, Tournament):
            return NotImplemented

        return self.id == other.id


    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Return whether competition has begun in the first stage."""
        return self.stages[0].has_started()

    def is_complete(self) -> bool:
        """Return whether all configured stages have been created and completed."""
        return (
            len(self.stages) == self.num_stages and 
            all(stage.is_complete() for stage in self.stages)
        )

    def is_incomplete(self) -> bool:
        """Return whether the tournament still has stages to create or complete."""
        return not self.is_complete()


    # --- Access Methods ---
    def get_stage_at(self, index: int) -> TournamentStage:
        """
        Return the created stage at the given zero-based index.

        Stages remain accessible after the tournament is complete.
        Configured stages that have not yet been created cannot be accessed.

        Parameters
        ----------
        index : int
            The zero-based index of the stage to retrieve.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the range of created stages.
        """
        self._validate_stage_index_for_accessing(index, 'get_stage_at')
        return self.stages[index]


    # --- Poule Stage Result Recording Methods ---
    def record_poule_match_score(self, stage_index: int, round_index: int, poule_index: int, 
                                 match_index: int, score1: int, score2: int) -> None:
        """
        Record scores for an incomplete match in the specified poule stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a PouleStage. 
        Scores correspond to the match's first and second entries.

        Earlier stages require tournament rollback before modification.
        The poule stage enforces its own round and match restrictions.
        """
        stage = self._get_latest_poule_stage_at(stage_index, 'record_poule_match_score')
        stage.record_match_score(round_index, poule_index, match_index, score1, score2)

    def record_poule_match_forfeit(self, stage_index: int, round_index: int, poule_index: int, 
                                   match_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for an incomplete match in the specified poule stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a PouleStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Earlier stages require tournament rollback before modification.
        The poule stage enforces its own round and match restrictions.
        """
        stage = self._get_latest_poule_stage_at(stage_index, 'record_poule_match_forfeit')
        stage.record_forfeit(round_index, poule_index, match_index, forfeiting_index)

    def replace_poule_match_result_with_score(self, stage_index: int, round_index: int, poule_index: int, 
                                              match_index: int, score1: int, score2: int) -> None:
        """
        Replace an existing match result with scores in the specified poule stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a PouleStage. 
        Scores correspond to the match's first and second entries.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The poule stage enforces its own round and match restrictions.
        """
        stage = self._get_latest_poule_stage_at(stage_index, 'replace_poule_match_result_with_score')
        stage.replace_with_score(round_index, poule_index, match_index, score1, score2)

    def replace_poule_match_result_with_forfeit(self, stage_index: int, round_index: int, poule_index: int, 
                                                match_index: int, forfeiting_index: int) -> None:
        """
        Replace an existing match result with a forfeit in the specified poule stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a PouleStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The poule stage enforces its own round and match restrictions.
        """
        stage = self._get_latest_poule_stage_at(stage_index, 'replace_poule_match_result_with_forfeit')
        stage.replace_with_forfeit(round_index, poule_index, match_index, forfeiting_index)


    # --- DE Stage Main Bracket Result Recording Methods ---
    def record_de_match_score(self, stage_index: int, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Record scores for an incomplete main-bracket match in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        Scores correspond to the match's first and second entries.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces its own round and matchup restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_match_score')
        stage.record_match_score(round_index, matchup_index, score1, score2)

    def record_de_match_forfeit(self, stage_index: int, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for an incomplete main-bracket match in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces its own round and matchup restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_match_forfeit')
        stage.record_forfeit(round_index, matchup_index, forfeiting_index)

    def replace_de_match_result_with_score(self, stage_index: int, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Replace an existing main-bracket match result with scores in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        Scores correspond to the match's first and second entries.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces its own round and matchup restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_match_result_with_score')
        stage.replace_with_score(round_index, matchup_index, score1, score2)

    def replace_de_match_result_with_forfeit(self, stage_index: int, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Replace an existing main-bracket match result with a forfeit in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces its own round and matchup restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_match_result_with_forfeit')
        stage.replace_with_forfeit(round_index, matchup_index, forfeiting_index)


    # --- DE Stage Third-Place Matchup Result Recording Methods ---
    def record_de_third_place_match_score(self, stage_index: int, score1: int, score2: int) -> None:
        """
        Record scores for an incomplete third-place match in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        Scores correspond to the match's first and second entries.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces the third-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_third_place_match_score')
        stage.record_third_place_match_score(score1, score2)

    def record_de_third_place_match_forfeit(self, stage_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for an incomplete third-place match in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces the third-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_third_place_match_forfeit')
        stage.record_third_place_match_forfeit(forfeiting_index)

    def replace_de_third_place_match_with_score(self, stage_index: int, score1: int, score2: int) -> None:
        """
        Replace an existing third-place match result with scores in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        Scores correspond to the match's first and second entries.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces the third-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_third_place_match_with_score')
        stage.replace_third_place_match_with_score(score1, score2)

    def replace_de_third_place_match_with_forfeit(self, stage_index: int, forfeiting_index: int) -> None:
        """
        Replace an existing third-place match result with a forfeit in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces the third-place matchup's availability and restrictions.
        """ 
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_third_place_match_with_forfeit')
        stage.replace_third_place_match_with_forfeit(forfeiting_index)


    # --- DE Stage Consolation Bracket Result Recording Methods ---
    def record_de_consolation_match_score(self, stage_index: int, consol_round_index: int, consol_matchup_index: int, 
                                          score1: int, score2: int) -> None:
        """
        Record scores for an incomplete consolation match in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        The round and matchup indices refer to the consolation bracket. 
        Scores correspond to the match's first and second entries.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces the consolation bracket's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_consolation_match_score')
        stage.record_consolation_match_score(consol_round_index, consol_matchup_index, score1, score2)

    def record_de_consolation_match_forfeit(self, stage_index: int, consol_round_index: int, consol_matchup_index: int, 
                                            forfeiting_index: int) -> None:
        """
        Record a forfeit for an incomplete consolation match in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        The round and matchup indices refer to the consolation bracket. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces the consolation bracket's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_consolation_match_forfeit')
        stage.record_consolation_match_forfeit(consol_round_index, consol_matchup_index, forfeiting_index)

    def replace_de_consolation_match_with_score(self, stage_index: int, consol_round_index: int, consol_matchup_index: int, 
                                                 score1: int, score2: int) -> None:
        """
        Replace an existing consolation match result with scores in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        The round and matchup indices refer to the consolation bracket. 
        Scores correspond to the match's first and second entries.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces the consolation bracket's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_consolation_match_with_score')
        stage.replace_consolation_match_with_score(consol_round_index, consol_matchup_index, score1, score2)

    def replace_de_consolation_match_with_forfeit(self, stage_index: int, consol_round_index: int, consol_matchup_index: int, 
                                                  forfeiting_index: int) -> None:
        """
        Replace an existing consolation match result with a forfeit in the specified DE stage.

        All indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a DEStage. 
        The round and matchup indices refer to the consolation bracket. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces the consolation bracket's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_consolation_match_with_forfeit')
        stage.replace_consolation_match_with_forfeit(consol_round_index, consol_matchup_index, forfeiting_index)


    # --- DE Stage Consolation Bracket Seventh-Place Matchup Result Recording Methods ---
    def record_de_seventh_place_consolation_match_score(self, stage_index: int, score1: int, score2: int) -> None:
        """
        Record scores for an incomplete seventh-place match in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        Scores correspond to the match's first and second entries.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces the seventh-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_seventh_place_consolation_match_score')
        stage.record_seventh_place_match_score(score1, score2)

    def record_de_seventh_place_consolation_match_forfeit(self, stage_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit for an incomplete seventh-place match in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Earlier stages require tournament rollback before modification.
        The DE stage enforces the seventh-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'record_de_seventh_place_consolation_match_forfeit')
        stage.record_seventh_place_match_forfeit(forfeiting_index)

    def replace_de_seventh_place_consolation_match_with_score(self, stage_index: int, score1: int, score2: int) -> None:
        """
        Replace an existing seventh-place match result with scores in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        Scores correspond to the match's first and second entries.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces the seventh-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_seventh_place_consolation_match_with_score')
        stage.replace_seventh_place_match_with_score(score1, score2)

    def replace_de_seventh_place_consolation_match_with_forfeit(self, stage_index: int, forfeiting_index: int) -> None:
        """
        Replace an existing seventh-place match result with a forfeit in the specified DE stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a DEStage. 
        ``forfeiting_index`` is 0 for the match's first entry or 1 for its second entry.

        Tournament completion does not prevent corrections to the latest stage.
        Earlier stages require tournament rollback before modification.
        The DE stage enforces the seventh-place matchup's availability and restrictions.
        """
        stage = self._get_latest_de_stage_at(stage_index, 'replace_de_seventh_place_consolation_match_with_forfeit')
        stage.replace_seventh_place_match_with_forfeit(forfeiting_index)


    # --- Round Management Methods ---
    def advance_poule_round(self, stage_index: int) -> None:
        """
        Create the next round in the specified poule stage.

        ``stage_index`` is zero-based and must identify the latest created tournament stage, which must be a PouleStage.

        The poule stage validates that advancement is allowed and creates the next round using its seeding rules. 
        Earlier stages require tournament rollback before modification.
        """
        stage = self._get_latest_poule_stage_at(stage_index, 'advance_poule_round')
        stage.advance_round()

    def rollback_to_poule_round(self, stage_index: int, round_index: int) -> None:
        """
        Roll back the specified poule stage to an existing round.

        Both indices are zero-based. 
        ``stage_index`` must identify the latest created tournament stage, which must be a PouleStage.

        The target round is retained, and subsequent rounds and their results are discarded. 
        Earlier stages require tournament rollback before their rounds can be modified.

        Rollback may be requested after tournament completion.
        The poule stage validates the target round and performs the rollback.
        """
        stage = self._get_latest_poule_stage_at(stage_index, 'rollback_to_poule_round')
        stage.rollback_to_round(round_index)


    # --- Stage Management Methods ---
    def advance_stage(self) -> None:
        """
        Create the next configured stage using the latest stage's final results.

        All existing stages must be complete. Active entries advance in ranked
        order, receiving consecutive seeds and retaining their previous places.

        Raises
        ------
        RuntimeError
            If no configured stages remain, an existing stage is incomplete,
            or fewer than two entries qualify for the next stage.

        Notes
        -----
        The new stage is appended only after its construction succeeds.
        """
        next_stage_index = len(self.stages)

        if next_stage_index >= self.num_stages:
            raise RuntimeError(
                f'Cannot advance {self.label} to the next stage since there are no more stages to advance to'
            )

        if any(stage.is_incomplete() for stage in self.stages):
            raise RuntimeError(
                f'Cannot advance {self.label} to the next stage because not all existing stages are complete yet'
            )

        advancing_seeded_entries = self._get_seeded_advancing_entries()

        if len(advancing_seeded_entries) < 2:
            raise RuntimeError(
                f'Cannot advance {self.label} to the next stage because there needs to be at least '
                f'two advancing entries - got {len(advancing_seeded_entries)} advancing entries'
            )

        next_stage = self._create_stage(
            stage_index=next_stage_index,
            seeded_entries=advancing_seeded_entries
        )

        self.stages.append(next_stage)

    def rollback_to_stage(self, stage_index: int) -> None:
        """
        Retain the specified stage and discard all subsequent stages.

        ``stage_index`` is zero-based and must identify an existing stage.
        The retained stage's rounds, matches, and results are unchanged.
        Discarded stages must be recreated through normal advancement.

        Rollback is allowed after tournament completion. 
        Selecting the latest created stage leaves the tournament unchanged.

        Raises
        ------
        TypeError
            If ``stage_index`` is not an integer.
        ValueError
            If ``stage_index`` is outside the range of created stages.
        """
        self._validate_stage_index_for_accessing(stage_index, 'rollback_to_stage')

        del self.stages[stage_index + 1:]


    # --- Result Calculation Methods ---
    def calculate_stage_results_at(self, stage_index: int) -> StageResults:
        """
        Return a snapshot of the specified stage's current results.

        ``stage_index`` is zero-based and must identify an existing stage.
        The stage may be incomplete or complete.
        """
        return self.get_stage_at(stage_index).calculate_results()

    def calculate_poule_stage_results_at(self, stage_index: int) -> PouleStageResults:
        """
        Return a snapshot of the specified poule stage's current results.

        ``stage_index`` is zero-based and must identify an existing PouleStage.
        The stage may be incomplete or complete.
        """
        stage = self._get_poule_stage_at(stage_index, 'calculate_poule_stage_results_at')
        return stage.calculate_results()

    def calculate_de_stage_results_at(self, stage_index: int) -> DEStageResults:
        """
        Return a snapshot of the specified DE stage's current results.

        ``stage_index`` is zero-based and must identify an existing DEStage.
        The stage may be incomplete or complete.
        """
        stage = self._get_de_stage_at(stage_index, 'calculate_de_stage_results_at')
        return stage.calculate_results()

    def calculate_results(self) -> TournamentResults:
        """Return a snapshot of the tournament's current results."""
        return TournamentResults(
            stages=self.stages, 
            is_complete=self.is_complete()
        )

    def calculate_final_results(self) -> TournamentResults:
        """
        Return a snapshot of the completed tournament's results.

        Raises
        ------
        RuntimeError
            If the tournament is incomplete.
        """
        if self.is_incomplete():
            raise RuntimeError(
                f'Cannot calculate final results for {self.label} since the tournament is not complete yet'
            )

        return self.calculate_results()


    # --- Creation Helper Methods ---
    def _create_seeded_entries(self, fencers: tuple[Fencer, ...]) -> tuple[SeededEntry, ...]:
        """
        Create tournament entries and initial seeds from validated fencers.

        Fencers retain their supplied order. 
        Entry IDs and seeds are assigned consecutively from 1. 
        Entry IDs are local to this tournament.
        Each seeded entry starts with no previous placement.
        """
        return tuple(
            SeededEntry(
                entry=TournamentEntry(
                    id=seed,
                    tournament_id=self.id,
                    fencer=fencer
                ),
                seed=seed,
                previous_place=None
            )
            for seed, fencer in enumerate(fencers, start=1)
        )

    def _create_stage(self, stage_index: int, seeded_entries: tuple[SeededEntry, ...]) -> TournamentStage:
        """
        Construct a stage using its configured settings and supplied seeding.

        ``stage_index`` is zero-based and identifies a configured stage, which need not exist yet. 
        The returned stage is not appended to stages.

        The concrete stage validates its settings and seeded entries.

        Raises
        ------
        TypeError
            If ``stage_index`` has an invalid type or the stage configuration is neither a PouleConfig nor a DEConfig.
        ValueError
            If stage_index is outside the range of configured stages.
        """
        self._validate_stage_index(stage_index, '_create_stage')

        stage_config = self.config.stage_configs[stage_index]
        stage_number = stage_index + 1

        if isinstance(stage_config, PouleConfig):
            return PouleStage(
                stage_number=stage_number,
                seeded_entries=seeded_entries,
                num_rounds=stage_config.num_rounds,
                score_to_win=stage_config.score_to_win,
                cut_value=self._get_post_stage_cut_value(stage_index),
                random_seed=self.random_seed
            )

        if isinstance(stage_config, DEConfig):
            return DEStage(
                stage_number=stage_number,
                seeded_entries=seeded_entries,
                score_to_win=stage_config.score_to_win,
                has_third_place_match=stage_config.has_third_place_match,
                use_consolation_bracket=stage_config.use_consolation_bracket,
                stop_at_round=stage_config.stop_at_round
            )

        raise TypeError(
            f'Unknown stage config type {type(stage_config).__name__} '
            f'in {self.__class__.__name__}._create_stage() for {self.label}'
        )


    # --- Stage Retrieval Helper Methods ---
    def _get_poule_stage_at(self, stage_index: int, method_name: str) -> PouleStage:
        """Return an existing poule stage at the given zero-based index."""
        self._validate_stage_index_for_accessing(stage_index, method_name)
        stage = self.stages[stage_index]

        if not isinstance(stage, PouleStage):
            raise TypeError(
                f'Stage at index {stage_index} must be a PouleStage '
                f'in Tournament.{method_name}() - got {type(stage).__name__}'
            )
        
        return stage

    def _get_de_stage_at(self, stage_index: int, method_name: str) -> DEStage:
        """Return an existing DE stage at the given zero-based index."""
        self._validate_stage_index_for_accessing(stage_index, method_name)
        stage = self.stages[stage_index]

        if not isinstance(stage, DEStage):
            raise TypeError(
                f'Stage at index {stage_index} must be a DEStage '
                f'in Tournament.{method_name}() - got {type(stage).__name__}'
            )

        return stage

    def _get_latest_poule_stage_at(self, stage_index: int, method_name: str) -> PouleStage:
        """
        Return the requested poule stage only if it is the latest created stage.

        The stage remains accessible through this helper after completion.
        Earlier stages require tournament rollback before modification.
        """
        stage = self._get_poule_stage_at(stage_index, method_name)
        self._validate_stage_index_is_latest_stage(stage_index, method_name)
        return stage

    def _get_latest_de_stage_at(self, stage_index: int, method_name: str) -> DEStage:
        """
        Return the requested DE stage only if it is the latest created stage.

        The stage remains accessible through this helper after completion.
        Earlier stages require tournament rollback before modification.
        """
        stage = self._get_de_stage_at(stage_index, method_name)
        self._validate_stage_index_is_latest_stage(stage_index, method_name)
        return stage


    # --- Entry Advancement Helper Methods ---
    def _get_seeded_advancing_entries(self) -> tuple[SeededEntry, ...]:
        """
        Seed active entries from the latest created stage's final results.

        The stage must be complete. 
        Active entries retain their ranked order and receive consecutive seeds starting at 1. 
        Each entry's stage placement is carried forward as ``previous_place``, preserving ties.
        """
        stage_results = self.stages[-1].calculate_final_results()

        advancing_results = (result for result in stage_results.ranked_results if result.status is StageEntryStatus.ACTIVE)

        return tuple(
            SeededEntry(
                entry=result.entry, 
                seed=seed, 
                previous_place=result.place
            ) 
            for seed, result in enumerate(advancing_results, start=1)
        )

    def _get_post_stage_cut_value(self, stage_index: int) -> float:
        """
        Return the configured cut proportion for the specified stage.

        ``stage_index`` must be a valid zero-based index into ``stage_configs``.
        The stage need not have been created.

        Return 0.0 if cuts are unspecified, the stage is not a poule stage, or the stage is the tournament's final stage. 
        Otherwise, select the cut by counting the poule stages preceding this stage.
        """
        if self.config.poule_cut_values is None:
            return 0.0
        
        if stage_index == self.num_stages - 1:
            return 0.0

        if not isinstance(self.config.stage_configs[stage_index], PouleConfig):
            return 0.0

        # Next poule index is the sum of all previous poule stage occurrences
        poule_index: int = sum(isinstance(stage_config, PouleConfig) for stage_config in self.config.stage_configs[:stage_index])

        return self.config.poule_cut_values[poule_index]


    # --- Validation Helper Methods ---
    def _validate_fencers(self, fencers: tuple[Fencer, ...], location: str) -> None:
        """
        Validate the fencers supplied for initial tournament seeding.

        Require a tuple containing at least two Fencer objects with positive,
        unique IDs and valid display names. Input order is preserved.

        Raises
        ------
        TypeError
            If fencers is not a tuple, an item is not a Fencer, 
            or a validated fencer attribute has an invalid type.
        ValueError
            If fewer than two fencers are supplied, an ID or display name is invalid, 
            or fencer IDs are repeated.
        """
        if not isinstance(fencers, tuple):
            raise TypeError(
                f'Fencers must be a tuple in {location} - got {type(fencers).__name__}'
            )

        if len(fencers) < 2:
            raise ValueError(
                f'{self.__class__.__name__} must have at least two fencers in {location} - got {len(fencers)}'
            )

        seen_fencer_ids: set[int] = set()

        for index, fencer in enumerate(fencers):
            if not isinstance(fencer, Fencer):
                raise TypeError(
                    f'Fencer at index {index} must be a Fencer object in {location} - got {type(fencer).__name__}'
                )

            validation.validate_positive_int(fencer.id, 'Fencer ID', location)
            validation.validate_string(fencer.display_name, 'Fencer display name', location)

            if fencer.id in seen_fencer_ids:
                raise ValueError(
                    f'Duplicate fencer ID {fencer.id} in {location}'
                )

            seen_fencer_ids.add(fencer.id)

    def _validate_config(self, config: TournamentConfig, location: str) -> None:
        """
        Validate the configuration object's type.

        TournamentConfig is responsible for validating its own settings.

        Raises
        ------
        TypeError
            If config is not a TournamentConfig.
        """
        if not isinstance(config, TournamentConfig):
            raise TypeError(
                f'Config must be a TournamentConfig object in {location} - got {type(config).__name__}'
            )

    def _validate_date(self, date: dt.datetime, location: str) -> None:
        """
        Validate that date is a datetime object.

        Both timezone-aware and naive datetime objects are accepted.

        Raises
        ------
        TypeError
            If date is not a datetime object.
        """
        if not isinstance(date, dt.datetime):
            raise TypeError(
                f'Date must be a datetime object in {location} - got {type(date).__name__}'
            )

    def _validate_stage_index(self, index: int, location: str) -> None:
        """
        Validate a zero-based index into the configured stage sequence.

        The corresponding stage need not have been created.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the range of configured stages.
        """
        validation.validate_int_in_range(index, 0, self.num_stages - 1, 'Stage index', self.__class__.__name__, location)

    def _validate_stage_index_for_accessing(self, index: int, location: str) -> None:
        """
        Validate a zero-based index into the created stages.

        Created stages remain accessible after tournament completion.

        Raises
        ------
        TypeError
            If index is not an integer.
        ValueError
            If index is outside the range of created stages.
        """
        validation.validate_int_in_range(index, 0, len(self.stages) - 1, 'Stage index', self.__class__.__name__, location)

    def _validate_stage_index_is_latest_stage(self, index: int, location: str) -> None:
        """
        Validate that an already-validated index identifies the latest stage.

        The caller must first validate index against the created stages.
        The latest stage may be incomplete or complete.

        Raises
        ------
        ValueError
            If index identifies an earlier stage.
        """
        latest_stage_index = len(self.stages) - 1

        if index != latest_stage_index:
            raise ValueError(
                f'Stage index must identify the latest created stage at index {latest_stage_index} '
                f'in {self.__class__.__name__}.{location}() - got stage_index={index}'
            )

    def _validate_participant_flow(self, num_entries: int, location: str) -> None:
        """
        Validate that the configured stages support a conservative participant count.

        Start with the validated initial entry count and follow the configured stage sequence. 
        Estimate the maximum poule eliminations by rounding the cut count downward, 
        without relying on ties to preserve additional entries.

        For stopped DE stages, 
        calculate the number of entries reaching the stopping round from the estimated bracket size.

        Raises
        ------
        ValueError
            If a stage's participant requirements cannot be satisfied using the conservative estimate.

        Notes
        -----
        Fencers and configuration must already be validated. 
        This check may reject configurations that would be feasible with fewer eliminations.
        """
        remaining_entries: int = num_entries

        for stage_index, stage_config in enumerate(self.config.stage_configs):
            stage_number = stage_index + 1

            if remaining_entries < 2:
                raise ValueError(
                    f'Stage {stage_number} requires at least 2 entries in {location}'
                    f', but the conservative estimate leaves {remaining_entries}'
                )
        
            if isinstance(stage_config, PouleConfig):
                cut_value = self._get_post_stage_cut_value(stage_index)
                remaining_entries -= floor(remaining_entries * cut_value)
                continue

            if stage_config.has_third_place_match and remaining_entries < 4:
                raise ValueError(
                    f'Stage {stage_number} requires at least 4 entries for a third-place match in {location}'
                    f', but the conservative estimate leaves {remaining_entries}'
                )

            if stage_config.use_consolation_bracket and remaining_entries < 6:
                raise ValueError(
                    f'Stage {stage_number} requires at least 6 entries for a consolation bracket in {location}'
                    f', but the conservative estimate leaves {remaining_entries}'
                )
            
            stop_at_round = stage_config.stop_at_round

            if stop_at_round is not None:
                num_rounds = (remaining_entries - 1).bit_length()

                if not 2 <= stop_at_round < num_rounds:
                    raise ValueError(
                        f'Stage {stage_number} cannot likely stop at round {stop_at_round} in {location}; '
                        f'The conservative estimate of {remaining_entries} entries produces {num_rounds} rounds, '
                        f'and the stopping round must be between round 2 and the penultimate round'
                    )
                
                remaining_entries = 2 ** (num_rounds - stop_at_round + 1)
