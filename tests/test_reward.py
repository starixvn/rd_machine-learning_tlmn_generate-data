import pytest
from tienlen_libs import Card

@pytest.mark.parametrize("player_card, expected", 
[
    ([Card.new("2s")], 2),
    ([Card.new("2s"), Card.new("2c")], 4),
    ([Card.new("2s"), Card.new("2h")], 6),
    ([Card.new("2s"), Card.new("2d")], 6),
    ([Card.new("2d"), Card.new("2h")], 8),
    ([Card.new("2s"), Card.new("2d"), Card.new("2h")], 10),
    ([Card.new("3s"), Card.new("3c"), Card.new("4d"), Card.new("4h"), Card.new("5c"), Card.new("5h")], 4),
    ([Card.new("3s"), Card.new("3c"), Card.new("3d"), Card.new("3h")], 8),
    ([Card.new("3s"), Card.new("3c"), Card.new("4d"), Card.new("4h"), Card.new("5c"), Card.new("5h"), Card.new("6s"), Card.new("6c")], 8),
    ([Card.new("3s"), Card.new("3c"), Card.new("3d"), Card.new("3h"), Card.new("4s"), Card.new("4c"), Card.new("5d"), Card.new("5h")], 12),
    ([Card.new("3s"), Card.new("3c"), Card.new("3d"), Card.new("3h"), Card.new("4s"), Card.new("4c"), 
      Card.new("5d"), Card.new("5h"), Card.new("6s"), Card.new("6c")], 16),
    ([Card.new("4s"), Card.new("4c"), Card.new("5d"), Card.new("5h"), Card.new("6s"), Card.new("6c"), Card.new("6h")], 4),
    ([Card.new("3s"), Card.new("4c"), Card.new("5d"), Card.new("6h"), Card.new("8c")], 0),
    ([Card.new("3s"), Card.new("4c"), Card.new("5d"), Card.new("6h"), Card.new("8c"), Card.new("2s")], 2),
])
def test_get_penalized_deuce_quartet_double_sequence(reward, player_card, expected):
    assert reward.get_penalized_deuce_quartet_double_sequence(player_card) == expected

@pytest.mark.parametrize("player1_card, player2_card, expected", 
[
    ([Card.new("2s")], [Card.new("4s"), Card.new("4c"), Card.new("4d"), Card.new("4h")], 0),
    ([], [Card.new("4s"), Card.new("4c"), Card.new("4d"), Card.new("4h")], -9),
    ([Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("5h")], [], 9),
    ([Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("2h")], [], 5),
    ([Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("2c")], [], 3),
    ([], [Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("2d")], -5),
    ([], [Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("2s")], -3),
    ([], [Card.new("5c"), Card.new("5d"), Card.new("2d"), Card.new("2h")], -9),
    ([Card.new("5c"), Card.new("5d"), Card.new("2s"), Card.new("2c")], [], 5),
    ([], [Card.new("3s"), Card.new("3c"), Card.new("4s"), Card.new("4c"), Card.new("5s"), Card.new("5c")], -5),
    ([Card.new("3s"), Card.new("3c"), Card.new("4s"), Card.new("4c"), Card.new("5s"), Card.new("5c")], [], 5),
    ([], [Card.new("4s"), Card.new("4h"), Card.new("5c"), Card.new("5d"), 
          Card.new("6s"), Card.new("6c"), Card.new("7s"), Card.new("7c")], -9),
])
def test_get_reward(reward, player1_card, player2_card, expected):
    assert reward.get_reward(player1_card, player2_card) == expected

@pytest.mark.parametrize("deuce_action, expected", 
[
    ([Card.new("2s")], 2),
    ([Card.new("2c")], 2),
    ([Card.new("2d")], 4),
    ([Card.new("2h")], 4),
    ([Card.new("2s"), Card.new("2c")], 4),
    ([Card.new("2s"), Card.new("2d")], 6),
    ([Card.new("2s"), Card.new("2h")], 6),
    ([Card.new("2c"), Card.new("2d")], 6),
    ([Card.new("2c"), Card.new("2h")], 6),
    ([Card.new("2d"), Card.new("2h")], 8),
    ([Card.new("2c"), Card.new("2d"), Card.new("2h")], 10),
])
def test_get_deuce_action_bomb_penalty(reward, deuce_action, expected):
    assert reward.get_deuce_action_bomb_penalty(deuce_action) == expected

@pytest.mark.parametrize("previous_action, current_action, expected", 
[
    ([Card.new("2s")], [Card.new("4s"), Card.new("4c"), Card.new("4d"), Card.new("4h")], 2),
    ([Card.new("2c")], [Card.new("4s"), Card.new("4c"), Card.new("4d"), Card.new("4h")], 2),
    ([Card.new("2d")], [Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("5h")], 4),
    ([Card.new("2h")], [Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("5h")], 4),
    ([], [Card.new("5s"), Card.new("5c"), Card.new("5d"), Card.new("5h")], 0),
    ([Card.new("3s"), Card.new("3c"), Card.new("4c"), Card.new("4h"), Card.new("5c"), Card.new("5d")],
     [Card.new("7s"), Card.new("7c"), Card.new("8c"), Card.new("8d"), Card.new("9s"), Card.new("9c")], 4),
    ([Card.new("3s"), Card.new("3c"), Card.new("3d"), Card.new("3h")],
     [Card.new("4s"), Card.new("4c"), Card.new("4d"), Card.new("4h")], 8),
    ([Card.new("3s"), Card.new("4c"), Card.new("5d"), Card.new("6h")],
     [Card.new("8s"), Card.new("9s"), Card.new("Ts"), Card.new("Js")], 0),
    ([Card.new("3s"), Card.new("3c"), Card.new("4c"), Card.new("4h"), 
      Card.new("5c"), Card.new("5d"), Card.new("6c"), Card.new("6d")],
     [Card.new("7s"), Card.new("7c"), Card.new("8c"), Card.new("8d"), 
      Card.new("9s"), Card.new("9c"), Card.new("Ts"), Card.new("Tc")], 8),
])
def test_get_bomb_beating_penalty(reward, previous_action, current_action, expected):
    assert reward.get_bomb_beating_penalty(previous_action, current_action) == expected

@pytest.mark.parametrize("input, expected", 
[
    ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0),
    ([0, 0, 2, 0, 0, 0, 0, 4, 0, 0, 0], 6),
    ([0, 0, 2, 0, 0, 0, 0, 4, -4, 0, 0, 0], -6),
    ([0, 0, 0, 0, 0, 0, 0, 5, 4, -4, 0, 0, 0], -13),
    ([0, 0, 0, 0, 0, 0, 0, -5, 4, 4, 0, 0, 0], 13),
    ([0, 0, 0, 0, 0, 0, 0, -5, 4, 4, 2, 0, 0], 15),
    ([0, 0, 0, 0, 0, 0, 0, -5, 4, 4, -2, 0, 0], -15),
    ([0, 0, 0, 0, 0, 0, 0, -5, 0, 4, 0, 0, 0], -1),
    ([0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2], 6),
    ([0, 0, 0, 0, 0, 0, 0, -4, 0, -2, 2], 0),
    ([0, 0, 0, 0, 0, -4, 4, -4, 0, -2], -14),
])
def test_cal_total_bomb_beating_reward(reward, input, expected):
    assert reward.cal_total_bomb_beating_reward(input) == expected