import pytest
from tienlen_libs import Reward
from main import Bot_Simulation
from agent_bot.bot_2_players_honestly import Bot_2_players_honestly

@pytest.fixture
def reward():
    return Reward()

@pytest.fixture
def bot_2_players_honestly_cls():
    return Bot_2_players_honestly()

@pytest.fixture
def bot_simulation_4_player():
    return Bot_Simulation(n_player=4)