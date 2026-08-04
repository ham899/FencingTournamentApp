from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule import Poule
from poules.poule_orders import POULE_BOUT_ORDER
from poules.poule_round import PouleRound

NAME_POOL = (
    'John',
    'Steve',
    'Hannah',
    'Emily',
    'Michael',
    'Sarah',
    'David',
    'Jill',
    'Parsa',
    'Chantelle',
    'Jessica',
    'Jack',
    'Edward',
    'Jane',
    'Joanna',
    'Stephen',
    'Robert',
    'Bob',
    'Peter',
    'Catherine',
    'Rob',
    'Isabella',
    'Albert',
    'Elizabeth',
    'Victoria',
    'Jeseph',
    'Mary',
    'William',
    'James',
    'Benjamin',
    'Lucas',
    'Mason',
    'Ethan',
    'Alexander',
    'Daniel',
    'Matthew',
    'Henry',
    'Sebastian',
    'Owen',
    'Gabriel',
    'Carter',
    'Wyatt',
    'Caleb',
    'Isaac',
    'Ryan',
    'Nathan',
    'Aaron',
    'Christian'
)

def make_fencer(fencer_id: int, name: str) -> Fencer:
    """Creates a valid Fencer for use in tests."""
    return Fencer(fencer_id, name)

def make_tournament_entry(id: int, 
                          fencer: Fencer, 
                          tournament_id: int, 
                          *, 
                          initial_seed: int | None = None, 
                          de_seed: int | None = None) -> TournamentEntry:
    """Creates a valid TournamentEntry for use in tests."""
    return TournamentEntry(id, tournament_id, fencer, initial_seed, de_seed)

def make_entries(n: int, tournament_id: int, *, initial_seed: bool = False, de_seed: bool = False) -> tuple[TournamentEntry, ...]:
    """Creates a tuple of valid TournamentEntry objects for use in tests."""
    return tuple(
        make_tournament_entry(
            id = i, 
            tournament_id = tournament_id,
            fencer = make_fencer(i, NAME_POOL[i]), 
            initial_seed = i if initial_seed else None, 
            de_seed = i if de_seed else None
        ) for i in range(1, n + 1)
    )

def make_poule_match(
        match_id: int, 
        tournament_id: int,
        entry1: TournamentEntry, 
        entry2: TournamentEntry, 
        poule_id: int, 
        match_index: int,
        *,
        score1: int | None = None,
        score2: int | None = None) -> PouleMatch:
    """Creates a valid uncompleted PouleMatch for use in tests."""
    poule_match = PouleMatch(
        id = match_id, 
        tournament_id = tournament_id, 
        entry1 = entry1, 
        entry2 = entry2, 
        poule_id = poule_id, 
        match_index = match_index
    )

    if score1 is not None and score2 is not None:
        poule_match.record_score(score1, score2)
    
    return poule_match

def make_poule_matches(
        entries: tuple[TournamentEntry, ...], 
        poule_id: int, 
        tournament_id: int,
        *,
        scores: tuple[int, int] = None) -> tuple[PouleMatch, ...]:
    """Creates a tuple of PouleMatch objects based on the official bout order."""
    bout_order = POULE_BOUT_ORDER[len(entries)]

    matches = []

    for i, fencer_number1, fencer_number2 in enumerate(bout_order):
        entry1 = entries[fencer_number1 - 1]
        entry2 = entries[fencer_number2 - 1]

        matches.append(
            make_poule_match(
                match_id = i + 1, 
                tournament_id = tournament_id, 
                entry1 = entry1, 
                entry2 = entry2, 
                poule_id = poule_id, 
                match_index = i,
                score1 = scores[i][0] if scores is None else None,
                score2 = scores[i][1] if scores is None else None
            )
        )

    return tuple(matches)

def make_poule(
        id: int, 
        tournament_id: int,
        poule_number: int, 
        entries: tuple[TournamentEntry, ...],
        *,
        scores: tuple[int, int] = None) -> Poule:
    """Creates a valid Poule for use in tests."""
    poule = Poule(id, tournament_id, poule_number, entries=entries)

    # Record scores if provided
    if scores:
        for i, score1, score2 in enumerate(scores):
            poule.record_match_result(i, score1, score2)
    
    return poule 

def make_poule_round(entries: tuple[TournamentEntry, ...], id, tournament_id, round_number) -> PouleRound:
    """Creates a valid PouleRound for use in tests."""
    return PouleRound(id, tournament_id, round_number, entries)