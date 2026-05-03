from dataclasses import dataclass, field
from TournamentEntry import TournamentEntry
from Matches import DEMatch
from DERound import DERound
from typing import Optional
import math


@dataclass
class DEBracket:
    # Attributes
    id: int
    tournament_id: int
    entries: list[TournamentEntry] # Entries must be seeded
    rounds: list[DERound] = field(default_factory=list)
    completed: bool = False
    current_round_index: int = 0
    bracket_size: Optional[int] = None # Fixed and a power of 2

    def __post_init__(self):
        # Validate input entries
        if self.entries is None:
            raise ValueError('Entries must not be none')
        if len(self.entries) == 0:
            raise ValueError('Entries must not be empty')
        if not isinstance(self.entries, list):
            raise TypeError('Input entries must be a list')
        for entry in self.entries:
            if not isinstance(entry, TournamentEntry):
                raise TypeError('Each entry in the list must be a Tournament Entry')
        
        # Check that the input entries are seeded
        n = len(self.entries)
        valid_seeds = list(range(1,n+1))
        for entry in self.entries:
            if entry.de_seed is None:
                raise ValueError('Entry must have a DE seed')
            if not isinstance(entry.de_seed, int):
                raise TypeError("An entry's DE seed must be an integer")
            if entry.de_seed <= 0 or entry.de_seed > n:
                raise ValueError("An entry's DE seed must be between 1 and the number of entries (inclusive)")
            try:
                valid_seeds.remove(entry.de_seed)
            except ValueError:
                raise ValueError('Entry seeds must be mapped one-to-one on 1..n')
        if len(valid_seeds) != 0:
            raise ValueError('Entry seeds must be mapped one-to-one on 1..n')
        
        # Set bracket size to the correct power of 2
        b = 1
        while b < n:
            b *= 2
        self.bracket_size = b

    def _generate_seed_order(self, size: int) -> list[int]:
        """Returns the ordered seeds for the top side of first-round matches."""
        if size == 2:
            return [1]
        
        prev = self._generate_seed_order(size//2)
        order = []

        for seed in prev:
            order.append(seed)
            order.append(size // 2 + 1 - seed)

        return order


    def _generate_first_round(self) -> None:
        """Uses the seeded entries to generate initial DE matches"""
        matches = []
        number_of_fencers_in_round = self.bracket_size // (2**0)
        higher_on_top = True
        seed_bout_order = self._generate_seed_order(number_of_fencers_in_round)
        for position, i in enumerate(seed_bout_order):
            f1 = None
            f2 = None

            # Find fencer i
            for entry in self.entries:
                if entry.de_seed == i:
                    f1 = entry

            # Find opponent
            for entry in self.entries:
                if entry.de_seed == number_of_fencers_in_round + 1 - i:
                    f2 = entry
            
            if higher_on_top:
                matches.append(DEMatch(
                    id = position+1,
                    tournament_id=self.tournament_id,
                    score_to_win=15,
                    fencer1_entry=f1, 
                    fencer2_entry=f2, 
                    round_number=self.current_round_index, 
                    position=position, 
                    next_match_position=position//2))
            else:
                matches.append(DEMatch(
                    id = position+1,
                    tournament_id=self.tournament_id,
                    score_to_win=15,
                    fencer1_entry=f2, 
                    fencer2_entry=f1, 
                    round_number=self.current_round_index, 
                    position=position, 
                    next_match_position=position//2))

            higher_on_top = not higher_on_top

        # Create a DE round and add to DE Bracket
        de_round = DERound(round_number=self.current_round_index, matches=matches)
        self.rounds.append(de_round)

    def generate_rounds(self) -> None:
        """Creates all rounds in the DE Bracket using the seeded entries and fills in the matches as much as possible initially."""
        if self.rounds:
            raise ValueError('Rounds have already been generated')

        total_number_rounds = int(math.log2(self.bracket_size))
        rounds_created = 0
        self._generate_first_round()
        rounds_created += 1

        # Create future empty rounds
        while rounds_created < total_number_rounds:
            de_round = DERound(rounds_created)

            # Fill the round with empty matches
            number_matches = self.bracket_size // (2**rounds_created) // 2
            for i in range(number_matches):
                m = DEMatch(id=i+1, tournament_id=self.tournament_id, round_number=rounds_created, position=i, next_match_position=i//2)
                de_round.add_match(m)

            self.rounds.append(de_round)            
            rounds_created += 1

        # Advance fencers with BYEs
        for m in self.rounds[0].matches:
            if m.fencer1_entry is None:
                m.winner_entry = m.fencer2_entry
                m.mark_complete()
                self.rounds[1].matches[m.next_match_position].fencer2_entry = m.fencer2_entry
            elif m.fencer2_entry is None:
                m.winner_entry = m.fencer1_entry
                m.mark_complete()
                self.rounds[1].matches[m.next_match_position].fencer1_entry = m.fencer1_entry


    def record_match(self, round_number: int, position: int, score1: int, score2: int) -> None:
        """Record the result of a match and advance the round"""
        # Validate the inputs
        if round_number < 0 or round_number >= len(self.rounds):
            raise ValueError('Round number must be between 0 and height of bracket')
        if position < 0 or position >= len(self.rounds[round_number].matches):
            raise ValueError('Position must be valid for the number of matches in this round')
        
        # Access the match
        m = self.rounds[round_number].matches[position]
        if score1 < 0 or score2 < 0 or score1 > 15 or score2 > 15 or (score1==score2):
            raise ValueError('Input scores must be valid')
        m.record_score(score1, score2)
        winner = m.get_winner()
        next_pos = m.next_match_position
        # Correctly add winner to either top or bottom position if there is a next match
        if round_number == len(self.rounds) - 1:
            self.completed = True
            return
        if m.position % 2 == 0:
            self.rounds[round_number+1].matches[next_pos].fencer1_entry = winner
            return
        else:
            self.rounds[round_number+1].matches[next_pos].fencer2_entry = winner
            return
        
    def is_complete(self) -> None:
        """Checks if the DE Bracket is complete."""
        return self.completed
    
    def get_winner(self) -> TournamentEntry:
        """Returns the winner entry of the DE Bracket, or returns None if Bracket is incomplete."""
        if not self.is_complete:
            return None
        last_round = self.rounds[-1]
        final = last_round.get_match(0)
        return final.get_winner()

    def get_current_round(self) -> int:
        """Returns the current round still to be completed in the tableau."""
        return self.bracket_size // 2**self.current_round_index