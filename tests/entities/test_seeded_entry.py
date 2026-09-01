import pytest

from dataclasses import FrozenInstanceError

from entities.seeded_entry import SeededEntry

def test_seeded_entry_creation_valid_1(entry1):
    seeded_entry = SeededEntry(entry1, 1)

    assert seeded_entry.entry is entry1
    assert seeded_entry.seed == 1

def test_seeded_entry_creation_valid_2(entry2):
    seeded_entry = SeededEntry(entry2, 5)

    assert seeded_entry.entry is entry2
    assert seeded_entry.seed == 5

def test_seeded_entry_creation_valid_3(entry3):
    seeded_entry = SeededEntry(entry3, 99)

    assert seeded_entry.entry is entry3
    assert seeded_entry.seed == 99

def test_seeded_entry_cannot_mutate_attributes(entry1, entry2):
    seeded_entry = SeededEntry(entry1, 1)

    with pytest.raises(FrozenInstanceError):
        seeded_entry.entry = entry2
    
    with pytest.raises(FrozenInstanceError):
        seeded_entry.seed = 100

@pytest.mark.parametrize('invalid_entry_type', [None, 'Ben', 0, 1.0, False, True, [], (), {}, object()])
def test_seeded_entry_creation_invalid_entry_type(invalid_entry_type):
    with pytest.raises(TypeError):
        SeededEntry(invalid_entry_type, 1)

@pytest.mark.parametrize('invalid_seed_type', [None, 1.0, False, True, 'first', [], (), {}])
def test_seeded_entry_creation_invalid_seed_type(entry1, invalid_seed_type):
    with pytest.raises(TypeError):
        SeededEntry(entry1, invalid_seed_type)

@pytest.mark.parametrize('invalid_seed_value', [-10, -5, -1, 0])
def test_seeded_entry_creation_invalid_seed_value(entry1, invalid_seed_value):
    with pytest.raises(ValueError):
        SeededEntry(entry1, invalid_seed_value)
