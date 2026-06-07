import pytest

from fencer import Fencer
from tournament_entry import TournamentEntry
from match import Match, PouleMatch, DEMatch, calculate_max_match_index_within_round

def test_calculate_max_match_index_within_round_outputs():
    assert calculate_max_match_index_within_round(round_index=0, max_round_index=0) == 0
    assert calculate_max_match_index_within_round(round_index=0, max_round_index=1) == 1
    assert calculate_max_match_index_within_round(round_index=1, max_round_index=1) == 0
    assert calculate_max_match_index_within_round(round_index=0, max_round_index=2) == 3
    assert calculate_max_match_index_within_round(round_index=1, max_round_index=2) == 1
    assert calculate_max_match_index_within_round(round_index=2, max_round_index=2) == 0
    assert calculate_max_match_index_within_round(round_index=0, max_round_index=3) == 7
    assert calculate_max_match_index_within_round(round_index=1, max_round_index=3) == 3
    assert calculate_max_match_index_within_round(round_index=2, max_round_index=3) == 1
    assert calculate_max_match_index_within_round(round_index=3, max_round_index=3) == 0
    assert calculate_max_match_index_within_round(round_index=0, max_round_index=4) == 15
    assert calculate_max_match_index_within_round(round_index=1, max_round_index=4) == 7
    assert calculate_max_match_index_within_round(round_index=2, max_round_index=4) == 3
    assert calculate_max_match_index_within_round(round_index=3, max_round_index=4) == 1
    assert calculate_max_match_index_within_round(round_index=4, max_round_index=4) == 0

@pytest.mark.parametrize('invalid_round_index_type', [None,'0',0.0,False,[],{}])
def test_calculate_max_match_index_within_round_invalid_round_index_types(invalid_round_index_type):
    with pytest.raises(TypeError):
        calculate_max_match_index_within_round(round_index=invalid_round_index_type, max_round_index=0)

@pytest.mark.parametrize('invalid_max_round_index_type', [None,'0',0.0,False,[],{}])
def test_calculate_max_match_index_within_round_invalid_max_round_index_types(invalid_max_round_index_type):
    with pytest.raises(TypeError):
        calculate_max_match_index_within_round(round_index=0, max_round_index=invalid_max_round_index_type)

@pytest.mark.parametrize('invalid_round_index_negative', [-1000,-100,-10,-1])
def test_calculate_max_match_index_within_round_invalid_round_index_negatives(invalid_round_index_negative):
    with pytest.raises(ValueError):
        calculate_max_match_index_within_round(round_index=invalid_round_index_negative, max_round_index=0)

@pytest.mark.parametrize('invalid_max_round_index_negative', [-1000,-100,-10,-1])
def test_calculate_max_match_index_within_round_invalid_max_round_index_negatives(invalid_max_round_index_negative):
    with pytest.raises(ValueError):
        calculate_max_match_index_within_round(round_index=0, max_round_index=invalid_max_round_index_negative)

def test_calculate_max_match_index_within_round_invalid_round_index_greater_than_maximum():
    with pytest.raises(ValueError):
        calculate_max_match_index_within_round(round_index=10,max_round_index=0)
    with pytest.raises(ValueError):
        calculate_max_match_index_within_round(round_index=4,max_round_index=1)
    with pytest.raises(ValueError):
        calculate_max_match_index_within_round(round_index=3,max_round_index=2)

### Constants ###
VALID_FENCER_ID1 = 1
VALID_FENCER_ID2 = 2
VALID_FENCER_ID3 = 3
VALID_DISPLAY_NAME1 = 'Bob'
VALID_DISPLAY_NAME2 = 'Bill'
VALID_DISPLAY_NAME3 = 'Ben'
VALID_ENTRY_ID1 = 1
VALID_ENTRY_ID2 = 2
VALID_ENTRY_ID3 = 3
TOURNY_ID = 1
POULE_ID = 1
VALID_MATCH_ID = 1
MAX_POULE_MATCH_INDEX = 20 # Assume standard poule size of 7 - indices 0 to 20
MAX_ROUND_INDEX = 4 # Assume max of 16 fencers in DE - rounds 0 to 4

@pytest.fixture
def entry1():
    fencer1 = Fencer(id=VALID_FENCER_ID1, display_name=VALID_DISPLAY_NAME1)
    return TournamentEntry(id=VALID_ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer1)

@pytest.fixture
def entry2():
    fencer2 = Fencer(id=VALID_FENCER_ID2, display_name=VALID_DISPLAY_NAME2)
    return TournamentEntry(id=VALID_ENTRY_ID2, tournament_id=TOURNY_ID, fencer=fencer2)

@pytest.fixture
def entry3():
    fencer3 = Fencer(id=VALID_FENCER_ID3, display_name=VALID_DISPLAY_NAME3)
    return TournamentEntry(id=VALID_ENTRY_ID3, tournament_id=TOURNY_ID, fencer=fencer3)

@pytest.fixture
def standard_poule_match(entry1, entry2):
    return PouleMatch(id=VALID_MATCH_ID,
                      tournament_id=TOURNY_ID,
                      entry1=entry1,
                      entry2=entry2,
                      poule_id=POULE_ID,
                      match_index=0,
                      max_match_index=MAX_POULE_MATCH_INDEX)

@pytest.fixture
def standard_de_match(entry1, entry2):
    return DEMatch(id=VALID_MATCH_ID,
                   tournament_id=TOURNY_ID,
                   entry1=entry1,
                   entry2=entry2,
                   round_index=0,
                   match_index=0,
                   max_round_index=MAX_ROUND_INDEX)

@pytest.fixture
def empty_de_match(entry1, entry2):
    return DEMatch(id=VALID_MATCH_ID,
                   tournament_id=TOURNY_ID,
                   round_index=0,
                   match_index=0,
                   max_round_index=MAX_ROUND_INDEX)

# Test ABC Match class first
def test_cannot_create_abstract_match(entry1, entry2):
    with pytest.raises(TypeError):
        Match(id=VALID_MATCH_ID, tournament_id=TOURNY_ID, score_to_win=5)
    with pytest.raises(TypeError):
        Match(id=VALID_MATCH_ID, tournament_id=TOURNY_ID, score_to_win=15, entry1=entry1, entry2=entry2)

# Test valid PouleMatch creation
def test_valid_poule_match_creation_defaults(entry1, entry2):
    poule_match = PouleMatch(id=VALID_MATCH_ID, 
                             tournament_id=TOURNY_ID, 
                             entry1=entry1, 
                             entry2=entry2, 
                             poule_id=POULE_ID, 
                             match_index=0, 
                             max_match_index=MAX_POULE_MATCH_INDEX)
    assert poule_match.id==VALID_MATCH_ID
    assert poule_match.tournament_id==TOURNY_ID
    assert poule_match.entry1==entry1
    assert poule_match.entry2==entry2
    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert poule_match.winner is None
    assert poule_match.completed==False
    assert poule_match.score_to_win==5
    assert poule_match.poule_id==POULE_ID
    assert poule_match.match_index==0

    with pytest.raises(AttributeError):
        poule_match.max_match_index

def test_valid_poule_match_creation_no_defaults(entry1, entry2):
    poule_match = PouleMatch(id=VALID_MATCH_ID, 
                             tournament_id=TOURNY_ID, 
                             entry1=entry1, 
                             entry2=entry2, 
                             score_to_win=8, 
                             poule_id=POULE_ID, 
                             match_index=0, 
                             max_match_index=MAX_POULE_MATCH_INDEX)
    assert poule_match.id==VALID_MATCH_ID
    assert poule_match.tournament_id==TOURNY_ID
    assert poule_match.entry1==entry1
    assert poule_match.entry2==entry2
    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert poule_match.winner is None
    assert poule_match.completed==False
    assert poule_match.score_to_win==8
    assert poule_match.poule_id==POULE_ID
    assert poule_match.match_index==0

    with pytest.raises(AttributeError):
        poule_match.max_match_index

# Test valid DEMatch creation
def test_valid_de_match_creation_defaults():
    de_match = DEMatch(id=VALID_MATCH_ID, 
                       tournament_id=TOURNY_ID, 
                       round_index=0, 
                       match_index=0, 
                       max_round_index=MAX_ROUND_INDEX)
    assert de_match.id==VALID_MATCH_ID
    assert de_match.tournament_id==TOURNY_ID
    assert de_match.entry1 is None
    assert de_match.entry2 is None
    assert de_match.score1 is None
    assert de_match.score2 is None
    assert de_match.winner is None
    assert de_match.completed==False
    assert de_match.score_to_win == 15
    assert de_match.round_index==0
    assert de_match.match_index==0

    with pytest.raises(AttributeError):
        de_match.max_round_index
    with pytest.raises(AttributeError):
        de_match.max_match_index

def test_valid_de_match_creation_no_defaults(entry1, entry2):
    de_match = DEMatch(id=VALID_MATCH_ID, 
                       tournament_id=TOURNY_ID, 
                       entry1=entry1, 
                       entry2=entry2, 
                       score_to_win=12, 
                       round_index=1, 
                       match_index=1,
                       max_round_index=MAX_ROUND_INDEX)
    assert de_match.id==VALID_MATCH_ID
    assert de_match.tournament_id==TOURNY_ID
    assert de_match.entry1==entry1
    assert de_match.entry2==entry2
    assert de_match.score1 is None
    assert de_match.score2 is None
    assert de_match.winner is None
    assert de_match.completed==False
    assert de_match.score_to_win==12
    assert de_match.round_index==1
    assert de_match.match_index==1

    with pytest.raises(AttributeError):
        de_match.max_round_index
    with pytest.raises(AttributeError):
        de_match.max_match_index

# Test invalid Match inputs through PouleMatch constructor
@pytest.mark.parametrize('invalid_id_types', [None, 'one', 1.0, True, [], {}])
def test_match_creation_invalid_id(entry1, entry2, invalid_id_types):
    with pytest.raises(TypeError):
        PouleMatch(id=invalid_id_types, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_match_creation_invalid_id_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=0, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=POULE_ID,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)

@pytest.mark.parametrize('invalid_id_negatives', [-1, -100, -999])
def test_match_creation_invalid_id_negative(entry1, entry2, invalid_id_negatives):
    with pytest.raises(ValueError):
        PouleMatch(id=invalid_id_negatives, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=POULE_ID,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)

@pytest.mark.parametrize('invalid_tournament_id_types', [None, 1.0, True, [], {}])
def test_match_creation_invalid_tournament_id(entry1, entry2, invalid_tournament_id_types):
    with pytest.raises(TypeError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=invalid_tournament_id_types, 
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=POULE_ID,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_match_creation_invalid_tournament_id_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=0,
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_match_creation_invalid_tournament_id_negative(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=-1, 
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)

@pytest.mark.parametrize('invalid_score_to_win_types', [None, 1.0, True, [], {}])
def test_match_creation_invalid_score_to_win_types(entry1, entry2, invalid_score_to_win_types):
    with pytest.raises(TypeError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   score_to_win=invalid_score_to_win_types, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_match_creation_invalid_score_to_win_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   score_to_win=0, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_match_creation_invalid_score_to_win_negative(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   score_to_win=-5, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)
        
@pytest.mark.parametrize('invalid_entry_types', ['John', 1.0, True, [], {}])
def test_match_creation_invalid_entry_types(entry1, entry2, invalid_entry_types):
    with pytest.raises(TypeError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=invalid_entry_types, 
                   entry2=invalid_entry_types, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)
    with pytest.raises(TypeError):
        DEMatch(id=VALID_MATCH_ID, 
                tournament_id=TOURNY_ID,
                entry1=invalid_entry_types,
                entry2=entry2,
                round_index=0,
                match_index=0,
                max_round_index=MAX_ROUND_INDEX)
    with pytest.raises(TypeError):
        DEMatch(id=VALID_MATCH_ID, 
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=invalid_entry_types,
                round_index=0,
                match_index=0,
                max_round_index=MAX_ROUND_INDEX)

# Test Match methods
@pytest.mark.parametrize('invalid_score_types', ['1', 1.0, True, [], {}]) # Record a None score is allowed for this method to reset scores, etc.
def test_match_record_score_invalid_type(standard_poule_match, standard_de_match, invalid_score_types):
    with pytest.raises(TypeError):
        standard_poule_match.record_score(score1=invalid_score_types, score2=5)
    with pytest.raises(TypeError):
        standard_poule_match.record_score(score1=1, score2=invalid_score_types)
    with pytest.raises(TypeError):
        standard_poule_match.record_score(score1=invalid_score_types, score2=invalid_score_types)
    with pytest.raises(TypeError):
        standard_de_match.record_score(score1=invalid_score_types, score2=15)
    with pytest.raises(TypeError):
        standard_de_match.record_score(score1=10, score2=invalid_score_types)
    with pytest.raises(TypeError):
        standard_de_match.record_score(score1=invalid_score_types, score2=invalid_score_types)

@pytest.mark.parametrize('invalid_poule_score_values', [-10, -1, 6, 10]) # Assumes default score to win (5)
def test_poule_match_record_score_invalid_value(standard_poule_match, invalid_poule_score_values):
    with pytest.raises(ValueError):
        standard_poule_match.record_score(score1=invalid_poule_score_values, score2=5)
    with pytest.raises(ValueError):
        standard_poule_match.record_score(score1=3, score2=invalid_poule_score_values)
    with pytest.raises(ValueError):
        standard_poule_match.record_score(score1=invalid_poule_score_values, score2=invalid_poule_score_values)

@pytest.mark.parametrize('invalid_de_score_values', [-100, -1, 16, 100]) # Assumes default score to win (15)
def test_de_match_record_score_invalid_value(standard_de_match, invalid_de_score_values):
    with pytest.raises(ValueError):
        standard_de_match.record_score(score1=invalid_de_score_values, score2=5)
    with pytest.raises(ValueError):
        standard_de_match.record_score(score1=15, score2=invalid_de_score_values)
    with pytest.raises(ValueError):
        standard_de_match.record_score(score1=invalid_de_score_values, score2=invalid_de_score_values)

def test_match_record_score_equal_scores(standard_poule_match, standard_de_match):
    with pytest.raises(ValueError):
        standard_poule_match.record_score(score1=0, score2=0)
    with pytest.raises(ValueError):
        standard_poule_match.record_score(score1=4, score2=4)
    with pytest.raises(ValueError):
        standard_poule_match.record_score(score1=5, score2=5)
    with pytest.raises(ValueError):
        standard_de_match.record_score(score1=0, score2=0)
    with pytest.raises(ValueError):
        standard_de_match.record_score(score1=11, score2=11)
    with pytest.raises(ValueError):
        standard_de_match.record_score(score1=15, score2=15)

def test_match_record_score_entry1_wins(standard_poule_match, standard_de_match):
    standard_poule_match.record_score(score1=5, score2=3)
    assert standard_poule_match.winner==standard_poule_match.entry1
    assert standard_poule_match.completed==True

    standard_de_match.record_score(score1=12, score2=5)
    assert standard_de_match.winner==standard_de_match.entry1
    assert standard_de_match.completed==True

def test_match_record_score_entry2_wins(standard_poule_match, standard_de_match):
    standard_poule_match.record_score(score1=2, score2=4)
    assert standard_poule_match.winner==standard_poule_match.entry2
    assert standard_poule_match.completed==True

    standard_de_match.record_score(score1=11, score2=15)
    assert standard_de_match.winner==standard_de_match.entry2
    assert standard_de_match.completed==True

def test_match_is_complete(standard_poule_match, standard_de_match):
    assert standard_poule_match.is_complete()==False
    standard_poule_match.record_score(4,5)
    assert standard_poule_match.is_complete()==True

    assert standard_de_match.is_complete()==False
    standard_de_match.record_score(15,14)
    assert standard_de_match.is_complete()==True

def test_match_mark_complete(standard_poule_match, standard_de_match):
    assert standard_poule_match.completed==False
    standard_poule_match.mark_complete()
    assert standard_poule_match.completed==True # Have as a feature despite there being no score (injuries, etc.)

    assert standard_de_match.completed==False
    standard_de_match.mark_complete()
    assert standard_de_match.completed==True

def test_match_set_winner(entry1, entry2, standard_poule_match, standard_de_match):
    assert standard_poule_match.winner is None
    assert standard_poule_match.completed==False
    standard_poule_match.set_winner(entry1)
    assert standard_poule_match.winner==entry1 # Have as a feature despite there being no score (injuries, etc.)
    assert standard_poule_match.completed==True

    assert standard_de_match.winner is None
    assert standard_de_match.completed==False
    standard_de_match.set_winner(entry2)
    assert standard_de_match.winner==entry2
    assert standard_de_match.completed==True

def test_match_set_winner_invalid_entry(entry3, standard_poule_match, standard_de_match):
    with pytest.raises(ValueError):
        standard_poule_match.set_winner(entry3)
    with pytest.raises(ValueError):
        standard_de_match.set_winner(entry3)

def test_match_get_loser(standard_poule_match, standard_de_match):
    assert standard_poule_match.get_loser() is None
    standard_poule_match.record_score(5,2)
    assert standard_poule_match.get_loser() == standard_poule_match.entry2
    
    assert standard_de_match.get_loser() is None
    standard_de_match.record_score(12,15)
    assert standard_de_match.get_loser() == standard_de_match.entry1

def test_de_match_get_loser_bye(entry1, entry2):
    bye_match1 = DEMatch(id=VALID_MATCH_ID, 
                         tournament_id=TOURNY_ID, 
                         entry1=entry1, 
                         round_index=0, 
                         match_index=0,
                         max_round_index=MAX_ROUND_INDEX)
    assert bye_match1.get_loser() is None
    assert bye_match1.winner == entry1

    bye_match2 = DEMatch(id=VALID_MATCH_ID, 
                         tournament_id=TOURNY_ID, 
                         entry2=entry2, 
                         round_index=1, 
                         match_index=1, 
                         max_round_index=MAX_ROUND_INDEX)
    assert bye_match2.get_loser() is None
    assert bye_match2.winner == entry2

# Test Poule Match class child
@pytest.mark.parametrize('invalid_poule_id_types', [None, 1.0, True, '1', [], {}])
def test_poule_match_invalid_poule_id_types(entry1, entry2, invalid_poule_id_types):
    with pytest.raises(TypeError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1,
                   entry2=entry2,
                   poule_id=invalid_poule_id_types,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_poule_match_invalid_poule_id_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=entry2, 
                   poule_id=0,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)

@pytest.mark.parametrize('invalid_poule_id_negatives', [-100, -10, -1])
def test_poule_match_invalid_poule_id_negative(entry1, entry2, invalid_poule_id_negatives):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID,
                   tournament_id=TOURNY_ID,
                   entry1=entry1,
                   entry2=entry2,
                   poule_id=invalid_poule_id_negatives,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_poule_match_type(standard_poule_match):
    assert standard_poule_match.match_type() == "poule"

def test_poule_match_requires_two_fencers_when_only_one_present(entry1):
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=None, 
                   poule_id=POULE_ID, 
                   match_index=0, 
                   max_match_index=MAX_POULE_MATCH_INDEX)

def test_poule_match_requires_two_fencers_when_none_present():
    # Test explicit case
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   entry1=None, 
                   entry2=None, 
                   poule_id=POULE_ID,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)
    # Test implicit case
    with pytest.raises(ValueError):
        PouleMatch(id=VALID_MATCH_ID, 
                   tournament_id=TOURNY_ID, 
                   poule_id=POULE_ID,
                   match_index=0,
                   max_match_index=MAX_POULE_MATCH_INDEX)        

# DE Match Tests
@pytest.mark.parametrize('invalid_round_index_type', [None, 0.0, '0', False, [], {}])
def test_de_match_invalid_round_index_type(entry1, entry2, invalid_round_index_type):
    with pytest.raises(TypeError):
        DEMatch(id=VALID_MATCH_ID, 
                tournament_id=TOURNY_ID, 
                entry1=entry1, 
                entry2=entry2, 
                round_index=invalid_round_index_type, 
                match_index=0,
                max_round_index=MAX_ROUND_INDEX)
    with pytest.raises(TypeError):
        DEMatch(id=VALID_MATCH_ID,
                tournament_id=TOURNY_ID,
                round_index=invalid_round_index_type,
                match_index=0,
                max_round_index=MAX_ROUND_INDEX)

@pytest.mark.parametrize('out_of_bounds_round_index', [-100,-10,-1,MAX_ROUND_INDEX+1,2*MAX_ROUND_INDEX])
def test_de_match_invalid_round_index_out_of_bounds(entry1, entry2, out_of_bounds_round_index):
    with pytest.raises(ValueError):
        DEMatch(id=VALID_MATCH_ID,
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=entry2,
                round_index=out_of_bounds_round_index,
                match_index=0,
                max_round_index=MAX_ROUND_INDEX)

@pytest.mark.parametrize('invalid_match_index_types', [None, '0', 0.0, False, [], {}])
def test_de_match_invalid_match_index(entry1, entry2, invalid_match_index_types):
    with pytest.raises(TypeError):
        DEMatch(id=VALID_MATCH_ID,
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=entry2,
                round_index=0,
                match_index=invalid_match_index_types)

@pytest.mark.parametrize('invalid_match_index_negatives', [-100,-10,-1])
def test_de_match_invalid_match_index_negatives(entry1, entry2, invalid_match_index_negatives):
    with pytest.raises(ValueError):
        DEMatch(id=VALID_MATCH_ID,
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=entry2,
                round_index=0,
                match_index=invalid_match_index_negatives,
                max_round_index=MAX_ROUND_INDEX)

def test_de_match_type(standard_de_match):
    assert standard_de_match.match_type() == 'DE'

def test_de_match_add_entry(entry1, entry2):
    empty_de_match = DEMatch(id=VALID_MATCH_ID, 
                tournament_id=TOURNY_ID, 
                round_index=0, 
                match_index=0,
                max_round_index=MAX_ROUND_INDEX)
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 is None
    empty_de_match.add_entry(entry=entry1, location=0)
    empty_de_match.add_entry(entry=entry2, location=1)
    assert empty_de_match.entry1 == entry1
    assert empty_de_match.entry2 == entry2

@pytest.mark.parametrize('invalid_entry_type', [None, 'entry1', 0, 0.0, False, [], {}])
def test_de_match_add_entry_invalid_entry_type(empty_de_match, invalid_entry_type):
    with pytest.raises(TypeError):
        empty_de_match.add_entry(entry=invalid_entry_type, location=0)

def test_de_match_add_entry_invalid_entry_value(empty_de_match):
    pass

@pytest.mark.parametrize('invalid_location_type', [None, 'top', 0.0, False, [], {}])
def test_de_match_add_entry_invalid_location_type(entry1, empty_de_match, invalid_location_type):
    with pytest.raises(TypeError):
        empty_de_match.add_entry(entry=entry1, location=invalid_location_type)

@pytest.mark.parametrize('invalid_location_value', [-100,-2,2,100])
def test_de_match_add_entry_invalid_location_value(entry1, empty_de_match, invalid_location_value):
    with pytest.raises(ValueError):
        empty_de_match.add_entry(entry=entry1, location=invalid_location_value)

def test_de_match_add_entry1(entry1, empty_de_match):
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 is None
    empty_de_match.add_entry1(entry1)
    assert empty_de_match.entry1 == entry1
    assert empty_de_match.entry2 is None

@pytest.mark.parametrize('invalid_entry_type', [None, 'entry1', 0, 0.0, False, [], {}])
def test_de_match_add_entry1_invalid_entry_type(empty_de_match, invalid_entry_type):
    with pytest.raises(TypeError):
        empty_de_match.add_entry1(invalid_entry_type)

def test_de_match_add_entry2(entry2, empty_de_match):
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 is None
    empty_de_match.add_entry2(entry2)
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 == entry2

@pytest.mark.parametrize('invalid_entry_type', [None, 'entry1', 0, 0.0, False, [], {}])
def test_de_match_add_entry2_invalid(empty_de_match, invalid_entry_type):
    with pytest.raises(TypeError):
        empty_de_match.add_entry2(invalid_entry_type)