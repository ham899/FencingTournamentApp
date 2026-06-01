from de_bracket import DEBracket
from tournament_entry import TournamentEntry
from fencer import Fencer

import pytest

### Constants ###
TOURNY_ID = 1
BRACKET_ID = 1

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
        TournamentEntry(id=8, tournament_id=TOURNY_ID, fencer=Fencer(id=8, display_name='Marco'), de_seed=8),
        TournamentEntry(id=9, tournament_id=TOURNY_ID, fencer=Fencer(id=9, display_name='Henry'), de_seed=9),
        TournamentEntry(id=10, tournament_id=TOURNY_ID, fencer=Fencer(id=10, display_name='Zoe'), de_seed=10),
        TournamentEntry(id=11, tournament_id=TOURNY_ID, fencer=Fencer(id=11, display_name='Dennis'), de_seed=11),
        TournamentEntry(id=12, tournament_id=TOURNY_ID, fencer=Fencer(id=12, display_name='Steven'), de_seed=12),
        TournamentEntry(id=13, tournament_id=TOURNY_ID, fencer=Fencer(id=13, display_name='Alex'), de_seed=13),
        TournamentEntry(id=14, tournament_id=TOURNY_ID, fencer=Fencer(id=14, display_name='Koan'), de_seed=14),
        TournamentEntry(id=15, tournament_id=TOURNY_ID, fencer=Fencer(id=15, display_name='Irene'), de_seed=15)
    ]

@pytest.fixture
def bracket(entries):
    return DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=entries)

@pytest.fixture
def completed_bracket(bracket):
    # Record top 16 results
    bracket.record_match_result(round_index=0, match_index=1, score1=15, score2=8)
    bracket.record_match_result(round_index=0, match_index=2, score1=15, score2=12)
    bracket.record_match_result(round_index=0, match_index=3, score1=8, score2=15)
    bracket.record_match_result(round_index=0, match_index=4, score1=15, score2=7)
    bracket.record_match_result(round_index=0, match_index=5, score1=5, score2=15)
    bracket.record_match_result(round_index=0, match_index=6, score1=13, score2=15)
    bracket.record_match_result(round_index=0, match_index=7, score1=1, score2=15)

    # Record top 8 results
    bracket.record_match_result(round_index=1, match_index=0, score1=15, score2=5)
    bracket.record_match_result(round_index=1, match_index=1, score1=14, score2=15)
    bracket.record_match_result(round_index=1, match_index=2, score1=15, score2=9)
    bracket.record_match_result(round_index=1, match_index=3, score1=15, score2=11)

    # Record semi final results
    bracket.record_match_result(round_index=2, match_index=0, score1=15, score2=10)
    bracket.record_match_result(round_index=2, match_index=1, score1=12, score2=15)

    # Record final result
    bracket.record_match_result(round_index=3, match_index=0, score1=13, score2=15)

    return bracket

def test_de_bracket_creation(entries):
    bracket = DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=entries)
    
    assert bracket.id == BRACKET_ID
    assert bracket.tournament_id == TOURNY_ID
    assert bracket.entries == entries
    assert bracket.size == 16
    assert bracket.rounds is not None
    assert len(bracket.rounds) == 4
    assert bracket.current_round_index == 0

    # Validate the matches in the initial round
    matches = bracket.rounds[0].matches

    assert matches[0].entry1 == entries[0]
    assert matches[0].entry2 is None
    assert matches[0].is_bye()
    assert matches[0].is_complete()

    assert bracket.rounds[1].get_match(0).entry1 == entries[0]
    assert bracket.rounds[1].get_match(0).entry2 is None
    
    assert matches[1].entry1 == entries[8]
    assert matches[1].entry2 == entries[7]
    assert not matches[1].is_complete()
    
    assert matches[2].entry1 == entries[4]
    assert matches[2].entry2 == entries[11]
    assert not matches[2].is_complete()
    
    assert matches[3].entry1 == entries[12]
    assert matches[3].entry2 == entries[3]
    assert not matches[3].is_complete()
    
    assert matches[4].entry1 == entries[2]
    assert matches[4].entry2 == entries[13]
    assert not matches[4].is_complete()
    
    assert matches[5].entry1 == entries[10]
    assert matches[5].entry2 == entries[5]
    assert not matches[5].is_complete()
    
    assert matches[6].entry1 == entries[6]
    assert matches[6].entry2 == entries[9]
    assert not matches[6].is_complete()
    
    assert matches[7].entry1 == entries[14]
    assert matches[7].entry2 == entries[1]
    assert not matches[7].is_complete()

def test_de_bracket_creation_invalid_types(entries):
    with pytest.raises(TypeError):
        DEBracket(id=True, tournament_id=TOURNY_ID, entries=entries)

    with pytest.raises(TypeError):
        DEBracket(id=BRACKET_ID, tournament_id=[], entries=entries)

    with pytest.raises(TypeError):
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries='entries')
    
    with pytest.raises(TypeError):
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[TournamentEntry(id=100, tournament_id=TOURNY_ID, fencer=Fencer(id=100, display_name='Sean'), de_seed=1), 'second entry'])

    with pytest.raises(TypeError):
        entry1 = TournamentEntry(id=100, tournament_id=TOURNY_ID, fencer=Fencer(id=100, display_name='Sean'), de_seed=1)
        entry2 = TournamentEntry(id=101, tournament_id=TOURNY_ID, fencer=Fencer(id=101, display_name='Dallas'), de_seed=2)
        entry2.de_seed = 'bad seed type'
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[entry1, entry2])

def test_de_bracket_creation_invalid_values(entries):
    with pytest.raises(ValueError):
        DEBracket(id=0, tournament_id=TOURNY_ID, entries=entries)

    with pytest.raises(ValueError):
        DEBracket(id=-1, tournament_id=TOURNY_ID, entries=entries)

    with pytest.raises(ValueError):
        DEBracket(id=BRACKET_ID, tournament_id=0, entries=entries)

    with pytest.raises(ValueError):
        DEBracket(id=BRACKET_ID, tournament_id=-1, entries=entries)

    with pytest.raises(ValueError):
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[])
    
    with pytest.raises(ValueError):
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[TournamentEntry(id=101, tournament_id=TOURNY_ID, fencer=Fencer(id=101, display_name='Dallas'), de_seed=1)])

    with pytest.raises(ValueError):
        entry1 = TournamentEntry(id=100, tournament_id=TOURNY_ID, fencer=Fencer(id=100, display_name='Sean'), de_seed=0)
        entry2 = TournamentEntry(id=101, tournament_id=TOURNY_ID, fencer=Fencer(id=101, display_name='Dallas'), de_seed=1)
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[entry1, entry2])

    with pytest.raises(ValueError):
        entry1 = TournamentEntry(id=100, tournament_id=TOURNY_ID, fencer=Fencer(id=100, display_name='Sean'), de_seed=1)
        entry2 = TournamentEntry(id=101, tournament_id=TOURNY_ID, fencer=Fencer(id=101, display_name='Dallas'), de_seed=3)
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[entry1, entry2])

    with pytest.raises(ValueError):
        entry1 = TournamentEntry(id=100, tournament_id=TOURNY_ID, fencer=Fencer(id=100, display_name='Sean'), de_seed=2)
        entry2 = TournamentEntry(id=101, tournament_id=TOURNY_ID, fencer=Fencer(id=101, display_name='Dallas'), de_seed=1)
        DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=[entry1, entry2])


def test_de_bracket_record_match_result(bracket):
    # Record top 16 results
    assert bracket.current_round_index == 0
    assert bracket.get_current_round_size() == 16
    assert bracket.get_current_round_name() == 'Round of 16'

    bracket.record_match_result(round_index=0, match_index=1, score1=15, score2=8)
    bracket.record_match_result(round_index=0, match_index=2, score1=15, score2=12)
    bracket.record_match_result(round_index=0, match_index=3, score1=8, score2=15)
    bracket.record_match_result(round_index=0, match_index=4, score1=15, score2=7)
    bracket.record_match_result(round_index=0, match_index=5, score1=5, score2=15)
    bracket.record_match_result(round_index=0, match_index=6, score1=13, score2=15)
    bracket.record_match_result(round_index=0, match_index=7, score1=1, score2=15)

    # Record top 8 results
    assert bracket.current_round_index == 1
    assert bracket.get_current_round_size() == 8
    assert bracket.get_current_round_name() == 'Quarter-Final'

    bracket.record_match_result(round_index=1, match_index=0, score1=15, score2=5)
    bracket.record_match_result(round_index=1, match_index=1, score1=14, score2=15)
    bracket.record_match_result(round_index=1, match_index=2, score1=15, score2=9)
    bracket.record_match_result(round_index=1, match_index=3, score1=15, score2=11)

    # Record semi final results
    assert bracket.current_round_index == 2
    assert bracket.get_current_round_size() == 4
    assert bracket.get_current_round_name() == 'Semi-Final'
    
    bracket.record_match_result(round_index=2, match_index=0, score1=15, score2=10)
    bracket.record_match_result(round_index=2, match_index=1, score1=12, score2=15)

    # Record final result
    assert bracket.current_round_index == 3
    assert bracket.get_current_round_size() == 2
    assert bracket.get_current_round_name() == 'Final'

    bracket.record_match_result(round_index=3, match_index=0, score1=13, score2=15)

    # Validate all results
    assert bracket.get_match(0,0).is_bye()
    assert bracket.get_match(0,0).winner.display_name() == 'Bob'
    assert bracket.get_match(0,0).is_complete()

    assert bracket.get_match(0,1).winner.display_name() == 'Henry'
    assert bracket.get_match(0,1).score1 == 15
    assert bracket.get_match(0,1).score2 == 8
    assert bracket.get_match(0,1).is_complete()

    assert bracket.get_match(0,2).winner.display_name() == 'Allen'
    assert bracket.get_match(0,2).score1 == 15
    assert bracket.get_match(0,2).score2 == 12
    assert bracket.get_match(0,2).is_complete()

    assert bracket.get_match(0,3).winner.display_name() == 'Jill'
    assert bracket.get_match(0,3).score1 == 8
    assert bracket.get_match(0,3).score2 == 15
    assert bracket.get_match(0,3).is_complete()

    assert bracket.get_match(0,4).winner.display_name() == 'John'
    assert bracket.get_match(0,4).score1 == 15
    assert bracket.get_match(0,4).score2 == 7
    assert bracket.get_match(0,4).is_complete()

    assert bracket.get_match(0,5).winner.display_name() == 'Alison'
    assert bracket.get_match(0,5).score1 == 5
    assert bracket.get_match(0,5).score2 == 15
    assert bracket.get_match(0,5).is_complete()

    assert bracket.get_match(0,6).winner.display_name() == 'Zoe'
    assert bracket.get_match(0,6).score1 == 13
    assert bracket.get_match(0,6).score2 == 15
    assert bracket.get_match(0,6).is_complete()

    assert bracket.get_match(0,7).winner.display_name() == 'Jane'
    assert bracket.get_match(0,7).score1 == 1
    assert bracket.get_match(0,7).score2 == 15
    assert bracket.get_match(0,7).is_complete()

    assert bracket.get_match(1,0).winner.display_name() == 'Bob'
    assert bracket.get_match(1,0).score1 == 15
    assert bracket.get_match(1,0).score2 == 5
    assert bracket.get_match(1,0).is_complete()

    assert bracket.get_match(1,1).winner.display_name() == 'Jill'
    assert bracket.get_match(1,1).score1 == 14
    assert bracket.get_match(1,1).score2 == 15
    assert bracket.get_match(1,1).is_complete()

    assert bracket.get_match(1,2).winner.display_name() == 'John'
    assert bracket.get_match(1,2).score1 == 15
    assert bracket.get_match(1,2).score2 == 9
    assert bracket.get_match(1,2).is_complete()

    assert bracket.get_match(1,3).winner.display_name() == 'Zoe'
    assert bracket.get_match(1,3).score1 == 15
    assert bracket.get_match(1,3).score2 == 11
    assert bracket.get_match(1,3).is_complete()

    assert bracket.get_match(2,0).winner.display_name() == 'Bob'
    assert bracket.get_match(2,0).score1 == 15
    assert bracket.get_match(2,0).score2 == 10
    assert bracket.get_match(2,0).is_complete()

    assert bracket.get_match(2,1).winner.display_name() == 'Zoe'
    assert bracket.get_match(2,1).score1 == 12
    assert bracket.get_match(2,1).score2 == 15
    assert bracket.get_match(2,1).is_complete()

    assert bracket.get_match(3,0).winner.display_name() == 'Zoe'
    assert bracket.get_match(3,0).score1 == 13
    assert bracket.get_match(3,0).score2 == 15
    assert bracket.get_match(3,0).is_complete()

def test_de_bracket_record_match_result_invalid_types(bracket):
    with pytest.raises(TypeError):
        bracket.record_match_result(round_index='0', match_index=0, score1=15, score2=8)
    with pytest.raises(TypeError):
        bracket.record_match_result(round_index=0, match_index=[0], score1=15, score2=8)
    with pytest.raises(TypeError):
        bracket.record_match_result(round_index=0, match_index=0, score1=True, score2=8)
    with pytest.raises(TypeError):
        bracket.record_match_result(round_index=0, match_index=0, score1=15, score2='8')

def test_de_bracket_record_match_result_invalid_values(bracket):
    # Invalid index values
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=-1, match_index=0, score1=15, score2=8)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=100, match_index=0, score1=15, score2=8)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=-1, score1=15, score2=8)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=100, score1=15, score2=8)
    
    # Invalid score values
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=-1, score2=8)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=15, score2=-1)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=16, score2=8)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=15, score2=16)
    
    # Testing tied scores
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=15, score2=15)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=0, score2=0)
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=1, score1=8, score2=8)
    
    # Can't record a result for a BYE match
    with pytest.raises(ValueError):
        bracket.record_match_result(round_index=0, match_index=0, score1=15, score2=10)

def test_de_bracket_is_complete(entries, completed_bracket):
    incomplete_bracket = DEBracket(id=BRACKET_ID, tournament_id=TOURNY_ID, entries=entries)
    
    assert not incomplete_bracket.is_complete()
    assert completed_bracket.is_complete()

def test_de_bracket_get_winner(entries, completed_bracket):
    assert completed_bracket.get_winner() == entries[9]
    assert completed_bracket.get_winner().display_name() == 'Zoe'

def test_de_bracket_get_round_losers(entries, completed_bracket):
    assert completed_bracket.get_round_losers(round_index=0) == [entries[7], entries[11], entries[12], entries[13], entries[10], entries[6], entries[14]]
    assert completed_bracket.get_round_losers(round_index=1) == [entries[8], entries[4], entries[5], entries[1]]
    assert completed_bracket.get_round_losers(round_index=2) == [entries[3], entries[2]]
    assert completed_bracket.get_round_losers(round_index=3) == [entries[0]]

def test_de_bracket_get_round_losers_invalid(completed_bracket):
    with pytest.raises(TypeError):
        completed_bracket.get_round_losers(round_index='first')
    with pytest.raises(ValueError):
        completed_bracket.get_round_losers(round_index=-1)
    with pytest.raises(ValueError):
        completed_bracket.get_round_losers(round_index=100)

def test_de_bracket_get_all_round_losers(entries, completed_bracket):
    assert completed_bracket.get_all_round_losers() == [[entries[7], entries[11], entries[12], entries[13], entries[10], entries[6], entries[14]],
                                                        [entries[8], entries[4], entries[5], entries[1]],
                                                        [entries[3], entries[2]],
                                                        [entries[0]]]
    
def test_de_bracket_get_round(entries, completed_bracket):
    round0 = completed_bracket.get_round(0)

    assert round0.matches[0].entry1 == entries[0]
    assert round0.matches[0].entry2 is None
    assert round0.matches[0].is_bye()
    assert round0.matches[0].is_complete()

    assert round0.matches[1].entry1 == entries[8]
    assert round0.matches[1].entry2 == entries[7]
    assert not round0.matches[1].is_bye()
    assert round0.matches[1].is_complete()

    assert round0.matches[2].entry1 == entries[4]
    assert round0.matches[2].entry2 == entries[11]
    assert not round0.matches[2].is_bye()
    assert round0.matches[2].is_complete()

    assert round0.matches[3].entry1 == entries[12]
    assert round0.matches[3].entry2 == entries[3]
    assert not round0.matches[3].is_bye()
    assert round0.matches[3].is_complete()

    assert round0.matches[4].entry1 == entries[2]
    assert round0.matches[4].entry2 == entries[13]
    assert not round0.matches[4].is_bye()
    assert round0.matches[4].is_complete()

    assert round0.matches[5].entry1 == entries[10]
    assert round0.matches[5].entry2 == entries[5]
    assert not round0.matches[5].is_bye()
    assert round0.matches[5].is_complete()

    assert round0.matches[6].entry1 == entries[6]
    assert round0.matches[6].entry2 == entries[9]
    assert not round0.matches[6].is_bye()
    assert round0.matches[6].is_complete()

    assert round0.matches[7].entry1 == entries[14]
    assert round0.matches[7].entry2 == entries[1]
    assert not round0.matches[7].is_bye()
    assert round0.matches[7].is_complete()

    round1 = completed_bracket.get_round(1)

    assert round1.matches[0].entry1 == entries[0]
    assert round1.matches[0].entry2 == entries[8]
    assert not round1.matches[0].is_bye()
    assert round1.matches[0].is_complete()

    assert round1.matches[1].entry1 == entries[4]
    assert round1.matches[1].entry2 == entries[3]
    assert round1.matches[1].is_complete()

    assert round1.matches[2].entry1 == entries[2]
    assert round1.matches[2].entry2 == entries[5]
    assert not round1.matches[2].is_bye()
    assert round1.matches[2].is_complete()

    assert round1.matches[3].entry1 == entries[9]
    assert round1.matches[3].entry2 == entries[1]
    assert not round1.matches[3].is_bye()
    assert round1.matches[3].is_complete()

    round2 = completed_bracket.get_round(2)

    assert round2.matches[0].entry1 == entries[0]
    assert round2.matches[0].entry2 == entries[3]
    assert not round2.matches[0].is_bye()
    assert round2.matches[0].is_complete()

    assert round2.matches[1].entry1 == entries[2]
    assert round2.matches[1].entry2 == entries[9]
    assert not round2.matches[1].is_bye()
    assert round2.matches[1].is_complete()

    round3 = completed_bracket.get_round(3)

    assert round3.matches[0].entry1 == entries[0]
    assert round3.matches[0].entry2 == entries[9]
    assert not round3.matches[0].is_bye()
    assert round3.matches[0].is_complete()

def test_de_bracket_get_round_invalid(completed_bracket):
    with pytest.raises(TypeError):
        completed_bracket.get_round(index='first')
    with pytest.raises(ValueError):
        completed_bracket.get_round(index=-1)
    with pytest.raises(ValueError):
        completed_bracket.get_round(index=100)

def test_de_bracket_get_match(completed_bracket):
    match = completed_bracket.get_match(round_index=1, match_index=2)

    assert match.entry1 == completed_bracket.entries[2]
    assert match.entry2 == completed_bracket.entries[5]
    assert match.score1 == 15
    assert match.score2 == 9
    assert match.winner.display_name() == 'John'
    assert match.get_loser().display_name() == 'Alison'
    assert match.is_complete()
    assert not match.is_bye()

def test_de_bracket_get_match_invalid(completed_bracket):
    with pytest.raises(TypeError):
        completed_bracket.get_match(round_index='first', match_index=0)
    with pytest.raises(TypeError):
        completed_bracket.get_match(round_index=0, match_index='first')
    with pytest.raises(ValueError):
        completed_bracket.get_match(round_index=-1, match_index=0)
    with pytest.raises(ValueError):
        completed_bracket.get_match(round_index=100, match_index=0)
    with pytest.raises(ValueError):
        completed_bracket.get_match(round_index=0, match_index=-1)
    with pytest.raises(ValueError):
        completed_bracket.get_match(round_index=0, match_index=100)

def test_de_bracket_calculate_final_results(entries, completed_bracket):
    bracket = DEBracket(id=BRACKET_ID+1, tournament_id=TOURNY_ID+1, entries=entries)
    with pytest.raises(ValueError):
        bracket.calculate_final_results()
    assert completed_bracket.calculate_final_results() == [entries[9], 
                                                           entries[0], 
                                                           entries[2], 
                                                           entries[3], 
                                                           entries[1], 
                                                           entries[4], 
                                                           entries[5], 
                                                           entries[8], 
                                                           entries[6], 
                                                           entries[7], 
                                                           entries[10], 
                                                           entries[11], 
                                                           entries[12], 
                                                           entries[13], 
                                                           entries[14]]