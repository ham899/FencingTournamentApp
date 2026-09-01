from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import validation

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from matches.match import Match


@dataclass(eq=False)
class TournamentMatch(Match, ABC):
    """
    Represent the shared behaviour of a match between two tournament entries.

    ``TournamentMatch`` is an abstract subclass of ``Match`` and cannot
    be instantiated directly. Concrete subclasses provide the match type,
    descriptive label, and score representation used for forfeits.

    Both entries are required. They must belong to the same 
    tournament and represent different fencers.

    A tournament match may be completed by recording a valid score or a
    single forfeit. For a forfeit, ``forfeited_index`` identifies the losing
    entry while the concrete subclass determines whether scores are recorded.
    Resetting the match clears both its result and its forfeit state.

    Attributes
    ----------
    entry1 : TournamentEntry
        The entry in position 1 of the match.
    entry2 : TournamentEntry
        The entry in position 2 of the match.
    forfeited_index : int | None, default=None, init=False
        The index of the entry that forfeited: ``0`` for ``entry1``, 
        ``1`` for ``entry2``, or ``None`` when the match is not a forfeit.
    """
    entry1: TournamentEntry
    entry2: TournamentEntry

    forfeited_index: int | None = field(default=None, init=False)


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the entries and inherited match configuration.

        Each entry is validated individually before the pair is checked. A
        valid pair contains distinct entries representing distinct fencers in
        the same tournament. The inherited ``Match`` validation is then
        used to validate ``score_to_win``.
        
        Raises
        ------
        TypeError
            If either entry, one of its validated attributes, 
            or ``score_to_win`` has an invalid type.
        ValueError
            If either entry contains an invalid value, if ``score_to_win`` is
            not positive, if the entries are equal, if they represent the
            same fencer, or if they belong to different tournaments.
        """    
        # Validate provided entries
        self._validate_entry_pair(self.entry1, self.entry2)

        # Get parent class to validate inherited attributes
        super().__post_init__()


    # --- Properties ---
    @property
    def tournament_id(self) -> int:
        """Return the tournament identifier shared by the two entries."""
        return self.entry1.tournament_id
    
    @property
    def fencer1(self) -> Fencer:
        """Return the fencer represented by ``entry1``."""
        return self.entry1.fencer
    
    @property
    def fencer2(self) -> Fencer:
        """Return the fencer represented by ``entry2``."""
        return self.entry2.fencer

    @property
    def entries(self) -> tuple[TournamentEntry, TournamentEntry]:
        """Return the entries as ``(entry1, entry2)``."""
        return (self.entry1, self.entry2)    

    @property
    def winner_index(self) -> int | None:
        """
        Return the index of the winning entry.

        A scored result is interpreted by ``Match``. 
        For a forfeit, the winner is the entry opposite ``forfeited_index``.

        Returns
        -------
        int | None
            ``0`` if ``entry1`` won, ``1`` if ``entry2`` won, 
            or ``None`` if the match is incomplete.

        Raises
        ------
        RuntimeError
            If a completed scored result has tied scores or the match 
            contains an incomplete or invalid forfeit state.
        """
        if self.is_forfeit():    
            return 1 - self._get_forfeited_index()
        
        return super().winner_index
    
    @property
    def winner(self) -> TournamentEntry | None:
        """
        Return the winning entry, or ``None`` if the match is incomplete.

        Raises
        ------
        RuntimeError
            If the result state is internally inconsistent.
        """
        winner_index = self.winner_index

        if winner_index is None:
            return None

        return self.entry_at(winner_index)
    
    @property
    def loser_index(self) -> int | None:
        """
        Return the index of the losing entry.

        A scored result is interpreted by ``Match``. 
        For a forfeit, ``forfeited_index`` is the loser.

        Returns
        -------
        int | None
            ``0`` if ``entry1`` lost, ``1`` if ``entry2`` lost, 
            or ``None`` if the match is incomplete.

        Raises
        ------
        RuntimeError
            If a completed scored result has tied scores or the match 
            contains an incomplete or invalid forfeit state.
        """
        if self.is_forfeit():            
            return self._get_forfeited_index()
        
        return super().loser_index

    @property
    def loser(self) -> TournamentEntry | None:
        """
        Return the losing entry, or ``None`` if the match is incomplete.

        Raises
        ------
        RuntimeError
            If the result state is internally inconsistent.
        """
        loser_index = self.loser_index

        if loser_index is None:
            return None
        
        return self.entry_at(loser_index)


    # --- Predicate Methods ---
    def has_entry(self, entry: TournamentEntry) -> bool:
        """
        Return whether the match contains an entry equal to ``entry``.

        Parameters
        ----------
        entry : TournamentEntry
            The entry to search for.
        """
        return entry in self.entries
    
    def is_forfeit(self) -> bool:
        """Return whether the match has a recorded forfeited entry."""
        return self.forfeited_index is not None
    

    # --- Entry Access Methods ---
    def entry_at(self, index: int) -> TournamentEntry:
        """
        Return the entry at a specified match position.

        Parameters
        ----------
        index : int
            The entry index: ``0`` for ``entry1`` or ``1`` for ``entry2``.

        Returns
        -------
        TournamentEntry
            The tournament entry at the input index.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is not ``0`` or ``1``.
        """
        validation.validate_int_in_range(index, 0, 1, 'Entry index', 'TournamentMatch', 'entry_at')

        return self.entry1 if index == 0 else self.entry2

    def opponent_entry_of_index(self, index: int) -> TournamentEntry:
        """
        Return the opponent of the entry at a specified match position.

        Parameters
        ----------
        index : int
            The entry index: ``0`` for ``entry1`` or ``1`` for ``entry2``.

        Returns
        -------
        TournamentEntry
            ``entry2`` when ``index`` is ``0``; otherwise, ``entry1``.

        Raises
        ------
        TypeError
            If ``index`` is not an integer.
        ValueError
            If ``index`` is not ``0`` or ``1``.
        """
        validation.validate_int_in_range(index, 0, 1, 'Entry index', 'TournamentMatch', 'opponent_entry_of_index')      

        return self.entry2 if index == 0 else self.entry1


    # --- State Change Methods ---
    def reset(self) -> None:
        """
        Reset the match to its initial incomplete state.

        The inherited scores and completion state are cleared, 
        and ``forfeited_index`` is restored to ``None``.
        """
        super().reset()
        
        self.forfeited_index = None


    # --- Result Recording Methods ---
    def record_score(self, score1: int, score2: int) -> None:
        """
        Record a scored result and mark the match complete.

        Any previous scored result is overwritten. A forfeit result must 
        be reset before it can be replaced by a scored result.

        Parameters
        ----------
        score1 : int
            The final score of ``entry1``.
        score2 : int
            The final score of ``entry2``.

        Raises
        ------
        TypeError
            If either score is not an integer.
        ValueError
            If the match already has a forfeit result, if either score is
            outside the permitted range, or if the scores are equal.
        """
        if self.is_forfeit():
            raise ValueError(f'{self.label} already has a forfeit result. Reset it before recording a score.')

        super().record_score(score1, score2)

    def forfeit(self, forfeiting_index: int) -> None:
        """
        Record a forfeit and mark the match complete.

        The entry at ``forfeiting_index`` is recorded as the loser. The concrete subclass 
        assigns the appropriate score representation before the match is marked complete.

        Parameters
        ----------
        forfeiting_index : int
            The forfeiting entry's index: ``0`` for ``entry1`` or ``1`` for ``entry2``.

        Raises
        ------
        TypeError
            If ``forfeiting_index`` is not an integer.
        ValueError
            If the match is already complete or ``forfeiting_index`` is not ``0`` or ``1``.
        """
        # Validate match state
        if self.is_complete():
            raise ValueError(f'{self.label} is already complete.')

        # Validate input entry
        validation.validate_int_in_range(forfeiting_index, 0, 1, 'Forfeiting index', 'TournamentMatch', 'forfeit')  

        # Set the forfeited index
        self.forfeited_index = forfeiting_index

        # Let subclass handle the score assignment
        self._assign_forfeit_scores()

        # Mark the match as complete
        self._mark_complete()


    # --- Abstract Helper Methods ---
    @abstractmethod
    def _assign_forfeit_scores(self) -> None:
        """
        Assign the subclass-specific scores for a forfeit.

        Implementations must leave either two valid, non-tied scores or two
        absent scores for ``Match._mark_complete`` to validate.
        """
        pass


    # --- Validation Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry, entry_name: str) -> None:
        """
        Validate one tournament entry and its relevant attributes.
        
        Parameters
        ----------
        entry : TournamentEntry
            The entry to validate.
        entry_name : str
            The name of the entry to be used in a potential error message.

        Raises
        ------
        TypeError
            If ``entry_name`` is not a string, if ``entry`` is not a ``TournamentEntry``, 
            if an identifier is not an integer, or if the entry does not contain a ``Fencer``.
        ValueError
            If an identifier is not positive.
        """
        if not isinstance(entry_name, str):
            raise TypeError(f'The provided entry_name must be a string - got {type(entry_name).__name__}')
        
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'{entry_name} must be a TournamentEntry object - got {type(entry).__name__}.')
        
        validation.validate_positive_int(entry.id, f'{entry_name} ID', 'TournamentMatch', '_validate_entry')
        validation.validate_positive_int(entry.tournament_id, f'{entry_name} Tournament ID', 'TournamentMatch', '_validate_entry')
        
        if not isinstance(entry.fencer, Fencer):
            raise TypeError(f'{entry_name} must have a Fencer object - got {type(entry.fencer).__name__}.')

    def _validate_entry_pair(self, entry1: TournamentEntry, entry2: TournamentEntry) -> None:
        """
        Validate two entries as participants in the same match.

        Each entry is first validated independently. The pair must then contain distinct 
        entries representing distinct fencers, and both entries must belong to the same tournament.

        Parameters
        ----------
        entry1 : TournamentEntry
            The first entry in the pair.
        entry2 : TournamentEntry
            The second entry in the pair.

        Raises
        ------
        TypeError
            If either entry or one of its validated attributes has an invalid type.
        ValueError
            If either entry contains an invalid value, if the entries are equal, if they 
            represent the same fencer, or if they have different tournament identifiers.
        """
        # Validate the entries in isolation
        self._validate_entry(entry1, 'Entry 1')
        self._validate_entry(entry2, 'Entry 2')

        # Validate the entries as a valid pair
        if entry1 == entry2:
            raise ValueError('Entry 1 and entry 2 cannot be the same entry; an entry can\'t fence themself.')
        
        if entry1.fencer == entry2.fencer:
            raise ValueError('Entry 1 and entry 2 cannot have the same fencer; an entry can\'t fence themself.')
        
        if entry1.tournament_id != entry2.tournament_id:
            raise ValueError('Entry 1 and entry 2 must have the same tournament ID.')  
        

    # --- Result Validation Helper Methods ---
    def _get_forfeited_index(self) -> int:
        """
        Return the forfeited index after validating the result state.

        Returns
        -------
        int
            ``0`` when ``entry1`` forfeited or ``1`` when ``entry2`` forfeited.

        Raises
        ------
        RuntimeError
            If the match is incomplete or ``forfeited_index`` is not ``0`` or ``1``.
        """
        if self.is_incomplete():
            raise RuntimeError(f'{self.label} is incomplete but has a forfeited index')
        
        forfeited_index = self.forfeited_index

        if type(forfeited_index) is not int or forfeited_index not in (0, 1):
            raise RuntimeError(f'{self.label} has an invalid forfeited index: {forfeited_index}')
        
        return forfeited_index
