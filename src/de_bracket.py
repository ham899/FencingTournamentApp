from dataclasses import dataclass, field
from tournament_entry import TournamentEntry
from match import DEMatch
from de_round import DERound
from utils import log2_int, is_power_of_two

@dataclass
class DEBracket:
    """
    Represents an entire DE bracket; a bracket is defined by a list of corresponding rounds. 
    
    The entries **must** be **seeded** and **sorted** in **ascending** order upon initialization of bracket.

    Attributes
    ----------
    id : int
        The unique identifier for the DE Bracket.
    tournament_id : int
        The unique identifier for the tournament this DE Bracket belongs to.
    entries : list[TournamentEntry]
        The list of entries in the DE Bracket, which must be seeded and sorted.
    size : int
        The size of the DE Bracket, which is a fixed power of 2 derived from the provided entries. It is the size of the largest round.
    rounds : list[DERound]
        The list of rounds in the DE Bracket, where the first round is initialized and filled with entries, and subsequent rounds are initialized to be empty.
    current_round_index : int
        The index of the current round still to be completed in the DE Bracket.
    """
    id: int
    tournament_id: int
    entries: list[TournamentEntry]
    size: int = field(init=False)
    rounds: list[DERound] = field(init=False, default_factory=list)
    current_round_index: int = field(init=False, default=0)
    
    def __post_init__(self):
        # Validate types
        if type(self.id) is not int:
            raise TypeError('ID must be an integer')
        if type(self.tournament_id) is not int:
            raise TypeError('Tournament ID must be an integer')
        if not isinstance(self.entries, list):
            raise TypeError('Entries must be a list')
        for entry in self.entries:
            if not isinstance(entry, TournamentEntry):
                raise TypeError('Entries must be a list of Tournament Entries')
        
        # Validate values
        if self.id < 1:
            raise ValueError('ID must be a positive integer')
        if self.tournament_id < 1:
            raise ValueError('Tournament ID must be a positive integer')
        n = len(self.entries)
        if n < 2:
            raise ValueError('The bracket must hold at least two entries')
        
        # Validate that entries have de seeds        
        for i, entry in enumerate(self.entries):
            if type(entry.de_seed) is not int:
                raise TypeError('An entry\'s DE seed must be an integer')
            if entry.de_seed <= 0 or entry.de_seed > n:
                raise ValueError('An entry\'s DE seed must be inclusively between 1 and the number of entries')
            if entry.de_seed != i+1:
                raise ValueError('The entries\' DE seeds must have a one-to-one mapping on 1..n and be in sorted order.')
                    
        # Set bracket size (power of 2)
        b = 1
        while b < n:
            b *= 2
        self.size = b
    
        # Initialize all the rounds in the bracket based on the provided entries
        self._init_all_rounds()

    def _generate_first_round(self):
        """ A helper function to generate the first round in the DE bracket. """

        # Get level seed order
        tree_level_seed_order = DERound._generate_tree_bracket_level(depth=log2_int(self.size))

        # Create DE matches
        n = len(self.entries)
        matches = []
        for i in range(0, self.size, 2):
            match_seed_tuple = (tree_level_seed_order[i], tree_level_seed_order[i+1])

            # Set entry 1
            if match_seed_tuple[0] <= n:
                entry1 = self.entries[match_seed_tuple[0]-1]
            else:
                entry1 = None

            # Set entry 2
            if match_seed_tuple[1] <= n:
                entry2 = self.entries[match_seed_tuple[1]-1]
            else:
                entry2 = None

            # Create match and add to list
            matches.append(DEMatch(id=i//2+1, tournament_id=self.tournament_id, entry1=entry1, entry2=entry2, round_index=0, match_index=i//2))

        # Create first round
        self.rounds.append(DERound(index=0, size=self.size, matches=matches))


    def _init_all_rounds(self):
        """ A helper function to initialize the first round with the appropriate matches and all subsequent rounds are initialized to be empty. BYEs are applied automatically where applicable. """
        
        # 1. Create first round
        self._generate_first_round()

        # 2. Initialize empty rounds
        num_rounds = log2_int(self.size)
        for round_index in range(1,num_rounds):
            round_size = self.size // (2**round_index)
            # Create a list of empty DE matches of the correct length
            matches = []
            i = 0
            for _ in range(round_size//2):
                matches.append(DEMatch(id=i+1, tournament_id=self.tournament_id, round_index=round_index, match_index=i))
                i+=1
            self.rounds.append(DERound(index=round_index, size=round_size, matches=matches))

        # 3. Advance fencers with BYEs in the first round where applicable
        for match in self.rounds[0].matches:
            if match.is_bye():
                # Add to top of next match
                if match.match_index % 2 == 0:
                    self.rounds[1].add_entry1(entry=match.entry1, match_index=match.match_index//2)
                # Add to bottom of next match
                else:
                    self.rounds[1].add_entry2(entry=match.entry2, match_index=match.match_index//2)
    
    def _advance_round_index(self) -> None:
        """ Advances the round index to the next round if all the matches in the current round are complete. """
        current_round = self.get_round(self.current_round_index)
        if current_round.is_complete():
            self.current_round_index += 1

    def record_match_result(self, round_index: int, match_index: int, score1: int, score2: int) -> None:
        """ Records the result of a match in the given round at the given match index using the scores provided. """
        if type(round_index) is not int:
            raise TypeError('Round index must be an integer')
        if type(match_index) is not int:
            raise TypeError('Match index must be an integer')
        if type(score1) is not int or type(score2) is not int:
            raise TypeError('Scores must be integers')
        if round_index < 0 or round_index >= len(self.rounds):
            raise ValueError(f'Round index must be between 0 and the number of rounds ({len(self.rounds)})')
        if match_index < 0 or match_index >= len(self.rounds[round_index].matches):
            raise ValueError(f'Match index must be valid for the number of matches in this round (between 0-{len(self.rounds[round_index].matches)})')
        match = self.get_match(round_index, match_index)
        if score1 < 0 or score2 < 0 or score1 > match.score_to_win or score2 > match.score_to_win or (score1==score2):
            raise ValueError(f'Input scores must be valid: between 0 and {match.score_to_win} and no tied scores allowed')
        if self.get_match(round_index, match_index).is_bye():
            raise ValueError('Cannot record the result of a match with a BYE')
        if self.get_match(round_index, match_index).entry1 is None or self.get_match(round_index, match_index).entry2 is None:
            raise ValueError('Cannot record scores if one or more of the entries is None')
        
        # Record score
        self.rounds[round_index].record_match_result(index=match_index, score1=score1, score2=score2)

        # Advance winner to the next round if possible
        if round_index+1 < len(self.rounds):
            match_winner = self.rounds[round_index].get_match(match_index).winner
            self.rounds[round_index+1].add_entry(entry=match_winner, match_index=match.match_index//2, location=match.match_index%2)

        # Advance to the next round if all matches are complete
        if self.get_round(round_index).is_complete():
            self._advance_round_index()

    def is_complete(self) -> bool:
        """ Checks if the entire DE Bracket is complete (all rounds are completed). """
        for round in self.rounds:
            if not round.is_complete():
                return False
        return True
    
    def get_winner(self) -> TournamentEntry:
        """ Returns the winner entry of the DE Bracket, or returns None if the bracket is incomplete. """
        num_rounds = log2_int(self.size)
        if len(self.rounds) != num_rounds:
            raise ValueError('Not all rounds have been initialized yet')
        if not self.is_complete():
            return None
        last_index = num_rounds-1
        final_round = self.rounds[last_index]
        final = final_round.get_match(0)
        return final.get_winner()
    
    def get_round_losers(self, round_index: int) -> list[TournamentEntry]:
        """ Returns a list of the losers in the specified round by index. """
        if type(round_index) is not int:
            raise TypeError('Round index must be an integer')
        if round_index < 0 or round_index >= len(self.rounds):
            raise ValueError(f'Round index must be within the range 0-{len(self.rounds)-1}')
        return self.rounds[round_index].get_losers()
    
    def get_all_round_losers(self) -> list[list[TournamentEntry]]:
        """ Return a list of losers in each round where the indexing matches the bracket\'s round indexing. """
        if len(self.rounds) != log2_int(self.size):
            raise ValueError('Not all rounds have been initialized yet')
        round_losers = []
        for i in range(len(self.rounds)):
            round_losers.append(self.get_round_losers(round_index=i))
        return round_losers
    
    def get_current_round_size(self) -> int:
        """ Returns the maximum number of positions the current round can hold (size). """
        return self.rounds[self.current_round_index].size
    
    def get_current_round_name(self) -> str:
        """ Returns the current round name as a string still to be copmleted in the tableau. """
        return self.rounds[self.current_round_index].get_round_name()
    
    def get_round(self, index: int) -> DERound:
        """ Returns the DE match at the index. """
        if type(index) is not int:
            raise TypeError('Input index must be an integer')
        if index < 0 or index >= len(self.rounds):
            raise ValueError(f'Input index must be within the range 0-{len(self.rounds)-1}')
        return self.rounds[index]

    def get_match(self, round_index: int, match_index: int) -> DEMatch:
        """ Returns the match using the round and match indices. """
        if type(round_index) is not int:
            raise TypeError('Round index must be an integer')
        if type(match_index) is not int:
            raise TypeError('Match index must be an integer')
        if round_index < 0 or round_index >= len(self.rounds):
            raise ValueError(f'Round index must be within the range 0-{len(self.rounds)-1}')
        if match_index < 0 or match_index >= len(self.get_round(round_index).matches):
            raise ValueError(f'Match index must be within the range 0-{len(self.get_round(round_index).matches)-1}')
        return self.get_round(round_index).get_match(match_index)

    def calculate_final_results(self):
        """ Calculates the final results of the DE bracket based on match results and DE seeds; this is also the final results for the tournament. """
        # Check that the tournament is over
        if not self.is_complete():
            raise ValueError('Cannot calculate final results if the bracket is not complete yet')

        # Build a list of entries for the results
        results = []
        results.append(self.get_winner())

        # Sort the round losers by who has the better de_seed
        all_losers = self.get_all_round_losers()
        for round_losers in all_losers:
            round_losers.sort(key=lambda entry: entry.de_seed)

        # Add the sorted entries to the results list
        for i in range(len(all_losers)-1, -1, -1):
            for entry in all_losers[i]:
                results.append(entry)
        
        return results