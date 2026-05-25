from poule import Poule
from tournament_entry import TournamentEntry
from fencer import Fencer
import random

import pytest

@pytest.fixture
def entries():
    return [TournamentEntry(id=1, tournament_id=1, fencer=Fencer(id=1, display_name='John')),
            TournamentEntry(id=2, tournament_id=1, fencer=Fencer(id=2, display_name='Steve')), 
            TournamentEntry(id=3, tournament_id=1, fencer=Fencer(id=3, display_name='Hannah')),
            TournamentEntry(id=4, tournament_id=1, fencer=Fencer(id=4, display_name='Emily')),
            TournamentEntry(id=5, tournament_id=1, fencer=Fencer(id=5, display_name='Michael')),
            TournamentEntry(id=6, tournament_id=1, fencer=Fencer(id=6, display_name='Sarah')),
            TournamentEntry(id=7, tournament_id=1, fencer=Fencer(id=7, display_name='Dave'))]

def test_poule_creation(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    assert poule.id == 1
    assert poule.tournament_id == 1
    assert poule.poule_number == 1
    assert poule.entries == entries
    assert poule.size == len(entries)
    assert poule.matches is not None
    assert poule.current_match_index == 0

def test_poule_creation_invalid_types(entries):
    with pytest.raises(TypeError):
        Poule(id='1', tournament_id=1, poule_number=1, entries=entries)

    with pytest.raises(TypeError):
        Poule(id=1, tournament_id='1', poule_number=1, entries=entries)

    with pytest.raises(TypeError):
        Poule(id=1, tournament_id=1, poule_number='1', entries=entries)

    with pytest.raises(TypeError):
        Poule(id=1, tournament_id=1, poule_number=1, entries='entries')
    
    with pytest.raises(TypeError):
        Poule(id=1, tournament_id=1, poule_number=1, entries=[1, 2, 3])

def test_poule_creation_invalid_values(entries):
    with pytest.raises(ValueError):
        Poule(id=0, tournament_id=1, poule_number=1, entries=entries)
    with pytest.raises(ValueError):
        Poule(id=1, tournament_id=0, poule_number=1, entries=entries)
    with pytest.raises(ValueError):
        Poule(id=1, tournament_id=1, poule_number=0, entries=entries)
    with pytest.raises(ValueError):
        Poule(id=1, tournament_id=1, poule_number=1, entries=[TournamentEntry(id=1, tournament_id=1, fencer=Fencer(id=1, display_name='John'))])

def test_poule_number_of_matches(entries):
    poule1 = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:2])
    assert poule1.number_of_matches() == 1
    assert poule1.number_of_matches() == len(poule1.matches)
    poule2 = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])
    assert poule2.number_of_matches() == 3
    assert poule2.number_of_matches() == len(poule2.matches)
    poule3 = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:4])
    assert poule3.number_of_matches() == 6
    assert poule3.number_of_matches() == len(poule3.matches)
    poule4 = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:5])
    assert poule4.number_of_matches() == 10
    assert poule4.number_of_matches() == len(poule4.matches)
    poule5 = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:6])
    assert poule5.number_of_matches() == 15
    assert poule5.number_of_matches() == len(poule5.matches)
    poule6 = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    assert poule6.number_of_matches() == 21
    assert poule6.number_of_matches() == len(poule6.matches)

def test_poule__create_match(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])
    m = poule._create_match(match_number=1, match_pair=(1, 2))
    assert m.id == 1
    assert m.entry1 == entries[0]
    assert m.entry2 == entries[1]
    assert m.poule_id == 1
    assert m.tournament_id == 1
    assert m.completed == False
    assert m.winner is None

def test_poule__create_match_invalid_types(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])
    with pytest.raises(TypeError):
        poule._create_match(match_number='1', match_pair=(1, 2))
    with pytest.raises(TypeError):
        poule._create_match(match_number=1, match_pair=True)

def test_poule__create_match_invalid_values(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])
    with pytest.raises(ValueError):
        poule._create_match(match_number=0, match_pair=(1, 2))
    with pytest.raises(ValueError):
        poule._create_match(match_number=100, match_pair=(1, 2))
    with pytest.raises(ValueError):
        poule._create_match(match_number=1, match_pair=(1,))
    with pytest.raises(ValueError):
        poule._create_match(match_number=1, match_pair=(0, 2))
    with pytest.raises(ValueError):
        poule._create_match(match_number=1, match_pair=(1, 4))

def test_poule_add_entry(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    old_matches = poule.matches[:]
    old_size = poule.size
    new_entry = TournamentEntry(id=8, tournament_id=1, fencer=Fencer(id=8, display_name='Carol'))
    poule.add_entry(new_entry)
    assert poule.entries == entries + [new_entry]
    assert poule.matches != old_matches
    assert poule.size == old_size + 1

def test_poule_add_invalid_entry(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    with pytest.raises(TypeError):
        poule.add_entry(10)
    with pytest.raises(ValueError):
        poule.add_entry(entries[3])

def test_poule_remove_entry(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    old_matches = poule.matches[:]
    old_size = poule.size
    poule.remove_entry(entries[0])
    assert poule.entries == entries[1:]
    assert poule.matches != old_matches
    assert poule.size == old_size - 1

def test_poule_remove_entry_invalid(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    with pytest.raises(TypeError):
        poule.remove_entry('John')
    with pytest.raises(ValueError):
        poule.remove_entry(TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Jake')))

def test_poule_generate_matches(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])
    assert poule.size == 3
    # Match 1: (1,2)
    assert poule.matches[0].entry1 == entries[0]
    assert poule.matches[0].entry2 == entries[1]
    # Match 2: (1,3)
    assert poule.matches[1].entry1 == entries[0]
    assert poule.matches[1].entry2 == entries[2]
    # Match 3: (2,3)
    assert poule.matches[2].entry1 == entries[1]
    assert poule.matches[2].entry2 == entries[2]

def test_poule_get_current_match(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    # First match in poule of 7: (1,4)
    current_match = poule.get_current_match()
    assert current_match.entry1 == entries[0]
    assert current_match.entry2 == entries[3]
    assert current_match.completed == False
    assert current_match.winner == None
    assert current_match.poule_id == 1
    assert current_match.id == 1

    # Perform all matches
    for _ in range(poule.number_of_matches()):
        poule.record_current_match_result(score1=5, score2=0)
    
    assert poule.get_current_match() is None

def test_poule_get_current_match_return_none(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    poule.matches = None
    assert poule.get_current_match() is None
    poule.generate_matches()
    poule.current_match_index = poule.number_of_matches()
    assert poule.get_current_match() is None

def test_poule_get_next_match(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    # Second match in poule of 7: (2,5)
    next_match = poule.get_next_match()
    assert next_match.entry1 == entries[1]
    assert next_match.entry2 == entries[4]
    assert next_match.poule_id == 1
    assert next_match.id == 2
    assert next_match.completed == False
    assert next_match.winner == None

    # Complete all matches up to the last match
    for _ in range(poule.number_of_matches()-1):
        poule.record_current_match_result(score1=5, score2=0)
    
    assert poule.get_next_match() is None

def test_poule_get_next_match_return_none(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    poule.matches = None
    assert poule.get_next_match() is None
    poule.generate_matches()
    poule.current_match_index = poule.number_of_matches()-1
    assert poule.get_next_match() is None

def test_poule_record_match_result(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    index = 5
    poule.record_match_result(match_index=index, score1=2, score2=3)
    # Check that first match is still incomplete
    m1 = poule.matches[0]
    assert m1.completed == False
    assert m1.winner is None
    assert m1.id == 1
    assert m1.poule_id == 1
    # Check that `index+1` match is complete
    m2 = poule.matches[index]
    assert m2.score1 == 2
    assert m2.score2 == 3
    assert m2.completed == True
    assert m2.winner == m2.entry2
    assert m2.id == index+1
    assert m2.poule_id == 1

def test_poule_record_match_result_invalid(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    # No matches present
    with pytest.raises(ValueError):
        poule.matches=None
        poule.record_match_result(match_index=1, score1=5, score2=1)
    
    # Regenerate matches
    poule.generate_matches()
    
    # Invalid match index
    with pytest.raises(TypeError):
        poule.record_match_result(match_index='ten', score1=5, score2=2)
    with pytest.raises(ValueError):
        poule.record_match_result(match_index=-1, score1=5, score2=2)
    with pytest.raises(ValueError):
        poule.record_match_result(match_index=poule.number_of_matches(), score1=2, score2=4)
    
    # Invalid scores
    with pytest.raises(TypeError):
        poule.record_match_result(match_index=2, score1='five', score2=2)
    with pytest.raises(TypeError):
        poule.record_match_result(match_index=2, score1=5, score2='two')
    with pytest.raises(ValueError):
        poule.record_match_result(match_index=2, score1=-1, score2=5)
    with pytest.raises(ValueError):
        poule.record_match_result(match_index=1, score1=2, score2=-1)

def test_poule_record_current_match_result(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    
    for i in range(poule.number_of_matches()):
        assert poule.current_match_index == i

        # Check match info before recording the result
        m = poule.get_current_match()
        assert m.id == i+1
        assert m.poule_id == 1
        assert m.completed == False
        assert m.winner is None

        # Record a score using randomization
        score1 = random.randint(0,5)
        score2 = random.randint(0,5)
        while score1 == score2:
            score2 = random.randint(0,5)
        poule.record_current_match_result(score1=score1, score2=score2)

        # Check match info after recording the result
        m = poule.matches[poule.current_match_index-1]
        assert m.id == i+1
        assert m.poule_id == 1
        assert m.completed == True
        assert m.winner is not None

        assert poule.current_match_index == i+1

def test_poule_record_current_match_result_out_of_bounds_index(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)

    # Attempt to record a match out of the bounds of number of matches
    for _ in range(poule.number_of_matches()):
        poule.record_current_match_result(5,2)
    with pytest.raises(ValueError):
        poule.record_current_match_result(5,2)

def test_poule_is_complete(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    # Complete all matches
    for _ in range(poule.number_of_matches()):
        poule.record_current_match_result(3,4)

    assert poule.is_complete() == True
    
def test_poule_is_complete_none_matches(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    poule.matches = None
    poule.is_complete() == False

def test_poule_calculate_results(entries):
    # Test a poule of 3
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])

    # Record first match: (1,2)
    poule.record_current_match_result(score1=5, score2=1)

    # Get current poule results
    poule_results = poule.calculate_results()
    assert poule_results.poule_id == poule.id
    
    # Validate John's current results
    assert poule_results.results[0].matches_fenced == 1
    assert poule_results.results[0].victories == 1
    assert poule_results.results[0].touches_scored == 5
    assert poule_results.results[0].touches_received == 1
    # Validate Steve's current results
    assert poule_results.results[1].matches_fenced == 1
    assert poule_results.results[1].victories == 0
    assert poule_results.results[1].touches_scored == 1
    assert poule_results.results[1].touches_received == 5
    # Validate Hannah's current results
    assert poule_results.results[2].matches_fenced == 0
    assert poule_results.results[2].victories == 0
    assert poule_results.results[2].touches_scored == 0
    assert poule_results.results[2].touches_received == 0

    # Record second match: (1,3)
    poule.record_current_match_result(score1=2, score2=5)

    # Get current poule results
    poule_results = poule.calculate_results()
    assert poule_results.poule_id == poule.id

    # Validate John's current results
    assert poule_results.results[0].matches_fenced == 2
    assert poule_results.results[0].victories == 1
    assert poule_results.results[0].touches_scored == 7
    assert poule_results.results[0].touches_received == 6
    # Validate Steve's current results
    assert poule_results.results[1].matches_fenced == 1
    assert poule_results.results[1].victories == 0
    assert poule_results.results[1].touches_scored == 1
    assert poule_results.results[1].touches_received == 5
    # Validate Hannah's current results
    assert poule_results.results[2].matches_fenced == 1
    assert poule_results.results[2].victories == 1
    assert poule_results.results[2].touches_scored == 5
    assert poule_results.results[2].touches_received == 2


    # Record final match: (2,3)
    poule.record_current_match_result(score1=4, score2=5)

    # Get final results
    poule_results = poule.calculate_results()
    assert poule_results.poule_id == poule.id
    
    # Validate John's final results
    assert poule_results.results[0].matches_fenced == 2
    assert poule_results.results[0].victories == 1
    assert poule_results.results[0].touches_scored == 7
    assert poule_results.results[0].touches_received == 6
    # Validate Steve's final results
    assert poule_results.results[1].matches_fenced == 2
    assert poule_results.results[1].victories == 0
    assert poule_results.results[1].touches_scored == 5
    assert poule_results.results[1].touches_received == 10
    # Validate Hannah's final results
    assert poule_results.results[2].matches_fenced == 2
    assert poule_results.results[2].victories == 2
    assert poule_results.results[2].touches_scored == 10
    assert poule_results.results[2].touches_received == 6

    # Validate final ranking
    poule_results.calculate_standings_display_names() == ['Hannah', 'John', 'Steve']