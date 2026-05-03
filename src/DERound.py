from dataclasses import dataclass, field
from Matches import DEMatch

@dataclass
class DERound:
    round_number: int # Indexes the rounds such that 0 is the first round
    matches: list[DEMatch] = field(default_factory=list) # Creates a new list every time a DERound instance is created

    def add_match(self, match: DEMatch) -> None:
        if not isinstance(match, DEMatch):
            raise TypeError('Input match must be of a DEMatch type')
        self.matches.append(match)
    
    def is_complete(self) -> bool:
        return all(match.completed for match in self.matches)
    
    def get_match(self, position: int) -> DEMatch:
        if not isinstance(position, int):
            raise TypeError('Position must be an integer')
        if position < 0 or position >= len(self.matches):
            raise ValueError('Position must be within match indexing')
        return self.matches[position]
    
    @staticmethod
    def get_round_name(bracket_size: int, round_number: int) -> str:
        if not isinstance(bracket_size, int):
            raise TypeError('The input bracket size must be an integer')
        if not isinstance(round_number, int):
            raise TypeError('The input round number must be an integer')
        
        if bracket_size <= 0:
            raise ValueError('Bracket size must be a positive integer')
        
        if round_number < 0:
            raise ValueError('Round number must be non-negative')

        remaining_fencers = bracket_size // (2**round_number)

        if remaining_fencers == 2:
            return 'Final'
        elif remaining_fencers == 4:
            return 'Semi-Final'
        elif remaining_fencers == 8:
            return 'Quarter-Final'
        else:
            return f'Round of {remaining_fencers}'