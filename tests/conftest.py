import pytest
from tienlen_libs import Reward
from test_main_full_4_3_editing import Bot_Simulation

@pytest.fixture
def reward():
    return Reward()

@pytest.fixture
def bot_simulation():
    return Bot_Simulation()