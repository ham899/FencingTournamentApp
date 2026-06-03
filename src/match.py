from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional

from tournament_entry import TournamentEntry


##### MATCH ABSTRACT BASE CLASS #####

@dataclass
class Match(ABC):
    """
    Represents a match between two entries in a tournament. It is an abstract class that acts as the parent for the poule and DE match subclasses.
    A match is meant to be instantiated with zero, one, or two entries depending on thhe context, and its scores are meant to be recorded after initialization.

    Note: this class **cannot** be instantiated directly because it is an **abstract class**.

    Note: for now, we will only consider single forfeits and not double forfeits or disqualifications.

    Attributes
    ----------
    id: int
        The unique identifier for the match.
    tournament_id: int
        The unique identifier for the tournament that the match belongs to.
    score_to_win: int
        The score required to win the match: typically 5 for poule matches and 15 for DE matches. 
        However, it can be customized when setting up the tournament.

    entry1: TournamentEntry, default=None
        The tournament entry for fencer 1 in the match. 
        A None value either represents a BYE or when the entry is still TBD in the DE bracket. 
        None values are not allowed for poule matches.
    entry2: TournamentEntry, default=None
        The tournament entry for fencer 2 in the match. 
        A None value either represents a BYE or when the entry is still TBD in the DE bracket. 
        None values are not allowed for poule matches.

    score1: Optional[int], default=None
        The score for fencer 1 in the match. It cannot be set upon initialization and defaults to None.
        This is optional to account for matches that are not yet completed, BYEs, and forfeits where no score is recorded.
    score2: Optional[int], default=None
        The score for fencer 2 in the match. It cannot be set upon initialization and defaults to None.
        This is optional to account for matches that are not yet completed, BYEs, and forfeits where no score is recorded.
    winner: Optional[TournamentEntry], default=None
        The tournament entry for the winner of the match. It also cannot be set upon initialization and defaults to None.
        This is optional to account for matches that are not yet completed and forfeits where there may not be a winner to record.
    completed: bool, default=False
        A boolean value indicating whether the match is completed or not.
        It cannot be set upon initialization and defaults to False as the match is not completed when it is first initialized.
        This is important to mark BYEs as completed and mark completed matches that did not reach the score to win value.
    """
    id: int
    tournament_id: int
    score_to_win: int

    entry1: TournamentEntry = field(default=None)
    entry2: TournamentEntry = field(default=None)

    score1: Optional[int] = field(default=None, init=False)
    score2: Optional[int] = field(default=None, init=False)
    winner: TournamentEntry = field(default=None, init=False)
    completed: bool = field(default=False, init=False) # Need to know this for BYEs and scores that are less than the score to win but timer ran out and match is over

    def __post_init__(self) -> None:
        """
        Validates the match's ID, tournament ID, score to win, and entries upon initialization.
        
        Raises
        ------
        TypeError
            If the match's ID, tournament ID, or score to win is not an integer, or if the entries are not of type TournamentEntry or None.
        ValueError
            If the match's ID, tournament ID, or score to win is not a positive integer.
        """
        # Validate input types
        if type(self.id) is not int:
            raise TypeError("Match ID must be an integer.")
        
        if type(self.tournament_id) is not int:
            raise TypeError("Tournament ID must be an integer.")
        
        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        if self.entry1 is not None and not isinstance(self.entry1, TournamentEntry):
            raise TypeError("Fencer 1 entry must be of type TournamentEntry or None.")
        
        if self.entry2 is not None and not isinstance(self.entry2, TournamentEntry):
            raise TypeError("Fencer 2 entry must be of type TournamentEntry or None.")
        
        # Validate input values
        if self.id < 1:
            raise ValueError("Match ID must be a positive integer.")
        
        if self.tournament_id < 1:
            raise ValueError("Tournament ID must be a positive integer.")
        
        if self.score_to_win < 1:
            raise ValueError("Score to win must be a positive integer.")

    @abstractmethod
    def match_type(self) -> str:
        """
        Returns the type of the match as a string.
        It is an abstract method that must be implemented by the subclasses to return either "poule" or "DE" depending on the type of match.
        
        Returns
        -------
        str
            The match type: either "poule" or "DE".
        """
        pass

    @abstractmethod
    def forfeit(self, entry_index: int) -> None:
        """
        Forfeits one of the entries in the match based on the input entry index. 
        The implementation of this method depends on the type of match and is defined in the subclasses.

        Parameters
        ----------
        entry_index : int
            The index of the entry to forfeit: either 0 for entry 1 or 1 for entry 2.
        """
        pass

    @abstractmethod
    def forfeit1(self) -> None:
        """ Forfeits entry 1 in the match. The implementation of this method depends on the type of match and is defined in the subclasses. """
        pass

    @abstractmethod
    def forfeit2(self) -> None:
        """ Forfeits entry 2 in the match. The implementation of this method depends on the type of match and is defined in the subclasses. """
        pass

    def is_complete(self) -> bool:
        """
        Returns true if the match has been marked complete; otherwise, returns false.
        Note: A match can be marked complete even if no scores are recorded in the case of BYEs and forfeits.
        
        Returns
        -------
        bool
            True if the match is marked complete; false otherwise.
        """
        return self.completed
    
    def mark_complete(self) -> None:
        """ Marks a match as complete. """
        self.completed = True
    
    def set_winner(self, entry: TournamentEntry) -> None:
        """
        Sets the winner of the match to the input entry after the input entry is validated, and marks the match as complete.

        Note: This method is independent of setting the score values.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to set as the winner of the match.

        Raises
        ------
        TypeError
            If the entry is not of type TournamentEntry.
        ValueError
            If the entry is not one of the entries in the match.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry to set as the winner of match {self.id} must be a TournamentEntry object.')
        
        if entry != self.entry1 and entry != self.entry2:
            raise ValueError(f'Entry to set as the winner of match {self.id} must be one of the entries in the match.')

        # Set winner and mark match as complete
        self.winner = entry
        self.mark_complete()

    def get_loser(self) -> Optional[TournamentEntry]:
        """
        Returns the loser of the match or returns None if there is no loser.
        There is no loser when a match is incomplete or when there is a BYE.

        Returns
        -------
        Optional[TournamentEntry]
            The loser of the match if there is one or None otherwise.
        """
        if not self.is_complete():
            return None

        # Case 1: Completed match is a BYE or forfeits
        if self.winner is not None:
            if self.entry1 is None or self.entry2 is None:
                return None
           # Case 2: Completed match with two entries and a winner
            else:
                return self.entry1 if self.entry1 != self.winner else self.entry2
        # Case 3: Completed match with no winner (e.g. due to a double forfeit; very rare)
        else:
            return None

    def record_score(self, score1: int, score2: int) -> None:
        """
        Record the result of a match by providing two scores: one for entry 1 and one for entry 2.

        Parameters
        ----------
        score1 : int
            The score for entry 1 in the match.
        score2 : int
            The score for entry 2 in the match.
        
        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If either score is negative, greater than the score to win the match, or if the scores are equal (matches cannot end in a tie).
        """
        # Validate input scores
        if type(score1) is not int or type(score2) is not int:
            raise TypeError(f'Scores must be integers to record the scores for match {self.id}.')
        
        if score1 < 0 or score1 > self.score_to_win or score2 < 0 or score2 > self.score_to_win:
            raise ValueError(f'Scores must be between 0 and {self.score_to_win} to record the scores for match {self.id}.')

        if score1 == score2:
            raise ValueError(f'The input scores cannot be equal to record the scores for match {self.id} - matches cannot end in a tie.')

        # Update score values
        self.score1 = score1
        self.score2 = score2

        # Set winner
        if self.score1 > self.score2:
            self.set_winner(self.entry1)
        else:
            self.set_winner(self.entry2)


##### POULE MATCH CLASS #####

@dataclass(kw_only=True) # Key-word only allows us to have attributes that do not need default values
class PouleMatch(Match):
    """
    Represents a poule match between two fencers in a tournament.
    This class is a subclass of the Match class and inherits its attributes and methods.
    Both fencers **must** be present for a poule match to be valid.
    Let entry 1 represent the fencer on the left of the referee and entry 2 represent the fencer on the right.

    Attributes
    ----------
    poule_id: int
        The unique identifier for the poule that the match belongs to.
    match_index: int
        The index of the match within the poule, using zero-indexing. This defines the match order.

    score_to_win: int, default=5
        The score required to win the match. It defaults to 5 for poule matches but can be customized when setting up the tournament.
    """
    poule_id: int
    match_index: int

    score_to_win: int = 5

    def __post_init__(self, max_match_index: int) -> None:
        """
        Validates the fields of the parent match class plus validates the poule ID, match index, and poule score to win.
        Importantly, checks that there is no None entries for a poule match.

        Parameters
        ----------
        max_match_index : int
            The maximum match index for the poule.

        Raises
        ------
        TypeError
            If any of the attribute types are invalid.
        ValueError
            If the poule ID is not positive, if the match index is out of bounds, and if there is a None entry.
        """
        # Call parent post init to validate common fields
        super().__post_init__()

        # Validate input types
        if type(self.poule_id) is not int:
            raise TypeError('Poule ID must be an integer.')

        if type(self.match_index) is not int:
            raise TypeError('Match index must be an integer.')

        if type(self.score_to_win) is not int:
            raise TypeError('Score to win must be an integer.')

        # Validate input values
        if self.poule_id < 1:
            raise ValueError('Poule ID must be a positive integer.')

        if self.match_index < 0 or self.match_index > max_match_index:
            raise ValueError(f'Match index must be between 0 and {max_match_index} for the poule.')

        # A poule match **must** be supplied with two valid entries
        if self.entry1 is None or self.entry2 is None:
            raise ValueError('A poule match requires two fencers. There are no BYEs in poule matches.')

    def match_type(self) -> str:
        """
        Returns the type of match as a string.

        Returns
        -------
        str
            The match type: "poule" for this class.
        """
        return "poule"
    
    def forfeit(self, entry_index: int) -> None:
        """
        Forfeits one of the entries in the match based on the input entry index. 
        For a poule match, the score is recorded as the maximum score to win for the winner and 0 for the loser as the result of a forfeit affects the poule results.
        
        Parameters
        ----------
        entry_index : int
            The index of the entry to forfeit: either 0 for entry 1 or 1 for entry 2.
        """
        if type(entry_index) is not int:
            raise TypeError(f'Entry index must be an integer to perform a forfeit in match {self.id}')
        if entry_index not in [0,1]:
            raise ValueError(f'Entry index must be either 0 or 1 to perform a forfeit in match {self.id}')
        if self.entry1 is None or self.entry2 is None:
            raise ValueError(f'Both entries must exist to perform a forfeit in match {self.id}')
        
        # Set score so the winner gets the maximum number of points and the loser gets 0 points
        if entry_index == 0:
            self.score1 = 0
            self.score2 = self.score_to_win
            self.set_winner(self.entry2)
        else:
            self.score1 = self.score_to_win
            self.score2 = 0
            self.set_winner(self.entry1)

    def forfeit1(self) -> None:
        """ Forfeits entry 1 in this poule match. """
        self.forfeit(0)

    def forfeit2(self) -> None:
        """ Forfeits entry 2 in this poule match. """
        self.forfeit(1)

    def __str__(self):
        if self.is_complete():
            return f'Poule Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (Finished)'
        return f'Poule Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (In-Progress)'


##### DE MATCH CLASS #####

@dataclass(kw_only=True) # Key-word only allows us to have attributes that do not need default values
class DEMatch(Match):
    """
    Represents a DE match between two fencers in a tournament. Unlike a poule match, to initialize a match, a fencer does not have to be present, allowing for BYEs and empty matches in the tableau.
    Entry 1 represents the fencer on the top branch of a match in the tableau and entry 2 represents the fencer on the bottom branch of a match in the DE bracket.
    This class is a subclass of the Match class and inherits its attributes and methods. It also has additional attributes to keep track of the round and match index within the round in the DE bracket.

    Attributes
    ----------
    round_index : int
        The index of the round the DE match exists in, using zero-indexing.
    match_index : int
        The index of the match within the round as specified by the round_index, using zero-indexing.
        Note: The index for the parent match in the following round can be obtained by match_index // 2.

    score_to_win : int, default=15
        The score required to win the match. It defaults to 15 for DE matches but can be customized when setting up the tournament.
    """
    round_index: int
    match_index: int

    score_to_win: int = 15
    
    def __post_init__(self, max_round_index: int, max_match_index: int) -> None:
        """
        Validates the fields of the parent match class plus validates the round index, match index, and DE score to win.
        DE matches allow None entries for BYE or empty match situations.
        However, if the match is initialized with one non-None entry and one None entry, it is assumed to be a BYE and the winner is derived.

        Case 1: Both entries present.
        
        Case 2: One None entry => assumed to be a BYE.
        
        Case 3: Both entries are None => assumed to be an empty match.

        Parameters
        ----------
        max_round_index : int
            The maximum round index for the DE bracket.
        max_match_index : int
            The maximum match index within the round for the DE bracket.

        Raises
        ------
        TypeError
            If any of the attribute types are invalid.
        ValueError
            If the round index or match index is negative, or if the score to win is not positive.
        """
        # Call parent post init to validate common fields
        super().__post_init__()

        # Validate input types
        if type(self.round_index) is not int:
            raise TypeError("Round index must be an integer.")
        
        if type(self.match_index) is not int:
            raise TypeError("Match index must be an integer.")

        if type(self.score_to_win) is not int:
            raise TypeError("Score to win must be an integer.")
        
        # Validate input values
        if self.score_to_win < 1:
            raise ValueError("Score to win must be a positive integer.")
        
        if self.round_index < 0 or self.round_index > max_round_index:
            raise ValueError("Round index must be a non-negative integer.")

        if self.match_index < 0 or self.match_index > max_match_index:
            raise ValueError("Match index must be a non-negative integer.")
        
        # Derive winner if match is a BYE
        if self.entry1 is not None and self.entry2 is None:
            self.set_winner(self.entry1)
        elif self.entry1 is None and self.entry2 is not None:
            self.set_winner(self.entry2)

    def match_type(self) -> str:
        """
        Returns the type of match as a string.
        
        Returns
        -------
        str
            The match type: "DE" for this class.
        """
        return "DE"
    
    def forfeit(self, entry_index: int) -> None:
        """
        Forfeits one of the entries in the match based on the input entry index. 
        For a DE match, no score is recorded for a forfeit as it does not affect the results of other matches in the DE bracket.
        
        Parameters
        ----------
        entry_index : int
            The index of the entry to forfeit: either 0 for entry 1 or 1 for entry 2.
        """
        if type(entry_index) is not int:
            raise TypeError(f'Entry index must be an integer to perform a forfeit in match {self.id}')
        if entry_index not in [0,1]:
            raise ValueError(f'Entry index must be either 0 or 1 to perform a forfeit in match {self.id}')
        if self.entry1 is None or self.entry2 is None:
            raise ValueError(f'Both entries must exist to perform a forfeit in match {self.id}')
        
        # Set winner and mark match complete; no score is recorded for a forfeit in a DE match as it does not affect the final results
        if entry_index == 0:
            self.set_winner(self.entry2)
        else:
            self.set_winner(self.entry1)

    def forfeit1(self) -> None:
        """ Forfeits entry 1 in this DE match. """
        self.forfeit(0)

    def forfeit2(self) -> None:
        """ Forfeits entry 2 in this DE match. """
        self.forfeit(1)
    
    def add_entry(self, entry: TournamentEntry, location: int) -> None:
        """
        Adds an entry to the match at the given location.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add to the match.
        location : int
            The location to add the entry to: either 0 for entry 1 or 1 for entry 2.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be a TournamentEntry object to add to match {self.id}')
        if type(location) is not int:
            raise TypeError(f'Location must be an integer to add an entry to match {self.id}')
        if location not in [0,1]:
            raise ValueError(f'Location must be either 0 or 1 to add an entry to match {self.id}')

        if location == 0:
            self.entry1 = entry
        else:
            self.entry2 = entry

    def add_entry1(self, entry: TournamentEntry) -> None:
        """
        Adds an entry to the match as entry 1.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add as entry 1 in the match.
        """
        self.add_entry(entry, 0)

    def add_entry2(self, entry: TournamentEntry) -> None:
        """
        Adds an entry to the match as entry 2.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add as entry 2 in the match.
        """
        self.add_entry(entry, 1)

    def is_bye(self) -> bool:
        """
        Returns true if the match is a BYE; otherwise, returns false.
        Note: BYEs only occur in the first round of the DE bracket.

        Returns
        -------
        bool
            True if the match is a BYE; false otherwise.
        """
        if self.round_index != 0:
            return False
        if self.match_index % 2 == 0:
            if self.entry1 is not None and self.entry2 is None:
                return True
            else:
                return False
        else:
            if self.entry1 is None and self.entry2 is not None:
                return True
            else:
                return False

    def next_match_index(self) -> int:
        """
        Returns the match index for the next match in the DE bracket that the winner of this match will advance to.

        Returns
        -------
        int
            The match index for the next match in the DE bracket that the winner of this match will advance to.
        """
        return self.match_index // 2
    
    def __str__(self):
        if self.entry1 is None and self.entry2 is None:
            return f'DE Match - BYE : BYE'
        elif self.entry2 is None:
            return f'DE Match - {self.entry1.fencer.display_name} : BYE'
        elif self.entry1 is None:
            return f'DE Match - BYE : {self.entry2.fencer.display_name}'
        elif self.completed:
            return f'DE Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (Finished)'
        else:
            return f'DE Match - {self.entry1.fencer.display_name} {self.score1} : {self.score2} {self.entry2.fencer.display_name} (In-Progress)'