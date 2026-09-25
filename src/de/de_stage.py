from dataclasses import dataclass, field, InitVar

import validation

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.de_matchup import DEMatchup
from de.results.de_stage_results import DEStageResults
from entities.seeded_entry import SeededEntry
from entities.tournament_entry import TournamentEntry


@dataclass(eq=False)
class DEStage:
    """
    Represent and manage a direct-elimination stage within a tournament.

    The stage owns a main direct-elimination bracket and 
    can optionally create a consolation bracket from the quarter-final losers to determine places five through eight. 
    
    It coordinates result changes across those brackets and 
    restores their prior state if consolation-bracket creation fails.

    Additionally, the main bracket can optionally stop before a configured round, 
    allowing the entries reaching that round to advance to a later tournament stage.
    A stopped stage **cannot** use third-place or consolation classification matches.

    Parameters
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    seeded_entries : tuple[SeededEntry, ...]
        The participating entries and their starting seeds.
    score_to_win : int, default=15
        The target score and maximum permitted recorded score for either entry.
    has_third_place_match : bool, default=False
        Whether the main bracket includes a match for third and fourth place.
    use_consolation_bracket : bool, default=False
        Whether quarter-final losers fence for places five through eight.
    stop_at_round : int | None, default=None
        The one-based number of the first main-bracket round that will not be fenced. 
        Entries reaching this round qualify to advance.

    Attributes
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    seeded_entries : tuple[SeededEntry, ...]
        The participating entries in ascending seed order.
    score_to_win : int
        The target score and maximum permitted recorded score for either entry.
    use_consolation_bracket : bool
        Whether this stage uses a consolation bracket.
    stop_at_round : int | None
        The one-based stopping-round number, or ``None`` if the main bracket is fenced to completion.
    main_bracket : DEBracket
        The stage's primary direct-elimination bracket.
    consolation_bracket : DEBracket | None
        The bracket for quarter-final losers, once those entries are known.
    """
    stage_number: int
    seeded_entries: tuple[SeededEntry, ...]
    score_to_win: int = field(default=15, kw_only=True)

    has_third_place_match: InitVar[bool] = field(default=False, kw_only=True)
    use_consolation_bracket: bool = field(default=False, kw_only=True)
    stop_at_round: int | None = field(default=None, kw_only=True)

    main_bracket: DEBracket = field(init=False)
    consolation_bracket: DEBracket | None = field(default=None, init=False)


    # --- Initialization and Validation ---
    def __post_init__(self, has_third_place_match: bool) -> None:
        """
        Validate the stage configuration and create the main bracket.

        Raises
        ------
        TypeError
            If an option has an invalid type, ``seeded_entries`` is not a tuple, 
            or a seeded item or its entry has an invalid type.
        ValueError
            If an integer is outside its permitted range, fewer than two entries are supplied, 
            entries or seeds are duplicated, entries belong to different tournaments, 
            an optional classification format does not have enough entries, 
            or incompatible bracket options are combined.
        """
        validation.validate_positive_int(self.stage_number, 'Stage number', 'DEStage')
        validation.validate_positive_int(self.score_to_win, 'Score to win', 'DEStage')

        self._validate_seeded_entries(self.seeded_entries)

        self.seeded_entries = tuple(sorted(self.seeded_entries, key=lambda seeded_entry: seeded_entry.seed))

        if type(has_third_place_match) is not bool:
            raise TypeError(f'The third-place match option must be a boolean - got {type(has_third_place_match).__name__}')
        
        if has_third_place_match and len(self.seeded_entries) < 4:
            raise ValueError(f'If a third-place match is chosen, there must be at least 4 seeded entries provided - got {len(self.seeded_entries)} entries')

        if type(self.use_consolation_bracket) is not bool:
            raise TypeError(f'The consolation bracket option must be a boolean - got {type(self.use_consolation_bracket).__name__}')
        
        if self.use_consolation_bracket and len(self.seeded_entries) < 6:
            raise ValueError(f'If a consolation bracket is chosen, there must be at least 6 seeded entries provided - got {len(self.seeded_entries)} entries')

        ordered_entries = tuple(seeded_entry.entry for seeded_entry in self.seeded_entries)

        self.main_bracket = DEBracket(
            stage_number = self.stage_number,
            seed_ordered_entries = ordered_entries,
            bracket_role = DEBracketRole.MAIN,
            score_to_win = self.score_to_win,
            has_third_place_match = has_third_place_match,
            stop_at_round = self.stop_at_round
        )

        if self.use_consolation_bracket and self.has_stop_round():
            raise ValueError(f'{self.label} cannot have a stopped main bracket and have a consolation bracket')


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying this DE stage."""
        return f'DE stage {self.stage_number} in tournament {self.tournament_id}'

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the stage entries."""
        return self.seeded_entries[0].entry.tournament_id

    @property
    def num_entries(self) -> int:
        """Return the number of entries participating in the stage."""
        return len(self.seeded_entries)

    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """Return the participating tournament entries in seed order."""
        return tuple(seeded_entry.entry for seeded_entry in self.seeded_entries)

    @property
    def qualified_entries(self) -> tuple[TournamentEntry, ...]:
        """Return entries that have reached the main bracket's stopping round."""
        return self.main_bracket.qualified_entries

    @property
    def num_qualified_entries(self) -> int:
        """Return the number of entries that have reached the stopping round."""
        return self.main_bracket.num_qualified_entries

    @property
    def advancing_entries(self) -> tuple[TournamentEntry, ...]:
        """Return entries advancing from the completed stopped main bracket."""
        return self.main_bracket.advancing_entries

    @property
    def expected_num_advancing_entries(self) -> int:
        """Return the expected number of advancing entries."""
        return self.main_bracket.expected_num_advancing_entries


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """
        Return whether ``other`` represents the same DE stage.

        Equality is based on tournament ID and stage number. Bracket state,
        configuration options, and recorded results are not considered.
        """
        if not isinstance(other, DEStage):
            return False
        
        return self.tournament_id == other.tournament_id and self.stage_number == other.stage_number


    # --- Predicate Methods ---
    def is_complete(self) -> bool:
        """
        Return whether every required bracket in the stage is complete.

        A stage without consolation is complete when its main bracket is complete. 
        A stage using consolation also requires the consolation bracket to exist and be complete.
        """
        if not self.main_bracket.is_complete():
            return False
        
        if not self.use_consolation_bracket:
            return True
        
        return self.consolation_bracket is not None and self.consolation_bracket.is_complete()
    
    def is_incomplete(self) -> bool:
        """Return whether the stage still has required matches to complete."""
        return not self.is_complete()
    
    def has_third_place_matchup(self) -> bool:
        """Return whether the main bracket includes a third-place matchup."""
        return self.main_bracket.has_third_place_matchup()

    def has_consolation_bracket(self) -> bool:
        """Return whether this DE stage has a consolation bracket."""
        return self.consolation_bracket is not None

    def has_stop_round(self) -> bool:
        """Return whether the main bracket of this DE stage has a stopping round."""
        return self.main_bracket.has_stop_round()

    def has_started(self) -> bool:
        """Return whether a result has been recorded in the main bracket."""
        return self.main_bracket.has_started()
    
    def has_entry(self, entry: TournamentEntry) -> bool:
        """
        Return whether ``entry`` participates in this stage.

        Parameters
        ----------
        entry : TournamentEntry
            The entry to locate.

        Returns
        -------
        bool
            ``True`` if the entry participates; otherwise, ``False``.

        Raises
        ------
        TypeError
            If ``entry`` is not a ``TournamentEntry``.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be a tournament entry object in DEStage.has_entry() - got {type(entry).__name__}')
        
        return entry in self.entries
    
    def _is_quarter_final_matchup(self, round_index: int, matchup_index: int) -> bool:
        """
        Return whether the indexed main-bracket matchup is a quarter-final.

        Raises
        ------
        TypeError
            If either index is not an integer.
        ValueError
            If either index is outside its valid range.
        """
        self.main_bracket.get_matchup(round_index, matchup_index)
        
        return self.main_bracket.num_rounds >= 3 and round_index == self.main_bracket.num_rounds - 3


    # --- Access Methods ---
    def get_matchup(self, round_index: int, matchup_index: int) -> DEMatchup:
        """
        Return the indexed matchup from the main bracket.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the main bracket.
        matchup_index : int
            The matchup's zero-based position within the round.

        Returns
        -------
        DEMatchup
            The requested main-bracket matchup.
        """
        return self.main_bracket.get_matchup(round_index, matchup_index)
    
    def get_consolation_matchup(self, round_index: int, matchup_index: int) -> DEMatchup:
        """
        Return the indexed matchup from the consolation bracket.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the consolation bracket.
        matchup_index : int
            The matchup's zero-based position within the round.

        Returns
        -------
        DEMatchup
            The requested consolation-bracket matchup.

        Raises
        ------
        ValueError
            If consolation is disabled, the consolation bracket does not yet exist, 
            or either index is outside its valid range.
        TypeError
            If either index has an invalid type.
        """
        bracket = self._get_consolation_bracket()
        return bracket.get_matchup(round_index, matchup_index)
    
    def get_ready_matchups(self) -> tuple[DEMatchup, ...]:
        """
        Return every matchup currently ready to receive a result.

        Main-bracket matchups precede consolation-bracket matchups. 
        The consolation bracket contributes no matchups until it exists.

        Returns
        -------
        tuple[DEMatchup, ...]
            Ready matchups in bracket and tableau order.
        """
        if not self.use_consolation_bracket or self.consolation_bracket is None:
            return self.main_bracket.get_ready_matchups()
        
        return self.main_bracket.get_ready_matchups() + self.consolation_bracket.get_ready_matchups()


    # --- State Change Methods ---
    def reset_match_result(self, round_index: int, matchup_index: int) -> None:
        """
        Reset an indexed result in the main bracket.

        Resetting a quarter-final discards an unstarted consolation bracket.
        If that update fails, the original main and consolation states are restored where possible.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the main bracket.
        matchup_index : int
            The matchup's zero-based position within the round.

        Raises
        ------
        TypeError
            If either index has an invalid type.
        ValueError
            If the result cannot be reset or the associated consolation bracket has already started.
        RuntimeError
            If the bracket contains an inconsistent matchup state or 
            rollback cannot restore the original state.
        """
        self._validate_quarter_final_undo(round_index, matchup_index)
        
        # Save the old matchup result
        matchup = self.main_bracket.get_matchup(round_index, matchup_index)
        old_score1, old_score2, old_forfeited_index = self._capture_matchup_result(matchup)

        # Save the original consolation bracket state
        old_consolation_bracket = self.consolation_bracket

        # Reset the main bracket match result
        self.main_bracket.reset_match_result(round_index, matchup_index)
        
        # Try to update the consolation bracket
        try:
            self._refresh_consolation_bracket_after_quarter_final_matchup_change(round_index, matchup_index)

        except Exception:
            try:
                if old_forfeited_index is not None:
                    self.main_bracket.record_forfeit(round_index, matchup_index, old_forfeited_index)

                else:
                    self.main_bracket.record_match_score(round_index, matchup_index, old_score1, old_score2)

            finally:
                self.consolation_bracket = old_consolation_bracket
            
            raise

    def reset_third_place_match_result(self) -> None:
        """
        Reset the main bracket's third-place result.

        Raises
        ------
        ValueError
            If the third-place matchup is unavailable, incomplete, or missing an entry.
        RuntimeError
            If the matchup contains both entries but no match.
        """
        self.main_bracket.reset_third_place_match_result()

    def reset_consolation_match_result(self, round_index: int, matchup_index: int) -> None:
        """
        Reset an indexed result in the consolation bracket.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the consolation bracket.
        matchup_index : int
            The matchup's zero-based position within the round.

        Raises
        ------
        TypeError
            If either index has an invalid type.
        ValueError
            If the consolation bracket is unavailable or the result cannot be reset.
        RuntimeError
            If the bracket contains an inconsistent matchup state.
        """
        bracket = self._get_consolation_bracket()
        bracket.reset_match_result(round_index, matchup_index)
    
    def reset_seventh_place_match_result(self) -> None:
        """
        Reset the seventh-place result in the consolation bracket.

        The seventh-place matchup is represented by the consolation bracket's third-place matchup.

        Raises
        ------
        ValueError
            If the consolation or seventh-place matchup is unavailable or has no result.
        RuntimeError
            If the matchup contains both entries but no match.
        """
        bracket = self._get_consolation_bracket()
        bracket.reset_third_place_match_result()


    # --- Main Bracket Result Recording Methods ---
    def record_match_score(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Record a new scored result in the main bracket.

        Completing the quarter-finals automatically creates the consolation bracket when that format is enabled. 
        If its creation fails, the newly recorded main-bracket result is reset.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the main bracket.
        matchup_index : int
            The matchup's zero-based position within the round.
        score1 : int
            The score of the top entry.
        score2 : int
            The score of the bottom entry.

        Raises
        ------
        TypeError
            If an index or score has an invalid type.
        ValueError
            If an index or score is invalid, the matchup cannot receive a new result, 
            or its winner cannot advance.
        RuntimeError
            If the bracket contains an inconsistent matchup state or rollback fails.
        """
        # Save the original consolation bracket state
        old_consolation_bracket = self.consolation_bracket
        
        # Attempt to record a result in the main bracket
        self.main_bracket.record_match_score(round_index, matchup_index, score1, score2)

        try:
            self._create_consolation_bracket_if_ready(round_index, matchup_index)

        except Exception:
            try:
                self.main_bracket.reset_match_result(round_index, matchup_index)

            finally:
                self.consolation_bracket = old_consolation_bracket

            raise

    def replace_with_score(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Replace a main-bracket result with a scored result.

        Replacing a quarter-final result rebuilds an unstarted consolation bracket from the updated losers. 
        If rebuilding fails, the previous main and consolation results are restored where possible.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the main bracket.
        matchup_index : int
            The matchup's zero-based position within the round.
        score1 : int
            The replacement score of the top entry.
        score2 : int
            The replacement score of the bottom entry.

        Raises
        ------
        TypeError
            If an index or score has an invalid type.
        ValueError
            If the replacement is invalid, a dependent matchup prevents the change, 
            or the consolation bracket has already started.
        RuntimeError
            If the bracket contains an inconsistent state or rollback fails.
        """
        self._validate_quarter_final_undo(round_index, matchup_index)

        # Save the original main bracket matchup's state
        matchup = self.main_bracket.get_matchup(round_index, matchup_index)
        old_score1, old_score2, old_forfeited_index = self._capture_matchup_result(matchup)

        # Save the original consolation bracket state
        old_consolation_bracket = self.consolation_bracket

        # Replace with the score, if it fails, the bracket will remain unchanged
        self.main_bracket.replace_with_score(round_index, matchup_index, score1, score2)

        # Try to update the consolation bracket if necessary
        try:
            self._refresh_consolation_bracket_after_quarter_final_matchup_change(round_index, matchup_index)

        # Restore the main bracket and the consolation bracket to their original states
        except Exception:
            try:
                self._replace_with_captured_result(round_index, matchup_index, old_score1, old_score2, old_forfeited_index)

            finally:
                self.consolation_bracket = old_consolation_bracket

            raise

    def record_forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Record a new forfeit result in the main bracket.

        Completing the quarter-finals automatically creates the consolation bracket when enabled. 
        If its creation fails, the recorded forfeit is reset.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the main bracket.
        matchup_index : int
            The matchup's zero-based position within the round.
        forfeiting_index : int
            The forfeiting entry's position: 
            ``0`` for the top entry or ``1`` for the bottom entry.

        Raises
        ------
        TypeError
            If an index has an invalid type.
        ValueError
            If an index is invalid, the matchup cannot receive a result, or its winner cannot advance.
        RuntimeError
            If the bracket contains an inconsistent matchup state or rollback fails.
        """
        # Save the original consolation bracket state
        old_consolation_bracket = self.consolation_bracket

        self.main_bracket.record_forfeit(round_index, matchup_index, forfeiting_index)

        try:
            self._create_consolation_bracket_if_ready(round_index, matchup_index)

        except Exception:
            try:
                self.main_bracket.reset_match_result(round_index, matchup_index)

            finally:
                self.consolation_bracket = old_consolation_bracket

            raise

    def replace_with_forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Replace a main-bracket result with a forfeit.

        Replacing a quarter-final result rebuilds an unstarted consolation bracket from the updated losers. 
        If rebuilding fails, the previous main and consolation results are restored where possible.

        Parameters
        ----------
        round_index : int
            The round's zero-based position in the main bracket.
        matchup_index : int
            The matchup's zero-based position within the round.
        forfeiting_index : int
            The forfeiting entry's position: 
            ``0`` for the top entry or ``1`` for the bottom entry.

        Raises
        ------
        TypeError
            If an index has an invalid type.
        ValueError
            If the replacement is invalid, a dependent matchup prevents the change, 
            or the consolation bracket has already started.
        RuntimeError
            If the bracket contains an inconsistent state or rollback fails.
        """
        self._validate_quarter_final_undo(round_index, matchup_index)

        # Save the original main bracket matchup's state
        matchup = self.main_bracket.get_matchup(round_index, matchup_index)
        old_score1, old_score2, old_forfeited_index = self._capture_matchup_result(matchup)

        # Save the original consolation bracket's state
        old_consolation_bracket = self.consolation_bracket

        # Replace with forfeit, if it fails, the bracket will be restored automatically
        self.main_bracket.replace_with_forfeit(round_index, matchup_index, forfeiting_index)
        
        # Try to update the consolation bracket
        try:
            self._refresh_consolation_bracket_after_quarter_final_matchup_change(round_index, matchup_index)

        # Restore the main bracekt and the consolation bracket to their original states
        except Exception:
            try:
                self._replace_with_captured_result(round_index, matchup_index, old_score1, old_score2, old_forfeited_index)

            finally:
                self.consolation_bracket = old_consolation_bracket
            
            raise


    # --- Main Bracket Third-place Match Result Recording Methods ---
    def record_third_place_match_score(self, score1: int, score2: int) -> None:
        """
        Record a new scored result for third place in the main bracket.

        Parameters
        ----------
        score1 : int
            The score of entry 1 in the third-place match.
        score2 : int
            The score of entry 2 in the third-place match.

        Raises
        ------
        TypeError
            If either score has an invalid type.
        ValueError
            If third place is disabled, the matchup is not ready, 
            a result already exists, or a score is invalid.
        RuntimeError
            If both entries exist but their match is missing.
        """
        self.main_bracket.record_third_place_match_score(score1, score2)

    def replace_third_place_match_with_score(self, score1: int, score2: int) -> None:
        """
        Replace the main bracket's third-place result with scores.

        Parameters
        ----------
        score1 : int
            The replacement score of entry 1 in the third-place match.
        score2 : int
            The replacement score of entry 2 in the third-place match.

        Raises
        ------
        TypeError
            If either score has an invalid type.
        ValueError
            If the matchup is unavailable, has no result, or a score is invalid.
        RuntimeError
            If both entries exist but their match is missing.
        """
        self.main_bracket.replace_third_place_match_with_score(score1, score2)

    def record_third_place_match_forfeit(self, forfeiting_index: int) -> None:
        """
        Record a new forfeit result for third place in the main bracket.

        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's position: ``0`` or ``1``.

        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer.
        ValueError
            If the index is invalid, the matchup is unavailable or not ready, or a result already exists.
        RuntimeError
            If both entries exist but their match is missing.
        """
        self.main_bracket.record_third_place_match_forfeit(forfeiting_index)

    def replace_third_place_match_with_forfeit(self, forfeiting_index: int) -> None:
        """
        Replace the main bracket's third-place result with a forfeit.

        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's position: ``0`` or ``1``.

        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer.
        ValueError
            If the index is invalid or the matchup is unavailable or has no result.
        RuntimeError
            If both entries exist but their match is missing.
        """
        self.main_bracket.replace_third_place_match_with_forfeit(forfeiting_index)


    # --- Consolation Bracket Result Recording Methods ---
    def record_consolation_match_score(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Record a new scored result in the consolation bracket.

        Parameters
        ----------
        round_index, matchup_index : int
            The zero-based round and matchup positions.
        score1 : int
            The score of the top entry.
        score2 : int
            The score of the bottom entry.

        Raises
        ------
        TypeError
            If an index or score has an invalid type.
        ValueError
            If consolation is unavailable or the result is invalid.
        RuntimeError
            If the bracket contains an inconsistent matchup state.
        """
        bracket = self._get_consolation_bracket()
        bracket.record_match_score(round_index, matchup_index, score1, score2)

    def replace_consolation_match_with_score(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Replace an indexed consolation-bracket result with scores.

        Parameters
        ----------
        round_index, matchup_index : int
            The zero-based round and matchup positions.
        score1 : int
            The replacement score of the top entry.
        score2 : int
            The replacement score of the bottom entry.

        Raises
        ------
        TypeError
            If an index or score has an invalid type.
        ValueError
            If consolation is unavailable or the replacement is invalid.
        RuntimeError
            If the bracket contains an inconsistent matchup state.
        """
        bracket = self._get_consolation_bracket()
        bracket.replace_with_score(round_index, matchup_index, score1, score2)

    def record_consolation_match_forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Record a new forfeit result in the consolation bracket.

        Parameters
        ----------
        round_index, matchup_index : int
            The zero-based round and matchup positions.
        forfeiting_index : int
            The forfeiting entry's position: ``0`` or ``1``.

        Raises
        ------
        TypeError
            If an index has an invalid type.
        ValueError
            If consolation is unavailable or the result is invalid.
        RuntimeError
            If the bracket contains an inconsistent matchup state.
        """
        bracket = self._get_consolation_bracket()
        bracket.record_forfeit(round_index, matchup_index, forfeiting_index)

    def replace_consolation_match_with_forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Replace an indexed consolation-bracket result with a forfeit.

        Parameters
        ----------
        round_index, matchup_index : int
            The zero-based round and matchup positions.
        forfeiting_index : int
            The forfeiting entry's position: ``0`` or ``1``.

        Raises
        ------
        TypeError
            If an index has an invalid type.
        ValueError
            If consolation is unavailable or the replacement is invalid.
        RuntimeError
            If the bracket contains an inconsistent matchup state.
        """
        bracket = self._get_consolation_bracket()
        bracket.replace_with_forfeit(round_index, matchup_index, forfeiting_index)


    # --- Consolation Bracket Third-place Match Recording Methods ---
    def record_seventh_place_match_score(self, score1: int, score2: int) -> None:
        """
        Record a new scored result for seventh place.

        Parameters
        ----------
        score1 : int
            The score of entry 1 in the seventh-place match.
        score2 : int
            The score of entry 2 in the seventh-place match.

        Raises
        ------
        TypeError
            If either score has an invalid type.
        ValueError
            If consolation or seventh place is unavailable, the matchup is not ready, 
            a result exists, or a score is invalid.
        RuntimeError
            If both entries exist but their match is missing.
        """
        bracket = self._get_consolation_bracket()
        bracket.record_third_place_match_score(score1, score2)
    
    def replace_seventh_place_match_with_score(self, score1: int, score2: int) -> None:
        """
        Replace the seventh-place result with scores.

        Parameters
        ----------
        score1 : int
            The replacement score of entry 1 in the seventh-place match.
        score2 : int
            The replacement score of entry 2 in the seventh-place match.

        Raises
        ------
        TypeError
            If either score has an invalid type.
        ValueError
            If the matchup is unavailable, has no result, or a score is invalid.
        RuntimeError
            If both entries exist but their match is missing.
        """
        bracket = self._get_consolation_bracket()
        bracket.replace_third_place_match_with_score(score1, score2)
    
    def record_seventh_place_match_forfeit(self, forfeiting_index: int) -> None:
        """
        Record a new forfeit result for seventh place.

        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's position: ``0`` or ``1``.

        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer.
        ValueError
            If the index is invalid, the matchup is unavailable or not ready,
            or a result already exists.
        RuntimeError
            If both entries exist but their match is missing.
        """
        bracket = self._get_consolation_bracket()
        bracket.record_third_place_match_forfeit(forfeiting_index)

    def replace_seventh_place_match_with_forfeit(self, forfeiting_index: int) -> None:
        """
        Replace the seventh-place result with a forfeit.

        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's position: ``0`` or ``1``.

        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer.
        ValueError
            If the index is invalid or the matchup is unavailable or has no result.
        RuntimeError
            If both entries exist but their match is missing.
        """
        bracket = self._get_consolation_bracket()
        bracket.replace_third_place_match_with_forfeit(forfeiting_index)


    # --- Result Calculation Methods ---
    def calculate_results(self) -> DEStageResults:
        """
        Calculate and return a snapshot of the current stage results.

        Returns
        -------
        DEStageResults
            Results combining the main and existing consolation brackets.
        """
        return DEStageResults(self.main_bracket, self.consolation_bracket)
    
    def calculate_results_display_names(self) -> tuple[str, ...]:
        """
        Return participant display names in current result order.

        Returns
        -------
        tuple[str, ...]
            Display names ordered by the current stage results.
        """
        stage_results = self.calculate_results()
        return tuple(entry_result.entry.display_name for entry_result in stage_results.entry_results)


    # --- Validation Helper Methods ---
    def _validate_seeded_entries(self, seeded_entries: tuple[SeededEntry, ...]) -> None:
        """
        Validate the stage's seeded-entry collection.

        Parameters
        ----------
        seeded_entries : tuple[SeededEntry, ...]
            The entries and their one-based seeds.

        Raises
        ------
        TypeError
            If the collection is not a tuple, an item is not a ``SeededEntry``, or an item does not contain a ``TournamentEntry``.
        ValueError
            If fewer than two entries are supplied, a seed is outside the valid range, 
            an entry ID or seed is duplicated, or entries belong to different tournaments.
        """
        if not isinstance(seeded_entries, tuple):
            raise TypeError(f'seeded_entries must be a tuple - got {type(seeded_entries).__name__}')
        
        if len(seeded_entries) < 2:
            raise ValueError(f'seeded_entries must contain at least two entries')

        seen_entry_ids: set[int] = set()
        seen_seeds: set[int] = set()

        for i, seeded_entry in enumerate(seeded_entries):
            if not isinstance(seeded_entry, SeededEntry):
                raise TypeError(f'Seeded entry at index {i} must be a SeededEntry - got {type(seeded_entry).__name__}')
            
            if not isinstance(seeded_entry.entry, TournamentEntry):
                raise TypeError(f'Seeded entry at index {i} must have an entry that is a TournamentEntry - got {type(seeded_entry.entry).__name__}')
            
            validation.validate_int_in_range(seeded_entry.seed, 1, len(seeded_entries), f'Seed of seeded entry at index {i}', 'DEStage')

            if seeded_entry.entry.id in seen_entry_ids:
                raise ValueError(f'Entry ID {seeded_entry.entry.id} occurs more than once in seeded_entries')

            if seeded_entry.seed in seen_seeds:
                raise ValueError(f'Seed {seeded_entry.seed} has occurred more than once in seeded_entries')

            if i == 0:
                tournament_id: int = seeded_entry.entry.tournament_id

            if seeded_entry.entry.tournament_id != tournament_id:
                raise ValueError(f'Seeded entry at index {i} must have tournament ID {tournament_id} - got {seeded_entry.entry.tournament_id}')
            
            seen_entry_ids.add(seeded_entry.entry.id)
            seen_seeds.add(seeded_entry.seed)

    def _get_consolation_bracket(self) -> DEBracket:
        """
        Return the stage's existing consolation bracket.

        Returns
        -------
        DEBracket
            The consolation bracket.

        Raises
        ------
        ValueError
            If consolation is disabled or its bracket does not yet exist.
        """
        if not self.use_consolation_bracket:
            raise ValueError(f'This DE stage does not have the consolation option chosen')
        
        if self.consolation_bracket is None:
            raise ValueError(f'The consolation bracket does not exist yet for this DE stage')

        return self.consolation_bracket

    def _get_consolation_entries(self) -> tuple[TournamentEntry, ...]:
        """
        Return completed quarter-final losers in original seed order.

        Returns
        -------
        tuple[TournamentEntry, ...]
            The entries eligible for the consolation bracket.

        Raises
        ------
        ValueError
            If the quarter-finals are incomplete.
        """
        quarterfinal = self.main_bracket.rounds[self.main_bracket.num_rounds - 3]

        if quarterfinal.is_incomplete():
            raise ValueError(
                f'Cannot get consolation entries before the quarter-finals are complete'
            )

        loser_ids = {loser.id for loser in quarterfinal.get_round_losers()}

        return tuple(seeded_entry.entry for seeded_entry in self.seeded_entries if seeded_entry.entry.id in loser_ids)

    def _create_consolation_bracket_if_ready(self, round_index: int, matchup_index: int) -> None:
        """
        Create the consolation bracket when the quarter-finals finish.

        No action is taken if consolation is disabled, a consolation bracket already exists, 
        the indexed matchup is not a quarter-final, or the quarter-final round remains incomplete. 
        Four consolation entries also produce a seventh-place matchup.

        Parameters
        ----------
        round_index : int
            The zero-based main-bracket round index just changed.
        matchup_index : int
            The zero-based matchup index just changed.

        Raises
        ------
        TypeError
            If either index has an invalid type.
        ValueError
            If either index is invalid or the derived consolation entries cannot form a valid bracket.
        """
        if not self.use_consolation_bracket:
            return
        
        if self.consolation_bracket is not None:
            return

        if self._is_quarter_final_matchup(round_index, matchup_index):
            if self.main_bracket.rounds[round_index].is_complete():
                consolation_entries = self._get_consolation_entries()

                self.consolation_bracket = DEBracket(
                    stage_number = self.stage_number,
                    seed_ordered_entries = consolation_entries,
                    bracket_role =  DEBracketRole.CONSOLATION,
                    score_to_win = self.score_to_win,
                    has_third_place_match = len(consolation_entries) == 4
                )

    def _validate_quarter_final_undo(self, round_index: int, matchup_index: int) -> None:
        """
        Validate a main-bracket change that may affect consolation entries.

        Parameters
        ----------
        round_index : int
            The zero-based main-bracket round index to change.
        matchup_index : int
            The zero-based matchup index to change.

        Raises
        ------
        TypeError
            If either index has an invalid type.
        ValueError
            If either index is invalid or the matchup is a quarter-final and 
            the consolation bracket has already started.
        """
        if not self.use_consolation_bracket:
            return

        if not self._is_quarter_final_matchup(round_index, matchup_index):
            return
        
        bracket = self.consolation_bracket

        if bracket is not None and bracket.has_started():
            raise ValueError('Reset the consolation results before changing a quarter-final result')

    def _refresh_consolation_bracket_after_quarter_final_matchup_change(self, round_index: int, matchup_index: int) -> None:
        """
        Refresh consolation after a quarter-final reset or replacement.

        A reset discards the old consolation bracket while the quarter-finals are incomplete. 
        A replacement immediately creates a new bracket from the updated losers. 
        Non-quarter-final changes have no effect.

        Parameters
        ----------
        round_index : int
            The zero-based main-bracket round index just changed.
        matchup_index : int
            The zero-based matchup index just changed.

        Raises
        ------
        TypeError
            If either index has an invalid type.
        ValueError
            If an index or the reconstructed bracket state is invalid.
        """
        if not self.use_consolation_bracket:
            return

        if not self._is_quarter_final_matchup(round_index, matchup_index):
            return

        # Set the consolation bracket to None
        self.consolation_bracket = None

        # A reset will not create a new consolation bracket; a replacement will create a new consolation bracket.
        self._create_consolation_bracket_if_ready(round_index, matchup_index)

    def _capture_matchup_result(self, matchup: DEMatchup) -> tuple[int | None, int | None, int | None]:
        """
        Capture the stored score and forfeit state of a matchup.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup whose current result state is captured.

        Returns
        -------
        tuple[int | None, int | None, int | None]
            ``score1``, ``score2``, and ``forfeited_index`` from the match.

        Raises
        ------
        RuntimeError
            If the matchup has no match to capture.
        """
        match = matchup.match

        if match is None:
            raise RuntimeError(f'Cannot capture the result of {matchup.label} because it has no match')

        return match.score1, match.score2, match.forfeited_index

    def _replace_with_captured_result(self, round_index: int, matchup_index: int, 
                                      score1: int | None, score2: int | None, forfeited_index: int | None) -> None:
        """
        Restore a main-bracket matchup from a captured result.

        Parameters
        ----------
        round_index : int
            The matchup's zero-based round position.
        matchup_index : int
            The matchup's zero-based position within the round.
        score1 : int | None
            The captured score of entry 1 in the matchup, required for a non-forfeit result.
        score2 : int | None
            The captured score of entry 2 in the matchup, required for a non-forfeit result.
        forfeited_index : int | None
            The captured forfeiting position, or ``None`` for a scored result.

        Raises
        ------
        TypeError
            If a captured value has an invalid type.
        ValueError
            If an index or captured result is invalid or the result cannot be replaced.
        RuntimeError
            If a scored result is missing either captured score or 
            the bracket contains an inconsistent matchup state.
        """
        if forfeited_index is not None:
            self.main_bracket.replace_with_forfeit(round_index, matchup_index, forfeited_index)
            return

        if score1 is None or score2 is None:
            raise RuntimeError('Cannot restore a scored matchup result because its captured scores are missing')

        self.main_bracket.replace_with_score(round_index, matchup_index, score1, score2)
