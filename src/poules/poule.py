from dataclasses import dataclass, field

import validation
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.results.poule_result import PouleResult
from poules.poule_orders import POULE_BOUT_ORDER


@dataclass(eq=False)
class Poule:
    """
    Represents one round-robin poule within a tournament.

    A poule owns an ordered list of tournament entries and a generated match
    schedule in which every entry fences every other entry once.

    Attributes
    ----------
    id : int
        Unique identifier of the poule.
    tournament_id : int
        Unique identifier of the tournament that owns the poule.
    poule_number : int
        Display or organizational number of the poule within its tournament.
        This may differ from ``id`` depending on persistence design.
    entries : list[TournamentEntry]
        Ordered entries in the poule. Entry at index ``i`` corresponds to
        fencer number ``i + 1`` in the official bout order. The input list is
        copied during initialization.
    matches : list[PouleMatch]
        Generated matches in official bout order. The list is regenerated when a
        supported entry-management operation changes the poule's entries.
    """
    id: int
    tournament_id: int
    poule_number: int
    entries: list[TournamentEntry]
    matches: list[PouleMatch] = field(default_factory=list, init=False) # Invariant: matches should reflect the current entries in the poule


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """Validates the supplied attributes, copies the entry list, and generates the initial match schedule."""
        validation.validate_positive_int(self.id, 'ID', 'Poule')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'Poule')
        validation.validate_positive_int(self.poule_number, 'Poule number', 'Poule')
        
        self._validate_own_entries_list()
        
        # Protect the poule's entry ordering from later caller-side list changes.
        self.entries = list(self.entries)        
        self._generate_own_matches()


    # --- Properties ---
    @property
    def size(self) -> int:
        """Returns the number of entries in the poule."""
        return len(self.entries)

    @property
    def number_matches(self) -> int:
        """Returns the number of scheduled all-play-all matches in the poule."""
        return self.size * (self.size - 1) // 2


    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """
        Returns whether another object represents the same poule.

        Two poules are equal when they have the same poule ID and tournament ID.
        """
        if not isinstance(other, Poule):
            return False
        
        return self.id == other.id and self.tournament_id == other.tournament_id


    # --- Predicate Methods ---
    def has_started(self) -> bool:
        """Returns whether any match in the poule is in progress or complete."""
        return any(match.is_in_progress() or match.is_complete() for match in self.matches)

    def is_complete(self) -> bool:
        """Returns whether every scheduled match in the poule is complete."""
        return all(match.is_complete() for match in self.matches)


    # --- Match Access Methods ---
    def get_match_at_index(self, index: int) -> PouleMatch:
        """
        Gets a poule match at a specified index.
        
        Parameters
        ----------
        index : int
            Zero-based index of the match in the official bout-order list.

        Returns
        -------
        PouleMatch
            The poule match at the index.

        Raises
        ------
        TypeError
            If the index is not an integer.
        ValueError
            If index is outside the valid range of match-list indices.
        """
        validation.validate_int_in_range(index, 0, len(self.matches) - 1, 'index', 'Poule', 'get_match_at_index')

        return self.matches[index]

    def get_current_match(self) -> PouleMatch | None:
        """
        Returns the first incomplete match in official bout order.

        If a match is in progress, it is returned before any not-yet-started match.
        Returns None when every scheduled match is complete.
        """
        return next((match for match in self.matches if match.is_incomplete()), None)

    def get_next_match(self) -> PouleMatch | None:
        """
        Returns the first incomplete match scheduled after the current incomplete match.

        Returns None when every match is complete or when no incomplete match follows the current incomplete match.
        """
        current_match = self.get_current_match()

        # Case: All matches are complete
        if current_match is None:
            return None

        # Case: Return next incomplete match after current match - "on deck match"
        current_match_index = current_match.match_index
        for match in self.matches[current_match_index + 1:]:
            if match.is_incomplete():
                return match
        
        # Case: No incomplete match follows the current match.
        return None


    # --- Entry Management Methods ---
    def add_entry(self, entry: TournamentEntry) -> None:
        """
        Adds an entry and regenerates the official poule match schedule.

        Completed results between existing entries are preserved in the replacement
        schedule. An entry cannot be added while any match is in progress.

        Parameters
        ----------
        entry : TournamentEntry
            Tournament entry to add to the poule.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry.
        ValueError
            If entry is already in the poule, belongs to another tournament, or would
            create a poule size without a supported bout order.
        RuntimeError
            If a match in the poule is currently in progress.
        """      
        if self._has_entry(entry):
            raise ValueError(f'Entry {entry.id} is already in poule {self.id}')

        # Reject adding an entry during an in-progress bout
        if any(match.is_in_progress() for match in self.matches):
            raise RuntimeError(f'Cannot add an entry while a match is in progress in poule {self.id}.')

        # Validate the result of adding the entry to the poule
        proposed_entries = self.entries + [entry]
        self._validate_entries_list(proposed_entries)

        # Generate new matches to potentially add to matches attribute
        new_matches = self._generate_matches(proposed_entries)

        # Transfer results of any already completed matches to new matches
        self._transfer_results(source_matches=self.matches, destination_matches=new_matches)

        # Commit the replacement schedule only after all prior steps succeed.
        self.entries = proposed_entries
        self.matches = new_matches

    def remove_entry(self, entry: TournamentEntry) -> None:
        """
        Removes a specified entry from the poule before starting the poule.
        
        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to remove from the poule.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry.
        ValueError
            If entry is not in this poule or belongs to another tournament.
        RuntimeError
            If the poule has already started.
        """        
        if not self._has_entry(entry):
            raise ValueError(f'Entry {entry.id} is not in poule {self.id}; the provided entry must be a part of the poule.')
        
        if self.has_started():
            raise RuntimeError(f'Cannot remove an entry after poule {self.id} has already started.')

        # Validate if the removal action results in a valid list of entries and matches
        proposed_entries = [e for e in self.entries if e != entry]

        self._validate_entries_list(proposed_entries)
        proposed_matches = self._generate_matches(proposed_entries)        

        # Update object attributes
        self.entries = proposed_entries
        self.matches = proposed_matches

    def scratch_entry(self, entry: TournamentEntry) -> None:
        """
        Raises NotImplementedError because scratch handling is not implemented yet.
        """
        raise NotImplementedError('Poule.scratch_entry() has not been implemented yet.')


    # --- Match Result Recording Methods ---
    def record_match_result(self, index: int, score1: int, score2: int) -> None:
        """
        Records the result of a specified scheduled match.

        Parameters
        ----------
        index : int
            Zero-based index of the match in the official bout-order list.
        score1 : int
            Score recorded for the first entry in the match.
        score2 : int
            Score recorded for the second entry in the match.

        Raises
        ------
        TypeError
            If index or either score has an invalid type.
        ValueError
            If index or either score has an invalid value.
        RuntimeError
            If the selected match cannot currently accept a recorded result.
        """
        match = self.get_match_at_index(index)
        match.record_score(score1, score2)

    def record_current_match_result(self, score1: int, score2: int) -> None:
        """
        Records the result of the first incomplete match in official bout order.

        Parameters
        ----------
        score1 : int
            Score recorded for the first entry in the match.
        score2 : int
            Score recorded for the second entry in the match.

        Raises
        ------
        TypeError
            If either score has an invalid type.
        ValueError
            If either score has an invalid value.
        RuntimeError
            If no incomplete match exists or the current match cannot accept a result.
        """
        match = self.get_current_match()
        
        if match is None:
            raise RuntimeError(f'Poule {self.id} is already complete.')

        match.record_score(score1, score2)


    # --- Result Calculation Methods ---
    def calculate_results(self) -> PouleResult:
        """
        Calculates and returns a snapshot of the current results for this poule.

        A new SinglePouleResults object is created on each call. Only completed
        matches contribute to the returned results; incomplete matches are ignored.
        """
        return PouleResult.from_matches(self.entries, self.matches, self.id, self.tournament_id)

    def calculate_results_names_only(self) -> list[str]:
        """Calculates and returns a snapshot of the ranking in the poule thus far as a list of display names only."""
        poule_result = PouleResult.from_matches(self.entries, self.matches, self.id, self.tournament_id)
        return [entry.display_name for entry in poule_result.entries]


    # --- Validation Helper Methods ---
    def _validate_poule_size(self, size: int) -> None:
        """
        Validates that a supported official bout order exists for a poule size.
        
        Parameters
        ----------
        size : int
            The size of the poule.

        Raises
        ------
        ValueError
            If the size is not supported by the known poule bout orders.
        """
        supported_sizes = list(POULE_BOUT_ORDER.keys())
        supported_sizes.sort()

        if size not in supported_sizes:
            raise ValueError(f'Cannot create a poule with {size} entries because no bout order exists for it; the supported sizes are {supported_sizes[0]}-{supported_sizes[-1]}.')

    def _validate_entry(self, entry: TournamentEntry) -> None:
        """
        Validates that a tournament entry is valid for this poule.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.

        Raises
        ------
        TypeError
            If the entry is not a TournamentEntry object.
        ValueError
            If the entry does not have the same tournament ID as the poule.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be a tournament entry - got {type(entry)}')
        
        if entry.tournament_id != self.tournament_id:
            raise ValueError(f'Entry {entry.id} must belong to this tournament ({self.tournament_id}) - got {entry.tournament_id}')

    def _has_entry(self, entry: TournamentEntry) -> bool:
        """
        Checks whether an entry is in this poule.
        
        Parameters
        ----------
        entry : TournamentEntry
            The entry under investigation.

        Returns
        -------
        bool
            True if the validated entry belongs to this poule; otherwise, False.

        Raises
        ------
        TypeError
            If the entry is not a TournamentEntry object.
        ValueError
            If the entry does not have the same tournament ID as the poule.
        """
        self._validate_entry(entry)
        return entry in self.entries

    def _validate_entries_list(self, entries: list[TournamentEntry]) -> None:
        """
        Validates a given list of tournament entries.
        
        Parameters
        ----------
        entries : list[TournamentEntry]
            A list of TournamentEntry objects to be validated.

        Raises
        ------
        TypeError
            If entries is not a list or contains an object that is not a TournamentEntry.
        ValueError
            If entries contains duplicates, includes an entry from another tournament,
            contains fewer than two entries, or has a size without a supported bout order.
        """
        # Validate that a list is provided
        if not isinstance(entries, list):
            raise TypeError(f'The entries variable must be of type list - got {type(entries)}')
        
        # Validate each entry in the list
        for i, entry in enumerate(entries):
            if not isinstance(entry, TournamentEntry):
                raise TypeError(f'All entries must of type TournamentEntry - entry at index {i} is of type {type(entry)}')
                
            if entry.tournament_id != self.tournament_id:
                raise ValueError(f'All entries must have the same tournament ID as the poule - entry at index {i} has tournament ID {entry.tournament_id} when poule has tournament ID {self.tournament_id}')

            if entries.count(entry) != 1:
                raise ValueError(f'The entries must be unique; entry {entry.id} at index {i} is not unique and has a duplicate entry in the list in poule {self.id}')            

        # Ensure enough entries are provided
        if len(entries) < 2:
            raise ValueError(f'There must be at least two entries in a poule - got {len(entries)}')

        # Validate that a bout order is present for this size
        self._validate_poule_size(len(entries))

    def _validate_own_entries_list(self) -> None:
        """Validates the poule's own list of entries."""
        self._validate_entries_list(self.entries)


    # --- Match Generation Helper Methods ---
    def _create_match(self, entries: list[TournamentEntry], match_id: int, match_index: int, match_pair: tuple[int, int]) -> PouleMatch:
        """
        Creates one scheduled poule match from an ordered list of valid entries.

        The match_pair values use one-based fencer numbers from the official bout
        order, while match_index is zero-based.

        Parameters
        ----------
        entries : list[TournamentEntry]
            Ordered, validated entries used to resolve fencer numbers in match_pair.
        match_id : int
            Identifier assigned to the generated match.
        match_index : int
            Zero-based position of the match in the generated schedule.
        match_pair : tuple[int, int]
            One-based pair of fencer numbers from the official bout order.

        Returns
        -------
        PouleMatch
            Newly created scheduled match.

        Raises
        ------
        TypeError
            If match_id, match_index, or either fencer number is not an integer, or if
            match_pair is not a tuple.
        ValueError
            If match_id is not positive; match_index or a fencer number is out of
            range; match_pair does not contain exactly two values; or both fencer
            numbers identify the same entry.
        """
        self._validate_entries_list(entries)
        validation.validate_positive_int(match_id, 'match_id', 'Poule', '_create_match')
        number_matches = len(entries) * (len(entries) - 1) // 2
        validation.validate_int_in_range(match_index, 0, number_matches - 1, 'index', 'Poule', '_create_match')

        # Validate the match pair tuple
        if not isinstance(match_pair, tuple):
            raise TypeError(f'Match pair must be a tuple - got {type(match_pair)}')
        
        if len(match_pair) != 2:
            raise ValueError(f'Match pair must be of length 2 - got {len(match_pair)}')
        
        # Validate the fencer numbers in the tuple
        fencer1_number, fencer2_number = match_pair

        validation.validate_int_in_range(fencer1_number, 1, len(entries), 'fencer number 1', 'Poule', '_create_match')
        validation.validate_int_in_range(fencer2_number, 1, len(entries), 'fencer number 2', 'Poule', '_create_match')

        if fencer1_number == fencer2_number:
            raise ValueError(f'Fencer numbers in match pair must be different - got {fencer1_number} and {fencer2_number}')

        # Get entries to create match with from poule entries list
        entry1 = entries[fencer1_number - 1]
        entry2 = entries[fencer2_number - 1]

        # Check that the entries are distinct
        if entry1 == entry2:
            raise ValueError(f'Entries in match pair must be different - got {entry1} and {entry2}')

        # Create and return poule match
        return PouleMatch(id=match_id, tournament_id=self.tournament_id, entry1=entry1, entry2=entry2, poule_id=self.id, match_index=match_index)

    def _generate_matches(self, entries: list[TournamentEntry]) -> list[PouleMatch]:
        """
        Validates an entry list and generates its official ordered match schedule.

        The supplied entry order determines which TournamentEntry objects correspond
        to the one-based fencer numbers used by the standard bout order.

        Parameters
        ----------
        entries : list[TournamentEntry]
            Entries for which to generate a fresh poule match schedule.

        Returns
        -------
        list[PouleMatch]
            Newly created matches in official bout order.

        Raises
        ------
        TypeError
            If entries is not a list or contains an object that is not a
            TournamentEntry.
        ValueError
            If entries contains duplicates, includes an entry from another tournament,
            contains fewer than two entries, or has a size without a supported bout
            order.
        """
        self._validate_entries_list(entries)
        
        match_order = POULE_BOUT_ORDER[len(entries)]

        return [self._create_match(entries, index+1, index, match_pair) for index, match_pair in enumerate(match_order)]

    def _generate_own_matches(self) -> None:
        """Regenerates this poule's match schedule from its current entries."""
        self.matches = self._generate_matches(self.entries)


    # --- Result Transfer Helper Methods ---
    def _transfer_results(self, source_matches: list[PouleMatch], destination_matches: list[PouleMatch]) -> None:
        """
        Replays completed source-match results into a rebuilt match schedule.

        Matches are paired by their two entries, regardless of entry order. When a
        matching destination bout reverses the entry order, ordinary scores and
        the forfeiting index are reversed before being recorded.

        Parameters
        ----------
        source_matches : list[PouleMatch]
            Existing match schedule containing any results to preserve.
        destination_matches : list[PouleMatch]
            Replacement match schedule that receives preserved completed results.

        Raises
        ------
        TypeError
            If either argument is not a list of PouleMatch objects.
        RuntimeError
            If a completed source match has no corresponding destination match.
        """
        # Validate inputs
        if not isinstance(source_matches, list):
            raise TypeError(f'Source matches in Poule._transfer_results() must be a list - got {type(source_matches)}.')
        
        for i, match in enumerate(source_matches):
            if not isinstance(match, PouleMatch):
                raise TypeError(f'All source matches must be of type PouleMatch in Poule._transfer_results() - got {type(match)} at index {i}.')

        if not isinstance(destination_matches, list):
            raise TypeError(f'Destination matches in Poule._transfer_results() must be a list - got {type(destination_matches)}.')
        
        for i, match in enumerate(destination_matches):
            if not isinstance(match, PouleMatch):
                raise TypeError(f'All destination matches must be of type PouleMatch in Poule._transfer_results() - got {type(match)} at index {i}.')
        
        # Get completed matches from source matches
        previous_results = [match for match in source_matches if match.is_complete()]

        # If no source matches were completed, do nothing
        if len(previous_results) == 0:
            return

        # Transfer results to destination matches
        for match_prev in previous_results:
            result_copied = False
            entries_prev = match_prev.entries()

            for match_new in destination_matches:                
                entries_new = match_new.entries()

                if entries_new == entries_prev:
                    if match_prev.is_forfeit():
                        forfeiting_index = match_prev.forfeited_index
                        match_new.forfeit(forfeiting_index)
                    else:
                        match_new.record_score(match_prev.score1, match_prev.score2)
                    
                    result_copied = True
                    break

                elif entries_new == entries_prev[::-1]:
                    if match_prev.is_forfeit():
                        forfeiting_index = 1 - match_prev.forfeited_index
                        match_new.forfeit(forfeiting_index)
                    else:
                        match_new.record_score( match_prev.score2, match_prev.score1)
                    
                    result_copied = True
                    break

            if not result_copied:
                raise RuntimeError(f'Could not transfer the result of match {match_prev.id} to any match in the destination matches.')