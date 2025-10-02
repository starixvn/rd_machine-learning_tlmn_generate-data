import pytest
from tienlen_libs import Card


@pytest.mark.parametrize("player_skip, player_action, expected", 
[
    ([True, True, True, True], [(), (), (2,), (3,)], [False, False, False, False]),
    ([True, False, True, False], [(), (), (2,), (3,)], [False, False, False, False]), 
    ([False, True, False, True], [(), (), (2,), (3,)], [False, False, False, False]),
    ([True, True, False, False], [(), (), (2,), (3,)], [False, False, False, False]),
    ([False, False, True, True], [(), (), (2,), (3,)], [False, False, False, False]),
    ([True, False, False, True], [(), (), (2,), (3,)], [False, False, False, False]),

    ([True, True, True, True], [(), (), -2, (3,)], [False, False, True, False]),
    ([True, False, True, False], [(), (), -2, (3,)], [False, False, True, False]), 
    ([False, True, False, True], [(), (), -2, (3,)], [False, False, False, False]),
    ([True, True, False, False], [(), (), -2, (3,)], [False, False, False, False]),
    ([False, False, True, True], [(), (), -2, (3,)], [False, False, True, False]),
    ([True, False, False, True], [(), (), -2, (3,)], [False, False, False, False]),
])
def test_reset_player_skip(bot_simulation_4_player, player_skip, player_action, expected):
    bot_simulation_4_player.reset_player_skip(player_skip, player_action)
    assert player_skip == expected


@pytest.mark.parametrize("state, other_player_card, expected", 
[
    (((6, 15, 22, 24, 25, 26, 27), 
    (0, 3, 5, 8, 11, 13, 20, 28, 31, 41, 42), 
    (9, 10, 12, 14, 16, 18, 19, 29, 37, 38, 44, 46),
    (1, 4, 7, 23, 30, 34, 36, 40, 45, 48, 49),
    (), (), (), False, True, True, True, 0), 
    [(4, 7, 11, 12, 14, 18, 19, 30, 31, 37, 45),
    (0, 1, 5, 8, 20, 23, 28, 34, 36, 40, 44, 49),
    (3, 9, 10, 13, 16, 29, 38, 41, 42, 46, 48)],
    {(6,): 7, (15,): 8, (22,): 8, (24,): 2, (24, 25, 26, 27): 3, (24, 25): 2, (24, 25, 26): 2})
])
def test_calculte_max_reward_for_all_actions_of_state(bot_simulation_4_player, 
                                                    state, other_player_card, expected):
    res = bot_simulation_4_player.calculte_max_reward_for_all_actions_of_state(state, other_player_card)
    assert res == expected