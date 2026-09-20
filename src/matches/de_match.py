from dataclasses import dataclass, field

import validation

from de.de_bracket_role import DEBracketRole
from matches.tournament_match import TournamentMatch


@dataclass(eq=False)
class DEMatch(TournamentMatch):
    """
    Represents a DE match between two fencers in a tournament. Entry 1 represents the fencer on the top branch of a matchup in the tableau 
    and entry 2 represents the fencer on the bottom branch. This class is a subclass of the TournamentMatch class and inherits its attributes and methods. 
    Additionally, it has attributes to keep track of the match position within a round, round position within the bracket, and stage position of the tableau.

    Attributes
    ----------
    match_number : int
        The one-based position of the match within a DE round; 
        the first match is the matchup at the "top" of the round.
    round_number : int
        The one-based position of the round within a DE stage; 
        the first round contains all the entries and the last round contains the final matchup.
    stage_number : int
        The one-based position of the stage in the tournament this match exists in.
    score_to_win : int, default=15
        The score required to win the match. 
        It defaults to 15 for DE matches but can be customized when setting up the tournament.
    bracket_role : DEBracketRole, default=DEBracketRole.MAIN
        The role of the bracket in its DE stage this match belongs to.
    """
    match_number: int
    round_number: int
    stage_number: int

    score_to_win: int = field(default=15, kw_only=True)
    bracket_role: DEBracketRole = field(default=DEBracketRole.MAIN, kw_only=True)

    
    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the DE match attributes and validates its inherited attributes.

        Raises
        ------
        TypeError
            If match, round, or stage number is not an integer or if bracket role is not a DEBracketRole.
        ValueError
            If match, round, or stage number is not positive.
        """
        location = 'DEMatch'

        # Validate DE match's defining attributes
        validation.validate_positive_int(self.match_number, 'DE match match number', location)
        validation.validate_positive_int(self.round_number, 'DE match round number', location)
        validation.validate_positive_int(self.stage_number, 'DE match stage number', location)

        if not isinstance(self.bracket_role, DEBracketRole):
            raise TypeError(f'Bracket role in {location} must be a DEBracketRole - got {type(self.bracket_role).__name__}')

        # Get parent to validate common attributes
        super().__post_init__()


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying the match."""
        return (
            f'Match {self.match_number} '
            f'in DE round {self.round_number} '
            f'of the {self.bracket_role.name.lower()} bracket '
            f'in tournament stage {self.stage_number} '
            f'in tournament {self.tournament_id}'
        )

    @property
    def match_type(self) -> str:
        """Returns the type of match as a string."""
        return 'de'

    @property
    def match_index(self) -> int:
        """Return the match's zero-based position within its DE round."""
        return self.match_number - 1
    
    @property
    def round_index(self) -> int:
        """Return the match's zero-based round position within the DE bracket."""
        return self.round_number - 1
    
    @property
    def stage_index(self) -> int:
        """Return the match's zero-based stage position within the tournament."""
        return self.stage_number - 1
    

    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """Verifies equality between this DE match and another object."""
        if not isinstance(other, DEMatch):
            return False

        return (
            self.tournament_id == other.tournament_id and
            self.stage_number == other.stage_number and
            self.round_number == other.round_number and
            self.match_number == other.match_number and 
            self.bracket_role == other.bracket_role
        )


    # --- TournamentMatch Hook Implementations ---
    def _assign_forfeit_scores(self) -> None:
        """Assigns subclass-specific forfeit scores - no scores are needed for a DE forfeit."""
        self.score1 = None
        self.score2 = None
