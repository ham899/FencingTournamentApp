from dataclasses import dataclass
from match import DEMatch
from tournament_entry import TournamentEntry
import math

def is_power_of_two(n: int) -> bool:
    """ Returns true if the input is a power of two, false otherwise. """
    if type(n) is not int:
        raise TypeError('Input must be an integer')
    if n <= 0:
        return False
    while n % 2 == 0:
        n = n // 2
    return n == 1

@dataclass
class DERound:
    """ 
    Represents a round in the DE bracket; a round must hold DE matches. 
    The number of matches it holds must be a power of two.
    A round can hold empty matches as the preceding matches have not been completed yet.
    The matches inputted must be such that the sum of the two de_seeds of the entries must equal the round size plus one.
    """
    index: int # Indexes the rounds such that 0 is the first round
    size: int # Represents the maximum number of entries the round can hold
    matches: list[DEMatch]

    def __post_init__(self):
        # Validate types
        if type(self.index) is not int:
            raise TypeError('Round index must be an integer')
        if type(self.size) is not int:
            raise TypeError('Round size must be an integer')
        if not isinstance(self.matches, list):
            raise TypeError('Matches must be held in a list')
        for match in self.matches:
            if not isinstance(match, DEMatch):
                raise TypeError('Matches list must hold DEMatch objects')
        
        # Validate values
        if self.index < 0:
            raise ValueError('Round index must be non-negative')
        if self.size < 0:
            raise ValueError('Round size must be non-negative')
        if not is_power_of_two(self.size):
            raise ValueError('Round size must be a power of two')
        
        # Check that there is congruency between round size and the number of matches inputted
        if self.size != 2*len(self.matches):
            raise ValueError('The number of matches present must equal round size')
        
        ### Validate matches ###
        for i, match in enumerate(self.matches):
            if match.round_index != self.index:
                raise ValueError('DE match round index must match the round it is being held in')
            if match.match_index != i:
                raise ValueError('Order of match indices in matches list must be valid')
            # If a complete match is given, validate the seed matchmaking
            if match.entry1 is not None and match.entry2 is not None and match.entry1.de_seed + match.entry2.de_seed != self.size + 1:
                raise ValueError(f'The sum of the entries\' de seeds must be equal to the round size plus 1. ({self.size+1})')

        # Make a copy of the input matches
        self.matches = list(self.matches)

    def get_match(self, index: int) -> DEMatch:
        """ Gets a specific match based on the provided index. Index 0 is the highest positioned match in the round. """
        if type(index) is not int:
            raise TypeError('Input index must be an integer')
        if index < 0 or index >= len(self.matches):
            raise ValueError(f'Input index must be within range 0-{len(self.matches)-1}')
        return self.matches[index]
    
    def record_match_result(self, index: int, score1: int, score2: int) -> None:
        """ Records a match result based on the given index and scores. """
        if type(index) is not int:
            raise TypeError('Index must be an integer')
        if type(score1) is not int or type(score2) is not int:
            raise TypeError('Scores must be a integers')
        
        if index < 0 or index >= len(self.matches):
            raise ValueError(f'Index must be within the range 0-{len(self.matches)-1}')
        if score1 < 0 or score2 < 0:
            raise ValueError('Scores must be non-negative integers')
        
        self.get_match(index=index).record_score(score1=score1, score2=score2)

    def is_complete(self) -> bool:
        """ Checks whether all matches in this round are complete. """
        return all(match.completed for match in self.matches)
        
    def get_winners(self) -> list[TournamentEntry]:
        """Returns the winners of the matches in this round. Note some matches may still be incomplete."""
        winners = []
        for match in self.matches:
            if match.is_complete():
                winner = match.get_winner()
                if winner is None:
                    raise ValueError('A match was marked complete with no winner set.')
                winners.append(winner)
        return winners

    def get_losers(self) -> list[TournamentEntry]:
        """Returns the losers of the matches in the round. Note some matches may still be incomplete."""
        losers = []
        for match in self.matches:
            if match.is_complete():
                loser = match.get_loser()
                if loser is None:
                    raise ValueError('A match was marked complete with no winner set.')
                losers.append(loser)
        return losers
    
    def get_round_name(self) -> str:
        """ Returns the conventionally titled name of the round for readability. """
        if self.size == 2:
            return 'Final'
        elif self.size == 4:
            return 'Semi-Final'
        elif self.size == 8:
            return 'Quarter-Final'
        else:
            return f'Round of {self.size}'
        
    @staticmethod
    def _generate_tree_bracket_level(depth):
        """ Returns the ordered list from top to bottom on the bracket of positions to fence each other. """

        current_depth = 0
        current_level = [1]

        while current_depth < depth:
            # Go to next depth
            current_depth += 1

            # Initialize a list to hold the next level values
            next_level = []

            # Define loop starting conditions
            invariant_sum = 2**current_depth+1
            is_left = True

            # Build the next level
            for item in current_level:
                complement = invariant_sum - item
                if is_left:
                    next_level += [item, complement]
                else:
                    next_level += [complement, item]
                
                is_left = not is_left

            # Set new current level
            current_level = next_level

        return current_level


    def get_position(self, match_index: int, location: int):
        """ Takes the match index and a location (0 for on top and 1 for on bottom) and the position/rank within the round (not the entry's DE seed) is returned. """
        if type(match_index) is not int:
            raise TypeError('Match index must be an integer')
        if type(location) is not int:
            raise TypeError('Location must be an integer')
        if match_index < 0 or match_index >= len(self.matches):
            raise ValueError(f'Match index must be within the appropriate range of matches (0-{len(self.matches)})')
        if location not in [0,1]:
            raise ValueError('Location input must be either 0 or 1')
        
        # Calculate the round's depth
        d = math.log2(self.size)
        
        # Generete the tree level of positions
        level = DERound._generate_tree_bracket_level(depth=d)

        # Return the position for this match and fencer (1 or 2)
        return level[match_index*2+location]