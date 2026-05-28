from de_round import DERound
from tournament_entry import TournamentEntry
from fencer import Fencer
from match import DEMatch

import pytest

### Constants ###
TOURNY_ID = 1

### Fixtures ###
@pytest.fixture
def entries():
    return [
        TournamentEntry(id=1, tournament_id=TOURNY_ID, fencer=Fencer(id=1, display_name='Bob'), de_seed=1),
        TournamentEntry(id=2, tournament_id=TOURNY_ID, fencer=Fencer(id=2, display_name='Jane'), de_seed=2),
        TournamentEntry(id=3, tournament_id=TOURNY_ID, fencer=Fencer(id=3, display_name='John'), de_seed=3),
        TournamentEntry(id=4, tournament_id=TOURNY_ID, fencer=Fencer(id=4, display_name='Jill'), de_seed=4),
        TournamentEntry(id=5, tournament_id=TOURNY_ID, fencer=Fencer(id=5, display_name='Allen'), de_seed=5),
        TournamentEntry(id=6, tournament_id=TOURNY_ID, fencer=Fencer(id=6, display_name='Alison'), de_seed=6),
        TournamentEntry(id=7, tournament_id=TOURNY_ID, fencer=Fencer(id=7, display_name='May'), de_seed=7),
        TournamentEntry(id=8, tournament_id=TOURNY_ID, fencer=Fencer(id=8, display_name='Marco'), de_seed=8)
    ]

@pytest.fixture
def matches(entries):
    return [
        DEMatch(id=1, tournament_id=TOURNY_ID, entry1=entries[0], entry2=entries[7], round_index=0, match_index=0),
        DEMatch(id=2, tournament_id=TOURNY_ID, entry1=entries[3], entry2=entries[4], round_index=0, match_index=1),
        DEMatch(id=3, tournament_id=TOURNY_ID, entry1=entries[2], entry2=entries[5], round_index=0, match_index=2),
        DEMatch(id=4, tournament_id=TOURNY_ID, entry1=entries[1], entry2=entries[6], round_index=0, match_index=3),
    ]

@pytest.fixture
def de_round(matches):
    return DERound(index=0, size=8, matches=matches)

### Tests ###
def test_de_round_creation(matches):
    de_round = DERound(index=0, size=8, matches=matches)
    assert de_round.index == 0
    assert de_round.size == 8
    assert de_round.matches == matches

def test_de_round_creation_invalid_types(matches):
    with pytest.raises(TypeError):
        DERound(index='0', size=8, matches=matches)
    with pytest.raises(TypeError):
        DERound(index=0, size=Fencer(id=10, display_name='Jack'), matches=matches)
    with pytest.raises(TypeError):
        DERound(index=0, size=8, matches=True)
    with pytest.raises(TypeError):
        DERound(index=0, size=8, matches=[matches[0], matches[1], 'invalid type', matches[3]])

def test_de_round_creation_invalid_values(matches):
    with pytest.raises(ValueError):
        DERound(index=-1, size=8, matches=matches)
    with pytest.raises(ValueError):
        DERound(index=0, size=-8, matches=matches)
    # Test non-power of two size
    with pytest.raises(ValueError):
        DERound(index=0, size=7, matches=matches)
    # Test mismatch between size and number of matches
    with pytest.raises(ValueError):
        DERound(index=0, size=8, matches=matches[:-1])    
    # Test invalid round index in input matches
    with pytest.raises(ValueError):
        DERound(index=0, size=8, matches=[DEMatch(id=1, tournament_id=TOURNY_ID, entry1=matches[0].entry1, entry2=matches[0].entry2, round_index=1, match_index=0), matches[1], matches[2], matches[3]])
    # Test incorrect order for match IDs
    with pytest.raises(ValueError):
        DERound(index=0, size=8, matches=[matches[1], matches[0], matches[2], matches[3]])

def test_de_round_creation_with_byes(matches):
    matches[0].entry2 = None # Fencer seeded first gets a bye
    de_round = DERound(index=0, size=8, matches=matches)
    assert de_round.index == 0
    assert de_round.size == 8
    assert de_round.matches == matches

def test_de_round_creation_invalid_seeds(matches):
    for i in range(0, len(matches), 2):
        matches[i].entry1.de_seed = i
        matches[i].entry2.de_seed = i+1

    with pytest.raises(ValueError):
        DERound(index=0, size=8, matches=matches)

def test_de_round_creation_empty_round():
    matches = [
        DEMatch(id=1, tournament_id=TOURNY_ID, round_index=0, match_index=0),
        DEMatch(id=2, tournament_id=TOURNY_ID, round_index=0, match_index=1),
        DEMatch(id=3, tournament_id=TOURNY_ID, round_index=0, match_index=2),
        DEMatch(id=4, tournament_id=TOURNY_ID, round_index=0, match_index=3),
    ]
    de_round = DERound(index=0, size=8, matches=matches)
    assert de_round.index == 0
    assert de_round.size == 8
    assert de_round.matches == matches

def test_de_round_get_match(de_round):
    m = de_round.get_match(index=2)
    assert m == de_round.matches[2]

def test_de_round_get_match_invalid(de_round):
    with pytest.raises(TypeError):
        de_round.get_match(index='four')
    with pytest.raises(ValueError):
        de_round.get_match(index=-1)
    with pytest.raises(ValueError):
        de_round.get_match(index=de_round.size)

def test_de_round_record_match_result(de_round):
    de_round.record_match_result(index=0, score1=15, score2=14)
    m0 = de_round.get_match(0)
    assert m0.score1 == 15
    assert m0.score2 == 14
    assert m0.completed == True
    assert m0.winner == m0.entry1

    de_round.record_match_result(index=1, score1=15, score2=11)
    m1 = de_round.get_match(1)
    assert m1.score1 == 15
    assert m1.score2 == 11
    assert m1.completed == True
    assert m1.winner == m1.entry1

    de_round.record_match_result(index=2, score1=9, score2=15)
    m2 = de_round.get_match(2)
    assert m2.score1 == 9
    assert m2.score2 == 15
    assert m2.completed == True
    assert m2.winner == m2.entry2

    de_round.record_match_result(index=3, score1=7, score2=11)
    m3 = de_round.get_match(3)
    assert m3.score1 == 7
    assert m3.score2 == 11
    assert m3.completed == True
    assert m3.winner == m3.entry2

def test_de_round_record_match_result_invalid(de_round):
    with pytest.raises(TypeError):
        de_round.record_match_result(index='zero', score1=2, score2=1)
    with pytest.raises(TypeError):
        de_round.record_match_result(index=0, score1='two', score2=1)
    with pytest.raises(TypeError):
        de_round.record_match_result(index=0, score1=2, score2=True)
    with pytest.raises(ValueError):
        de_round.record_match_result(index=-1, score1=15, score2=14)
    with pytest.raises(ValueError):
        de_round.record_match_result(index=len(de_round.matches), score1=15, score2=14)
    with pytest.raises(ValueError):
        de_round.record_match_result(index=0, score1=-1, score2=1)
    with pytest.raises(ValueError):
        de_round.record_match_result(index=0, score1=1, score2=-2)

def test_de_round_is_complete(de_round):
    for i in range(len(de_round.matches)):
        de_round.record_match_result(index=i, score1=15, score2=14)
    assert de_round.is_complete()

def test_de_round_get_winners(entries, de_round):
    for i in range(len(de_round.matches)):
        de_round.record_match_result(index=i, score1=15, score2=14)
    winners = de_round.get_winners()
    assert winners == [entries[0], entries[3], entries[2], entries[1]]

def test_de_round_get_losers(entries, de_round):
    for i in range(len(de_round.matches)):
        de_round.record_match_result(index=i, score1=15, score2=14)
    losers = de_round.get_losers()
    assert losers == [entries[7], entries[4], entries[5], entries[6]]

def test_de_round_get_round_name():
    # Top 16
    entries_16 = [
        TournamentEntry(id=1, tournament_id=TOURNY_ID, fencer=Fencer(id=1, display_name='Bob'), de_seed=1),
        None,
        TournamentEntry(id=3, tournament_id=TOURNY_ID, fencer=Fencer(id=3, display_name='John'), de_seed=9),
        TournamentEntry(id=4, tournament_id=TOURNY_ID, fencer=Fencer(id=4, display_name='Jill'), de_seed=8),
        TournamentEntry(id=5, tournament_id=TOURNY_ID, fencer=Fencer(id=5, display_name='Allen'), de_seed=5),
        TournamentEntry(id=6, tournament_id=TOURNY_ID, fencer=Fencer(id=6, display_name='Alison'), de_seed=12),
        TournamentEntry(id=7, tournament_id=TOURNY_ID, fencer=Fencer(id=7, display_name='May'), de_seed=13),
        TournamentEntry(id=8, tournament_id=TOURNY_ID, fencer=Fencer(id=8, display_name='Marco'), de_seed=4),
        TournamentEntry(id=9, tournament_id=TOURNY_ID, fencer=Fencer(id=9, display_name='Jack'), de_seed=3),
        TournamentEntry(id=10, tournament_id=TOURNY_ID, fencer=Fencer(id=10, display_name='Jill'), de_seed=14),
        TournamentEntry(id=11, tournament_id=TOURNY_ID, fencer=Fencer(id=11, display_name='Bill'), de_seed=11),
        TournamentEntry(id=12, tournament_id=TOURNY_ID, fencer=Fencer(id=12, display_name='Will'), de_seed=6),
        TournamentEntry(id=13, tournament_id=TOURNY_ID, fencer=Fencer(id=13, display_name='Emily'), de_seed=7),
        TournamentEntry(id=14, tournament_id=TOURNY_ID, fencer=Fencer(id=14, display_name='Emma'), de_seed=10),
        None,
        TournamentEntry(id=16, tournament_id=TOURNY_ID, fencer=Fencer(id=16, display_name='Ella'), de_seed=2)
    ]
    matches_16 = [
        DEMatch(id=1, tournament_id=TOURNY_ID, entry1=entries_16[0], entry2=entries_16[1], round_index=0, match_index=0),
        DEMatch(id=2, tournament_id=TOURNY_ID, entry1=entries_16[2], entry2=entries_16[3], round_index=0, match_index=1),
        DEMatch(id=3, tournament_id=TOURNY_ID, entry1=entries_16[4], entry2=entries_16[5], round_index=0, match_index=2),
        DEMatch(id=4, tournament_id=TOURNY_ID, entry1=entries_16[6], entry2=entries_16[7], round_index=0, match_index=3),
        DEMatch(id=5, tournament_id=TOURNY_ID, entry1=entries_16[8], entry2=entries_16[9], round_index=0, match_index=4),
        DEMatch(id=6, tournament_id=TOURNY_ID, entry1=entries_16[10], entry2=entries_16[11], round_index=0, match_index=5),
        DEMatch(id=7, tournament_id=TOURNY_ID, entry1=entries_16[12], entry2=entries_16[13], round_index=0, match_index=6),
        DEMatch(id=8, tournament_id=TOURNY_ID, entry1=entries_16[14], entry2=entries_16[15], round_index=0, match_index=7)
    ]
    top_16 = DERound(index=0, size=16, matches=matches_16)
    assert top_16.get_round_name() == 'Round of 16'

    # Top 8
    entries_8 = [
        TournamentEntry(id=1, tournament_id=TOURNY_ID, fencer=Fencer(id=1, display_name='Bob'), de_seed=1),
        TournamentEntry(id=2, tournament_id=TOURNY_ID, fencer=Fencer(id=2, display_name='Jane'), de_seed=8),
        TournamentEntry(id=3, tournament_id=TOURNY_ID, fencer=Fencer(id=3, display_name='John'), de_seed=5),
        TournamentEntry(id=4, tournament_id=TOURNY_ID, fencer=Fencer(id=4, display_name='Jill'), de_seed=4),
        TournamentEntry(id=5, tournament_id=TOURNY_ID, fencer=Fencer(id=5, display_name='Allen'), de_seed=3),
        TournamentEntry(id=6, tournament_id=TOURNY_ID, fencer=Fencer(id=6, display_name='Alison'), de_seed=6),
        TournamentEntry(id=7, tournament_id=TOURNY_ID, fencer=Fencer(id=7, display_name='May'), de_seed=7),
        TournamentEntry(id=8, tournament_id=TOURNY_ID, fencer=Fencer(id=8, display_name='Marco'), de_seed=2)
    ]
    matches_8 = [
        DEMatch(id=1, tournament_id=TOURNY_ID, entry1=entries_8[0], entry2=entries_8[1], round_index=0, match_index=0),
        DEMatch(id=2, tournament_id=TOURNY_ID, entry1=entries_8[2], entry2=entries_8[3], round_index=0, match_index=1),
        DEMatch(id=3, tournament_id=TOURNY_ID, entry1=entries_8[4], entry2=entries_8[5], round_index=0, match_index=2),
        DEMatch(id=4, tournament_id=TOURNY_ID, entry1=entries_8[6], entry2=entries_8[7], round_index=0, match_index=3)
    ]
    top_8 = DERound(index=0, size=8, matches=matches_8)
    assert top_8.get_round_name() == 'Quarter-Final'

    # Top 4
    entries_4 = [
        TournamentEntry(id=1, tournament_id=TOURNY_ID, fencer=Fencer(id=1, display_name='Bob'), de_seed=1),
        None,
        TournamentEntry(id=3, tournament_id=TOURNY_ID, fencer=Fencer(id=3, display_name='John'), de_seed=3),
        TournamentEntry(id=4, tournament_id=TOURNY_ID, fencer=Fencer(id=4, display_name='Jill'), de_seed=2)
    ]
    matches_4 = [
        DEMatch(id=1, tournament_id=TOURNY_ID, entry1=entries_4[0], entry2=entries_4[1], round_index=0, match_index=0),
        DEMatch(id=2, tournament_id=TOURNY_ID, entry1=entries_4[2], entry2=entries_4[3], round_index=0, match_index=1)
    ]
    top_4 = DERound(index=0, size=4, matches=matches_4)
    assert top_4.get_round_name() == 'Semi-Final'

    # Top 2
    entries_2 = [
        TournamentEntry(id=1, tournament_id=TOURNY_ID, fencer=Fencer(id=1, display_name='Bob'), de_seed=1),
        TournamentEntry(id=2, tournament_id=TOURNY_ID, fencer=Fencer(id=2, display_name='Jane'), de_seed=2)
    ]
    matches_2 = [
        DEMatch(id=1, tournament_id=TOURNY_ID, entry1=entries_2[0], entry2=entries_2[1], round_index=0, match_index=0)
    ]
    top_2 = DERound(index=0, size=2, matches=matches_2)
    assert top_2.get_round_name() == 'Final'


def test_de_round_static__generate_tree_bracket_level():
    assert DERound._generate_tree_bracket_level(depth=0) == [1]

    assert DERound._generate_tree_bracket_level(depth=1) == [1,2]

    assert DERound._generate_tree_bracket_level(depth=2) == [1,4,3,2]

    assert DERound._generate_tree_bracket_level(depth=3) == [1,8,5,4,3,6,7,2]

    assert DERound._generate_tree_bracket_level(depth=4) == [1,16,9,8,5,12,13,4,3,14,11,6,7,10,15,2]

    assert DERound._generate_tree_bracket_level(depth=5) == [1,32,17,16,9,24,25,8,5,28,21,12,13,20,29,4,3,30,19,14,11,22,27,6,7,26,23,10,15,18,31,2]

def test_de_round_get_position(de_round):
    assert de_round.get_position(match_index=0, location=0) == 1
    assert de_round.get_position(match_index=0, location=1) == 8
    assert de_round.get_position(match_index=1, location=0) == 5
    assert de_round.get_position(match_index=1, location=1) == 4
    assert de_round.get_position(match_index=2, location=0) == 3
    assert de_round.get_position(match_index=2, location=1) == 6
    assert de_round.get_position(match_index=3, location=0) == 7
    assert de_round.get_position(match_index=3, location=1) == 2

def test_de_round_get_position_invalid(de_round):
    with pytest.raises(TypeError):
        de_round.get_position(match_index='zero', location=0)
    with pytest.raises(TypeError):
        de_round.get_position(match_index=0, location='top')
    with pytest.raises(ValueError):
        de_round.get_position(match_index=-1, location=0)
    with pytest.raises(ValueError):
        de_round.get_position(match_index=len(de_round.matches), location=0)
    with pytest.raises(ValueError):
        de_round.get_position(match_index=0, location=-1)
    with pytest.raises(ValueError):
        de_round.get_position(match_index=0, location=2)

def test_de_round_add_entry(de_round):
    de_round.matches[0].entry1 = None
    de_round.matches[0].entry2 = None

    assert de_round.get_match(0).entry1 is None
    assert de_round.get_match(0).entry2 is None

    entry1 = TournamentEntry(id=50, tournament_id=TOURNY_ID, fencer=Fencer(id=50, display_name='Edward'), de_seed=4)
    entry2 = TournamentEntry(id=51, tournament_id=TOURNY_ID, fencer=Fencer(id=51, display_name='Edwin'), de_seed=5)

    de_round.add_entry(entry=entry1, match_index=0, location=0)
    de_round.add_entry(entry=entry2, match_index=0, location=1)

    assert de_round.get_match(0).entry1 == entry1
    assert de_round.get_match(0).entry2 == entry2

def test_de_round_add_entry_invalid(de_round):
    entry = TournamentEntry(id=50, tournament_id=TOURNY_ID, fencer=Fencer(id=50, display_name='Edward'), de_seed=4)
    with pytest.raises(TypeError):
        de_round.add_entry(entry=True, match_index=0, location=0)
    with pytest.raises(TypeError):
        de_round.add_entry(entry=entry, match_index='0', location=0)
    with pytest.raises(TypeError):
        de_round.add_entry(entry=entry, match_index=0, location='Allen')
    with pytest.raises(ValueError):
        de_round.add_entry(entry=entry, match_index=-1, location=0)
    with pytest.raises(ValueError):
        de_round.add_entry(entry=entry, match_index=len(de_round.matches), location=0)
    with pytest.raises(ValueError):
        de_round.add_entry(entry=entry, match_index=0, location=-1)
    with pytest.raises(ValueError):
        de_round.add_entry(entry=entry, match_index=0, location=2)

def test_de_round_add_entry1(de_round):
    de_round.matches[0].entry1 = None
    de_round.matches[0].entry2 = None

    assert de_round.get_match(0).entry1 is None
    assert de_round.get_match(0).entry2 is None

    entry1 = TournamentEntry(id=50, tournament_id=TOURNY_ID, fencer=Fencer(id=50, display_name='Edward'), de_seed=4)
    de_round.add_entry1(entry1, match_index=0)

    assert de_round.get_match(0).entry1 == entry1
    assert de_round.get_match(0).entry2 is None

def test_de_round_add_entry1(de_round):
    entry = TournamentEntry(id=50, tournament_id=TOURNY_ID, fencer=Fencer(id=50, display_name='Edward'), de_seed=4)
    with pytest.raises(TypeError):
        de_round.add_entry1('Edward', 0)
    with pytest.raises(TypeError):
        de_round.add_entry1(entry, 'First')
    with pytest.raises(ValueError):
        de_round.add_entry1(entry, -1)
    with pytest.raises(ValueError):
        de_round.add_entry1(entry, len(de_round.matches)+100)

def test_de_round_add_entry2(de_round):
    de_round.matches[0].entry1 = None
    de_round.matches[0].entry2 = None

    assert de_round.get_match(0).entry1 is None
    assert de_round.get_match(0).entry2 is None

    entry2 = TournamentEntry(id=51, tournament_id=TOURNY_ID, fencer=Fencer(id=51, display_name='Edwin'), de_seed=5)
    de_round.add_entry2(entry2, match_index=0)

    assert de_round.get_match(0).entry1 is None
    assert de_round.get_match(0).entry2 == entry2

def test_de_round_add_entry2(de_round):
    entry = TournamentEntry(id=50, tournament_id=TOURNY_ID, fencer=Fencer(id=50, display_name='Edward'), de_seed=4)
    with pytest.raises(TypeError):
        de_round.add_entry2('Edward', 0)
    with pytest.raises(TypeError):
        de_round.add_entry2(entry, 'First')
    with pytest.raises(ValueError):
        de_round.add_entry2(entry, -1)
    with pytest.raises(ValueError):
        de_round.add_entry2(entry, len(de_round.matches)+100)