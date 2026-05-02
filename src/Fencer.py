from dataclasses import dataclass
from typing import ClassVar

# Represents a single fencer; a fencer can fence in multiple tournaments
@dataclass
class Fencer:
    # Attributes
    id: int
    display_name: str

    # Static variable
    max_name_length: ClassVar[int] = 30

    def __post_init__(self):
        name = self.display_name.strip()
        if not Fencer._validate_name(name):
            raise ValueError(
                f"Name must be 1-{Fencer.max_name_length} non-space characters"
            )
        self.display_name = name

    # Helper Method
    @staticmethod
    def _validate_name(name: str) -> bool:
        """ A static helper function to check whether a given name is valid. """
        name = name.strip() # Remove leading and trailing whitespace
        return isinstance(name, str) and 0 < len(name) <= Fencer.max_name_length

    # Methods
    def update_display_name(self, name: str) -> bool:
        """ Updates the display name of the Fencer; input string is validated internally. """
        if Fencer._validate_name(name):
            self.display_name = name.strip()
            return True
        return False
    
    def __str__(self):
        return f'Fencer ID: {self.id} ({self.display_name})'