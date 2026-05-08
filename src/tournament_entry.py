from dataclasses import dataclass
from src.fencer import Fencer
from typing import Optional

@dataclass
class TournamentEntry:
    """Represents an entry participating in a tournament."""
    id: int
    tournament_id: int
    fencer: Fencer
    initial_seed: Optional[int] = None
    de_seed: Optional[int] = None

    def __post_init__(self):
        # Validate types
        if type(self.id) is not int:
            raise TypeError("ID must be an integer")
        
        if type(self.tournament_id) is not int:
            raise TypeError("Tournament ID must be an integer")
        
        if not isinstance(self.fencer, Fencer):
            raise TypeError("Fencer must be an instance of Fencer class")
        
        if self.initial_seed is not None and type(self.initial_seed) is not int:
            raise TypeError("Initial seed must be an integer")

        if self.de_seed is not None and type(self.de_seed) is not int:
            raise TypeError("DE seed must be an integer")

        # Validate values
        if self.id <= 0:
            raise ValueError("ID must be a positive integer")
        
        if self.tournament_id <= 0:
            raise ValueError("Tournament ID must be a positive integer")

        if self.initial_seed is not None and self.initial_seed <= 0:
            raise ValueError("Initial seed must be a positive integer")

        if self.de_seed is not None and self.de_seed <= 0:
            raise ValueError("DE seed must be a positive integer")

    def __eq__(self, other):
        if not isinstance(other, TournamentEntry):
            return False
        return self.id == other.id

    # Methods to set the seed values
    def set_initial_seed(self, seed: int) -> None:
        """ Sets the initial seed of the entry. """
        if seed is None:
            self.initial_seed = None
            return
        if type(seed) is not int:
            raise TypeError("Initial seed must be an integer")
        if seed <= 0:
            raise ValueError("Initial seed must be a positive integer")

        self.initial_seed = seed

    def set_de_seed(self, seed: int) -> None:
        """ Sets the DE seed of the entry. """
        if seed is None:
            self.de_seed = None
            return
        if type(seed) is not int:
            raise TypeError("DE seed must be an integer")
        if seed <= 0:
            raise ValueError("DE seed must be a positive integer")

        self.de_seed = seed

    def __str__(self):
        return f'Tournament Entry ID: {self.id} (Display Name: {self.fencer.display_name} - Tournament: {self.tournament_id})'