import pytest

from de.de_bracket import DEBracket


# --- Constants ---
INVALID_INT_TYPES = [None, False, True, 'three', 2.0, [], (), {}, object()]


# --- calculate_number_of_de_rounds tests ---
@pytest.mark.parametrize(('number_de_entries', 'expected_rounds'), [
    (2, 1),
    (3, 2),
    (4, 2),
    (5, 3),
    (6, 3),
    (7, 3),
    (8, 3),
    (9, 4),
    (10, 4),
    (11, 4),
    (12, 4),
    (13, 4),
    (14, 4),
    (15, 4),
    (16, 4),
    (17, 5),
    (32, 5),
    (33, 6),
    (64, 6),
    (65, 7),
    (100, 7),
    (200, 8),
    (500, 9),
    (1000, 10)
])
def test_calculate_number_de_rounds_valid(number_de_entries, expected_rounds):
    assert DEBracket._calculate_number_de_rounds(number_de_entries=number_de_entries) == expected_rounds

@pytest.mark.parametrize('invalid_number_de_entries_type', INVALID_INT_TYPES)
def test_calculate_number_de_rounds_invalid_number_de_entries_type(invalid_number_de_entries_type):
    with pytest.raises(TypeError):
        DEBracket._calculate_number_de_rounds(number_de_entries=invalid_number_de_entries_type)

@pytest.mark.parametrize('invalid_number_de_entries_value', [-10, -1, 0, 1])
def test_calculate_number_de_rounds_invalid_number_de_entries_value(invalid_number_de_entries_value):
    with pytest.raises(ValueError):
        DEBracket._calculate_number_de_rounds(number_de_entries=invalid_number_de_entries_value)

    
# --- calculate_number_matches_in_de_round tests ---
@pytest.mark.parametrize(('round_index', 'number_de_entries', 'expected_matches'), [
    # 2-entry bracket
    (0, 2, 1),

    # 3-entry bracket: 4-slot bracket with one BYE
    (0, 3, 2),
    (1, 3, 1),

    # 4-entry bracket
    (0, 4, 2),
    (1, 4, 1),

    # 5-entry bracket: 8-slot bracket with BYEs
    (0, 5, 4),
    (1, 5, 2),
    (2, 5, 1),

    # 8-entry bracket
    (0, 8, 4),
    (1, 8, 2),
    (2, 8, 1),

    # 14-entry bracket: 16-slot bracket with BYEs
    (0, 14, 8),
    (1, 14, 4),
    (2, 14, 2),
    (3, 14, 1),

    # 16-entry bracket
    (0, 16, 8),
    (1, 16, 4),
    (2, 16, 2),
    (3, 16, 1),

    # 17-entry bracket: 32-slot bracket with BYEs
    (0, 17, 16),
    (1, 17, 8),
    (2, 17, 4),
    (3, 17, 2),
    (4, 17, 1)
])
def test_calculate_number_matchups_in_de_round_valid(round_index, number_de_entries, expected_matches):
    assert DEBracket._calculate_number_matchups_in_de_round(round_index=round_index, number_de_entries=number_de_entries) == expected_matches

@pytest.mark.parametrize('invalid_round_index_type', INVALID_INT_TYPES)
def test_calculate_number_matchups_in_de_round_invalid_round_index_type(invalid_round_index_type):
    valid_number_of_de_entries = 8
    with pytest.raises(TypeError):
        DEBracket._calculate_number_matchups_in_de_round(round_index=invalid_round_index_type, number_de_entries=valid_number_of_de_entries)

@pytest.mark.parametrize('invalid_round_index_negative', [-10, -5, -1])
def test_calculate_number_matchups_in_de_round_invalid_round_index_negative(invalid_round_index_negative):
    valid_number_of_de_entries = 11
    with pytest.raises(ValueError):
        DEBracket._calculate_number_matchups_in_de_round(round_index=invalid_round_index_negative, number_de_entries=valid_number_of_de_entries)

@pytest.mark.parametrize('invalid_number_de_entries_type', INVALID_INT_TYPES)
def test_calculate_number_matchups_in_de_round_invalid_number_de_entries_type(invalid_number_de_entries_type):
    with pytest.raises(TypeError):
        DEBracket._calculate_number_matchups_in_de_round(round_index=0, number_de_entries=invalid_number_de_entries_type)

@pytest.mark.parametrize('invalid_number_de_entries_value', [-10, -1, 0, 1])
def test_calculate_number_matchups_in_de_round_invalid_number_de_entries_value(invalid_number_de_entries_value):
    with pytest.raises(ValueError):
        DEBracket._calculate_number_matchups_in_de_round(round_index=0, number_de_entries=invalid_number_de_entries_value)

@pytest.mark.parametrize(('round_index', 'number_de_entries'), [
    (1, 2),
    (2, 3),
    (3, 6),
    (4, 14),
    (5, 17)
])
def test_calculate_number_matchups_in_de_round_invalid_round_index_greater_than_maximum(round_index, number_de_entries):
    with pytest.raises(ValueError):
        DEBracket._calculate_number_matchups_in_de_round(round_index=round_index, number_de_entries=number_de_entries)
