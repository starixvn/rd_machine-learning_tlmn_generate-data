import pytest
from tienlen_libs import Reward
from main import Bot_Simulation

@pytest.fixture
def reward():
    return Reward()

@pytest.fixture
def bot_simulation():
    return Bot_Simulation()