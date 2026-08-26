from dataclasses import dataclass, field

import validation

from matches.tournament_match import TournamentMatch


@dataclass(eq=False)
class PouleMatch(TournamentMatch):
    """
    Represent a poule match between two tournament entries.

    Both entries are required. ``entry1`` represents the fencer to the
    referee's right, and ``entry2`` represents the fencer to the referee's left.

    The match, poule, and round numbers are all one-based. ``round_number``
    represents the round's overall position within the tournament, regardless
    of whether that round is a poule round or another type of round.

    A forfeit is recorded by assigning ``score_to_win`` to the non-forfeiting entry and zero to the forfeiting entry.

    Attributes
    ----------
    match_number : int
        The match's one-based position within the poule's official bout order.
    poule_number : int
        The poule's one-based position within its round.
    round_number : int
        The match's one-based round position within the tournament.
    score_to_win : int, default=5
        The conventional target score and maximum permitted recorded score for either entry.
    """
    match_number: int
    poule_number: int
    round_number: int

    score_to_win: int = field(default=5, kw_only=True)


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the poule match numbers and inherited match configuration.

        Raises
        ------
        TypeError
            If ``match_number``, ``poule_number``, ``round_number``, or ``score_to_win`` is 
            not an integer, or if an entry or one of its validated attributes has an invalid type.
        ValueError
            If any number is not positive, if either entry contains an invalid value, if the entries are equal, 
            if they represent the same fencer, or if they belong to different tournaments.
        """
        validation.validate_positive_int(self.match_number, 'Match number', 'PouleMatch')
        validation.validate_positive_int(self.poule_number, 'Poule number', 'PouleMatch')
        validation.validate_positive_int(self.round_number, 'Round number', 'PouleMatch')
        
        super().__post_init__()


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying the match."""
        return (
            f'Match {self.match_number} in poule {self.poule_number} '
            f'of round {self.round_number} '
            f'in tournament {self.tournament_id}'
        )

    @property
    def match_type(self) -> str:
        """Return the match type."""
        return 'poule'
        
    @property
    def match_index(self) -> int:
        """Return the match's zero-based position within its poule."""
        return self.match_number - 1
    
    @property
    def poule_index(self) -> int:
        """Return the poule's zero-based position within its round."""
        return self.poule_number - 1
    
    @property
    def round_index(self) -> int:
        """Return the round's zero-based position within the tournament."""
        return self.round_number - 1


    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """
        Return whether ``other`` represents the same scheduled poule match.

        Equality is based on tournament ID, round number, poule number, and
        match number. Entries and recorded results are not considered.
        """
        if not isinstance(other, PouleMatch):
            return False

        return (
            self.tournament_id == other.tournament_id and 
            self.round_number == other.round_number and
            self.poule_number == other.poule_number and 
            self.match_number == other.match_number
        )


    # --- TournamentMatch Hook Implementations ---
    def _assign_forfeit_scores(self) -> None:
        """
        Assign the poule-specific scores for a forfeit.

        The non-forfeiting entry receives ``score_to_win``, and the forfeiting entry receives zero.

        Raises
        ------
        RuntimeError
            If ``forfeited_index`` is not ``0`` or ``1``.
        """
        forfeited_index = self.forfeited_index

        if type(forfeited_index) is not int or forfeited_index not in (0, 1):
            raise RuntimeError(f'{self.label} cannot assign a forfeit score without a valid forfeited index')

        if forfeited_index == 0:
            self.score1 = 0
            self.score2 = self.score_to_win
        else:
            self.score1 = self.score_to_win
            self.score2 = 0
