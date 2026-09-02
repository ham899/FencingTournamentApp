# tests/factories.py

from entities.fencer import Fencer
from matches.poule_match import PouleMatch
from poules.poule import Poule
from poules.poule_orders import POULE_BOUT_ORDER
from sample_names import SAMPLE_NAMES
from entities.tournament_entry import TournamentEntry


def make_fencer(id: int, name: str) -> Fencer:
    """Creates a valid Fencer for use in tests."""
    return Fencer(id, name)

def make_tournament_entry(id: int, tournament_id: int, fencer: Fencer) -> TournamentEntry:
    """Creates a valid TournamentEntry for use in tests."""
    return TournamentEntry(id, tournament_id, fencer)

def make_entries(n: int, tournament_id: int) -> tuple[TournamentEntry, ...]:
    """Creates a tuple of valid TournamentEntry objects for use in tests."""
    return tuple(
        make_tournament_entry(
            id = i + 1, 
            tournament_id = tournament_id,
            fencer = make_fencer(id=i + 1, name=SAMPLE_NAMES[i])
        ) for i in range(n)
    )

def make_entry_at_number(number: int, tournament_id: int) -> TournamentEntry:
    """Gets a specific tournament entry from make_entries()."""
    return make_entries(number, tournament_id)[-1]

def make_poule_match(entry1: TournamentEntry, entry2: TournamentEntry, match_number: int, poule_number: int, stage_number: int, 
                     *, score1: int | None = None, score2: int | None = None) -> PouleMatch:
    """Creates a valid uncompleted PouleMatch for use in tests."""
    if (score1 is None and score2 is not None) or (score1 is not None and score2 is None):
        raise ValueError(f'The provided scores must either both be None or both be not None - got score1={score1} and score2={score2}')

    poule_match = PouleMatch(
        entry1 = entry1,
        entry2 = entry2,
        match_number = match_number,
        poule_number = poule_number,
        stage_number = stage_number
    )

    if score1 is not None and score2 is not None:
        poule_match.record_score(score1, score2)
    
    return poule_match

def make_poule_matches(entries: tuple[TournamentEntry, ...], poule_number: int, stage_number: int, 
                       *, scores: tuple[tuple[int, int], ...] = None) -> tuple[PouleMatch, ...]:
    """Creates a tuple of PouleMatch objects based on the official bout order."""
    bout_order = POULE_BOUT_ORDER[len(entries)]

    matches = []

    for i, (fencer_number1, fencer_number2) in enumerate(bout_order):
        entry1 = entries[fencer_number1 - 1]
        entry2 = entries[fencer_number2 - 1]

        matches.append(
            make_poule_match(
                entry1 = entry1, 
                entry2 = entry2,

                match_number = i + 1,
                poule_number = poule_number,
                stage_number = stage_number, 

                score1 = scores[i][0] if scores is not None and i < len(scores) else None,
                score2 = scores[i][1] if scores is not None and i < len(scores) else None
            )
        )

    return tuple(matches)

def make_poule(poule_number: int, stage_number: int, entries: tuple[TournamentEntry, ...], 
               *, scores: tuple[tuple[int, int], ...] = None) -> Poule:
    """Creates a valid Poule for use in tests."""
    poule = Poule(poule_number, stage_number, entries)

    # Record scores if provided
    if scores:
        for i, (score1, score2) in enumerate(scores):
            poule.record_match_result(i, score1, score2)
    
    return poule
