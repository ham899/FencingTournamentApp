from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import validation
from entities.tournament_entry import TournamentEntry
from matches.match import Match
from entities.fencer import Fencer


# kw_only=True allows tournament_id to be a required subclass field even though Match has inherited fields with defaults.
@dataclass(eq=False, kw_only=True)
class TournamentMatch(Match, ABC):
    """
    Represents a match between two entries in a tournament.
    It is an abstract class that cannot be instantiated.
    It is the parent for the PouleMatch and DEMatch subclasses.
    A tournament match is meant to be instantiated with zero, one, or two entries depending on the context,
    and its scores are meant to be recorded after initialization.

    **Note:** **Do not** fill in the fencers for a tournament match; it will not be accepted; only use tournament entries.

    **Note:** A None value is **not allowed** for a tournament entry in a poule match.

    **Note:** For a DE match, a None value for a tournament entry either represents a BYE or when the entry is still TBD in a DE bracket.

    Attributes
    ----------
    tournament_id: int
        The unique identifier for the tournament that the match belongs to.

    entry1: TournamentEntry | None, default=None
        The tournament entry for fencer 1 in the match.

    entry2: TournamentEntry | None, default=None
        The tournament entry for fencer 2 in the match.

    forfeited_index: int | None, default=None, init=False
        The index of the entry that forfeited the match; 0 for entry 1, 1 for entry 2, or None for no forfeit.
    """
    tournament_id: int

    entry1: TournamentEntry | None = None
    entry2: TournamentEntry | None = None

    forfeited_index: int | None = field(default=None, init=False)

    # --- Initialization and validation ---
    def __post_init__(self) -> None:
        """
        Ensures the fencers attributes are not provided, 
        validates tournament match attributes, 
        fills in fencer information based on the entries,
        validates inherited attributes from Match class, 
        and ensures entry-fencer data are in synchronization.
        
        Raises
        ------
        TypeError
            If the tournament ID is not an integer, or if either of the entries are not either a TournamentEntry or None.
        ValueError
            If Fencer objects are provided, if the tournament ID is not a positive integer, 
            or if one of the entries' tournament IDs doesn't match this match's tournament ID, or if the entries are the same.
        """
        # Check that fencer objects are not provided
        if self.fencer1 is not None or self.fencer2 is not None:
            raise ValueError('Do not provide fencer objects for a tournament match.')

        # Validate tournament match attributes
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'TournamentMatch')
        self._validate_own_entries()
        
        # Fill in fencer data if entries are provided
        self._set_fencer_attributes_from_entries()

        # Get parent class to validate inherited attributes
        super().__post_init__()

        # Check that the entry-fencer data is still in sync
        self._validate_fencer_entry_sync()

    # --- Properties ---
    @property
    @abstractmethod
    def match_type(self) -> str:
        """Returns the type of the match as a string - implemented by subclasses."""
        pass

    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """Checks equality between this TournamentMatch and another object based on their IDs and tournament IDs."""
        if type(other) is not type(self):
            return False
        return self.id == other.id and self.tournament_id == other.tournament_id

    # --- Predicate Methods ---
    def has_no_entries(self) -> bool:
        """Checks if neither entry is present in the match."""
        return self.entry1 is None and self.entry2 is None
    
    def has_exactly_one_entry(self) -> bool:
        """Checks if exactly one entry is present in the match."""
        return (self.entry1 is not None) ^ (self.entry2 is not None)
    
    def has_at_least_one_entry(self) -> bool:
        """Checks if at least one entry is present in the match."""
        return self.entry1 is not None or self.entry2 is not None

    def has_both_entries(self) -> bool:
        """Checks if both entries are present in the match."""
        return self.entry1 is not None and self.entry2 is not None

    def has_entry(self, entry: TournamentEntry) -> bool:
        """Checks if the input entry is present in the match."""
        return entry in self.entries()
    
    def is_forfeit(self) -> bool:
        """Checks if a match was a forfeit based on the forfeited index."""
        return self.forfeited_index is not None

    # --- Entry Access Methods ---
    def entry_at_index(self, index: int) -> TournamentEntry | None:
        """
        Gets the entry at the input index.

        Parameters
        ----------
        index: int
            The index of the entry to get; 0 for entry 1, 1 for entry 2.

        Returns
        -------
        TournamentEntry | None
            The tournament entry at the input index, or None if there is no entry at that index.

        Raises
        ------
        TypeError
            If the input index is not an integer.
        ValueError
            If the input index is not 0 or 1.
        """
        self._validate_entry_index(index)
        return self.entry1 if index == 0 else self.entry2

    def opponent_entry_of_index(self, index: int) -> TournamentEntry | None:
        """
        Get the opponent entry of the entry at the input index.

        Parameters
        ----------
        index: int
            The index of the entry to get the opponent for; 0 for entry 1, 1 for entry 2.

        Returns
        -------
        TournamentEntry | None
            The opponent entry of the match for the input index, or None if there is no opponent entry at the opposite index.
        """
        self._validate_entry_index(index)
        return self.entry2 if index == 0 else self.entry1
    
    def entries(self) -> tuple[TournamentEntry | None, TournamentEntry | None]:
        """Returns a tuple of the entries in the match in the order (entry1, entry2)."""
        return (self.entry1, self.entry2)
    
    # --- Result Query Methods ---
    @abstractmethod
    def winner_entry(self) -> TournamentEntry | None:
        """
        Gets the winner entry of the match.
        
        Returns
        -------
        TournamentEntry | None
            The winner entry of the match, or None if there is no winner. (e.g. double-forfeit, incomplete match, etc.)
        """
        pass

    def winner(self) -> TournamentEntry | None:
        """An alias for the winner_entry() method."""
        return self.winner_entry()

    @abstractmethod
    def loser_entry(self) -> TournamentEntry | tuple[TournamentEntry, TournamentEntry] | None:
        """
        Gets the loser entry of the match.

        Returns
        -------
        TournamentEntry | tuple[TournamentEntry, TournamentEntry] | None
            The loser entry of the match, a tuple containing both entries if there is a double-forfeit, or None if there is no loser (e.g. BYE, incomplete match, etc.)
        """
        pass

    def loser(self) -> TournamentEntry | tuple[TournamentEntry, TournamentEntry] | None:
        """An alias for the loser_entry() method."""
        return self.loser_entry()

    # --- Entry Mutation Methods ---
    def set_entry(self, entry: TournamentEntry | None, index: int) -> None:
        """
        Sets the entry at the input index to the provided entry. 
        None is accepted as an input only when permitted by the concrete match subclass.

        **Note:** **Can** overwrite an existing entry.

        Parameters
        ----------
        entry: TournamentEntry | None
            The tournament entry to set at the input index, or None to clear the entry.
        index: int
            The index of the entry to set; 0 for entry 1, 1 for entry 2.
        
        Raises
        ------
        TypeError
            If the input index is not an integer, or if the entry is not a TournamentEntry or None.
        ValueError
            If the input index is not 0 or 1, if the match has already started, or if the entry's tournament ID does not 
            match the match's tournament ID, or if the entry pair is invalid (e.g. same entry or same fencer).
        """
        # Ensure match has not started yet
        if not self.has_not_started():
            raise ValueError(f'Cannot change entries in match {self.id} after it has started. Reset the match first.')
        
        # Validate inputs
        self._validate_entry_index(index)
        self._validate_entry(entry, f'Entry {index + 1}')
        
        # Check that the proposed entry pair is valid before setting the new entry
        proposed_entry1 = entry if index == 0 else self.entry1
        proposed_entry2 = entry if index == 1 else self.entry2
        self._validate_entry_pair(proposed_entry1, proposed_entry2)

        # Set new entry
        if index == 0:
            self.entry1 = entry
        else:
            self.entry2 = entry
        
        # Update fencer attributes based on the new entries
        self._set_fencer_attributes_from_entries()

    # --- State Transition Methods ---
    def start(self) -> None:
        """Starts the match after confirming both entries are present."""
        self._require_both_entries()
        super().start()

    def restart(self) -> None:
        """Restarts the match after confirming both entries are present."""
        self._require_both_entries()
        super().restart()
        self.forfeited_index = None
        self._clear_result_status()

    def reset(self) -> None:
        """Resets the match to its not-started state and clears result status."""
        super().reset()
        self.forfeited_index = None
        self._clear_result_status()

    def end(self) -> None:
        """Ends a live tournament match and records a normal result type."""
        super().end()
        self._assign_normal_result_status()

    # --- Result Recording Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """
        Records the score for the match and marks it as complete.

        Parameters
        ----------
        score1: int
            The score for entry 1.
        score2: int
            The score for entry 2.

        Raises
        ------
        ValueError
            If the match already has a forfeit result, if either entry is missing, or if the scores are invalid.
        """
        if self.is_forfeit():
            raise ValueError(f'Match {self.id} already has a forfeit result. Reset it before recording a score.')
    
        if not self.has_both_entries():
            raise ValueError(f'Match {self.id} must have both entries present to record a score.')

        super().record_score(score1, score2)
        self._assign_normal_result_status()

    def forfeit(self, forfeiting_index: int) -> None:
        """
        Forfeits the match for the entry at the input index.
        Subclasses define how the forfeit status is assigned.

        Parameters
        ----------
        forfeiting_index: int
            The index of the entry that is forfeiting the match; 0 for entry 1, 1 for entry 2.
        """
        # Validate match state
        if self.is_complete():
            raise ValueError(f'Match {self.id} is already complete.')

        # Validate input entry
        self._validate_entry_index(forfeiting_index)

        # Ensure both entries are present to perform a forfeit
        if not self.has_both_entries():
            raise ValueError(f'Both entries must exist to perform a forfeit in match {self.id}')

        # Set the forfeited index
        self.forfeited_index = forfeiting_index

        # Let subclass handle any additional status changes for a forfeit
        self._assign_forfeit_status()

        # Mark the match as complete
        self._mark_complete()

    def forfeit1(self) -> None:
        """Forfeits entry 1 in this tournament match. Alias for forfeit method, but entry1 specifically."""
        self.forfeit(forfeiting_index=0)

    def forfeit2(self) -> None:
        """Forfeits entry 2 in this tournament match. Alias for forfeit method, but entry2 specifically."""
        self.forfeit(forfeiting_index=1)

    # --- Abstract Helper Methods ---
    @abstractmethod
    def _assign_normal_result_status(self) -> None:
        """Assigns the subclass-specific normal result state."""
        pass

    @abstractmethod
    def _assign_forfeit_status(self) -> None:
        """
        Assigns subclass-specific forfeit result state.

        Subclasses are responsible for setting any forfeit-specific status and
        adjusting scores as needed before the match is marked complete.
        """
        pass

    @abstractmethod
    def _clear_result_status(self) -> None:
        """A helper method to clear the result status of the match - implemented by subclasses."""
        pass

    # --- Helper Methods ---
    def _validate_entry_index(self, index: int) -> None:
        """A helper method to validate that an input index is an integer and either 0 or 1."""
        validation.validate_int_in_range(index, 0, 1, 'Entry index', 'TournamentMatch', '_validate_entry_index')

    def _validate_fencer_entry_sync(self) -> None:
        """A helper method to validate that the fencer attributes are in sync with the entries in the match."""
        expected_fencer1 = self.entry1.fencer if self.entry1 is not None else None
        expected_fencer2 = self.entry2.fencer if self.entry2 is not None else None
        
        if self.fencer1 is not expected_fencer1:
            raise ValueError(f'Entry 1 and fencer1 are out of sync in match {self.id}.')
        
        if self.fencer2 is not expected_fencer2:
            raise ValueError(f'Entry 2 and fencer2 are out of sync in match {self.id}.')

    def _set_fencer_attributes_from_entries(self) -> None:
        """A helper method to set the fencer1 and fencer2 attributes based on the entries in the match."""
        self.fencer1 = self.entry1.fencer if self.entry1 is not None else None
        self.fencer2 = self.entry2.fencer if self.entry2 is not None else None

    def _validate_entry(self, entry: TournamentEntry | None, entry_name: str) -> None:
        """
        A helper method to validate a possible tournament entry.
        
        Parameters
        ----------
        entry : TournamentEntry | None
            The tournament entry to validate, allowed to be None.
        entry_name : str
            The name of the entry to be used in a potential error message.

        Raises
        ------
        TypeError
            If the entry name is not a string, if the entry is not a TournamentEntry or None, 
            if the entry's ID or tournament ID is not an integer, if the entry's fencer attribute is not a Fencer object, 
            or if either the initial seed or DE seed is not an integer if provided.
        ValueError
            If the entry's ID or tournament ID is not a positive integer, if the entry's tournament ID does not match the match's 
            tournament ID, or if either the initial seed or DE seed is not a positive integer if provided.

        """
        if not isinstance(entry_name, str):
            raise TypeError(f'The provided entry_name must be a string - got {type(entry_name).__name__}')
        if entry is None:
            return
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'{entry_name} must be a TournamentEntry object - got {type(entry).__name__}.')
        validation.validate_positive_int(entry.id, f'{entry_name} ID', 'TournamentMatch', '_validate_entry')
        validation.validate_positive_int(entry.tournament_id, f'{entry_name} Tournament ID', 'TournamentMatch', '_validate_entry')
        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'{entry_name} must belong to tournament {self.tournament_id} - got {entry.tournament_id}.')
        if not isinstance(entry.fencer, Fencer):
            raise TypeError(f'{entry_name} must have a Fencer object - got {type(entry.fencer).__name__}.')
        validation.validate_optional_positive_int(entry.initial_seed, f'{entry_name} Initial Seed', 'TournamentMatch', '_validate_entry')
        validation.validate_optional_positive_int(entry.de_seed, f'{entry_name} DE Seed', 'TournamentMatch', '_validate_entry')

    def _validate_entry_pair(self, entry1: TournamentEntry | None, entry2: TournamentEntry | None) -> None:
        """
        A helper method to validate a pair of tournament entries. The method validates the entries on their own, but also 
        as a valid pair for a tournament match.

        **Note:** None entries are allowed and can be an entry in a valid pair.

        Parameters
        ----------
        entry1 : TournamentEntry | None
            The first entry in the pair.
        entry2 : TournamentEntry | None
            The second entry in the pair.

        Raises
        ------
        TypeError
            If the entry name is not a string, if the entry is not a TournamentEntry or None,
            if the entry's ID or tournament ID is not an integer, if the entry's fencer attribute is not a Fencer object,
            or if either the initial seed or DE seed is not an integer if provided.
        ValueError
            If the entries are the same, or if they have the same fencer (an entry cannot fence itself), 
            or if either entry's tournament ID does not match the match's tournament ID, or if either the initial seed or DE seed is not a positive integer if provided.
        """
        # Validate the entries in isolation
        self._validate_entry(entry1, 'Entry 1')
        self._validate_entry(entry2, 'Entry 2')

        # Validate the entries as a valid pair
        if entry1 is not None and entry2 is not None:
            if entry1 == entry2:
                raise ValueError('Entry 1 and entry 2 cannot be the same entry; an entry can\'t fence themself.')
            if entry1.fencer == entry2.fencer:
                raise ValueError('Entry 1 and entry 2 cannot have the same fencer; an entry can\'t fence themself.')

    def _validate_own_entries(self) -> None:
        """A helper method to validate the match's own entries."""
        self._validate_entry_pair(self.entry1, self.entry2)

    def _require_both_entries(self) -> None:
        """A helper method to validate that the match has both its entries."""
        if not self.has_both_entries():
            raise ValueError(f'Match {self.id} must have both entries present to perform this operation.')