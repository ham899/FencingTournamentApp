from dataclasses import dataclass
from Fencer import Fencer
from typing import Optional

# Represents an entry participating in a tournament
@dataclass
class TournamentEntry:
    # Attributes
    id: int
    tournament_id: int
    fencer: Fencer
    initial_seed: Optional[int] = None
    de_seed: Optional[int] = None

    def __post_init__(self):
        if not TournamentEntry._validate_positive_int(self.id):
            raise ValueError("ID must be a positive integer")
        
        if not TournamentEntry._validate_positive_int(self.tournament_id):
            raise ValueError("Tournament ID must be a positive integer")
        
        if not TournamentEntry._validate_positive_int(self.fencer.id):
            raise ValueError("Fencer ID must be a positive integer")
        
        if self.initial_seed is not None and not TournamentEntry._validate_seed(self.initial_seed):
            raise ValueError("Initial seed value is invalid")

        if self.de_seed is not None and not TournamentEntry._validate_seed(self.de_seed):
            raise ValueError("DE seed value is invalid")

    # Static Helper Methods
    @staticmethod
    def _validate_seed(seed: int) -> bool:
        """ A static helper function to validate a seed value. """
        return type(seed) is int and seed > 0
    
    @staticmethod
    def _validate_positive_int(value: int) -> bool:
        """ A static helper function to check if a value is a positive integer. """
        return type(value) is int and value > 0

    # Methods to set the seed values
    def set_initial_seed(self, seed: int) -> bool:
        """ Sets the initial seed of the entry. """
        if TournamentEntry._validate_seed(seed):
            self.initial_seed = seed
            return True
        return False

    def set_de_seed(self, seed: int) -> bool:
        """ Sets the DE seed of the entry. """
        if TournamentEntry._validate_seed(seed):
            self.de_seed = seed
            return True
        return False

    def __str__(self):
        return f'Tournament Entry ID: {self.id} (Display Name: {self.fencer.display_name}, Tournament: {self.tournament_id})'