import pytest
from fencer import Fencer
from tournament_entry import TournamentEntry
from match import Match, PouleMatch, DEMatch

@pytest.fixture
def entry1():
    fencer1 = Fencer(id=1, display_name='Bob')
    return TournamentEntry(id=1, tournament_id=1, fencer=fencer1)

@pytest.fixture
def entry2():
    fencer2 = Fencer(id=2, display_name='Bill')
    return TournamentEntry(id=2, tournament_id=1, fencer=fencer2)

@pytest.fixture
def entry3():
    fencer3 = Fencer(id=3, display_name='Ben')
    return TournamentEntry(id=3, tournament_id=1, fencer=fencer3)

# Test ABC Match class first
def test_cannot_create_abstract_match():
    with pytest.raises(TypeError):
        Match(id=1, tournament_id=1, score_to_win=5)

# Test valid PouleMatch creation
def test_valid_poule_match_creation_defaults(entry1, entry2):
    poule_match = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    assert poule_match.id==1
    assert poule_match.tournament_id==1
    assert poule_match.entry1==entry1
    assert poule_match.entry2==entry2
    assert poule_match.poule_id==1
    assert poule_match.score1==0
    assert poule_match.score2==0
    assert poule_match.score_to_win==5
    assert poule_match.winner_entry is None
    assert poule_match.completed==False

def test_valid_poule_match_creation_no_defaults(entry1, entry2):
    poule_match = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=8, poule_id=1)
    assert poule_match.id==1
    assert poule_match.tournament_id==1
    assert poule_match.entry1==entry1
    assert poule_match.entry2==entry2
    assert poule_match.poule_id==1
    assert poule_match.score1==0
    assert poule_match.score2==0
    assert poule_match.score_to_win==8
    assert poule_match.winner_entry is None
    assert poule_match.completed==False

# Test valid DEMatch creation
def test_valid_de_match_creation_defaults():
    de_match = DEMatch(id=1, tournament_id=1, round_index=0, match_index=0)
    assert de_match.id==1
    assert de_match.tournament_id==1
    assert de_match.round_index==0
    assert de_match.match_index==0
    assert de_match.score_to_win == 15
    assert de_match.entry1 is None
    assert de_match.entry2 is None
    assert de_match.winner_entry is None
    assert de_match.completed==False

def test_valid_de_match_creation_no_defaults(entry1, entry2):
    de_match = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=12, round_index=1, match_index=1)
    assert de_match.id==1
    assert de_match.tournament_id==1
    assert de_match.entry1==entry1
    assert de_match.entry2==entry2
    assert de_match.score_to_win==12
    assert de_match.round_index==1
    assert de_match.match_index==1
    assert de_match.winner_entry is None
    assert de_match.completed==False

# Test invalid Match inputs through PouleMatch constructor
def test_match_invalid_id(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id='one', tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        PouleMatch(id=0, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        PouleMatch(id=-1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)

def test_match_invalid_tournament_id(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id='one', entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=0, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=-1, entry1=entry1, entry2=entry2, poule_id=1)

def test_match_invalid_score_to_win(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win='five', poule_id=1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=0, poule_id=1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=-5, poule_id=1)

# Test Match methods through PouleMatch child
def test_match_record_score_invalid_type(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(TypeError):
        m.record_score(score1='1', score2=5)
    with pytest.raises(TypeError):
        m.record_score(score1=1, score2='5')
    with pytest.raises(TypeError):
        m.record_score(score1='1', score2='5')

def test_match_record_score_invalid_value(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        m1.record_score(score1=-1, score2=5)
    with pytest.raises(ValueError):
        m1.record_score(score1=6, score2=3)

    m2 = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index=0)
    with pytest.raises(ValueError):
        m2.record_score(score1=17, score2=5)
    with pytest.raises(ValueError):
        m2.record_score(score1=7, score2=-1)

def test_match_record_score_equal_scores(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        m1.record_score(score1=4, score2=4)
    m2 = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index=0)
    with pytest.raises(ValueError):
        m2.record_score(score1=11, score2=11)

def test_match_record_score_entry1_wins(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    m1.record_score(score1=5, score2=3)
    assert m1.winner_entry==entry1
    assert m1.completed==True

    m2 = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index=0)
    m2.record_score(score1=12, score2=5)
    assert m2.winner_entry==entry1
    assert m2.completed==True

def test_match_record_score_entry2_wins(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    m1.record_score(score1=2, score2=4)
    assert m1.winner_entry==entry2
    assert m1.completed==True

    m2 = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index=0)
    m2.record_score(score1=11, score2=15)
    assert m2.winner_entry==entry2
    assert m2.completed==True

def test_match_is_complete(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    assert m.is_complete()==False
    m.record_score(4,5)
    assert m.is_complete()==True

def test_match_mark_complete(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    m.mark_complete()
    assert m.completed == True # Have as a feature despite score being 0-0 (injuries, etc.)

def test_set_winner(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    m.set_winner(entry1)
    assert m.winner_entry==entry1 # Have as a feature despite score being 0-0 (injuries, etc.)
    assert m.completed==True

def test_set_winner_invalid_entry(entry1, entry2, entry3):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    with pytest.raises(ValueError):
        m.set_winner(entry3)

def test_get_winner(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    assert m.get_winner()==None
    m.record_score(5,1)
    assert m.get_winner()==entry1

def test_get_winner_bye(entry1):
    m = DEMatch(id=1, tournament_id=1, entry1=entry1, round_index=0, match_index=0)
    assert m.get_winner() == entry1

def test_get_loser(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    assert m.get_loser() is None
    m.record_score(5,2)
    assert m.get_loser() == entry2

def test_get_loser_bye(entry1):
    m = DEMatch(id=1, tournament_id=1, entry1=entry1, round_index=0, match_index=0)
    assert m.get_loser() is None

# Test Poule Match class child
def test_poule_match_invalid_poule_id(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id='1')
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=True)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=0)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=-1)

def test_poule_match_type(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, poule_id=1)
    assert m.match_type() == "poule"

def test_poule_match_requires_two_fencers_one_present(entry1):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=None, poule_id=1)

def test_poule_match_requires_two_fencers_none_present():
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=None, entry2=None, poule_id=1)

# DE Match Tests
def test_de_match_invalid_round_index(entry1, entry2):
    with pytest.raises(TypeError):
        DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index='0', match_index=0)
    with pytest.raises(ValueError):
        DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=-1, match_index=0)

def test_de_match_invalid_match_index(entry1, entry2):
    with pytest.raises(TypeError):
        DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index='1')
    with pytest.raises(ValueError):
        DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index=-1)

def test_de_match_type(entry1, entry2):
    m = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, round_index=0, match_index=0)
    assert m.match_type() == 'DE'

def test_de_match_add_entry1(entry1):
    m = DEMatch(id=1, tournament_id=1, round_index=0, match_index=0)
    assert m.entry1 is None
    assert m.entry2 is None
    m.add_entry1(entry1)
    assert m.entry1 == entry1
    assert m.entry2 is None

def test_de_match_add_entry2(entry2):
    m = DEMatch(id=1, tournament_id=1, round_index=0, match_index=0)
    assert m.entry1 is None
    assert m.entry2 is None
    m.add_entry2(entry2)
    assert m.entry1 is None
    assert m.entry2 == entry2