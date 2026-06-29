from poules.poule_results import EntryPouleResult, SinglePouleResults, TournamentPouleResults
from entities.tournament_entry import TournamentEntry
from entities.fencer import Fencer
import pytest

@pytest.fixture
def entry1():
    return TournamentEntry(id=1, tournament_id=1, fencer=Fencer(id=1, display_name='John'))

@pytest.fixture
def entry2():
    return TournamentEntry(id=2, tournament_id=1, fencer=Fencer(id=2, display_name='Steve'))

@pytest.fixture
def entry3():
    return TournamentEntry(id=3, tournament_id=1, fencer=Fencer(id=3, display_name='Hannah'))

@pytest.fixture
def entry4():
    return TournamentEntry(id=4, tournament_id=1, fencer=Fencer(id=4, display_name='Emily'))

@pytest.fixture
def entry5():
    return TournamentEntry(id=5, tournament_id=1, fencer=Fencer(id=5, display_name='Michael'))

@pytest.fixture
def entry6():
    return TournamentEntry(id=6, tournament_id=1, fencer=Fencer(id=6, display_name='Sarah'))

@pytest.fixture
def entry7():
    return TournamentEntry(id=7, tournament_id=1, fencer=Fencer(id=7, display_name='Dave'))

@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return [entry1, entry2, entry3, entry4, entry5, entry6, entry7]


# Test EntryPouleResult (EPR) class
def test_entry_poule_result_creation_with_defaults(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=1)
    assert epr.entry is not None
    assert epr.entry == entry1
    assert epr.poule_id == 1
    assert epr.matches == 0
    assert epr.victories == 0
    assert epr.touches_scored == 0
    assert epr.touches_received == 0

def test_entry_poule_result_creation_no_defaults(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=1, matches=6, victories=4, touches_scored=21, touches_received=18)
    assert epr.entry == entry1
    assert epr.poule_id == 1
    assert epr.matches == 6
    assert epr.victories == 4
    assert epr.touches_scored == 21
    assert epr.touches_received == 18

def test_entry_poule_result_invalid_types(entry1):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=True, poule_id=1)
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id='1')
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=1, matches='6')
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=1, victories='4')
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=1, touches_scored=Fencer(id=10, display_name='Joshua'))
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=1, touches_received=True)

def test_entry_poule_result_invalid_values(entry1):
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=0)
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=-1)
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=1, matches=-5)
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=1, victories=-3)
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=1, touches_scored=-10)
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=1, touches_received=-2)

def test_entry_poule_result_equality():
    epr1 = EntryPouleResult(entry=TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Yvonne')), poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    epr2 = EntryPouleResult(entry=TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Yvonne')), poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr1 == epr2

def test_entry_poule_result_inequality(entry1):
    epr1 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr2 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr1 != epr2 # Note: equality does not depend on the entry

def test_entry_poule_result_greater_than(entry1):
    epr1 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr2 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr1 > epr2

def test_entry_poule_result_less_than(entry1):
    epr1 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr2 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr2 < epr1

def test_entry_poule_result_add_match_result(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=1)
    epr.add_match_result(touches_scored=5, touches_received=3, is_victory=True)
    assert epr.matches == 1
    assert epr.victories == 1
    assert epr.touches_scored == 5
    assert epr.touches_received == 3
    epr.add_match_result(touches_scored=2, touches_received=5, is_victory=False)
    assert epr.matches == 2
    assert epr.victories == 1
    assert epr.touches_scored == 7
    assert epr.touches_received == 8
    epr.add_match_result(touches_scored=2, touches_received=1, is_victory=True)
    assert epr.matches == 3
    assert epr.victories == 2
    assert epr.touches_scored == 9
    assert epr.touches_received == 9

def test_entry_poule_result_add_match_result_invalid_types(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=1)
    with pytest.raises(TypeError):
        epr.add_match_result(touches_scored='5', touches_received=3, is_victory=True)
    with pytest.raises(TypeError):
        epr.add_match_result(touches_scored=5, touches_received=True, is_victory=True)
    with pytest.raises(TypeError):
        epr.add_match_result(touches_scored=5, touches_received=3, is_victory=(1,))

def test_entry_poule_result_add_match_result_invalid_values(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=1)
    with pytest.raises(ValueError):
        epr.add_match_result(touches_scored=5, touches_received=-1, is_victory=True)
    with pytest.raises(ValueError):
        epr.add_match_result(touches_scored=-2, touches_received=5, is_victory=False)
    with pytest.raises(ValueError):
        epr.add_match_result(touches_scored=2, touches_received=5, is_victory=True)
    with pytest.raises(ValueError):
        epr.add_match_result(touches_scored=5, touches_received=3, is_victory=False)
    with pytest.raises(ValueError):
        epr.add_match_result(touches_scored=5, touches_received=5, is_victory=True)
    with pytest.raises(ValueError):
        epr.add_match_result(touches_scored=5, touches_received=5, is_victory=False)

# Test PouleResult (PR) class
def test_poule_result_creation_with_defaults():
    pr = SinglePouleResults(poule_id=1)
    assert pr.poule_id == 1
    assert pr.results == []

def test_poule_result_creation_no_defaults(entries):
    eprs = []
    for i, entry in enumerate(entries):
        eprs.append(EntryPouleResult(entry=entry, poule_id=1, matches=1, victories=1, touches_scored=1, touches_received=1))

    pr = SinglePouleResults(poule_id=1, results=eprs)
    assert pr.poule_id == 1
    assert len(pr.results) == 7
    for i in range(7):
        assert pr.results[i].entry == entries[i]
        assert pr.results[i].poule_id == 1
        assert pr.results[i].matches == 1
        assert pr.results[i].victories == 1
        assert pr.results[i].touches_scored == 1
        assert pr.results[i].touches_received == 1

def test_poule_result_creation_invalid_types(entry1):
    with pytest.raises(TypeError):
        SinglePouleResults(poule_id='1')
    with pytest.raises(TypeError):
        SinglePouleResults(poule_id=1, results=True)
    with pytest.raises(TypeError):
        SinglePouleResults(poule_id=1, results=[EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10), 'random string'])

def test_poule_result_creation_invalid_values():
    with pytest.raises(ValueError):
        SinglePouleResults(poule_id=0)
    with pytest.raises(ValueError):
        SinglePouleResults(poule_id=-1)

def test_poule_result_add_entry_poule_result(entry1):
    pr = SinglePouleResults(poule_id=1)
    epr = EntryPouleResult(entry=entry1, poule_id=1, matches=4, victories=2, touches_scored=11, touches_received=9)
    pr.results.append(epr)
    assert len(pr.results) == 1
    assert pr.results[0] == epr
    assert pr.results[0].entry == entry1
    assert pr.results[0].poule_id == 1
    assert pr.results[0].matches == 4
    assert pr.results[0].victories == 2
    assert pr.results[0].touches_scored == 11
    assert pr.results[0].touches_received == 9

def test_poule_result_init_entry_poule_results(entries):
    n = len(entries)
    pr = SinglePouleResults(poule_id=1)
    assert pr.results == []
    pr.init_entry_poule_results(entries=entries)
    for i in range(n):
        assert pr.results[i].entry == entries[i]
        assert pr.results[i].poule_id == 1
        assert pr.results[i].matches == 0
        assert pr.results[i].victories == 0
        assert pr.results[i].touches_scored == 0
        assert pr.results[i].touches_received == 0

def test_poule_result_add_match_result_to_entry(entries):
    pr = SinglePouleResults(poule_id=1)
    pr.init_entry_poule_results(entries=entries)
    pr.add_match_result_to_entry(entry_index=0, touches_scored=5, touches_received=2, is_victory=True)
    pr.add_match_result_to_entry(entry_index=6, touches_scored=2, touches_received=5, is_victory=False)
    assert pr.results[0].matches==1
    assert pr.results[0].victories==1
    assert pr.results[0].touches_scored==5
    assert pr.results[0].touches_received==2

    assert pr.results[6].matches==1
    assert pr.results[6].victories==0
    assert pr.results[6].touches_scored==2
    assert pr.results[6].touches_received==5

def test_poule_result_add_match_result_to_entry_invalid_types(entries):
    pr = SinglePouleResults(poule_id=1)
    pr.init_entry_poule_results(entries=entries)
    with pytest.raises(TypeError):
        pr.add_match_result_to_entry(entry_index='0', touches_scored=5, touches_received=2, is_victory=True)
    with pytest.raises(TypeError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored='5', touches_received=2, is_victory=True)
    with pytest.raises(TypeError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored=5, touches_received=True, is_victory=True)
    with pytest.raises(TypeError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored=5, touches_received=2, is_victory=(1,))

def test_poule_result_add_match_result_to_entry_invalid_values(entries):
    pr = SinglePouleResults(poule_id=1)
    pr.init_entry_poule_results(entries=entries)
    with pytest.raises(ValueError):
        pr.add_match_result_to_entry(entry_index=-1, touches_scored=5, touches_received=2, is_victory=True)
    with pytest.raises(ValueError):
        pr.add_match_result_to_entry(entry_index=7, touches_scored=5, touches_received=2, is_victory=True)
    with pytest.raises(ValueError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored=-5, touches_received=2, is_victory=True)
    with pytest.raises(ValueError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored=5, touches_received=-2, is_victory=True)
    with pytest.raises(ValueError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored=2, touches_received=5, is_victory=True)
    with pytest.raises(ValueError):
        pr.add_match_result_to_entry(entry_index=0, touches_scored=5, touches_received=2, is_victory=False)

def test_poule_result_calculate_standings(entries):
    # Make PouleEntryResults for each entry
    eprs = [None] * 7
    eprs[0] = EntryPouleResult(entry=entries[0], poule_id=1, matches=6, victories=3, touches_scored=22, touches_received=21)
    eprs[1] = EntryPouleResult(entry=entries[1], poule_id=1, matches=6, victories=1, touches_scored=12, touches_received=28)
    eprs[2] = EntryPouleResult(entry=entries[2], poule_id=1, matches=6, victories=6, touches_scored=30, touches_received=13)
    eprs[3] = EntryPouleResult(entry=entries[3], poule_id=1, matches=6, victories=4, touches_scored=24, touches_received=20)
    eprs[4] = EntryPouleResult(entry=entries[4], poule_id=1, matches=6, victories=5, touches_scored=28, touches_received=18)
    eprs[5] = EntryPouleResult(entry=entries[5], poule_id=1, matches=6, victories=1, touches_scored=18, touches_received=27)
    eprs[6] = EntryPouleResult(entry=entries[6], poule_id=1, matches=6, victories=1, touches_scored=19, touches_received=26)

    # Make PouleResult and calculate standings
    pr = SinglePouleResults(poule_id=1, results=eprs)
    standings = pr.calculate_standings()

    # Check that the original results are unchanged
    for i in range(7):
        assert pr.results[i].entry.id == eprs[i].entry.id

    # Check that the standings are in the correct order
    assert standings[0].entry.id == eprs[2].entry.id
    assert standings[1].entry.id == eprs[4].entry.id
    assert standings[2].entry.id == eprs[3].entry.id
    assert standings[3].entry.id == eprs[0].entry.id
    assert standings[4].entry.id == eprs[6].entry.id
    assert standings[5].entry.id == eprs[5].entry.id
    assert standings[6].entry.id == eprs[1].entry.id

def test_poule_result_calculate_standings_display_names(entries):
    # Make PouleEntryResults for each entry
    eprs = [None] * 7
    eprs[0] = EntryPouleResult(entry=entries[0], poule_id=1, matches=6, victories=3, touches_scored=22, touches_received=21)
    eprs[1] = EntryPouleResult(entry=entries[1], poule_id=1, matches=6, victories=1, touches_scored=12, touches_received=28)
    eprs[2] = EntryPouleResult(entry=entries[2], poule_id=1, matches=6, victories=6, touches_scored=30, touches_received=13)
    eprs[3] = EntryPouleResult(entry=entries[3], poule_id=1, matches=6, victories=4, touches_scored=24, touches_received=20)
    eprs[4] = EntryPouleResult(entry=entries[4], poule_id=1, matches=6, victories=5, touches_scored=28, touches_received=18)
    eprs[5] = EntryPouleResult(entry=entries[5], poule_id=1, matches=6, victories=1, touches_scored=18, touches_received=27)
    eprs[6] = EntryPouleResult(entry=entries[6], poule_id=1, matches=6, victories=1, touches_scored=19, touches_received=26)

    # Make PouleResult and calculate standings display names
    pr = SinglePouleResults(poule_id=1, results=eprs)
    display_names = pr.calculate_standings_display_names()

    # Check that the display names are in the correct order
    assert display_names == ['Hannah', 'Michael', 'Emily', 'John', 'Dave', 'Sarah', 'Steve']

# Test PouleResults (PRs) class
def test_poule_results_creation_with_defaults():
    prs = TournamentPouleResults()
    assert prs.results == []

def test_poule_results_creation_no_defaults(entries):
    # Make PouleEntryResults for each entry
    eprs = [None] * 7
    eprs[0] = EntryPouleResult(entry=entries[0], poule_id=1, matches=6, victories=3, touches_scored=22, touches_received=21)
    eprs[1] = EntryPouleResult(entry=entries[1], poule_id=1, matches=6, victories=1, touches_scored=12, touches_received=28)
    eprs[2] = EntryPouleResult(entry=entries[2], poule_id=1, matches=6, victories=6, touches_scored=30, touches_received=13)
    eprs[3] = EntryPouleResult(entry=entries[3], poule_id=1, matches=6, victories=4, touches_scored=24, touches_received=20)
    eprs[4] = EntryPouleResult(entry=entries[4], poule_id=1, matches=6, victories=5, touches_scored=28, touches_received=18)
    eprs[5] = EntryPouleResult(entry=entries[5], poule_id=1, matches=6, victories=1, touches_scored=18, touches_received=27)
    eprs[6] = EntryPouleResult(entry=entries[6], poule_id=1, matches=6, victories=1, touches_scored=19, touches_received=26)

    # Create PouleResults instance
    prs = TournamentPouleResults(results=eprs)

    # Validate that the results are in sorted order
    prs.results[0].entry.id == eprs[2].entry.id
    prs.results[1].entry.id == eprs[4].entry.id
    prs.results[2].entry.id == eprs[3].entry.id
    prs.results[3].entry.id == eprs[0].entry.id
    prs.results[4].entry.id == eprs[6].entry.id
    prs.results[5].entry.id == eprs[5].entry.id
    prs.results[6].entry.id == eprs[1].entry.id

def test_poule_results_creation_invalid_types():
    with pytest.raises(TypeError):
        TournamentPouleResults(results=True)
    with pytest.raises(TypeError):
        TournamentPouleResults(results=[EntryPouleResult(entry=TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Yvonne')), poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10), 'bad value'])

def test_is_sorted_on_creation():
    epr1 = EntryPouleResult(entry=TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Yvonne')), poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    epr2 = EntryPouleResult(entry=TournamentEntry(id=13, tournament_id=1, fencer=Fencer(id=13, display_name='Zach')), poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr3 = EntryPouleResult(entry=TournamentEntry(id=14, tournament_id=1, fencer=Fencer(id=14, display_name='Xavier')), poule_id=1, matches=5, victories=2, touches_scored=12, touches_received=15)
    epr4 = EntryPouleResult(entry=TournamentEntry(id=15, tournament_id=1, fencer=Fencer(id=15, display_name='Wendy')), poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    prs = TournamentPouleResults(results=[epr1, epr2, epr3, epr4])
    assert prs.results[0].entry.id == epr4.entry.id # Quicksort happened to put epr4 before epr2, randomization not applied yet for final poule results
    assert prs.results[1].entry.id == epr2.entry.id
    assert prs.results[2].entry.id == epr1.entry.id
    assert prs.results[3].entry.id == epr3.entry.id