import pytest
from fencer import Fencer

def test_fencer_creation_valid():
    fencer = Fencer(id=1, display_name='Sam')
    assert fencer.id == 1
    assert fencer.display_name == 'Sam'

def test_fencer_creation_valid_name_strip():
    fencer = Fencer(id=1, display_name='  Frank Jones ')
    assert fencer.id == 1
    assert fencer.display_name == 'Frank Jones'

def test_fencer_creation_invalid_id_type():
    with pytest.raises(TypeError):
        Fencer(id='Hello', display_name='Amy')

def test_fencer_creation_invalid_id_zero():
    with pytest.raises(ValueError):
        Fencer(id=0, display_name='Sam')

def test_fencer_creation_invalid_id_negative():
    with pytest.raises(ValueError):
        Fencer(id=-1, display_name='Steve')

def test_fencer_creation_invalid_display_name_type():
    with pytest.raises(TypeError):
        Fencer(id=1, display_name=100)

def test_fencer_creation_invalid_empty_input_string():
    with pytest.raises(ValueError):
        Fencer(id=1, display_name='')

def test_fencer_creation_invalid_whitespace_only_name():
    with pytest.raises(ValueError):
        Fencer(id=1, display_name='      ')

def test_fencer_creation_invalid_name_too_long():
    with pytest.raises(ValueError):
        Fencer(id=1, display_name='abcdefghijklmnopqrstuvwxyz0123456789')

def test_fencer_update_display_name_valid():
    fencer = Fencer(id=1, display_name='Katherine')
    fencer.update_display_name('Catherine')
    assert fencer.id == 1
    assert fencer.display_name == 'Catherine'

def test_fencer_update_display_name_valid_name_strip():
    fencer = Fencer(id=1, display_name='Katherine')
    fencer.update_display_name('    Catherine     ')
    assert fencer.id == 1
    assert fencer.display_name == 'Catherine'

def test_fencer_update_display_name_invalid_type():
    fencer = Fencer(id=1, display_name='Katherine')
    with pytest.raises(TypeError):
        fencer.update_display_name(1)

def test_fencer_update_display_name_invalid_empty_input_string():
    fencer = Fencer(id=1, display_name='Katherine')
    with pytest.raises(ValueError):
        fencer.update_display_name('')

def test_fencer_update_display_name_invalid_whitespace_only_input():
    fencer = Fencer(id=1, display_name='Katherine')
    with pytest.raises(ValueError):
        fencer.update_display_name('     ')

def test_fencer_equality():
    fencer1 = Fencer(id=1, display_name='Kate')
    fencer2 = Fencer(id=1, display_name='Kate')
    assert fencer1 == fencer2
    fencer3 = Fencer(id=1, display_name='Katie')
    assert fencer1 == fencer3

def test_fencer_inequality():
    fencer1 = Fencer(id=1, display_name='Kate')
    fencer2 = Fencer(id=2, display_name='Daniel')
    assert fencer1 != fencer2
    fencer3 = Fencer(id=3, display_name='Daniel')
    assert fencer2 != fencer3