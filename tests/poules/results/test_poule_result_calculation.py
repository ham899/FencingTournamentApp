from poules.results.poule_result import PouleResult

# --- Constants ---
POULE_ID1 = 1
TOURNY_ID1 = 1

def test_poule_result_creation_valid_completed_matches(entries, completed_poule_matches):
    poule_result = PouleResult(entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)

    assert poule_result.entries == entries

    assert poule_result.entry_results[0].num_matches == 6
    assert poule_result.entry_results[0].num_victories == 3
    assert poule_result.entry_results[0].victory_ratio == 3 / 6
    assert poule_result.entry_results[0].touches_scored == 22
    assert poule_result.entry_results[0].touches_received == 21
    assert poule_result.entry_results[0].indicator == 1

    assert poule_result.entry_results[1].num_matches == 6
    assert poule_result.entry_results[1].num_victories == 1
    assert poule_result.entry_results[1].victory_ratio == 1 / 6
    assert poule_result.entry_results[1].touches_scored == 12
    assert poule_result.entry_results[1].touches_received == 28
    assert poule_result.entry_results[1].indicator == -16

    assert poule_result.entry_results[2].num_matches == 6
    assert poule_result.entry_results[2].num_victories == 6
    assert poule_result.entry_results[2].victory_ratio == 6 / 6
    assert poule_result.entry_results[2].touches_scored == 30
    assert poule_result.entry_results[2].touches_received == 13
    assert poule_result.entry_results[2].indicator == 17

    assert poule_result.entry_results[3].num_matches == 6
    assert poule_result.entry_results[3].num_victories == 4
    assert poule_result.entry_results[3].victory_ratio == 4 / 6
    assert poule_result.entry_results[3].touches_scored == 24
    assert poule_result.entry_results[3].touches_received == 20
    assert poule_result.entry_results[3].indicator == 4

    assert poule_result.entry_results[4].num_matches == 6
    assert poule_result.entry_results[4].num_victories == 5
    assert poule_result.entry_results[4].victory_ratio == 5 / 6
    assert poule_result.entry_results[4].touches_scored == 28
    assert poule_result.entry_results[4].touches_received == 18
    assert poule_result.entry_results[4].indicator == 10

    assert poule_result.entry_results[5].num_matches == 6
    assert poule_result.entry_results[5].num_victories == 1
    assert poule_result.entry_results[5].victory_ratio == 1 / 6
    assert poule_result.entry_results[5].touches_scored == 18
    assert poule_result.entry_results[5].touches_received == 27
    assert poule_result.entry_results[5].indicator == -9

    assert poule_result.entry_results[6].num_matches == 6
    assert poule_result.entry_results[6].num_victories == 1
    assert poule_result.entry_results[6].victory_ratio == 1 / 6
    assert poule_result.entry_results[6].touches_scored == 19
    assert poule_result.entry_results[6].touches_received == 26
    assert poule_result.entry_results[6].indicator == -7


# --- Property Tests ---
def test_poule_result_entries_property(entries, poule_result):
    assert poule_result.entries == entries

def test_poule_result_ranked_results_property(poule_result):
    expected_results = (poule_result.entry_results[2], 
                        poule_result.entry_results[4], 
                        poule_result.entry_results[3], 
                        poule_result.entry_results[0], 
                        poule_result.entry_results[6], 
                        poule_result.entry_results[5], 
                        poule_result.entry_results[1])
    
    assert poule_result.ranked_results == expected_results

def test_poule_result_ranked_results_display_names_property(poule_result):
    assert poule_result.ranked_results_display_names == ('Hannah', 'Michael', 'Emily', 'John', 'Dave', 'Sarah', 'Steve')

