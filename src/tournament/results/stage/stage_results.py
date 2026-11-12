from abc import ABC, abstractmethod
from dataclasses import dataclass

import validation

from entities.tournament_entry import TournamentEntry
from tournament.results.stage.stage_entry_result import StageEntryResult


@dataclass(frozen=True, slots=True)
class StageResults(ABC):
    """
    Represent a snapshot of a tournament stage's results.

    Subclasses provide a nonempty tuple of ranked entry results.
    All results must belong to the same tournament and this stage,
    with each tournament entry represented exactly once.

    The ranking may be provisional while the stage is incomplete.

    Attributes
    ----------
    stage_number : int
        The stage's one-based position within the tournament.
    """
    stage_number: int


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the stage number.

        Raises
        ------
        TypeError
            If the stage number is not an integer.
        ValueError
            If the stage number is not positive.
        """
        location = self.__class__.__name__
        validation.validate_positive_int(self.stage_number, 'Stage number', location)


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the represented entries."""
        return self._ranked_results[0].tournament_id

    @property
    def num_entries(self) -> int:
        """Return the number of represented entries."""
        return len(self._ranked_results)

    @property
    @abstractmethod
    def _ranked_results(self) -> tuple[StageEntryResult, ...]:
        """Return the entry results in stage ranking order."""
        pass

    @property
    def ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the entries in the same order as ``ranked_results``."""
        return tuple(result.entry for result in self._ranked_results)

    @property
    def ranked_names(self) -> tuple[str, ...]:
        """Return the display names in the same order as ``ranked_results``."""
        return tuple(result.display_name for result in self._ranked_results)
