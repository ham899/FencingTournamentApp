from dataclasses import dataclass

from abc import ABC, abstractmethod

import validation

from entities import SeededEntry, TournamentEntry
from tournament.results.stage import StageResults


@dataclass(eq=False)
class TournamentStage(ABC):
    """
    Define the shared interface and initial seeding for a tournament stage.

    A stage contains entries from one tournament. 
    Its concrete subclass manages poule rounds or a direct-elimination bracket and calculates result snapshots.
    During initialization, the entries are validated and stored in ascending seed order. 
    Subclasses must call ``super().__post_init__()`` before using the entries to create rounds or brackets.

    Attributes
    ----------
    stage_number : int
        The stage's one-based position within its tournament.
    seeded_entries : tuple[SeededEntry, ...]
        The participating entries with unique seeds from 1 through the number of entries, 
        stored in ascending seed order after initialization.
    """
    stage_number: int
    seeded_entries: tuple[SeededEntry, ...]


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the stage number and seeded entries, then sort by seed.

        Raises
        ------
        TypeError
            If the stage number is not an integer, 
            seeded_entries is not a tuple, or an item or its seed has an invalid type.
        ValueError
            If the stage number is not positive, fewer than two entries are supplied, 
            entries come from different tournaments, an entry or fencer is repeated, 
            or the seeds are not unique integers from 1 through the number of entries.
        """
        location = type(self).__name__

        # Validate stage attributes
        validation.validate_positive_int(self.stage_number, 'Stage number', location)
        self._validate_seeded_entries(self.seeded_entries, location)

        # Sort the seeded entries by seed in ascending order
        self.seeded_entries = tuple(sorted(self.seeded_entries, key=lambda seeded_entry: seeded_entry.seed))


    # --- Properties ---
    @property
    @abstractmethod
    def label(self) -> str:
        """Return a descriptive label for this stage."""
        pass

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the stage's entries."""
        return self.seeded_entries[0].entry.tournament_id

    @property
    def num_entries(self) -> int:
        """Return the number of entries participating in this stage."""
        return len(self.seeded_entries)

    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """Return the participating entries in ascending seed order."""
        return tuple(seeded_entry.entry for seeded_entry in self.seeded_entries)


    # --- Predicate Methods ---
    @abstractmethod
    def has_started(self) -> bool:
        """Return whether competition has begun in this stage."""
        pass

    @abstractmethod
    def is_complete(self) -> bool:
        """Return whether this stage has met its configured completion conditions."""
        pass

    def is_incomplete(self) -> bool:
        """Return whether this stage still has required work to complete."""
        return not self.is_complete()


    # --- Result Calculation Methods ---
    @abstractmethod
    def calculate_results(self) -> StageResults:
        """Return a snapshot of the stage's current results, whether complete or incomplete."""
        pass

    def calculate_final_results(self) -> StageResults:
        """
        Calculate results for a completed stage.

        Raises
        ------
        RuntimeError
            If the stage is incomplete.
        """
        if self.is_incomplete():
            raise RuntimeError(
                'Cannot calculate final results for an incomplete stage '
                f'{self.stage_number} in tournament {self.tournament_id}'
            )

        return self.calculate_results()


    # --- Validation Helper Methods ---
    def _validate_seeded_entries(self, seeded_entries: tuple[SeededEntry, ...], location: str) -> None:
        """
        Validate the initial entries and their one-based stage seeds.

        Parameters
        ----------
        seeded_entries : tuple[SeededEntry, ...]
            The entries and initial seeds to validate.
        location : str
            The concrete stage class name used in error messages.

        Raises
        ------
        TypeError
            If seeded_entries is not a tuple, an item is not a SeededEntry,
            its entry is not a TournamentEntry, or a seed is not an integer.
        ValueError
            If fewer than two entries are supplied, entries do not share a tournament ID, 
            an entry or fencer ID is repeated, or seeds are duplicated or outside the range from 1 through the number of entries.
        """
        if not isinstance(seeded_entries, tuple):
            raise TypeError(f'Seeded entries must be a tuple in {location}')

        if len(seeded_entries) < 2:
            raise ValueError(f'At least two seeded entries are required in {location}')

        tournament_id: int | None = None
        entry_ids: set[int] = set()
        fencer_ids: set[int] = set()
        seeds: set[int] = set()

        for i, seeded_entry in enumerate(seeded_entries):
            if not isinstance(seeded_entry, SeededEntry):
                raise TypeError(f'Item {i} must be a SeededEntry in {location}')

            entry = seeded_entry.entry
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'Item {i} must contain a TournamentEntry in {location}')

            validation.validate_int_in_range(seeded_entry.seed, 1, len(seeded_entries), f'Seed at index {i}', location)

            if tournament_id is None:
                tournament_id = entry.tournament_id

            elif entry.tournament_id != tournament_id:
                raise ValueError(f'Entries must share a tournament ID in {location}')

            if entry.id in entry_ids:
                raise ValueError(f'Entry ID {entry.id} is duplicated in {location}')

            if entry.fencer.id in fencer_ids:
                raise ValueError(f'Fencer ID {entry.fencer.id} is duplicated in {location}')

            if seeded_entry.seed in seeds:
                raise ValueError(f'Seed {seeded_entry.seed} is duplicated in {location}')

            entry_ids.add(entry.id)
            fencer_ids.add(entry.fencer.id)
            seeds.add(seeded_entry.seed)
