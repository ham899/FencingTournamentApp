from dataclasses import dataclass

import validation


@dataclass(frozen=True, slots=True)
class PouleStats:
    """
    Represents an immutable snapshot of an entry's aggregate poule statistics.

    The statistics may represent completed matches from a single poule or multiple poule rounds. 
    This object's fields cannot be reassigned after initialization.

    Attributes
    ----------
    num_matches : int
        The number of completed poule matches represented.
    num_victories : int
        The number of completed poule matches won by the entry.
    touches_scored : int
        The total number of touches credited to the entry in completed poule matches.
    touches_received : int
        The total number of touches credited against the entry in completed poule matches.
    """
    num_matches: int
    num_victories: int
    touches_scored: int
    touches_received: int


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the supplied statistics.

        Raises
        ------
        TypeError
            If num_matches, num_victories, touches_scored, or touches_received is not an integer.
        ValueError
            If a statistic is negative, if the number of victories exceeds the number of matches, 
            or if touches are recorded when no matches have been completed.
        """
        location = 'PouleStats'

        validation.validate_non_negative_int(self.num_matches, 'number of matches', location)
        validation.validate_non_negative_int(self.num_victories, 'number of victories', location)
        validation.validate_non_negative_int(self.touches_scored, 'touches scored', location)
        validation.validate_non_negative_int(self.touches_received, 'touches received', location)

        # Validate that the result statistics are possible
        if self.num_victories > self.num_matches:
            raise ValueError(
                f'Number of victories cannot be greater than the number of matches in {location} - '
                f'got {self.num_victories} victories and {self.num_matches} matches'
            )

        if self.num_matches == 0:
            if self.touches_scored > 0:
                raise ValueError(
                    f'Touches scored cannot be greater than 0 when the entry has completed no matches in {location} - '
                    f'got {self.touches_scored} touches scored and {self.num_matches} matches'
                )

            if self.touches_received > 0:
                raise ValueError(
                    f'Touches received cannot be greater than 0 when the entry has completed no matches in {location} - '
                    f'got {self.touches_received} touches received and {self.num_matches} matches'
                )


    # --- Arithmetic Methods ---
    def __add__(self, other: object) -> "PouleStats":
        """
        Return the combined statistics of two PouleStats objects.

        Add the corresponding match, victory, and touch totals.
        The combined victory ratio and indicator are calculated from the combined totals.

        Parameters
        ----------
        other : PouleStats
            The statistics to combine with this object's statistics.

        Returns
        -------
        PouleStats
            A new statistics object containing the combined totals.

        Notes
        -----
        The caller is responsible for ensuring that the statistics belong
        to the same entry and represent non-overlapping sets of matches.
        """
        if not isinstance(other, PouleStats):
            return NotImplemented

        return PouleStats(
            num_matches = self.num_matches + other.num_matches,
            num_victories = self.num_victories + other.num_victories,
            touches_scored = self.touches_scored + other.touches_scored,
            touches_received = self.touches_received + other.touches_received
        )


    # --- Properties ---
    @property
    def victory_ratio(self) -> float:
        """Return the entry's victory ratio, or 0.0 if no matches have been completed."""
        return 0.0 if self.num_matches == 0 else self.num_victories / self.num_matches

    @property
    def indicator(self) -> int:
        """Return touches scored minus touches received for the entry."""
        return self.touches_scored - self.touches_received
