from dataclasses import dataclass
from typing import ClassVar

@dataclass
class Fencer:
    """Represents a fencer with an ID and a display name. Single fencers can participate in multiple tournaments."""
    id: int
    display_name: str
    max_name_length: ClassVar[int] = 25

    def __post_init__(self):
        # Validate types
        if type(self.id) is not int:
            raise TypeError("A fencer's ID must be an integer")

        if not isinstance(self.display_name, str):
            raise TypeError("A fencer's input name must be a string")
        
        # Validate id value
        if self.id < 1:
            raise ValueError('Fencer ID must be a positive integer')

        # Trim name
        name = self.display_name.strip()

        # Check that name is a valid length
        if len(name) == 0 or len(name) > Fencer.max_name_length:
            raise ValueError(f"Name must be between 1-{Fencer.max_name_length} characters")
        
        # Set valid display name
        self.display_name = name

    def update_display_name(self, name: str) -> None:
        """ Updates the display name of the fencer; input string is validated internally. """
        # Validate input
        if not isinstance(name, str):
            raise TypeError('New display name must be a string')
        
        # Trim input
        name = name.strip()

        # Check that name is a valid length
        if len(name) == 0 or len(name) > Fencer.max_name_length:
            raise ValueError(f"Name must be between 1-{Fencer.max_name_length} characters")
        
        # Set new display name
        self.display_name = name
    
    def __str__(self):
        return f'{self.display_name} (ID: {self.id})'