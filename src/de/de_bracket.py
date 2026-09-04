from dataclasses import dataclass, field, InitVar

import validation

from de.de_matchup import DEMatchup
from de.de_round import DERound
from entities.tournament_entry import TournamentEntry
from matches.de_match import DEMatch


@dataclass(eq=False)
class DEBracket:
    """
    Represent a complete direct-elimination bracket within a tournament stage.

    Parameters
    ----------
    stage_number : int
        The DE stage's one-based position within its tournament.
    seed_ordered_entries : tuple[TournamentEntry, ...]
        The entries provided for bracket initialization in ascending seed order.

    Attributes
    ----------
    stage_number : int
        The DE stage's one-based position within its tournament.
    rounds : tuple[DERound, ...]
        All rounds in progression order, made on initialization.
    """
    stage_number: int
    seed_ordered_entries: InitVar[tuple[TournamentEntry, ...]]
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
            If the stage number is not an integer, the entries are not a tuple, 
            an item is not a ``TournamentEntry``, 
            or a generated matchup or match encounters an invalid attribute type.
        ValueError
            If the stage number is not positive, fewer than two entries are supplied, entry IDs repeat, 
            tournament IDs differ, or the generated matchups cannot form valid rounds or matches.
        """
        validation.validate_positive_int(self.stage_number, 'Stage number', 'DEBracket')
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

        Return ``None`` when every round is complete. A later round can
        already contain ready matchups while this round remains incomplete.
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
        """
        Return the first incomplete round, or ``None`` if complete.

        The returned round is the stored object, not a copy.
        """
        index = self.current_round_index
        return None if index is None else self.rounds[index]

    @property
    def current_round_size(self) -> int | None:
        """
        Return the first incomplete round's size, or ``None`` if complete.

        The size counts all entry positions in that round, 
        including empty positions still awaiting an advancing winner.
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
            ``True`` if ``other`` is a ``DEBracket`` with the same 
            tournament ID and stage number; otherwise, ``False``.
        """
        if not isinstance(other, DEBracket):
            return False

        return self.tournament_id == other.tournament_id and self.stage_number == other.stage_number
    

    # --- Predicate Methods ---    
    def is_complete(self) -> bool:
        """
        Return whether every round has produced all of its winners.

        Completed scored matches, forfeits, and first-round byes count
        toward completion. Later-round matchups awaiting an entry do not.
        """ 
        return all(round.is_complete() for round in self.rounds)
    
    def is_incomplete(self) -> bool:
        """Return whether at least one bracket round remains incomplete."""
        return not self.is_complete()
    
    def has_started(self) -> bool:
        """
        Return whether an actual match currently has a recorded result.

        Completed scored matches and forfeits count as recorded results;
        Automatic first-round byes do not count.
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
            Twice the round's number of matchups. Empty positions are
            included, so this need not equal the number of entries present.

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
    
    def get_round_losers(self, round_index: int) -> tuple[TournamentEntry, ...]:
        """
        Return the currently known losers of a specified round.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.

        Returns
        -------
        tuple[TournamentEntry, ...]
            Losers of completed matches, including forfeits, in matchup order. 
            Incomplete matchups and byes are omitted.

        Raises
        ------
        TypeError
            If ``round_index`` is not an integer.
        ValueError
            If ``round_index`` is outside the valid range of round indices.
        """
        self._validate_round_index(round_index, 'get_round_losers')
        return self.rounds[round_index].losers
    
    def get_all_round_losers(self) -> tuple[tuple[TournamentEntry, ...], ...]:
        """
        Return the currently known losers grouped by bracket round.

        Returns
        -------
        tuple[tuple[TournamentEntry, ...], ...]
            One tuple per round, in first-round-to-final order. 
            Each inner tuple contains that round's losers in matchup order.
        """
        return tuple(de_round.losers for de_round in self.rounds)
    
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
    
    
    # --- Result Recording Methods ---
    def record_match_result(self, round_index: int, matchup_index: int, score1: int, score2: int) -> None:
        """
        Record a scored result and advance its winner when a next round exists.

        The matchup must contain both entries and its generated match.
        Scores are recorded through the round and matchup before the winner
        is added to the next round. The final has no advancement destination.

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round.
        score1 : int
            The final score of the matchup's top entry.
        score2 : int
            The final score of the matchup's bottom entry.

        Raises
        ------
        TypeError
            If an index or score is not an integer, 
            or an entry needed for advancement has an invalid type.
        ValueError
            If an index is invalid, the matchup lacks an entry, 
            a score is outside the permitted range, the scores are tied, 
            or the match has a forfeit result. Also raised if advancement would duplicate an entry, 
            fill an occupied position, or produce an invalid entry pair in the next round.
        RuntimeError
            If both entries are present but the match is missing, or a completed matchup being advanced has no winner.
        """
        self._validate_matchup_index(round_index, matchup_index, 'record_match_result')
        self._validate_score_pair((score1, score2), 'record_match_result')

        self.rounds[round_index].record_match_result(matchup_index, score1, score2)

        self._advance_matchup_winner(round_index, matchup_index)

    def forfeit(self, round_index: int, matchup_index: int, forfeiting_index: int) -> None:
        """
        Record a forfeit and advance the opposing entry when possible.

        The matchup must contain both entries and an incomplete match.
        The non-forfeiting entry wins without recorded scores. 

        Parameters
        ----------
        round_index : int
            The round's zero-based position within the bracket.
        matchup_index : int
            The matchup's zero-based position within that round.
        forfeiting_index : int
            The forfeiting entry's position within the matchup:
            ``0`` for the top entry or ``1`` for the bottom entry.

        Raises
        ------
        TypeError
            If an index is not an integer, or an entry needed for advancement has an invalid type.
        ValueError
            If an index is invalid, the matchup lacks an entry, or its match is already complete. 
            Also raised if advancement would duplicate an entry, fill an occupied position, 
            or produce an invalid entry pair in the next round.
        RuntimeError
            If both entries are present but the match is missing, or a completed matchup being advanced has no winner.
        """
        self._validate_matchup_index(round_index, matchup_index, 'forfeit')
        self._validate_forfeiting_index(forfeiting_index, 'forfeit')

        self.rounds[round_index].forfeit(matchup_index, forfeiting_index)

        self._advance_matchup_winner(round_index, matchup_index)


    # --- Bracket Construction Helper Methods ---
    def _generate_first_round(self, ordered_entries: tuple[TournamentEntry, ...]) -> DERound:
        """
        Construct the first round from entries in ascending seed order.

        No BYE advancement is applied.

        Parameters
        ----------
        ordered_entries : tuple[TournamentEntry, ...]
            At least two prevalidated entries in ascending seed order.

        Returns
        -------
        DERound
            Round 1 with its matchups in top-to-bottom tableau order,
            including any single-entry matchups representing BYEs.

        Raises
        ------
        TypeError
            If constructing a matchup, match, or round encounters an invalid attribute type.
        ValueError
            If fewer than two entries are supplied or the generated matchups cannot form valid rounds or matches.
        """
        # Extract data from input entries
        num_entries = len(ordered_entries)
        expected_num_rounds = DEBracket._calculate_number_de_rounds(num_entries)
        
        # Get tree level position order
        tree_level_position_order = DERound._generate_tree_bracket_level(expected_num_rounds)

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
                    matchup_number=matchup_index+1,
                    round_number=1,
                    stage_number=self.stage_number,
                    tournament_id=ordered_entries[0].tournament_id,
                    entry1=entry1,
                    entry2=entry2
                )
            )

        # Convert matchups to tuple format
        matchups = tuple(matchups)

        # Return the first round in this bracket
        return DERound(
            matchups=matchups,
            round_number=1,
            stage_number=self.stage_number
        )

    def _init_all_rounds(self, ordered_entries: tuple[TournamentEntry, ...]) -> tuple[DERound, ...]:
        """
        Construct the first bracket round populated by the provided ordered entries and 
        construct all subsequent rounds with empty matchups, and advance first-round BYE winners.

        Parameters
        ----------
        ordered_entries : tuple[TournamentEntry, ...]
            At least two prevalidated entries in ascending seed order.

        Returns
        -------
        tuple[DERound, ...]
            Every round in opening-round-to-final order, with initial BYEs already propagated.

        Raises
        ------
        TypeError
            If constructing a round or advancing a BYE winner encounters an invalid attribute type.
        ValueError
            If the entry count is less than two, a generated structure is invalid, 
            or a BYE winner cannot be added to its destination.
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
                        matchup_number=matchup_index+1,
                        round_number=round_index + 1,
                        stage_number=self.stage_number,
                        tournament_id=ordered_entries[0].tournament_id
                    )
                )

            # Convert the round's matchups to a tuple
            matchups = tuple(matchups)
            
            subsequent_rounds.append(
                DERound(
                    matchups=matchups, 
                    round_number=round_index+1, 
                    stage_number=self.stage_number
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


    # --- Advancement Helper Methods ---
    def _advance_matchup_winner(self, round_index: int, matchup_index: int) -> None:
        """
        Add a completed matchup's winner to its next-round position if possible.

        If a the source matchup is incomplete, this helper does nothing.
        No advancement is performed after the final.

        Parameters
        ----------
        round_index : int
            The source round's zero-based position within the bracket.
        matchup_index : int
            The source matchup's zero-based position within that round.

        Raises
        ------
        TypeError
            If an inspected index or the winning entry has an invalid type.
        ValueError
            If an inspected index is invalid, 
            the winner belongs to another tournament or already occupies the next round, 
            the destination is occupied, or the resulting entry pair is invalid.
        RuntimeError
            If a completed source matchup has no winner when a next round exists.
        """
        next_round_index = round_index + 1

        if next_round_index < self.num_rounds:
            matchup = self.get_matchup(round_index, matchup_index)

            if matchup.is_complete():
                winner = matchup.winner

                if winner is None:
                    raise RuntimeError(
                        f'Cannot advance the winner of {matchup.label}: '
                        f'the matchup is complete but has no winner'
                    )

                self.rounds[next_round_index].add_entry_to_matchup(
                    winner, 
                    matchup.next_matchup_index, 
                    matchup.next_matchup_entry_index
                )


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
    
    def _validate_score_pair(self, scores: tuple[int, int], method_name: str | None = None) -> None:
        """
        Validate a pair of non-negative, non-tied integer scores.

        Parameters
        ----------
        scores : tuple[int, int]
            Exactly two scores, ordered as the top entry's score followed by the bottom entry's score.
        method_name : str | None, default=None
            The calling method's name, used to provide context in the error messages.

        Raises
        ------
        TypeError
            If ``scores`` is not a tuple, either score is not an integer,
            or ``method_name`` is neither a string nor ``None``.
        ValueError
            If the tuple does not contain exactly two scores, a score is negative, or the scores are equal.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method_name must be either a string or None in DEBracket._validate_score_pair() - got {type(method_name).__name__}')

        location = 'DEBracket' if method_name is None else f'DEBracket.{method_name}()'

        if not isinstance(scores, tuple):
            raise TypeError(f'Scores must be a tuple in {location} - got {type(scores).__name__}')
        
        if len(scores) != 2:
            raise ValueError(f'Scores must contain exactly two values in {location} - got {len(scores)}')
        
        score1, score2 = scores

        validation.validate_non_negative_int(score1, 'Score 1', 'DEBracket', method_name)
        validation.validate_non_negative_int(score2, 'Score 2', 'DEBracket', method_name)

        if score1 == score2:
            raise ValueError(f'Scores cannot be tied in {location} - got score1={score1}, score2={score2}')

    def _validate_seed_ordered_entries(self, ordered_entries: tuple[TournamentEntry, ...]) -> None:
        """
        Validate the entry collection used to construct the bracket.

        Parameters
        ----------
        ordered_entries : tuple[TournamentEntry, ...]
            The entries ordered in ascending seed order to validate.

        Raises
        ------
        TypeError
            If ``ordered_entries`` is not a tuple or an item is not a ``TournamentEntry``.
        ValueError
            If fewer than two entries are supplied, an entry ID appears more than once, 
            or an entry's tournament ID differs from the first entry's tournament ID.
        """
        if not isinstance(ordered_entries, tuple):
            raise TypeError(f'Seed ordered entries must be a tuple in DEBracket - got {type(ordered_entries).__name__}')
        
        if len(ordered_entries) < 2:
            raise ValueError(f'DEBracket requires at least two entries - got {len(ordered_entries)}')
        
        seen_entry_ids: set[int] = set()
        
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

            seen_entry_ids.add(entry.id)


    # --- Bracket Size Calculation Helpers ---
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
            The round's zero-based position, 
            from ``0`` for the first round through ``number_of_rounds - 1`` for the final.
        number_de_entries : int
            The total number of actual entrants in the bracket, not the number currently present in this round. 

        Returns
        -------
        int
            The number of matchups to construct in the specified round,
            including positions that are empty or represent BYEs.

        Raises
        ------
        TypeError
            If either argument is not an integer.
        ValueError
            If ``number_de_entries`` is less than two 
            or ``round_index`` is outside the range for the resulting bracket.
        """
        validation.validate_int_at_least(number_de_entries, 2, 'number_de_entries', 'DEBracket', '_calculate_number_matchups_in_de_round')

        number_of_rounds = DEBracket._calculate_number_de_rounds(number_de_entries)
        
        validation.validate_int_in_range(round_index, 0, number_of_rounds - 1, 'round_index', 'DEBracket', '_calculate_number_matchups_in_de_round')
        
        return 2 ** (number_of_rounds - round_index - 1)
