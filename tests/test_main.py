import pytest
from tienlen_libs import Card


@pytest.mark.parametrize("input, expected", 
[
    ([True, True, True, True], [False, False, False, False]),
    ([True, False, True, False], [False, False, False, False]), 
    ([False, True, False, True], [False, False, False, False]),
    ([True, True, False, False], [False, False, False, False]),
    ([False, False, True, True], [False, False, False, False]),
    ([True, False, False, True], [False, False, False, False])
])
def test_reset_player_skip(bot_simulation_4_player, input, expected):
    assert bot_simulation_4_player.reset_player_skip(input) == expected