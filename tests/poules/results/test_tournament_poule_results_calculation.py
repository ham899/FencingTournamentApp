import pytest

import factories

from constants import TOURNY_ID1, POULE_ID1, POULE_ID2, POULE_ID3

from poules.results.tournament_poule_results import TournamentPouleResults

# --- Constants ---
RANDOM_SEED = 36
POULE_NUMBER1, POULE_NUMBER2, POULE_NUMBER3 = 1, 2, 3
POULE_IDS = (POULE_ID1, POULE_ID2, POULE_ID3)


# --- Fixtures ---
@pytest.fixture
def entries_21():
    return factories.make_entries(n=21, tournament_id=TOURNY_ID1, initial_seed=True)

@pytest.fixture
def entries_poule1(entries_21):
    return (entries_21[0], entries_21[5], entries_21[6], entries_21[11], entries_21[12], entries_21[17], entries_21[18])

@pytest.fixture
def entries_poule2(entries_21):
    return (entries_21[1], entries_21[4], entries_21[7], entries_21[10], entries_21[13], entries_21[16], entries_21[19])

@pytest.fixture
def entries_poule3(entries_21):
    return (entries_21[2], entries_21[3], entries_21[8], entries_21[9], entries_21[14], entries_21[15], entries_21[20])

@pytest.fixture
def poule1_incomplete(entries_poule1):
    return factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_poule1)

@pytest.fixture
def poule2_incomplete(entries_poule2):
    return factories.make_poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries_poule2)

@pytest.fixture
def poule3_incomplete(entries_poule3):
    return factories.make_poule(POULE_ID3, TOURNY_ID1, POULE_NUMBER3, entries_poule3)

@pytest.fixture
def poules_incomplete(poule1_incomplete, poule2_incomplete, poule3_incomplete):
    return (poule1_incomplete, poule2_incomplete, poule3_incomplete)

@pytest.fixture
def results_incomplete(poules_incomplete):
    return TournamentPouleResults(TOURNY_ID1, poules_incomplete, RANDOM_SEED)

@pytest.fixture
def poule1_partial(entries_poule1):
    match_results = ((5,3), (5,1), (0,5), (4,5), (2,5), (5,0), (5,0))
    
    return factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_poule1, scores=match_results)

@pytest.fixture
def poule2_partial(entries_poule2):
    match_results = ((3,5), (2,5), (5,4), (5,0), (4,5), (1,5), (3,5))
    
    return factories.make_poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries_poule2, scores=match_results)

@pytest.fixture
def poule3_partial(entries_poule3):
    match_results = ((5,0), (5,3), (4,5), (2,5), (5,2), (5,3), (5,4))
    
    return factories.make_poule(POULE_ID3, TOURNY_ID1, POULE_NUMBER3, entries_poule3, scores=match_results)

@pytest.fixture
def poules_partially_complete(poule1_partial, poule2_partial, poule3_partial):
    return (poule1_partial, poule2_partial, poule3_partial)

@pytest.fixture
def results_partially_complete(poules_partially_complete):
    return TournamentPouleResults(TOURNY_ID1, poules_partially_complete, RANDOM_SEED)

@pytest.fixture
def poule1_complete(entries_poule1):
    match_results = ((5,3), (5,1), (0,5), (4,5), (2,5), (5,0), (5,0), 
                     (5,2), (4,5), (5,3), (5,3), (1,5), (2,5), (3,5), 
                     (4,5), (0,5), (5,4), (2,5), (5,4), (3,5), (5,1))
    
    return factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_poule1, scores=match_results)

@pytest.fixture
def poule2_complete(entries_poule2):
    match_results = ((3,5), (2,5), (5,4), (5,0), (4,5), (1,5), (3,5), 
                     (5,1), (5,4), (5,3), (5,2), (5,2), (5,1), (5,2), 
                     (5,3), (5,4), (2,5), (3,5), (0,5), (5,4), (4,5))
    
    return factories.make_poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries_poule2, scores=match_results)

@pytest.fixture
def poule3_complete(entries_poule3):
    match_results = ((5,0), (5,3), (4,5), (2,5), (5,2), (5,3), (5,4), 
                     (2,5), (3,5), (5,3), (5,4), (0,5), (2,5), (0,5), 
                     (5,4), (5,4), (5,1), (5,2), (5,1), (5,4), (4,5))
    
    return factories.make_poule(POULE_ID3, TOURNY_ID1, POULE_NUMBER3, entries_poule3, scores=match_results)

@pytest.fixture
def poules_complete(poule1_complete, poule2_complete, poule3_complete):
    return (poule1_complete, poule2_complete, poule3_complete)

@pytest.fixture
def results_complete(poules_complete):
    return TournamentPouleResults(TOURNY_ID1, poules_complete, RANDOM_SEED)


# --- Result Calculation Tests ---
def test_tournament_poule_results_incomplete_poules(results_incomplete):
    assert results_incomplete.tournament_id == TOURNY_ID1
    assert results_incomplete.random_seed == RANDOM_SEED
    
    poule_name_order = (
        ('John', 'Sarah', 'Dave', 'Jessica', 'Edward', 'Catherine', 'Peter'),
        ('Steve', 'Michael', 'Jill', 'Jack', 'Jane', 'Robert', 'Isabella'),
        ('Hannah', 'Emily', 'Parsa', 'Chantelle', 'Stephen', 'Joanna', 'Albert')
    )

    expected_results_name_order = (
        ('Catherine', 'Dave', 'Edward', 'Jessica', 'John', 'Peter', 'Sarah'),
        ('Isabella', 'Jack', 'Jane', 'Jill', 'Michael', 'Robert', 'Steve'),
        ('Albert', 'Chantelle', 'Emily', 'Hannah', 'Joanna', 'Parsa', 'Stephen')
    )

    assert len(results_incomplete.poule_results) == 3

    for i, poule_result in enumerate(results_incomplete.poule_results):
        assert poule_result.poule_id == POULE_IDS[i]
        assert poule_result.tournament_id == TOURNY_ID1

        assert len(poule_result.entry_results) == 7

        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.entry.display_name == poule_name_order[i][j]
            assert entry_result.poule_id == POULE_IDS[i]
            assert entry_result.tournament_id == TOURNY_ID1

            assert entry_result.num_matches == 0
            assert entry_result.num_victories == 0
            assert entry_result.touches_scored == 0
            assert entry_result.touches_received == 0
            assert entry_result.victory_ratio == 0.0
            assert entry_result.indicator == 0

        assert poule_result.ranked_results_display_names == expected_results_name_order[i]

    assert len(results_incomplete.round_results) == 21

def test_tournament_poule_results_partially_complete_poules(results_partially_complete):
    expected_results = (
        (
            ('John', 2, 2, 10, 7, 1.0, 3), 
            ('Sarah', 2, 2, 10, 1, 1.0, 9), 
            ('Dave', 2, 0, 0, 10, 0.0, -10), 
            ('Jessica', 2, 1, 8, 7, 0.5, 1), 
            ('Edward', 2, 0, 3, 10, 0.0, -7), 
            ('Catherine', 2, 2, 10, 0, 1.0, 10), 
            ('Peter', 2, 0, 4, 10, 0.0, -6)
        ),
        (
            ('Steve', 2, 0, 3, 10, 0.0, -7), 
            ('Michael', 2, 0, 3, 10, 0.0, -7), 
            ('Jill', 2, 2, 10, 5, 1.0, 5), 
            ('Jack', 2, 2, 10, 7, 1.0, 3), 
            ('Jane', 2, 1, 9, 7, 0.5, 2), 
            ('Robert', 2, 0, 7, 10, 0.0, -3), 
            ('Isabella', 2, 2, 10, 3, 1.0, 7)
        ),
        (
            ('Hannah', 2, 2, 10, 2, 1.0, 8), 
            ('Emily', 2, 2, 10, 6, 1.0, 4), 
            ('Parsa', 2, 0, 7, 10, 0.0, -3), 
            ('Chantelle', 2, 0, 2, 10, 0.0, -8), 
            ('Stephen', 2, 1, 8, 7, 0.5, 1), 
            ('Joanna', 2, 2, 10, 8, 1.0, 2), 
            ('Albert', 2, 0, 6, 10, 0.0, -4)
        )
    )

    expected_results_name_order = (
        ('Catherine', 'Sarah', 'John', 'Jessica', 'Peter', 'Edward', 'Dave'),
        ('Isabella', 'Jill', 'Jack', 'Jane', 'Robert', 'Michael', 'Steve'),
        ('Hannah', 'Emily', 'Joanna', 'Stephen', 'Parsa', 'Albert', 'Chantelle')
    )

    assert len(results_partially_complete.poule_results) == 3

    for i, poule_result in enumerate(results_partially_complete.poule_results):
        assert poule_result.poule_id == POULE_IDS[i]
        assert poule_result.tournament_id == TOURNY_ID1

        assert len(poule_result.entry_results) == 7

        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.poule_id == POULE_IDS[i]
            assert entry_result.tournament_id == TOURNY_ID1

            assert entry_result.entry.display_name == expected_results[i][j][0]
            assert entry_result.num_matches == expected_results[i][j][1]
            assert entry_result.num_victories == expected_results[i][j][2]
            assert entry_result.touches_scored == expected_results[i][j][3]
            assert entry_result.touches_received == expected_results[i][j][4]
            assert entry_result.victory_ratio == expected_results[i][j][5]
            assert entry_result.indicator == expected_results[i][j][6]

        assert poule_result.ranked_results_display_names == expected_results_name_order[i]

    expected_partial_poule_round_results = (
        'Catherine', 'Sarah', 'Hannah', 'Isabella', 'Jill', 'Emily', 'John',
        'Jack', 'Joanna', 'Jane', 'Jessica', 'Stephen', 'Robert', 'Parsa',
        'Albert', 'Peter', 'Steve', 'Edward', 'Michael', 'Chantelle', 'Dave'
    ) # Note: Jack/John, Stephen/Jessica, Parsa/Robert, Edward/Michael/Steve are exact ties. Their displayed order is produced by RANDOM_SEED = 36.
    
    assert results_partially_complete.round_results_display_names == expected_partial_poule_round_results

def test_tournament_poule_results_complete_poules(results_complete):
    expected_results = (
        (
            ('John', 6, 3, 20, 23, 0.5, -3), 
            ('Sarah', 6, 5, 28, 16, 5 / 6, 12), 
            ('Dave', 6, 2, 15, 26, 1 / 3, -11), 
            ('Jessica', 6, 2, 23, 23, 1 / 3, 0), 
            ('Edward', 6, 3, 22, 24, 0.5, -2), 
            ('Catherine', 6, 6, 30, 9, 1.0, 21), 
            ('Peter', 6, 0, 13, 30, 0.0, -17)
        ),
        (
            ('Steve', 6, 2, 16, 28, 1 / 3, -12), 
            ('Michael', 6, 0, 14, 30, 0.0, -16), 
            ('Jill', 6, 5, 29, 18, 5 / 6, 11), 
            ('Jack', 6, 5, 29, 19, 5 / 6, 10), 
            ('Jane', 6, 4, 27, 15, 2 / 3, 12), 
            ('Robert', 6, 1, 17, 28, 1 / 6, -11), 
            ('Isabella', 6, 4, 25, 19, 2 / 3, 6)
        ),
        (
            ('Hannah', 6, 6, 30, 12, 1.0, 18), 
            ('Emily', 6, 4, 27, 17, 2 / 3, 10), 
            ('Parsa', 6, 2, 19, 27, 1 / 3, -8), 
            ('Chantelle', 6, 0, 12, 30, 0.0, -18), 
            ('Stephen', 6, 2, 20, 26, 1 / 3, -6), 
            ('Joanna', 6, 5, 29, 19, 5 / 6, 10), 
            ('Albert', 6, 2, 20, 26, 1 / 3, -6)
        )
    )

    expected_results_name_order = (
        ('Catherine', 'Sarah', 'Edward', 'John', 'Jessica', 'Dave', 'Peter'),
        ('Jill', 'Jack', 'Jane', 'Isabella', 'Steve', 'Robert', 'Michael'),
        ('Hannah', 'Joanna', 'Emily', 'Albert', 'Stephen', 'Parsa', 'Chantelle')
    )

    assert len(results_complete.poule_results) == 3

    for i, poule_result in enumerate(results_complete.poule_results):
        assert poule_result.poule_id == POULE_IDS[i]
        assert poule_result.tournament_id == TOURNY_ID1

        assert len(poule_result.entry_results) == 7

        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.poule_id == POULE_IDS[i]
            assert entry_result.tournament_id == TOURNY_ID1

            assert entry_result.entry.display_name == expected_results[i][j][0]
            assert entry_result.num_matches == expected_results[i][j][1]
            assert entry_result.num_victories == expected_results[i][j][2]
            assert entry_result.touches_scored == expected_results[i][j][3]
            assert entry_result.touches_received == expected_results[i][j][4]
            assert entry_result.victory_ratio == expected_results[i][j][5]
            assert entry_result.indicator == expected_results[i][j][6]

        assert poule_result.ranked_results_display_names == expected_results_name_order[i]

    expected_poule_round_results = (
        ('Catherine', 'Hannah', 'Sarah', 'Jill', 'Joanna', 'Jack', 'Jane',
         'Emily', 'Isabella', 'Edward', 'John', 'Jessica', 'Albert', 'Stephen',
         'Parsa', 'Dave', 'Steve', 'Robert', 'Michael', 'Peter', 'Chantelle')
    ) # Note: Jack/Joanna and Albert/Stephen are exact ties. Their displayed order is produced by RANDOM_SEED = 36.

    assert results_complete.round_results_display_names == expected_poule_round_results

def test_tournament_poule_results_ranks_by_victory_ratio_not_number_of_victories():
    entries = factories.make_entries(n=11, tournament_id=TOURNY_ID1, initial_seed=True)

    entries_poule1 = (
        entries[0], # John
        entries[3], # Emily
        entries[4], # Michael
        entries[7], # Jill
        entries[8], # Parsa
        entries[10] # Jack
    )
    
    entries_poule2 = (
        entries[1], # Steve
        entries[2], # Hannah
        entries[5], # Sarah
        entries[6]  # Dave
    )

    # Poule 1 bout order: [(1,2), (4,5), (2,3), (5,6), (3,1), (6,4), (2,5), (1,4), (5,3), (1,6), (4,2), (3,6), (5,1), (3,4), (6,2)]
    scores_poule1 = (
        (5, 2), (4, 5), (2, 5), (2, 5), (5, 4),
        (5, 1), (5, 4), (5, 2), (5, 3), (4, 5),
        (0, 5), (5, 2), (5, 4), (5, 0), (5, 1)
    )

    # Poule 2 bout order: [(1,4), (2,3), (1,3), (2,4), (3,4), (1,2)]
    scores_poule2 = ((5, 1), (1, 5), (3, 5), (5, 4), (3, 5), (5, 2))

    poule1 = factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_poule1, scores=scores_poule1)
    
    poule2 = factories.make_poule(POULE_ID2, TOURNY_ID1,POULE_NUMBER2, entries_poule2, scores=scores_poule2)

    results = TournamentPouleResults(TOURNY_ID1, (poule1, poule2), RANDOM_SEED)

    assert len(results.poule_results) == 2
    assert len(results.poule_results[0].entry_results) == 6
    assert len(results.poule_results[1].entry_results) == 4

    expected_result_stats = (
        (
            (2 / 5, 3, 22),    # John
            (2 / 5, -4, 15),   # Emily
            (4 / 5, 10, 23),   # Michael
            (0.0, -18, 7),     # Jill
            (3 / 5, 0, 21),    # Parsa
            (4 / 5, 9, 22)     # Jack
        ),
        (
            (2 / 3, 5, 13),    # Steve
            (1 / 3, -6, 8),    # Hannah
            (2 / 3, 4, 13),    # Sarah
            (1 / 3, -3, 10)    # Dave
        )
    )

    for i, poule_result in enumerate(results.poule_results):
        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.victory_ratio == expected_result_stats[i][j][0]
            assert entry_result.indicator == expected_result_stats[i][j][1]
            assert entry_result.touches_scored == expected_result_stats[i][j][2]

    expected_round_results_names = ('Michael', 'Jack', 'Steve', 'Sarah', 'Parsa', 'John', 'Emily', 'Dave', 'Hannah', 'Jill')

    assert results.round_results_display_names == expected_round_results_names

def test_tournament_poule_results_uses_indicator_after_equal_victory_ratios():
    entries = factories.make_entries(n=5, tournament_id=TOURNY_ID1, initial_seed=True)

    entries_poule1 = (entries[0], entries[3], entries[4])
    entries_poule2 = (entries[1], entries[2])

    # Poule 1 bout order: [(1,2), (1,3), (2,3)]
    scores_poule1 = ((5, 1), (4, 5), (4, 5))
    
    # Poule 2 bout order: [(1,2)]
    scores_poule2 = ((5, 2),)

    poule1 = factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_poule1, scores=scores_poule1)
    poule2 = factories.make_poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries_poule2, scores=scores_poule2)

    results = TournamentPouleResults(TOURNY_ID1, (poule1, poule2), RANDOM_SEED)

    assert len(results.poule_results) == 2
    assert len(results.poule_results[0].entry_results) == 3
    assert len(results.poule_results[1].entry_results) == 2

    expected_result_stats = (
        (
            (0.5, 3, 9), # John
            (0.0, -5, 5), # Emily
            (1.0, 2, 10) # Michael
        ),
        (
            (1.0, 3, 5), # Steve
            (0.0, -3, 2) # Hannah
        )
    )

    for i, poule_result in enumerate(results.poule_results):
        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.victory_ratio == expected_result_stats[i][j][0]
            assert entry_result.indicator == expected_result_stats[i][j][1]
            assert entry_result.touches_scored == expected_result_stats[i][j][2]

    expected_round_results_names = ('Steve', 'Michael', 'John', 'Hannah', 'Emily')

    assert results.round_results_display_names == expected_round_results_names

def test_tournament_poule_results_uses_touches_scored_after_ratio_and_indicator():
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1, initial_seed=True)

    entries_poule1 = (entries[0], entries[3])
    entries_poule2 = (entries[1], entries[2])

    poule1 = factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_poule1, scores=((5, 3),))
    poule2 = factories.make_poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries_poule2, scores=((4, 2),))

    results = TournamentPouleResults(TOURNY_ID1, (poule1, poule2), RANDOM_SEED)

    assert len(results.poule_results) == 2
    assert len(results.poule_results[0].entry_results) == 2
    assert len(results.poule_results[1].entry_results) == 2

    expected_result_stats = (
        (
            (1.0, 2, 5), # John
            (0.0, -2, 3) # Emily
        ),
        (
            (1.0, 2, 4), # Steve
            (0.0, -2, 2) # Hannah
        )
    )

    for i, poule_result in enumerate(results.poule_results):
        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.victory_ratio == expected_result_stats[i][j][0]
            assert entry_result.indicator == expected_result_stats[i][j][1]
            assert entry_result.touches_scored == expected_result_stats[i][j][2]

    expected_round_results_names = ('John', 'Steve', 'Emily', 'Hannah')

    assert results.round_results_display_names == expected_round_results_names

def test_tournament_poule_results_is_score_snapshot():
    entries = factories.make_entries(n=2, tournament_id=TOURNY_ID1, initial_seed=True)
    poule = factories.make_poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries, scores=((5, 2),))

    original_results = TournamentPouleResults(TOURNY_ID1, (poule,), RANDOM_SEED)

    poule.record_match_result(0, 1, 5)

    assert original_results.round_results[0].entry == entries[0]
    assert original_results.round_results[0].num_victories == 1
    assert original_results.round_results[0].touches_scored == 5
    assert original_results.round_results[0].touches_received == 2

    assert original_results.round_results[1].entry == entries[1]
    assert original_results.round_results[1].num_victories == 0
    assert original_results.round_results[1].touches_scored == 2
    assert original_results.round_results[1].touches_received == 5    

    updated_results = TournamentPouleResults(TOURNY_ID1, (poule,), RANDOM_SEED)

    assert updated_results.round_results[0].entry == entries[1]
    assert updated_results.round_results[0].num_victories == 1
    assert updated_results.round_results[0].touches_scored == 5
    assert updated_results.round_results[0].touches_received == 1

    assert updated_results.round_results[1].entry == entries[0]
    assert updated_results.round_results[1].num_victories == 0
    assert updated_results.round_results[1].touches_scored == 1
    assert updated_results.round_results[1].touches_received == 5