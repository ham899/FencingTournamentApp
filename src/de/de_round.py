from dataclasses import dataclass

import validation

from de.de_matchup import DEMatchup
from entities.tournament_entry import TournamentEntry
from matches.de_match import DEMatch
from utils import is_power_of_two


@dataclass(eq=False)
class DERound:
    """
    Represent one round of matchups in a direct-elimination tableau.

    A DE round contains a nonempty, power-of-two number of matchups ordered from the top of the tableau to the bottom. 
    Each matchup must belong to the same tournament, DE stage, and round, 
    and its matchup number must agree with its one-based position in ``matchups``. 
    A tournament entry may occupy at most one position in the round.

    The round's size is derived from its number of matchups. 
    Each matchup contributes two entry positions, including positions that are currently empty.

    Attributes
    ----------
    matchups : tuple[DEMatchup, ...]
        The round's matchups in top-to-bottom tableau order. 
        The number of matchups must be a power of two.
    round_number : int
        The round's one-based position within its DE tableau.
    stage_number : int
        The DE stage's one-based position within the tournament.
    """
    matchups: tuple[DEMatchup, ...]
    round_number: int
    stage_number: int


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the round identifiers and matchup structure.

        Raises
        ------
        TypeError
            If the round or stage number is not an integer, 
            ``matchups`` is not a tuple, an item is not a ``DEMatchup``, 
            or a stored match is neither a ``DEMatch`` nor ``None``.
        ValueError
            If the round or stage number is not positive, ``matchups`` is empty,
            the number of matchups is not a power of two, 
            a matchup's identifiers do not agree with its position or this round, 
            the matchups do not share a tournament ID, or an entry appears more than once.
        """
        validation.validate_positive_int(self.round_number, 'Round number', 'DERound')
        validation.validate_positive_int(self.stage_number, 'Stage number', 'DERound')
        
        self._validate_matchups(self.matchups)


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying this DE round."""
        return (
            f'The {self.round_name} '
            f'in stage {self.stage_number} '
            f'of tournament {self.tournament_id}'
        )
    
    @property
    def round_name(self) -> str:
        """Return the conventional name determined by the round's size."""
        if self.size == 2: 
            return 'Final'
        
        if self.size == 4: 
            return 'Semi-Final'
        
        if self.size == 8: 
            return 'Quarter-Final'
        
        return f'Round of {self.size}'

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID shared by the round's matchups."""
        return self.matchups[0].tournament_id

    @property
    def num_matchups(self) -> int:
        """Return the number of matchups in the round."""
        return len(self.matchups)
    
    @property
    def size(self) -> int:
        """Return the total number of entry positions in the round."""
        return 2 * self.num_matchups
    
    @property
    def entries(self) -> tuple[TournamentEntry, ...]:
        """
        Return the entries currently occupying positions in the round.

        Entries are returned in top-to-bottom matchup order, 
        with the top entry preceding the bottom entry within each matchup. 
        Empty positions are omitted.
        """
        return tuple(entry for matchup in self.matchups for entry in matchup.entries if entry is not None)


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """
        Return whether ``other`` represents the same DE round.

        Equality is based on tournament ID, stage number, and round number.
        Matchups, entries, and recorded results are not considered.
        """

        if not isinstance(other, DERound):
            return False

        return (
            self.tournament_id == other.tournament_id and
            self.stage_number == other.stage_number and
            self.round_number == other.round_number
        )


    # --- Predicate Methods ---
    def is_complete(self) -> bool:
        """Return whether every matchup is complete, including first-round byes."""
        return all(matchup.is_complete() for matchup in self.matchups)

    def is_incomplete(self) -> bool:
        """Return whether at least one matchup in the round is incomplete."""
        return not self.is_complete()

    def has_entry(self, entry: TournamentEntry) -> bool:
        """
        Return whether the specified entry currently appears in the round.

        Parameters
        ----------
        entry : TournamentEntry
            The entry whose presence is being checked.

        Returns
        -------
        bool
            ``True`` if the entry occupies a position in the round; otherwise, ``False``.

        Raises
        ------
        TypeError
            If ``entry`` is not a ``TournamentEntry``.
        ValueError
            If ``entry`` belongs to another tournament.
        """
        self._validate_entry(entry, 'has_entry')
        return entry in self.entries


    # --- Access Methods ---
    def get_matchup_at(self, index: int) -> DEMatchup:
        """
        Return the matchup at the specified index.

        Parameters
        ----------
        index : int
            The matchup's zero-based position in the round. 
            Index ``0`` refers to the matchup at the top of the tableau.

        Returns
        -------
        DEMatchup
            The matchup at ``index``.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is outside the valid range of matchup indices.
        """
        self._validate_matchup_index(index, 'get_matchup_at')
        return self.matchups[index]


    # --- Entry Management Methods ---
    def add_entry_to_matchup(self, entry: TournamentEntry, matchup_index: int, entry_index: int) -> None:
        """
        Add an entry to a specified position in a matchup.

        If adding the entry fills both matchup positions, 
        the matchup automatically creates its DE match.

        If validation or match creation fails, the round remains unchanged.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to add.
        matchup_index : int
            The matchup's zero-based position in the round.
        entry_index : int
            The entry position within the matchup: 
            ``0`` for the top position or
            ``1`` for the bottom position.

        Raises
        ------
        TypeError
            If ``entry`` is not a ``TournamentEntry``, either index is not an integer, 
            or match creation detects an invalid attribute type.
        ValueError
            If the entry belongs to another tournament, 
            already appears in this round, 
            either index is outside its valid range, the destination is occupied, 
            or the resulting entry pair cannot form a valid DE match.
        """
        self._validate_entry(entry, 'add_entry_to_matchup')
        self._validate_matchup_index(matchup_index, 'add_entry_to_matchup')

        validation.validate_int_in_range(entry_index, 0, 1, 'Entry index', 'DERound', 'add_entry_to_matchup')

        if entry in self.entries:
            raise ValueError(
                f'Cannot add entry {entry.id} to {self.label} because it already occupies a position in the round'
            )

        matchup = self.get_matchup_at(matchup_index)
    
        matchup.add_entry(entry, entry_index)


    # --- Bracket Position Generation Helper Methods ---
    @staticmethod
    def generate_tree_bracket_level(depth: int) -> tuple[int, ...]:
        """
        Generate the seed ordering at a specified tableau depth.

        The returned values identify the seeds occupying successive
        positions from the top of the tableau to the bottom.

        Parameters
        ----------
        depth : int
            The number of levels by which to expand the tableau tree from its root. 
            A depth of 0 produces one position, and a depth of ``n`` produces ``2**n`` positions.

        Returns
        -------
        tuple[int, ...]
            The one-based branch positions at the requested depth in top-to-bottom tableau order.

        Examples
        --------
        >>> DERound.generate_tree_bracket_level(0)
        (1,)
        >>> DERound.generate_tree_bracket_level(2)
        (1, 4, 3, 2)
        >>> DERound.generate_tree_bracket_level(3)
        (1, 8, 5, 4, 3, 6, 7, 2)

        Raises
        ------
        TypeError
            If ``depth`` is not an integer.
        ValueError
            If ``depth`` is negative.
        """
        validation.validate_int_at_least(depth, 0, 'Depth', 'DERound', 'generate_tree_bracket_level')

        # Start the position tree at depth 0
        current_depth = 0
        current_level = [1]

        # Build the position tree from the root
        while current_depth < depth:
            # Go to next depth
            current_depth += 1

            # Initialize a list to hold the next level values
            next_level = []

            # Define the loop's starting conditions
            invariant_sum = 2**current_depth + 1
            is_left = True

            # Build the next level
            for position_value in current_level:
                complement_value = invariant_sum - position_value
                
                if is_left:
                    next_level += [position_value, complement_value]
                else:
                    next_level += [complement_value, position_value]
                
                is_left = not is_left

            # Move up the position tree to the next level
            current_level = next_level

        return tuple(current_level)


    # --- Validation Helper Methods ---
    def _validate_matchup_index(self, index: int, method_name: str | None = None) -> None:
        """
        Validate a zero-based matchup index for this round.

        Parameters
        ----------
        index : int
            The matchup index to validate.
        method_name : str | None, default=None
            The name of the calling method, used to provide context in validation error messages.

        Raises
        ------
        TypeError
            If ``method_name`` is neither a string nor ``None``, or if ``index`` is not an integer.
        ValueError
            If ``index`` is outside the valid range of matchup indices.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(
                'method_name must be a string or None in DERound._validate_matchup_index() - '
                f'got {type(method_name).__name__}'
            )

        validation.validate_int_in_range(index, 0, self.num_matchups - 1, 'Matchup index', 'DERound', method_name)

    def _validate_entry(self, entry: TournamentEntry, method_name: str | None = None) -> None:
        """
        Validate an entry for use with this DE round.

        A valid entry must be a ``TournamentEntry`` belonging to the same tournament as the round. 
        This helper does not determine whether the entry already appears in the round.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.
        method_name : str | None, default=None
            The name of the calling method, used to provide context in validation error messages.

        Raises
        ------
        TypeError
            If ``method_name`` is neither a string nor ``None``, or if ``entry`` is not a ``TournamentEntry``.
        ValueError
            If ``entry`` belongs to a different tournament.
        """
        if method_name is not None and not isinstance(method_name, str):
            raise TypeError(
                f'method_name must be a string or None in DERound._validate_entry() - got {type(method_name).__name__}'
            )

        location = f'in DERound.{method_name}()' if method_name is not None else 'in DERound'

        if not isinstance(entry, TournamentEntry):
            raise TypeError(
                f'Entry must be a TournamentEntry {location} - got {type(entry).__name__}'
            )

        if entry.tournament_id != self.tournament_id:
            raise ValueError(
                f'Entry {entry.id} must have tournament ID {self.tournament_id} '
                f'{location} - got {entry.tournament_id}'
            )

    def _validate_matchups(self, matchups: tuple[DEMatchup, ...]) -> None:
        """
        Validate the round's matchup collection and structural invariants.

        Parameters
        ----------
        matchups : tuple[DEMatchup, ...]
            The matchup collection to validate.

        Raises
        ------
        TypeError
            If ``matchups`` is not a tuple, an item is not a ``DEMatchup``,
            or a matchup's stored match is neither a ``DEMatch`` nor ``None``.
        ValueError
            If ``matchups`` is empty, its length is not a power of two, 
            a matchup number does not agree with its tuple position, 
            a matchup's round or stage number does not agree with this round,
            the matchups do not share a tournament ID, 
            or the same tournament entry ID appears in more than one position.
        """
        if not isinstance(matchups, tuple):
            raise TypeError(f'Matchups must be a tuple in DERound - got {type(matchups).__name__}')
        
        if not matchups:
            raise ValueError('Matchups must contain at least one DEMatchup in DERound - got 0')
        
        if not is_power_of_two(len(matchups)):
            raise ValueError(f'The number of matchups must be a power of two in DERound - got {len(matchups)}')
        
        seen_entry_ids: set[int] = set()

        for i, matchup in enumerate(matchups):
            if not isinstance(matchup, DEMatchup):
                raise TypeError(f'Matchup at index {i} is not a DEMatchup in DERound - got {type(matchup).__name__}')
            
            if i == 0:
                tournament_id = matchups[0].tournament_id
            
            if matchup.matchup_number != i + 1:
                raise ValueError(
                    f'Matchup at index {i}\'s matchup number {matchup.matchup_number}'
                    f' does not agree with its matchup position {i + 1} in DERound'
                )
            
            if matchup.round_number != self.round_number:
                raise ValueError(
                    f'Matchup at index {i}\'s round number {matchup.round_number} '
                    f'does not match the round\'s round number {self.round_number} in DERound'
                )

            if matchup.stage_number != self.stage_number:
                raise ValueError(
                    f'Matchup at index {i}\'s stage number {matchup.stage_number} '
                    f'does not match the round\'s stage number {self.stage_number} in DERound'
                )
            
            if matchup.tournament_id != tournament_id:
                raise ValueError(
                    f'All matchups must have the same tournament ID: matchup 1 has tournament ID '
                    f'{tournament_id} and matchup {i + 1} has tournament ID {matchup.tournament_id} in DERound'
                )

            if matchup.match is not None and not isinstance(matchup.match, DEMatch):
                raise TypeError(
                    f'Matchup at index {i}\'s match must either be a DEMatch or None '
                    f'in DERound - got {type(matchup.match).__name__}'
                )
            
            for entry in matchup.entries:
                if entry is None:
                    continue
                
                if entry.id in seen_entry_ids:
                    raise ValueError(
                        f'Entry {entry.id} appears more than once in DERound for '
                        f'tournament {tournament_id}, stage {self.stage_number}, round {self.round_number}'
                    )
                
                seen_entry_ids.add(entry.id)
