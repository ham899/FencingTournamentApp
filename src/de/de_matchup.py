from dataclasses import dataclass, field

import validation

from entities.tournament_entry import TournamentEntry
from matches.de_match import DEMatch


@dataclass(eq=False)
class DEMatchup:
    """
    Represent one matchup position in a DE tableau.

    A matchup may contain zero, one, or two tournament entries. 
    When both entries are present, the matchup automatically creates and stores a ``DEMatch`` between them. 
    A first-round matchup containing exactly one entry represents a bye and is complete without a match. 
    A later-round matchup containing one entry remains incomplete while awaiting its other entry.

    ``entry1`` occupies the top branch of the matchup, while ``entry2`` occupies the bottom branch. 
    The matchup, round, and stage numbers are all one-based.

    Attributes
    ----------
    matchup_number : int
        The matchup's one-based position within its DE round.
    round_number : int
        The round's one-based position within the tableau.
    stage_number : int
        The DE stage's one-based position within the tournament.
    tournament_id : int
        The identifier of the tournament containing the matchup.
    entry1 : TournamentEntry | None, default=None
        The entry occupying the top branch, or ``None`` if that position is empty.
    entry2 : TournamentEntry | None, default=None
        The entry occupying the bottom branch, or ``None`` if that position is empty.
    score_to_win : int, default=15
        The target score and maximum permitted recorded score for either entry.
    match : DEMatch | None, default=None, init=False
        The match generated when both entries are present, or ``None`` otherwise.
    """
    matchup_number: int
    round_number: int
    stage_number: int
    tournament_id: int

    entry1: TournamentEntry | None = None
    entry2: TournamentEntry | None = None
    score_to_win: int = field(default=15, kw_only=True)

    match: DEMatch | None = field(default=None, init=False)


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the matchup identifiers and optional entries.

        A DE match is created automatically when both entries are provided.

        Raises
        ------
        TypeError
            If an identifying number or `score_to_win` is not an integer, 
            an entry is not a ``TournamentEntry``, 
            or the entries cannot form a valid DE match because of an invalid attribute type.
        ValueError
            If an identifying number or `score_to_win` is not positive, 
            an entry belongs to another tournament, 
            or the entries cannot form a valid DE match.
        """
        validation.validate_positive_int(self.matchup_number, 'Matchup number', 'DEMatchup')
        validation.validate_positive_int(self.round_number, 'Round number', 'DEMatchup')
        validation.validate_positive_int(self.stage_number, 'Stage number', 'DEMatchup')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'DEMatchup')
        validation.validate_positive_int(self.score_to_win, 'Score to win', 'DEMatchup')

        self._validate_optional_entry(self.entry1, 'Entry 1')
        self._validate_optional_entry(self.entry2, 'Entry 2')
        
        if self.entry1 is not None and self.entry2 is not None:
            self.match = self._create_match(self.entry1, self.entry2)


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label for this DE matchup."""
        return (
            f'Matchup {self.matchup_number} '
            f'in round {self.round_number} '
            f'in stage {self.stage_number} '
            f'in tournament {self.tournament_id}'
        )
    
    @property
    def matchup_index(self) -> int:
        """Return the matchup's zero-based position within its DE round."""
        return self.matchup_number - 1
    
    @property
    def round_index(self) -> int:
        """Return the round's zero-based position within the tableau."""
        return self.round_number - 1
    
    @property
    def stage_index(self) -> int:
        """Return the stage's zero-based position within the tournament."""
        return self.stage_number - 1
    
    @property
    def next_matchup_index(self) -> int:
        """
        Return the next-round matchup's zero-based position.

        This property describes the matchup's advancement path 
        but does not determine whether a next round exists.
        """
        return self.matchup_index // 2
    
    @property
    def next_matchup_number(self) -> int:
        """Return the one-based position of the matchup in the next round."""
        return self.next_matchup_index + 1
    
    @property
    def next_matchup_entry_index(self) -> int:
        """
        Return the winner's entry index in the next-round matchup.

        The winner of an odd-numbered matchup advances to index ``0``, 
        while the winner of an even-numbered matchup advances to index ``1``.
        """
        return self.matchup_index % 2
    
    @property
    def entries(self) -> tuple[TournamentEntry | None, TournamentEntry | None]:
        """Return the matchup entries as ``(entry1, entry2)``."""
        return (self.entry1, self.entry2)

    @property
    def winner(self) -> TournamentEntry | None:
        """Return the winner of a bye or completed match, or ``None`` otherwise."""
        if self.is_bye():
            if self.entry1 is not None:
                return self.entry1
            else:
                return self.entry2

        if self.match is None:
            return None

        return self.match.winner

    @property
    def loser(self) -> TournamentEntry | None:
        """Return the loser of a completed match, or ``None`` otherwise."""
        if self.match is None:
            return None

        return self.match.loser


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """
        Return whether ``other`` represents the same tableau position.

        Equality is based on tournament ID, stage number, round number, and matchup number. 
        Entries and match results are not considered.
        """
        if not isinstance(other, DEMatchup):
            return False
        
        return (
            self.tournament_id == other.tournament_id and
            self.stage_number == other.stage_number and
            self.round_number == other.round_number and
            self.matchup_number == other.matchup_number
        )


    # --- Predicate Methods ---
    def has_no_entries(self) -> bool:
        """Return whether both matchup positions are empty."""
        return self.entry1 is None and self.entry2 is None

    def is_missing_an_entry(self) -> bool:
        """Return whether at least one matchup position is empty."""
        return self.entry1 is None or self.entry2 is None
    
    def has_an_entry(self) -> bool:
        """Return whether at least one entry is present."""
        return not self.has_no_entries()
    
    def has_exactly_one_entry(self) -> bool:
        """Return whether exactly one entry is present."""
        return self.has_an_entry() and self.is_missing_an_entry()
    
    def has_both_entries(self) -> bool:
        """Return whether both entries are present."""
        return not self.is_missing_an_entry()
        
    def has_entry(self, entry: TournamentEntry) -> bool:
        """
        Return whether the specified entry is present in the matchup.
        
        Parameters
        ----------
        entry : TournamentEntry
            The entry whose presence in the matchup is being checked.
        
        Returns
        -------
        bool
            ``True`` if the entry is present; otherwise ``False``.

        Raises
        ------
        TypeError
            If ``entry`` is not a ``TournamentEntry``.
        ValueError
            If ``entry`` belongs to another tournament.
        """
        self._validate_entry(entry, method_name='has_entry')

        return entry in self.entries
    
    def has_entry_at(self, index: int) -> bool:
        """
        Return whether the specified matchup position contains an entry.

        Parameters
        ----------
        index : int
            The entry index: ``0`` for the top position 
            or ``1`` for the bottom position.

        Returns
        -------
        bool
            ``True`` if the position contains an entry; otherwise ``False``.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is not ``0`` or ``1``.
        """
        self._validate_entry_index(index, 'has_entry_at')
        return self.entry1 is not None if index == 0 else self.entry2 is not None
    
    def has_match(self) -> bool:
        """Return whether the matchup currently contains a DE match."""
        return self.match is not None
    
    def is_first_round(self) -> bool:
        """Return whether the matchup is in the first round of the tableau."""
        return self.round_number == 1

    def is_bye(self) -> bool:
        """Return whether this is a first-round matchup containing exactly one entry."""
        return self.is_first_round() and self.has_exactly_one_entry()
    
    def is_complete(self) -> bool:
        """Return whether the matchup is a bye or contains a completed match."""
        if self.is_bye():
            return True
        
        return self.match is not None and self.match.is_complete()

    def is_incomplete(self) -> bool:
        """Return whether the matchup is incomplete."""
        return not self.is_complete()
    

    # --- Retrieval Methods ---
    def entry_at(self, index: int) -> TournamentEntry | None:
        """
        Return the entry at the specified matchup position.
        
        Parameters
        ----------
        index : int
            The entry index to retrieve the entry from.

        Returns
        -------
        TournamentEntry | None
            The entry at the specified position, or ``None`` if it is empty.
        
        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is not ``0`` or ``1``.
        """
        self._validate_entry_index(index, 'entry_at')
        return self.entry1 if index == 0 else self.entry2
    

    # --- Entry Mutation Methods ---
    def add_entry(self, entry: TournamentEntry, index: int) -> None:
        """
        Add an entry at the specified matchup position.

        A DE match is created automatically if this causes both positions to become occupied.

        Parameters
        ----------
        entry : TournamentEntry
            The entry to add.
        index : int
            The entry index: ``0`` for the top position 
            or ``1`` for the bottom position.

        Raises
        ------
        TypeError
            If ``entry`` is not a ``TournamentEntry`` or ``index`` is not an integer.
        ValueError
            If the entry belongs to another tournament, 
            the index is invalid, the position is already occupied, 
            or the resulting entry pair cannot form a valid DE match.
        """
        self._validate_entry(entry, method_name='add_entry')
        self._validate_entry_index(index, method_name='add_entry')

        if self.has_entry_at(index):
            raise ValueError(
                f'Cannot add an entry at index {index} in {self.label} because that position is already occupied'
            )

        # Check that a valid match can be created before committing the changes
        entry1 = entry if index == 0 else self.entry1
        entry2 = entry if index == 1 else self.entry2

        if entry1 == entry2:
            raise ValueError(
                f'Cannot add entry {entry.id} to {self.label} because that entry is already present at the other position'
            )

        match = None

        if entry1 is not None and entry2 is not None:
            match = self._create_match(entry1, entry2)

        # Commit the changes after validating
        self.entry1, self.entry2, self.match = entry1, entry2, match

    def remove_entry(self, index: int) -> None:
        """
        Remove the entry at the specified matchup position.

        If the matchup contains an incomplete DE match, that match is discarded.
        An entry cannot be removed from a completed match until the match is reset.
        
        Parameters
        ----------
        index : int
            The entry index: ``0`` for the top position 
            or ``1`` for the bottom position.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is not ``0`` or ``1``, the position is empty, 
            or the matchup contains a completed match.
        """
        self._validate_entry_index(index, method_name='remove_entry')

        if not self.has_entry_at(index):
            raise ValueError(
                f'Cannot remove an entry at index {index} from {self.label} because that position is empty'
            )

        if self.match is not None and self.match.is_complete():
            raise ValueError(
                f'Cannot remove an entry from {self.label} because its DE match is complete. Reset the match first.'
            )
        
        if index == 0:
            self.entry1 = None
        else:
            self.entry2 = None

        if self.match is not None:
            self.match = None


    # --- State Change Methods ---
    def reset(self) -> None:
        """Clear both entries and discard any recorded match result."""
        self.entry1, self.entry2, self.match = None, None, None

    def reset_match(self) -> None:
        """
        Reset the contained DE match while preserving both matchup entries.

        Any recorded scores, completion state, and forfeit result are cleared.

        Raises
        ------
        ValueError
            If the matchup does not currently contain a DE match.
        """
        if self.match is None:
            raise ValueError(
                f'Cannot reset the match in {self.label} because the matchup does not contain a DE match'
            )

        self.match.reset()


    # --- Result Recording Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """
        Record a scored result for the matchup's DE match.

        Any existing scored result is overwritten. 
        A forfeit result must be reset before it can be replaced by a scored result.
        
        Parameters
        ----------
        score1 : int
            The final score of ``entry1``.
        score2 : int
            The final score of ``entry2``.
        
        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If the matchup does not contain both entries, 
            either score is outside the permitted range, 
            the scores are tied, or the match already has a forfeit result.
        RuntimeError
            If both entries are present but the matchup's match is unexpectedly missing.
        """
        if self.is_missing_an_entry():
            raise ValueError(
                f'Cannot record a score for {self.label} because the matchup does not contain both entries'
            )
        
        if self.match is None:
            raise RuntimeError(
                f'Cannot record a score for {self.label}: both entries are present, but its DE match is missing'
            )

        self.match.record_score(score1, score2)
    
    def forfeit(self, forfeiting_index: int) -> None:
        """
        Record a forfeit by the entry at the specified index.
        
        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's index: ``0`` for ``entry1`` or ``1`` for ``entry2``.
        
        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer.
        ValueError
            If the matchup does not contain both entries, the index is not ``0`` or ``1``,
            or the match is already complete.
        RuntimeError
            If both entries are present but the matchup's match is unexpectedly missing.
        """
        if self.is_missing_an_entry():
            raise ValueError(
                f'Cannot record a forfeit for {self.label} because the matchup does not contain both entries'
            )

        if self.match is None:
            raise RuntimeError(
                f'Cannot record a forfeit for {self.label}: both entries are present, but its DE match is missing'
            )

        self.match.forfeit(forfeiting_index)

    
    # --- Creation Helper Methods ---
    def _create_match(self, entry1: TournamentEntry, entry2: TournamentEntry) -> DEMatch:
        """
        Create a DE match for this tableau position.
        
        Parameters
        ----------
        entry1 : TournamentEntry
            The entry occupying the match's top position.
        entry2 : TournamentEntry
            The entry occupying the match's bottom position.

        Returns
        -------
        DEMatch
            A newly created DE match for this matchup.
        """
        return DEMatch(
            entry1 = entry1, 
            entry2 = entry2, 
            match_number = self.matchup_number, 
            round_number = self.round_number, 
            stage_number = self.stage_number,
            score_to_win = self.score_to_win
        )


    # --- Validation Helper Methods ---
    def _validate_entry_index(self, index: int, method_name: str | None = None) -> None:
        """
        Validate an entry index of ``0`` or ``1``.

        Parameters
        ----------
        index : int
            The entry index to validate.
        method_name : str | None, default=None
            The calling method's name, used to provide context in error messages.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(
                f'method name must be either a string or None in '
                f'DEMatchup._validate_entry_index() - got {type(method_name).__name__}'
            )

        validation.validate_int_in_range(index, 0, 1, 'Entry index', 'DEMatchup', method_name)
    
    def _validate_entry(self, entry: TournamentEntry, entry_name: str = 'Entry', method_name: str | None = None) -> None:
        """
        Validate an entry for inclusion in this matchup.
        
        Parameters
        ----------
        entry : TournamentEntry
            The entry to validate.
        entry_name : str, default='Entry'
            The label used to identify the entry in error messages.
        method_name : str | None, default=None
            The calling method's name, used to provide context in error messages.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(f'method name must be either a string or None in DEMatchup._validate_entry()')

        location = f'in DEMatchup.{method_name}()' if method_name is not None else 'in DEMatchup'

        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'{entry_name} must be a TournamentEntry {location} - got {type(entry).__name__}')
        
        if entry.tournament_id != self.tournament_id:
            raise ValueError(
                f'{entry_name} must have tournament ID {self.tournament_id} {location} - got {entry.tournament_id}'
            )

    def _validate_optional_entry(self, entry: TournamentEntry | None, entry_name: str = 'Entry') -> None:
        """
        Validate an optional matchup entry.
        
        Parameters
        ----------
        entry : TournamentEntry | None
            The optional entry to validate.
        entry_name : str, default='Entry'
            The label used to identify the entry in error messages.
        """
        if entry is not None:
            self._validate_entry(entry, entry_name)
