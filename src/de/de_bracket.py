from dataclasses import dataclass, field, InitVar

import validation

from de.de_matchup import DEMatchup
from de.de_round import DERound
from entities.tournament_entry import TournamentEntry
from matches.de_match import DEMatch


@dataclass(eq=False)
class DEBracket:
    """
    Represent a direct-elimination bracket within a tournament stage.

    All rounds are constructed during initialization. 
    Entries are placed in the first round according to their supplied seed order, 
    and first-round bye winners are automatically advanced.

    Recording a match result advances its winner when a next round exists.
    An existing result can be reset or replaced only while its next matchup remains incomplete.

    Parameters
    ----------
    stage_number : int
        The DE stage's one-based position within its tournament.
    seed_ordered_entries : tuple[TournamentEntry, ...]
        At least two entries in ascending seed order, with the highest seed first. 
        Tuple position determines the bracket seed; the entries are not sorted internally.
        Entries must have distinct entry IDs and fencer IDs and belong
        to the same tournament. 
        This initialization-only argument is not stored as an attribute.
    score_to_win : int, default=15
        The target score and maximum permitted recorded score for either entry in matches created for this bracket.

    Attributes
    ----------
    stage_number : int
        The DE stage's one-based position within its tournament.
    rounds : tuple[DERound, ...]
        All bracket rounds in opening-round-to-final order.
    score_to_win : int, default=15
        The target score used when constructing the bracket's matches.
    """
    stage_number: int
    seed_ordered_entries: InitVar[tuple[TournamentEntry, ...]]
    score_to_win: int = field(default=15, kw_only=True)
    rounds: tuple[DERound, ...] = field(init=False)


    # --- Initialization and Validation ---
    def __post_init__(self, seed_ordered_entries: tuple[TournamentEntry, ...]) -> None:
        """
        Validate the initialization inputs and construct every bracket round.

        The BYE winners are automatically advanced to the next round.

        Parameters
        ----------
        seed_ordered_entries : tuple[TournamentEntry, ...]
            The initialization-only collection of entries in ascending seed order.

        Raises
        ------
        TypeError
            If the stage number or `score_to_win` is not an integer, 
            the entries are not a tuple, an item is not a ``TournamentEntry``, 
            or a generated matchup or match encounters an invalid attribute type.
        ValueError
            If the stage number or ``score_to_win`` is not positive,
            fewer than two entries are supplied, entry IDs or fencer IDs repeat, 
            tournament IDs differ, or the generated matchups cannot form valid rounds or matches.
        """
        validation.validate_positive_int(self.stage_number, 'Stage number', 'DEBracket')
        validation.validate_positive_int(self.score_to_win, 'Score to win', 'DEBracket')

        self._validate_seed_ordered_entries(seed_ordered_entries)
    
        self.rounds = self._init_all_rounds(seed_ordered_entries)


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying the tournament and DE stage."""
        return f'DE bracket for tournament {self.tournament_id} in stage {self.stage_number}'

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the first round's matchups."""
        return self.first_round.tournament_id
    
    @property
    def num_entries(self) -> int:
        """Return the number of actual entrants, excluding empty bye positions."""
        return len(self.entries)
    
    @property
    def num_rounds(self) -> int:
        """Return the total number of rounds, including the final."""
        return len(self.rounds)
    
    @property
    def bracket_size(self) -> int:
        """
        Return the number of entry positions in the opening round.

        This is the smallest power of two greater than or equal to the initial number of entrants. 
        Empty BYE positions are included.
        """
        return self.rounds[0].size

    @property
    def current_round_index(self) -> int | None:
        """
        Return the first incomplete round's zero-based index, or ``None``.

        Return ``None`` when every round is complete. 
        A later round can already contain ready matchups while this round remains incomplete.
        """
        return next((i for i, de_round in enumerate(self.rounds) if de_round.is_incomplete()), None)

    @property
    def current_round_number(self) -> int | None:
        """
        Return the first incomplete round's one-based number, or ``None``.

        Return ``None`` when the bracket is complete.
        """
        index = self.current_round_index
        return None if index is None else index + 1
    
    @property
    def current_round(self) -> DERound | None:
        """Return the first incomplete round, or ``None`` if complete."""
        index = self.current_round_index
        return None if index is None else self.rounds[index]

    @property
    def current_round_size(self) -> int | None:
        """
        Return the first incomplete round's size, or ``None`` if complete.

        The size counts all entry positions in that round, including empty positions still awaiting an advancing winner.
        """
        index = self.current_round_index
        return None if index is None else self.rounds[index].size
    
    @property
    def current_round_name(self) -> str | None:
        """Return the first incomplete round's name, or ``None`` if complete."""
        index = self.current_round_index
        return None if index is None else self.rounds[index].round_name
    
    @property
    def first_round(self) -> DERound:
        """Return the opening round containing the bracket's original entrants."""
        return self.rounds[0]

    @property
    def round_one_seed_order(self) -> tuple[int, ...]:
        """
        Return bracket seed numbers in first-round tableau order.

        The tuple contains one seed number per opening-round entry position, 
        including seed numbers beyond the initial entry count.
        Those positions are left empty to create first-round byes.
        """
        return DERound.generate_tree_bracket_level(depth=self.num_rounds)
    
    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """
        Return the entries occupying the first round in tableau order.

        Entries are returned in top-to-bottom matchup order, 
        with the top entry preceding the bottom entry within each matchup. 
        Empty positions are omitted.
        """
        return self.first_round.entries
    
    @property
    def winner(self) -> TournamentEntry | None:
        """
        Return the final matchup's winner once every round is complete.

        Return ``None`` while any round in the bracket remains incomplete.
        """
        if self.is_incomplete():
            return None
        
        return self.rounds[-1].matchups[0].winner
    

    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """
        Return whether ``other`` represents the same tournament bracket.

        Equality is based on tournament ID and stage number. 
        Entrants, round contents, and recorded results are not considered.

        Parameters
        ----------
        other : object
            The object to compare with this bracket.

        Returns
        -------
        bool
            ``True`` if ``other`` is a ``DEBracket`` with the same tournament ID and stage number; otherwise, ``False``.
        """
        if not isinstance(other, DEBracket):
            return False

        return self.tournament_id == other.tournament_id and self.stage_number == other.stage_number
    

    # --- Predicate Methods ---
    def is_complete(self) -> bool:
        """
        Return whether every round in the bracket is complete.

        Completed scored matches, forfeits, and first-round byes count toward completion. 
        Later-round matchups awaiting an entry do not.
        """
        return all(round.is_complete() for round in self.rounds)
    
    def is_incomplete(self) -> bool:
        """Return whether at least one bracket round remains incomplete."""
        return not self.is_complete()
    
    def has_started(self) -> bool:
        """
        Return whether any match currently has a recorded result.

        Scored results and forfeits count; automatic first-round byes do not.
        Return ``False`` if all recorded match results have been reset.
        """
        return any(
            matchup.has_match() and matchup.match.is_complete()
            for de_round in self.rounds 
            for matchup in de_round.matchups
        )

    def has_entry(self, entry: TournamentEntry) -> bool:
        """
        Return whether the specified tournament entry belongs to the bracket.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry whose membership is being checked.

        Returns
        -------
        bool
            ``True`` if the entry appears in the first round; otherwise, ``False``.

        Raises
        ------
        TypeError
            If ``entry`` is not a ``TournamentEntry``.
        ValueError
            If ``entry`` belongs to another tournament.
        """
        return self.first_round.has_entry(entry)


    # --- Access Methods ---
    def get_round(self, index: int) -> DERound:
        """
        Return the round at the specified round index.

        Parameters
        ----------
        index : int
            The round's zero-based position. 
            Index ``0`` is the first round, and ``num_rounds - 1`` is the final round.

        Returns
        -------
        DERound
            The stored round at ``index``.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is outside the valid range of round indices.
        """
        self._validate_round_index(index, 'get_round')
        return self.rounds[index]

    def get_round_size(self, index: int) -> int:
        """
        Return the number of entry positions in a specified round.

        Parameters
        ----------
        index : int
            The round's zero-based position within the bracket.

        Returns
        -------
        int
            Twice the round's number of matchups. 
            Empty positions are included, so this need not equal the number of entries present.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is outside the valid range of round indices.
        """
        self._validate_round_index(index, 'get_round_size')
        return self.get_round(index).size

    def get_matchup(self, round_index: int, matchup_index: int) -> DEMatchup:
        """
        Return the matchup at the specified round and matchup indices.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round, 
            counted from the top of the tableau.

        Returns
        -------
        DEMatchup
            The stored matchup at the specified position.

        Raises
        ------
        TypeError
            If either index is not an integer.
        ValueError
            If either index is outside its corresponding valid range.
        """ 
        self._validate_matchup_index(round_index, matchup_index, 'get_matchup')
        return self.get_round(round_index).get_matchup_at(matchup_index)
    
    def _get_next_matchup(self, matchup: DEMatchup) -> DEMatchup | None:
        """
        Return the next-round matchup reached by this matchup's winner.

        The matchup is assumed to belong to this bracket.
        Its round and matchup numbers determine the advancement path.

        Parameters
        ----------
        matchup : DEMatchup
            The source matchup whose advancement destination is requested.

        Returns
        -------
        DEMatchup | None
            The stored destination matchup, or ``None`` for the final.

        Raises
        ------
        TypeError
            If a derived round or matchup index is not an integer.
        ValueError
            If a derived round or matchup index is outside its valid range.
        """
        if self._is_final_matchup(matchup):
            return None
        
        return self.get_matchup(matchup.round_index + 1, matchup.next_matchup_index)

    def get_match(self, round_index: int, matchup_index: int) -> DEMatch | None:
        """
        Return the match contained in a specified bracket matchup.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round.

        Returns
        -------
        DEMatch | None
            The stored match, or ``None`` if the matchup has no match.

        Raises
        ------
        TypeError
            If either index is not an integer.
        ValueError
            If either index is outside its corresponding valid range.
        """
        self._validate_matchup_index(round_index, matchup_index, 'get_match')
        return self.get_matchup(round_index, matchup_index).match
        
    def get_ready_matchups(self) -> tuple[DEMatchup, ...]:
        """
        Return incomplete matchups that already contain matches.

        Returns
        -------
        tuple[DEMatchup, ...]
            Ready matchups in round order, then top-to-bottom matchup order.
        """
        return tuple(
            matchup for de_round in self.rounds for matchup in de_round.matchups 
            if matchup.has_match() and matchup.is_incomplete()
        )


    # --- State Change Methods ---
    def reset_match_result(self, round_index: int, matchup_index: int) -> None:
        """
        Clear a recorded match result and undo its winner's advancement.

        The selected matchup retains both entries and its match, 
        but its scores, forfeit state, and completion state are cleared.

        The next matchup must be incomplete before this operation is allowed.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round,
            counted from the top of the tableau.

        Raises
        ------
        TypeError
            If either index is not an integer.
        ValueError
            If either index is outside its valid range, the selected matchup is a bye, 
            either entry is missing, no result has been recorded, or the next matchup is complete.
        RuntimeError
            If both entries are present but the selected matchup has no match,
            or the expected destination position is empty or contains an entry unequal to the recorded winner.
        """
        self._validate_matchup_index(round_index, matchup_index, method_name='reset_match_result')
        
        matchup = self.get_matchup(round_index, matchup_index)

        self._validate_matchup_eligibility_to_undo(matchup, 'reset')

        if self._is_final_matchup(matchup):
            matchup.reset_match()
            return
        
        # Save the matchup's match info
        old_score1, old_score2, old_forfeited_index, old_completed = self._capture_match_result(matchup)

        # Save the next matchup's entry and match info
        next_matchup = self._get_next_matchup(matchup)
        old_next_entry1, old_next_entry2, old_next_match = self._capture_matchup(next_matchup)

        # Try to remove the previously advanced entry and reset the matchup
        try:
            next_matchup.remove_entry(matchup.next_matchup_entry_index)
            matchup.reset_match()

        # Restore the original matchup match state and restore the original destination entries and match
        except Exception:
            self._restore_match_result(matchup, old_score1, old_score2, old_forfeited_index, old_completed)
            self._restore_matchup(next_matchup, old_next_entry1, old_next_entry2, old_next_match)
            
            raise


    # --- Result Recording Methods ---
    def record_match_score(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Record a scored result and advance the winner to the next round.

        The selected matchup must contain an incomplete match.

        When a next matchup exists, the winner is added to its designated entry position, which must be empty.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round, counted from the top of the tableau.
        score1 : int
            The final score of the selected matchup's top entry.
        score2 : int
            The final score of the selected matchup's bottom entry.

        Raises
        ------
        TypeError
            If an index or score is not an integer, or advancement encounters an invalid entry attribute type.
        ValueError
            If an index is outside its valid range, a score is outside the permitted range, the scores are tied, 
            the selected matchup is a bye, either entry is missing, or the match is already complete.
            Also raised if the destination position is occupied or the winner cannot be added to the next round.
        RuntimeError
            If both entries are present but the selected matchup has no match,
            or the completed matchup has no winner when advancement is required.
        """
        method_name = 'record_match_score'
        self._validate_scores(score1, score2, method_name=method_name)
        self._record_match_result(round_index, matchup_index, method_name, score1=score1, score2=score2)

    def replace_with_score(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Replace a recorded scored or forfeit result with new scores.

        The selected matchup must contain a completed match.

        When a next matchup exists, it must be incomplete.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round, counted from the top of the tableau.
        score1 : int
            The new final score of the selected matchup's top entry.
        score2 : int
            The new final score of the selected matchup's bottom entry.

        Raises
        ------
        TypeError
            If an index or score is not an integer, or advancement encounters an invalid entry attribute type.
        ValueError
            If an index is outside its valid range, a score is outside the permitted range, the scores are tied, 
            the selected matchup is a bye, either entry is missing, no result has been recorded, or the next matchup is complete.
            Also raised if the new winner cannot be added to the next round.
        RuntimeError
            If both entries are present but the selected matchup has no match,
            the expected destination position is empty or contains an entry unequal to the previous winner, 
            or the replacement result has no winner when advancement is required.
        """
        method_name = 'replace_with_score'
        self._validate_scores(score1, score2, method_name)
        self._replace_match_result(round_index, matchup_index, method_name, score1=score1, score2=score2)

    def record_forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit and advance the opposing entry to the next round.

        The selected matchup must contain an incomplete match.

        When a next matchup exists, the winner is added to its designated entry position, which must be empty.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round, counted from the top of the tableau.
        forfeiting_index : int
            The forfeiting entry's position within the selected matchup:
            ``0`` for the top entry or ``1`` for the bottom entry.

        Raises
        ------
        TypeError
            If any index is not an integer, or advancement encounters an invalid entry attribute type.
        ValueError
            If an index is outside its valid range, the selected matchup is a bye, either entry is missing, 
            or the match is already complete.
            Also raised if the destination position is occupied or the winner cannot be added to the next round.
        RuntimeError
            If both entries are present but the selected matchup has no match, 
            or the completed matchup has no winner when advancement is required.
        """
        method_name = 'record_forfeit'
        self._validate_forfeiting_index(forfeiting_index, method_name)
        self._record_match_result(round_index, matchup_index, method_name, forfeiting_index=forfeiting_index)

    def replace_with_forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Replace a recorded scored or forfeit result with a forfeit.

        The selected matchup must contain a completed match.

        When a next matchup exists, it must be incomplete.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round, counted from the top of the tableau.
        forfeiting_index : int
            The forfeiting entry's position within the selected matchup:
            ``0`` for the top entry or ``1`` for the bottom entry.

        Raises
        ------
        TypeError
            If any index is not an integer, or advancement encounters an invalid entry attribute type.
        ValueError
            If an index is outside its valid range, the selected matchup is a bye, either entry is missing, 
            no result has been recorded, or the next matchup is complete.
            Also raised if the new winner cannot be added to the next round.
        RuntimeError
            If both entries are present but the selected matchup has no match,
            the expected destination position is empty or contains an entry unequal to the previous winner, 
            or the replacement result has no winner when advancement is required.
        """
        method_name = 'replace_with_forfeit'
        self._validate_forfeiting_index(forfeiting_index, method_name)
        self._replace_match_result(round_index, matchup_index, method_name, forfeiting_index=forfeiting_index)


    ##########################
    ##### HELPER METHODS #####
    ##########################

    # --- Predicate Helper Methods ---
    def _is_final_matchup(self, matchup: DEMatchup) -> bool:
        """Return whether the matchup's round number identifies the final round."""
        return matchup.round_number == self.num_rounds
    
    def _is_next_matchup_entry_position_available(self, matchup: DEMatchup) -> bool:
        """Return whether the winner's designated next-round position is empty. Return ``True`` for the final."""
        if self._is_final_matchup(matchup):
            return True
        
        next_matchup = self._get_next_matchup(matchup)

        return not next_matchup.has_entry_at(matchup.next_matchup_entry_index)


    # --- State Capture Helper Methods ---
    def _capture_match_result(self, matchup: DEMatchup) -> tuple[int | None, int | None, int | None, bool]:
        """
        Capture the contained match's result values for later restoration.

        The matchup is assumed to contain a match.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup whose match result is being captured.

        Returns
        -------
        tuple[int | None, int | None, int | None, bool]
            The values ``(score1, score2, forfeited_index, completed)``.
        """
        match = matchup.match
        return match.score1, match.score2, match.forfeited_index, match._completed
    
    def _capture_matchup(self, matchup: DEMatchup) -> tuple[TournamentEntry | None, TournamentEntry | None, DEMatch | None]:
        """
        Capture the matchup's entry and match references for later restoration.

        The referenced objects are not copied. Changes to their internal
        attributes are not preserved separately by this helper.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup whose references are being captured.

        Returns
        -------
        tuple[TournamentEntry | None, TournamentEntry | None, DEMatch | None]
            The references ``(entry1, entry2, match)``.
        """
        return matchup.entry1, matchup.entry2, matchup.match


    # --- State Restoration Helper Methods ---
    def _restore_match_result(self, matchup: DEMatchup, score1: int | None, score2: int | None, forfeited_index: int | None, completed: bool) -> None:
        """
        Restore previously captured result values on the contained match.

        Assign the values directly without validation or winner advancement.
        The matchup is assumed to contain the match being restored.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup whose contained match is being restored.
        score1 : int | None
            The previously captured top-entry score.
        score2 : int | None
            The previously captured bottom-entry score.
        forfeited_index : int | None
            The previously captured forfeiting entry index, or ``None``.
        completed : bool
            The previously captured completion state.
        """
        matchup.match.score1 = score1
        matchup.match.score2 = score2
        matchup.match.forfeited_index = forfeited_index
        matchup.match._completed = completed

    def _restore_matchup(self, matchup: DEMatchup, entry1: TournamentEntry | None, entry2: TournamentEntry | None, match: DEMatch | None) -> None:
        """
        Restore previously captured entry and match references.

        Assign the references directly without validation or match creation.
        This helper does not restore the referenced objects' internal state.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup whose references are being restored.
        entry1 : TournamentEntry | None
            The previously captured top entry.
        entry2 : TournamentEntry | None
            The previously captured bottom entry.
        match : DEMatch | None
            The previously captured match.
        """
        matchup.entry1 = entry1
        matchup.entry2 = entry2
        matchup.match = match


    # --- Bracket Size Calculation Static Helper Methods ---
    @staticmethod
    def _calculate_number_de_rounds(number_de_entries: int) -> int:
        """
        Calculate the number of rounds needed to produce one winner.

        The result is the ceiling of the base-two logarithm of the entry count. 
        Counts that are not powers of two require first-round byes but use the same number of rounds as the next power of two.

        Parameters
        ----------
        number_de_entries : int
            The number of actual entrants, which must be at least two.

        Returns
        -------
        int
            The total number of rounds, including the final.

        Examples
        --------
        >>> DEBracket._calculate_number_de_rounds(2)
        1
        >>> DEBracket._calculate_number_de_rounds(6)
        3
        >>> DEBracket._calculate_number_de_rounds(8)
        3

        Raises
        ------
        TypeError
            If ``number_de_entries`` is not an integer.
        ValueError
            If ``number_de_entries`` is less than two.
        """
        validation.validate_int_at_least(number_de_entries, 2, 'number_de_entries', 'DEBracket', '_calculate_number_de_rounds')

        return (number_de_entries - 1).bit_length()

    @staticmethod
    def _calculate_number_matchups_in_de_round(round_index: int, number_de_entries: int) -> int:
        """
        Calculate the number of matchup positions in a bracket round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position, from ``0`` for the opening
            round through one less than the calculated number of rounds.
        number_de_entries : int
            The total number of actual entrants in the bracket, not the number currently present in this round. 

        Returns
        -------
        int
            The number of matchups to construct in the specified round,
            including positions that are empty or represent BYEs.

        Examples
        --------
        >>> DEBracket._calculate_number_matchups_in_de_round(0, 6)
        4
        >>> DEBracket._calculate_number_matchups_in_de_round(1, 6)
        2
        >>> DEBracket._calculate_number_matchups_in_de_round(2, 6)
        1

        Raises
        ------
        TypeError
            If either argument is not an integer.
        ValueError
            If ``number_de_entries`` is less than two or ``round_index`` is outside the range for the resulting bracket.
        """
        validation.validate_int_at_least(number_de_entries, 2, 'number_de_entries', 'DEBracket', '_calculate_number_matchups_in_de_round')

        number_of_rounds = DEBracket._calculate_number_de_rounds(number_de_entries)
        
        validation.validate_int_in_range(round_index, 0, number_of_rounds - 1, 'round_index', 'DEBracket', '_calculate_number_matchups_in_de_round')
        
        return 2 ** (number_of_rounds - round_index - 1)


    # --- Bracket Construction Helper Methods ---
    def _generate_first_round(self, ordered_entries: tuple[TournamentEntry, ...]) -> DERound:
        """
        Construct the opening round from entries in ascending seed order.

        Tuple position determines each entry's bracket seed. 
        Entries are arranged in tableau order within the smallest power-of-two bracket that accommodates them. 
        Seed positions beyond the entry count are left empty, creating first-round byes.

        Matches are created for matchups containing both entries.
        Bye winners are not advanced by this helper.

        Parameters
        ----------
        ordered_entries : tuple[TournamentEntry, ...]
            At least two prevalidated entries in ascending seed order, with the highest seed first.

        Returns
        -------
        DERound
            The opening round with matchups in top-to-bottom tableau order,
            including any single-entry matchups representing byes.

        Raises
        ------
        TypeError
            If constructing a matchup, match, or round encounters an invalid attribute type.
        ValueError
            If fewer than two entries are supplied or constructing a matchup, match, or round encounters an invalid value.
        """
        # Extract data from input entries
        num_entries = len(ordered_entries)
        expected_num_rounds = DEBracket._calculate_number_de_rounds(num_entries)
        
        # Get tree level position order
        tree_level_position_order = DERound.generate_tree_bracket_level(expected_num_rounds)

        # Matchup position pairings
        matchup_position_pairings = []

        for i in range(0, len(tree_level_position_order), 2):
            position1 = tree_level_position_order[i]
            position2 = tree_level_position_order[i+1]
            matchup_position_pairings.append((position1, position2))            

        # Create DE matchups
        matchups = []
        
        for matchup_index, (entry1_position, entry2_position) in enumerate(matchup_position_pairings):
            # Get entry 1 from ordered entries
            if entry1_position <= num_entries:
                entry1 = ordered_entries[entry1_position - 1]
            else:
                entry1 = None # BYE slot

            # Get entry 2 from ordered entries
            if entry2_position <= num_entries:
                entry2 = ordered_entries[entry2_position - 1]
            else:
                entry2 = None #BYE slot

            # Create the matchup and add to `matchups`
            matchups.append(
                DEMatchup(
                    matchup_number = matchup_index + 1,
                    round_number = 1,
                    stage_number = self.stage_number,
                    tournament_id = ordered_entries[0].tournament_id,
                    entry1 = entry1,
                    entry2 = entry2, 
                    score_to_win = self.score_to_win
                )
            )

        # Convert matchups to tuple format
        matchups = tuple(matchups)

        # Return the first round in this bracket
        return DERound(
            matchups = matchups,
            round_number = 1,
            stage_number = self.stage_number
        )

    def _init_all_rounds(self, ordered_entries: tuple[TournamentEntry, ...]) -> tuple[DERound, ...]:
        """
        Construct every bracket round and advance first-round bye winners.

        The opening round is populated using the supplied seed order.
        All later rounds are initially created with empty matchups,
        with each successive round containing half as many matchups until the final.

        First-round bye winners are then added to their designated second-round positions. 
        The constructed rounds are returned for the caller to store.

        Parameters
        ----------
        ordered_entries : tuple[TournamentEntry, ...]
            At least two prevalidated entries in ascending seed order, with the highest seed first.

        Returns
        -------
        tuple[DERound, ...]
            All rounds in opening-round-to-final order, 
            with first-round bye winners already advanced.

        Raises
        ------
        TypeError
            If constructing a matchup, match, or round, or advancing a bye winner, encounters an invalid attribute type.
        ValueError
            If fewer than two entries are supplied, a generated structure contains an invalid value, 
            or a bye winner cannot be added to its destination.
        """
        # 1. Create first round
        first_round = self._generate_first_round(ordered_entries)

        # 2. Create subsequent rounds initialized as empty matchups
        subsequent_rounds = []

        num_entries = len(ordered_entries)
        expected_num_rounds = DEBracket._calculate_number_de_rounds(num_entries)

        for round_index in range(1, expected_num_rounds):
            round_num_matchups = DEBracket._calculate_number_matchups_in_de_round(round_index, num_entries)
            
            # Create a list of empty DE matchups of the correct length
            matchups = []
            
            for matchup_index in range(round_num_matchups):
                matchups.append(
                    DEMatchup(
                        matchup_number = matchup_index+1,
                        round_number = round_index + 1,
                        stage_number = self.stage_number,
                        tournament_id = ordered_entries[0].tournament_id, 
                        score_to_win = self.score_to_win
                    )
                )

            # Convert the round's matchups to a tuple
            matchups = tuple(matchups)
            
            subsequent_rounds.append(
                DERound(
                    matchups = matchups, 
                    round_number = round_index + 1, 
                    stage_number = self.stage_number
                )
            )

        # 3. Combine all the rounds into one tuple
        rounds = (first_round,) + tuple(subsequent_rounds)

        # 4. Advance first-round bye winners into their round 2 positions
        for matchup in first_round.matchups:
            if matchup.is_bye():
                rounds[1].add_entry_to_matchup(
                    matchup.winner, 
                    matchup.next_matchup_index,
                    matchup.next_matchup_entry_index
                )

        return rounds


    # --- Entry Advancement Helper Methods ---
    def _advance_matchup_winner(self, matchup: DEMatchup) -> None:
        """
        Add a completed matchup's winner to its designated next-round position.

        Do nothing if the source matchup is incomplete or is the final; otherwise, add its winner to the next round.

        Parameters
        ----------
        matchup : DEMatchup
            The source matchup, assumed to belong to this bracket.

        Raises
        ------
        TypeError
            If a destination index or the winning entry has an invalid type,
            or creating the destination match detects an invalid attribute type.
        ValueError
            If a destination index is invalid, the winner belongs to another tournament or already appears in the next round, 
            the destination position is occupied, or the resulting entry pair cannot form a valid match.
        RuntimeError
            If a completed source matchup has no winner when a next round exists, 
            or its recorded result is internally inconsistent.
        """
        if not self._is_final_matchup(matchup):
            if matchup.is_complete():
                winner = matchup.winner

                if winner is None:
                    raise RuntimeError(
                        f'Cannot advance the winner of {matchup.label}: '
                        f'the matchup is complete but has no winner'
                    )

                self.rounds[matchup.round_index + 1].add_entry_to_matchup(
                    winner, 
                    matchup.next_matchup_index, 
                    matchup.next_matchup_entry_index
                )


    # --- Match Result Recording Template Helper Methods ---
    def _record_match_result(self, round_index: int, matchup_index: int, method_name: str, *, score1=None, score2=None, forfeiting_index=None) -> None:
        """
        Record a match result and advance its winner when a next round exists.

        The operation is selected by ``method_name``.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round.
        method_name : str
            The operation to perform: ``'record_match_score'`` or ``'record_forfeit'``.
        score1 : int | None, default=None
            The top entry's score, required for ``'record_match_score'``.
            Ignored when recording a forfeit.
        score2 : int | None, default=None
            The bottom entry's score, required for ``'record_match_score'``.
            Ignored when recording a forfeit.
        forfeiting_index : int | None, default=None
            The forfeiting entry's index, required for ``'record_forfeit'``:
            ``0`` for the top entry or ``1`` for the bottom entry.
            Ignored when recording scores.

        Raises
        ------
        TypeError
            If an index or required result value has an invalid type,
            or advancement encounters an invalid entry attribute type.
        ValueError
            If ``method_name`` is unsupported, if ``record_match_score`` is selected but the scores are not provided, 
            if ``record_forfeit`` is selected but a forfeiting index is not provided, if an index or result value is invalid, 
            the matchup is ineligible for recording, or the winner cannot be added to the next round.
        RuntimeError
            If the source matchup's match or winner state is inconsistent.
        """
        location = 'DEBracket._record_match_result()'

        if method_name not in ('record_match_score', 'record_forfeit'):
            raise ValueError(f'method_name must be either \'record_match_score\' or \'record_forfeit\' in {location}')

        if method_name == 'record_match_score' and (score1 is None or score2 is None):
            raise ValueError(f'If method_name is \'record_match_score\', then arguments for score1 and score2 must be provided in {location}')

        elif method_name == 'record_forfeit' and forfeiting_index is None:
            raise ValueError(f'If method_name is \'record_forfeit\', then an argument for forfeiting_index must be provided in {location}')

        matchup = self.get_matchup(round_index, matchup_index)

        # Validate that the matchup can have its result recorded
        self._validate_matchup_eligibility_to_record(matchup)

        # If it is the final, simply record the result
        if self._is_final_matchup(matchup):
            if method_name == 'record_match_score':
                matchup.record_match_score(score1, score2)
            else:
                matchup.record_forfeit(forfeiting_index)

            return
        
        # Save the matchup's match info
        old_score1, old_score2, old_forfeited_index, old_completed = self._capture_match_result(matchup)

        # Save the next matchup's entry and match info
        next_matchup = self._get_next_matchup(matchup)
        old_next_entry1, old_next_entry2, old_next_match = self._capture_matchup(next_matchup)

        # Try to record the result and advance the winner
        try:
            if method_name=='record_match_score':
                matchup.record_match_score(score1, score2)

            else:
                matchup.record_forfeit(forfeiting_index)

            self._advance_matchup_winner(matchup)

        # Restore the original matchup's match state and restore the original destination's entries and match
        except Exception:
            self._restore_match_result(matchup, old_score1, old_score2, old_forfeited_index, old_completed)
            self._restore_matchup(next_matchup, old_next_entry1, old_next_entry2, old_next_match)

            raise

    def _replace_match_result(self, round_index: int, matchup_index: int, method_name: str, *, score1=None, score2=None, forfeiting_index=None) -> None:
        """
        Replace a recorded result and update the advancing entry.

        The operation is selected by ``method_name``.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round.
        method_name : str
            The operation to perform: ``'replace_with_score'`` or ``'replace_with_forfeit'``.
        score1 : int | None, default=None
            The new top-entry score, required for ``'replace_with_score'``.
            Ignored when replacing the result with a forfeit.
        score2 : int | None, default=None
            The new bottom-entry score, required for ``'replace_with_score'``.
            Ignored when replacing the result with a forfeit.
        forfeiting_index : int | None, default=None
            The forfeiting entry's index, required for ``'replace_with_forfeit'``:
            ``0`` for the top entry or ``1`` for the bottom entry.
            Ignored when replacing the result with scores.

        Raises
        ------
        TypeError
            If an index or required result value has an invalid type, or advancement encounters an invalid entry attribute type.
        ValueError
            If ``method_name`` is unsupported, if ``replace_with_score`` is selected but no scores are provided, 
            if ``replace_with_forfeit`` is selected but no forfeiting index is provided, an index or result value is invalid, 
            the existing result cannot be undone, or the new winner cannot be added to the next round.
        RuntimeError
            If the source match is missing, the previously advanced entry is missing or differs from the recorded winner, 
            or the source result has an inconsistent winner state.
        """
        location = 'DEBracket._replace_match_result()'

        if method_name not in ('replace_with_score', 'replace_with_forfeit'):
            raise ValueError(f'method_name must be either \'replace_with_score\' or \'replace_with_forfeit\' in {location}')
        
        if method_name == 'replace_with_score' and (score1 is None or score2 is None):
            raise ValueError(f'If method_name is \'replace_with_score\', then arguments for score1 and score2 must be provided {location}')

        elif method_name == 'replace_with_forfeit' and forfeiting_index is None:
            raise ValueError(f'If method_name is \'replace_with_forfeit\', then an argument for forfeiting_index must be provided in {location}')
        
        matchup = self.get_matchup(round_index, matchup_index)
        
        self._validate_matchup_eligibility_to_undo(matchup, 'replace')

        if self._is_final_matchup(matchup):
            if method_name == 'replace_with_score':
                matchup.replace_with_score(score1, score2)
            
            else:
                matchup.replace_with_forfeit(forfeiting_index)

            return

        # Save the matchup's match info
        old_score1, old_score2, old_forfeited_index, old_completed = self._capture_match_result(matchup)

        # Save the next matchup's entry and match info
        next_matchup = self._get_next_matchup(matchup)
        old_next_entry1, old_next_entry2, old_next_match = self._capture_matchup(next_matchup)

        # Try to remove advanced winner, replace matchup result with new result, and advance new winner
        try:
            next_matchup.remove_entry(matchup.next_matchup_entry_index)
            
            if method_name == 'replace_with_score':
                matchup.replace_with_score(score1, score2)

            else:
                matchup.replace_with_forfeit(forfeiting_index)

            self._advance_matchup_winner(matchup)

        except Exception:
            # Restore the original matchup match state and restore the original destination entries and match
            self._restore_match_result(matchup, old_score1, old_score2, old_forfeited_index, old_completed)
            self._restore_matchup(next_matchup, old_next_entry1, old_next_entry2, old_next_match)
            
            raise


    # --- Validation Helper Methods ---
    def _validate_round_index(self, index: int, method_name: str | None = None) -> None:
        """
        Validate a zero-based index into the bracket's round tuple.

        Parameters
        ----------
        index : int
            The index to validate.
        method_name : str | None, default=None
            The calling method's name, used to provide context in the error messages.

        Raises
        ------
        TypeError
            If ``index`` is not an integer, or ``method_name`` is neither a string nor ``None``.
        ValueError
            If ``index`` is outside the valid range of round indices.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in DEBracket._validate_round_index() - got {type(method_name).__name__}')

        location = 'DEBracket' if method_name is None else f'DEBracket.{method_name}()'
        
        if type(index) is not int:
            raise TypeError(f'Round index must be an integer in {location} - got {type(index).__name__}')
        
        if index < 0 or index >= self.num_rounds:
            raise ValueError(
                f'Round index must be between 0 and {self.num_rounds - 1} '
                f'(inclusive) in {location} - got {index}'
            )

    def _validate_matchup_index(self, round_index: int, matchup_index: int, method_name: str | None = None) -> None:
        """
        Validate a round index and a matchup index within that round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within the selected round.
        method_name : str | None, default=None
            The calling method's name, used to provide context in the error messages.

        Raises
        ------
        TypeError
            If either index is not an integer, or ``method_name`` is neither a string nor ``None``.
        ValueError
            If either index is outside its corresponding valid range.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in DEBracket._validate_matchup_index() - got {type(method_name).__name__}')

        self._validate_round_index(round_index, method_name)
        
        location = 'DEBracket' if method_name is None else f'DEBracket.{method_name}()'

        if type(matchup_index) is not int:
            raise TypeError(f'Matchup index must be an integer in {location} - got {type(matchup_index).__name__}')

        if matchup_index < 0 or matchup_index >= self.rounds[round_index].num_matchups:
            raise ValueError(
                f'Matchup index must be between 0 and {self.rounds[round_index].num_matchups - 1} (inclusive) '
                f'for round index {round_index} in {location} - got {matchup_index}'
            )
    
    def _validate_forfeiting_index(self, forfeiting_index: int, method_name: str | None = None) -> None:
        """
        Validate a forfeiting entry index of ``0`` or ``1``.

        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's position: ``0`` for the top entry or ``1`` for the bottom entry.
        method_name : str | None, default=None
            The calling method's name, used to provide context in the error messages.

        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer, or ``method_name`` is neither a string nor ``None``.
        ValueError
            If ``forfeiting_index`` is neither ``0`` nor ``1``.
        """
        validation.validate_int_in_range(forfeiting_index, 0, 1, 'Forfeiting index', 'DEBracket', method_name)
    
    def _validate_scores(self, score1: int, score2: int, method_name: str | None = None) -> None:
        """
        Validate two distinct integer scores within the permitted range.

        Parameters
        ----------
        score1 : int
            The score for entry 1.
        score2 : int
            The score for entry 2.
        method_name : str | None, default=None
            The calling method's name, used to provide context in error messages.

        Raises
        ------
        TypeError
            If either score is not an integer, or ``method_name`` is neither a string nor ``None``.
        ValueError
            If either score is not between 0 and ``score_to_win``, or the scores are equal.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in DEBracket._validate_score_pair() - got {type(method_name).__name__}')

        location = 'DEBracket' if method_name is None else f'DEBracket.{method_name}()'

        validation.validate_int_in_range(score1, 0, self.score_to_win, 'Score 1', 'DEBracket', method_name)
        validation.validate_int_in_range(score2, 0, self.score_to_win, 'Score 2', 'DEBracket', method_name)

        if score1 == score2:
            raise ValueError(f'Score1 and score2 cannot be tied in {location} - got score1={score1}, score2={score2}')

    def _validate_seed_ordered_entries(self, ordered_entries: tuple[TournamentEntry, ...]) -> None:
        """
        Validate the entry collection used to construct the bracket.

        Parameters
        ----------
        ordered_entries : tuple[TournamentEntry, ...]
            The entries to validate, supplied in ascending seed order with the highest seed first.

        Raises
        ------
        TypeError
            If ``ordered_entries`` is not a tuple or an item is not a ``TournamentEntry``.
        ValueError
            If fewer than two entries are supplied, an entry ID or fencer ID appears more than once, 
            or the entries have different tournament IDs.
        """
        if not isinstance(ordered_entries, tuple):
            raise TypeError(f'Seed ordered entries must be a tuple in DEBracket - got {type(ordered_entries).__name__}')
        
        if len(ordered_entries) < 2:
            raise ValueError(f'DEBracket requires at least two entries - got {len(ordered_entries)}')
        
        seen_entry_ids: set[int] = set()
        seen_fencer_ids: set[int] = set()
        
        for i, entry in enumerate(ordered_entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(
                    f'Entry at index {i} in seed_ordered_entries must be a TournamentEntry in DEBracket - got {type(entry).__name__}'
                )
            
            if entry.id in seen_entry_ids:
                raise ValueError(f'Entry ID {entry.id} at index {i} in seed_ordered_entries has already appeared in DEBracket')
            
            if i == 0:
                tournament_id: int = entry.tournament_id

            if entry.tournament_id != tournament_id:
                raise ValueError(
                    f'Entry ID {entry.id} at index {i} in seed_ordered_entries must have '
                    f'tournament ID {tournament_id} in DEBracket - got {entry.tournament_id}'
                )
            
            if entry.fencer.id in seen_fencer_ids:
                raise ValueError(f'Fencer {entry.fencer.id} appears more than once in seed_ordered_entries')

            seen_entry_ids.add(entry.id)
            seen_fencer_ids.add(entry.fencer.id)

    def _validate_matchup_eligibility_to_record(self, matchup: DEMatchup) -> None:    
        """
        Check whether the matchup is eligible to receive a new result.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup to check before recording a result.

        Raises
        ------
        ValueError
            If the matchup is a bye, either entry is missing, 
            the match is already complete, or the destination position is occupied.
        RuntimeError
            If both entries are present but the matchup has no match.
        """
        if matchup.is_bye():
            raise ValueError(f'Cannot record a result for {matchup.label} because it is a BYE')

        if matchup.is_missing_an_entry():
            raise ValueError(f'Cannot record a result for {matchup.label} beacuse both entries are required')
        
        if matchup.match is None:
            raise RuntimeError(f'{matchup.label} contains both entries but has no DE match')

        if matchup.is_complete():
            raise ValueError(f'Cannot record a result for {matchup.label} because it is already complete')

        if not self._is_final_matchup(matchup) and not self._is_next_matchup_entry_position_available(matchup):
            raise ValueError(
                f'Cannot record a result for {matchup.label} because the winner does not have an entry position to proceed to in the next round'
            )
    
    def _validate_matchup_eligibility_to_undo(self, matchup: DEMatchup, action_name: str) -> None:
        """
        Check whether a recorded result can be reset or replaced.

        Parameters
        ----------
        matchup : DEMatchup
            The matchup whose recorded result would be undone.
        action_name : str
            The action label used in error messages.

        Raises
        ------
        ValueError
            If the matchup is a bye, either entry is missing, 
            no result has been recorded, or the next matchup is complete.
        RuntimeError
            If both entries are present but the matchup has no match,
            the destination position is empty or contains an entry unequal to the recorded winner, 
            or the recorded winner state is internally inconsistent.
        """
        if matchup.is_bye():
            raise ValueError(f'Cannot {action_name} the result for {matchup.label} because it is a BYE')
        
        if matchup.is_missing_an_entry():
            raise ValueError(f'Cannot {action_name} a result for {matchup.label} beacuse both entries are required')
        
        if matchup.match is None:
            raise RuntimeError(f'{matchup.label} contains both entries but has no DE match')

        if matchup.is_incomplete():
            raise ValueError(f'Cannot {action_name} the result for {matchup.label} because there is no result to {action_name}')

        if not self._is_final_matchup(matchup):
            next_matchup = self._get_next_matchup(matchup)

            if next_matchup.is_complete():
                raise ValueError(f'Cannot {action_name} the result for {matchup.label} until its next matchup {next_matchup.label}\'s result has been reset first')
            
            if not next_matchup.has_entry_at(matchup.next_matchup_entry_index):
                raise RuntimeError(f'Matchup {next_matchup.label} does not has an entry at index {matchup.next_matchup_entry_index} when its previous matchup has a recorded result')
            
            if next_matchup.entry_at(matchup.next_matchup_entry_index) != matchup.winner:
                raise RuntimeError(f'The next matchup {next_matchup.label}\'s entry at position {matchup.next_matchup_entry_index} does not match the current matchup\'s winner')
