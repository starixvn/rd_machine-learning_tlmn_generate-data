import pytest
from tienlen_libs import Reward
from main_full_4_3_fast import Bot_Simulation

@pytest.fixture
def reward():
    return Reward()

@pytest.fixture
def bot_simulation():
    return Bot_Simulation()