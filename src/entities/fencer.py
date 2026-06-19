from dataclasses import dataclass
from typing import ClassVar

import validation

@dataclass(eq=False)
class Fencer:
    """
    Represents a fencer with an ID and a display name; a single fencer can participate in multiple tournaments (be multiple entries).
    
    Attributes
    ----------
    id : int
        A unique identifier for the fencer.

    display_name : str
        The name of the fencer to be displayed in the tournament; leading and trailing whitespace will be trimmed from the input.
        
    max_name_length : ClassVar[int]
        A class variable that defines the maximum allowed length for a fencer's display name; it is set to 25 characters.
    """
    id: int
    display_name: str
    
    max_name_length: ClassVar[int] = 25

    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the fencer's ID and display name upon initialization. 
        The display name is also trimmed of leading and trailing whitespace; the trimmed name is used for input string length.

        Raises
        ------
        TypeError
            If the fencer's ID is not an integer or if the display name is not a string.
        ValueError
            If the fencer's ID is not a positive integer or if the display name is empty or exceeds the maximum allowed length after trimming.
        """
        validation.validate_positive_int(self.id, 'ID', 'Fencer')

        validated_name = Fencer._validate_display_name(self.display_name)
        
        # Set valid display name
        self.display_name = validated_name

    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """
        Determines if two fencers are equal based on their IDs.
        It is based on IDs only since display names are allowed to change.

        Parameters
        ----------
        other : object
            The object to compare with the current fencer.

        Returns
        -------
        bool
            True if the other object is a Fencer with the same ID, False otherwise.
        """
        if not isinstance(other, Fencer):
            return False
        return self.id == other.id


    # --- Update Methods ---
    def update_display_name(self, name: str) -> None:
        """
        Updates the display name of the fencer.

        Parameters
        ----------
        name : str
            The new display name for the fencer; leading and trailing whitespace will be trimmed from the input.

        Raises
        ------
        TypeError
            If the new display name is not a string.
        ValueError
            If the new display name is empty or exceeds the maximum allowed length after trimming.
        """
        # Set new display name
        self.display_name = Fencer._validate_display_name(name)


    # --- Helper Methods ---
    @staticmethod
    def _validate_display_name(name: str) -> str:
        """
        Validates a display name by trimming leading and trailing whitespace and checking that the resulting name is a valid length.

        Parameters
        ----------
        name : str
            The display name to validate.

        Returns
        -------
        str
            The validated display name with leading and trailing whitespace removed.

        Raises
        ------
        TypeError
            If the input name is not a string.
        ValueError
            If the input name is empty or exceeds the maximum allowed length after trimming.
        """
        if not isinstance(name, str):
            raise TypeError('Display name must be a string')

        # Trim input name
        name = name.strip()

        # Check that name is a valid length
        if len(name) == 0 or len(name) > Fencer.max_name_length:
            raise ValueError(f'Input name must be between 1-{Fencer.max_name_length} characters inclusive, ignoring leading and trailing whitespace')
        
        return name