# tests/conftest.py

import pytest

import constants

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from sample_names import SAMPLE_NAMES


# --- Fencers ---
@pytest.fixture
def fencer1() -> Fencer:
    return Fencer(id=constants.FENCER_ID1, display_name=SAMPLE_NAMES[0])

@pytest.fixture
def fencer2() -> Fencer:
    return Fencer(id=constants.FENCER_ID2, display_name=SAMPLE_NAMES[1])

@pytest.fixture
def fencer3() -> Fencer:
    return Fencer(id=constants.FENCER_ID3, display_name=SAMPLE_NAMES[2])

@pytest.fixture
def fencer4() -> Fencer:
    return Fencer(id=constants.FENCER_ID4, display_name=SAMPLE_NAMES[3])

@pytest.fixture
def fencer5() -> Fencer:
    return Fencer(id=constants.FENCER_ID5, display_name=SAMPLE_NAMES[4])

@pytest.fixture
def fencer6() -> Fencer:
    return Fencer(id=constants.FENCER_ID6, display_name=SAMPLE_NAMES[5])

@pytest.fixture
def fencer7() -> Fencer:
    return Fencer(id=constants.FENCER_ID7, display_name=SAMPLE_NAMES[6])


# --- Entries ---
@pytest.fixture
def entry1(fencer1: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID1, tournament_id=constants.TOURNY_ID1, fencer=fencer1)

@pytest.fixture
def entry2(fencer2: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID2, tournament_id=constants.TOURNY_ID1, fencer=fencer2)

@pytest.fixture
def entry3(fencer3: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID3, tournament_id=constants.TOURNY_ID1, fencer=fencer3)

@pytest.fixture
def entry4(fencer4: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID4, tournament_id=constants.TOURNY_ID1, fencer=fencer4)

@pytest.fixture
def entry5(fencer5: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID5, tournament_id=constants.TOURNY_ID1, fencer=fencer5)

@pytest.fixture
def entry6(fencer6: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID6, tournament_id=constants.TOURNY_ID1, fencer=fencer6)

@pytest.fixture
def entry7(fencer7: Fencer) -> TournamentEntry:
    return TournamentEntry(id=constants.ENTRY_ID7, tournament_id=constants.TOURNY_ID1, fencer=fencer7)