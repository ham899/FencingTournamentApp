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

# Test Valid PouleMatch Creation
def test_valid_poule_match_creation_defaults(entry1, entry2):
    poule_match = PouleMatch(id=1, 
                             tournament_id=1, 
                             entry1=entry1, 
                             entry2=entry2)
    assert poule_match.id==1
    assert poule_match.tournament_id==1
    assert poule_match.entry1==entry1
    assert poule_match.entry2==entry2
    assert poule_match.score1==0
    assert poule_match.score2==0
    assert poule_match.score_to_win==5
    assert poule_match.completed==False
    assert poule_match.poule_id is None
    assert poule_match.winner_entry is None

def test_valid_poule_match_creation_no_defaults(entry1, entry2):
    poule_match = PouleMatch(id=1, 
                             tournament_id=1, 
                             entry1=entry1, 
                             entry2=entry2, 
                             score1=2,
                             score2=4,
                             score_to_win=10,
                             winner_entry=None,
                             poule_id=1)
    assert poule_match.id==1
    assert poule_match.tournament_id==1
    assert poule_match.entry1==entry1
    assert poule_match.entry2==entry2
    assert poule_match.score1==2
    assert poule_match.score2==4
    assert poule_match.score_to_win==10
    assert poule_match.completed==False
    assert poule_match.poule_id==1
    assert poule_match.winner_entry is None


def test_valid_de_match_creation_defaults(entry1, entry2):
    de_match = DEMatch(id=1, tournament_id=1)
    assert de_match.entry1 is None
    assert de_match.entry2 is None
    assert de_match.score1 == 0
    assert de_match.score2 == 0
    assert de_match.score_to_win == 15
    assert de_match.id==1
    assert de_match.tournament_id==1
    assert de_match.winner_entry is None
    assert de_match.completed==False
    assert de_match.round_index is None
    assert de_match.match_index is None

# Test invalid Match inputs through PouleMatch constructor
def test_poule_match_invalid_id(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id='one', tournament_id=1, entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        PouleMatch(id=0, tournament_id=1, entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        PouleMatch(id=-1, tournament_id=1, entry1=entry1, entry2=entry2)

def test_poule_match_invalid_tournament_id(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id='one', entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=0, entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=-1, entry1=entry1, entry2=entry2)

def test_poule_match_invalid_score_to_win(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win='five')
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=0)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=-5)

def test_poule_match_invalid_score(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=5, score1=-1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=5, score2=-1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=5, score1=5, score2=6)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=2, score1=3, score2=1)

def test_poule_match_invalid_equal_scores(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=5, score1=3, score2=3, winner_entry=entry1)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=5, score1=3, score2=3, completed=True)

def test_poule_match_valid_scores_entry1_wins(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=5, score2=3, completed=True)
    assert m.winner_entry == entry1
    assert m.completed == True

def test_poule_match_valid_scores_entry2_wins(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=2, score2=5, winner_entry=entry2)
    assert m.winner_entry == entry2
    assert m.completed == True

def test_poule_match_incomplete_match(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score_to_win=5, score1=2, score2=3)
    assert m.winner_entry is None
    assert m.completed == False

def test_poule_match_nonzero_score_with_none_entry(entry1):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=None, score_to_win=5, score1=1, score2=0)
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=None, entry2=entry1, score_to_win=5, score1=1, score2=0)

def test_poule_match_winner_entry_no_score(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, winner_entry=entry1)

def test_poule_match_winner_entry_equal_scores(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=2, score2=2, winner_entry=entry1)

    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=3, score2=3, winner_entry=entry2)

def test_poule_match_invalid_winner_entry_type(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, winner_entry='hello')
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, winner_entry=Fencer(id=1, display_name='B'))

def test_winner_entry_validation(entry1, entry2, entry3):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=5, score2=2, winner_entry=entry3)
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=3, score2=2, winner_entry=entry1)
    assert m1.winner_entry == entry1
    m2 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=3, score2=4, winner_entry=entry2)
    assert m2.winner_entry == entry2

def test_poule_match_invalid_completed_type(entry1, entry2):
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, completed='yes')
    with pytest.raises(TypeError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, completed=1)

def test_poule_match_make_complete_with_no_winner_entry(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=1, score2=5, completed=True)
    assert m1.winner_entry==entry2
    m2 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=3, score2=1, completed=True)
    assert m2.winner_entry==entry1

# Test Match methods through PouleMatch child
def test_poule_match_record_score_invalid_type(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    with pytest.raises(TypeError):
        m.record_score(score1='1', score2=5)
    with pytest.raises(TypeError):
        m.record_score(score1=1, score2='5')
    with pytest.raises(TypeError):
        m.record_score(score1='1', score2='5')

def test_match_record_score_invalid_value(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        m1.record_score(score1=-1, score2=5)
    with pytest.raises(ValueError):
        m1.record_score(score1=6, score2=3)

    m2 = DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2)
    with pytest.raises(ValueError):
        m2.record_score(score1=17, score2=5)
    with pytest.raises(ValueError):
        m2.record_score(score1=7, score2=-1)

def test_match_record_score_equal_scores(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        m1.record_score(score1=4, score2=4)
    m2 = DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2)
    with pytest.raises(ValueError):
        m2.record_score(score1=11, score2=11)

def test_match_record_score_entry1_wins(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    m1.record_score(score1=5, score2=3)
    assert m1.winner_entry==entry1
    assert m1.completed==True

    m2 = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    m2.record_score(score1=12, score2=5)
    assert m2.winner_entry==entry1
    assert m2.completed==True

def test_poule_match_record_score_entry2_wins(entry1, entry2):
    m1 = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    m1.record_score(score1=2, score2=4)
    assert m1.winner_entry==entry2
    assert m1.completed==True

    m2 = DEMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    m2.record_score(score1=11, score2=15)
    assert m2.winner_entry==entry2
    assert m2.completed==True

def test_poule_match_is_complete(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    assert m.is_complete() == False
    m.record_score(4,5)
    assert m.is_complete() == True

def test_mark_complete(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    m.mark_complete()
    assert m.completed == True

def test_set_winner(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    m.set_winner(entry1)
    assert m.winner_entry==entry1

def test_set_winner_invalid_entry(entry1, entry2, entry3):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    with pytest.raises(ValueError):
        m.set_winner(entry3)

def test_get_winner(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=5, score2=2)
    assert m.get_winner() == entry1

def test_get_winner_none(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    assert m.get_winner() is None

def test_get_winner_bye(entry1):
    m = DEMatch(id=1, tournament_id=1, entry1=entry1)
    assert m.get_winner() == entry1

def test_get_loser(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2, score1=5, score2=2)
    assert m.get_loser() == entry2

def test_get_loser_none(entry1, entry2):
    m = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    assert m.get_loser() is None

def test_get_loser_bye(entry1):
    m = DEMatch(id=1, tournament_id=1, entry1=entry1)
    assert m.get_loser() is None

# Test Poule Match class
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
    match = PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=entry2)
    assert match.match_type() == "poule"

def test_poule_match_requires_two_fencers_one_present(entry1):
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=entry1, entry2=None)

def test_poule_match_requires_two_fencers_none_present():
    with pytest.raises(ValueError):
        PouleMatch(id=1, tournament_id=1, entry1=None, entry2=None)

# DE Match Tests
def test_de_match_valid_inputs_no_defaults():
    pass

def test_de_match_valid_inputs_with_defaults():
    pass

def test_de_match_invalid_round_index(entry1, entry2):
    with pytest.raises(TypeError):
        DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2, round_index='0')
    with pytest.raises(ValueError):
        DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2, round_index=-1)

def test_de_match_invalid_match_index(entry1, entry2):
    with pytest.raises(TypeError):
        DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2, match_index='1')
    with pytest.raises(ValueError):
        DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2, match_index=-1)

def test_de_match_type(entry1, entry2):
    m = DEMatch(id=1, tournament_id=1, fencer1_entry=entry1, fencer2_entry=entry2)
    assert m.match_type() == 'DE'