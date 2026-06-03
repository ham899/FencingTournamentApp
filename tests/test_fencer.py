import pytest

from fencer import Fencer

### Constants ###
VALID_ID1 = 1
VALID_ID2 = 2
VALID_ID3 = 3
VALID_NAME = 'Sam'

def test_fencer_creation_valid():
    fencer = Fencer(id=VALID_ID1, display_name=VALID_NAME)
    assert fencer.id == VALID_ID1
    assert fencer.display_name == VALID_NAME

def test_fencer_creation_valid_name_strip():
    fencer = Fencer(id=VALID_ID1, display_name='  Frank Jones ')
    assert fencer.id == VALID_ID1
    assert fencer.display_name == 'Frank Jones'

@pytest.mark.parametrize('invalid_id_types', [
    None, '1', 1.0, True, [], {}
])
def test_fencer_creation_invalid_id_type(invalid_id_types):
    with pytest.raises(TypeError):
        Fencer(id=invalid_id_types, display_name=VALID_NAME)

def test_fencer_creation_invalid_id_zero():
    with pytest.raises(ValueError):
        Fencer(id=0, display_name=VALID_NAME)

def test_fencer_creation_invalid_id_negative():
    with pytest.raises(ValueError):
        Fencer(id=-1, display_name=VALID_NAME)

@pytest.mark.parametrize('invalid_display_name_types', [
    None, 1, 1.0, False, [], {}
])
def test_fencer_creation_invalid_display_name_type(invalid_display_name_types):
    with pytest.raises(TypeError):
        Fencer(id=VALID_ID1, display_name=invalid_display_name_types)

def test_fencer_creation_invalid_empty_input_string():
    with pytest.raises(ValueError):
        Fencer(id=VALID_ID1, display_name='')

def test_fencer_creation_invalid_whitespace_only_name():
    with pytest.raises(ValueError):
        Fencer(id=VALID_ID1, display_name='      ')

def test_fencer_creation_invalid_name_too_long():
    with pytest.raises(ValueError):
        Fencer(id=VALID_ID1, display_name='abcdefghijklmnopqrstuvwxyz0123456789')

def test_fencer_update_display_name_valid():
    fencer = Fencer(id=VALID_ID1, display_name='Katherine')
    fencer.update_display_name('Catherine')
    assert fencer.id == VALID_ID1
    assert fencer.display_name == 'Catherine'

def test_fencer_update_display_name_valid_name_strip():
    fencer = Fencer(id=VALID_ID1, display_name='Katherine')
    fencer.update_display_name('    Catherine     ')
    assert fencer.id == 1
    assert fencer.display_name == 'Catherine'

def test_fencer_update_display_name_invalid_type():
    fencer = Fencer(id=VALID_ID1, display_name='Katherine')
    with pytest.raises(TypeError):
        fencer.update_display_name(1)

def test_fencer_update_display_name_invalid_empty_input_string():
    fencer = Fencer(id=VALID_ID1, display_name='Katherine')
    with pytest.raises(ValueError):
        fencer.update_display_name('')

def test_fencer_update_display_name_invalid_whitespace_only_input():
    fencer = Fencer(id=VALID_ID1, display_name='Katherine')
    with pytest.raises(ValueError):
        fencer.update_display_name('     ')

def test_fencer_equality():
    fencer1 = Fencer(id=VALID_ID1, display_name='Kate')
    fencer2 = Fencer(id=VALID_ID1, display_name='Kate')
    assert fencer1 == fencer2 # Exact same fencer
    fencer3 = Fencer(id=VALID_ID1, display_name='Katie')
    assert fencer1 == fencer3 # Same ID, but name has changed - should still be equal

def test_fencer_inequality():
    fencer1 = Fencer(id=VALID_ID1, display_name='Kate')
    fencer2 = Fencer(id=VALID_ID2, display_name='Daniel')
    assert fencer1 != fencer2 # Two completely different fencers
    fencer3 = Fencer(id=VALID_ID3, display_name='Daniel')
    assert fencer2 != fencer3 # Different IDs mean different fencers, even if names are the same