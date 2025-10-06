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
    assert reward.get_penalized_deuce_quartet_double_sequence(tuple(player_card)) == expected

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


@pytest.mark.parametrize("input, expected", 
[
    ([0, 1, 2, 3, 47], 0),
    ([0, 1, 2, 3, 47, 48], 1),
    ([0, 1, 2, 3, 48, 50], 2),
    ([0, 1, 2, 3, 49, 51], 2),
    ([0, 1, 2, 3, 40, 50], 1),
    ([0, 1, 2, 3, 48, 49, 51], 3),
    ([50, 1, 2, 3, 48, 49, 51], 4),
    ([0, 1, 2, 3, 50, 51], 2),
    ([0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2], 0),
    ([0, 10, 20, 30, 40], 0),
    ([0, 11, 22, 30, 48, 49, 50, 51], 4),
])
def test_count_n_deuce_in_card(reward, input, expected):
    assert reward.count_n_deuce_in_card(input) == expected


@pytest.mark.parametrize("input, expected", 
[
    ("3s 3c 3d", 0),
    ("4s", 0),
    ("6c 8s", 0),
    ("3s 3c 3d 3h", 1),
    ("4s 4c 4d 4h", 1),
    ("5s 5c 5d 5h", 1),
    ("6s 6c 6d 6h", 1),
    ("7s 7c 7d 7h", 1),
    ("8s 8c 8d 8h", 1),
    ("9s 9c 9d 9h", 1),
    ("Ts Tc Td Th", 1),
    ("Js Jc Jd Jh", 1),
    ("Qs Qc Qd Qh", 1),
    ("Ks Kc Kd Kh", 1),
    ("As Ac Ad Ah", 1),
    ("3s 3c 4s 4c 5s 5c", 1),
    ("4s 4c 5s 5c 6s 6c", 1),
    ("5s 5c 6s 6c 7s 7c", 1),
    ("6s 6c 7s 7c 8s 8c", 1),
    ("7s 7c 8s 8c 9s 9c", 1),
    ("8s 8c 9s 9c Ts Tc", 1),
    ("9s 9c Ts Tc Js Jc", 1),
    ("Ts Tc Js Jc Qs Qc", 1),
    ("Js Jc Qs Qc Ks Kc", 1),
    ("Qs Qc Ks Kc As Ac", 1),
    ("3s 3c 4s 4c 5s 5c 6s 6c", 1),
    ("4s 4c 5s 5c 6s 6c 7s 7c", 1),
    ("5s 5c 6s 6c 7s 7c 8s 8c", 1),
    ("6s 6c 7s 7c 8s 8c 9s 9c", 1),
    ("7s 7c 8s 8c 9s 9c Ts Tc", 1),
    ("8s 8c 9s 9c Ts Tc Js Jc", 1),
    ("9s 9c Ts Tc Js Jc Qs Qc", 1),
    ("Ts Tc Js Jc Qs Qc Ks Kc", 1),
    ("Js Jc Qs Qc Ks Kc As Ac", 1),
    ("3s 3c 3d 3h 5s 5c 6s 6c", 1),
    ("4s 4c 4d 4h 6s 6c 7s 7c", 1),
    ("5s 5c 5d 5h 7s 7c 8s 8c", 1),
    ("6s 6c 6d 6h 8s 8c 9s 9c", 1),
    ("7s 7c 7d 7h 9s 9c Ts Tc", 1),
    ("8s 8c 8d 8h Ts Tc Js Jc", 1),
    ("9s 9c 9d 9h Js Jc Qs Qc", 1),
    ("Ts Tc Td Th Qs Qc Ks Kc", 1),
    ("Js Jc Jd Jh Ks Kc As Ac", 1),
    ("3s 3c 3d 3h 4s 4c 5s 5c 6s 6c", 2),
    ("4s 4c 4d 4h 5s 5c 6s 6c 7s 7c", 2),
    ("5s 5c 5d 5h 6s 6c 7s 7c 8s 8c", 2),
    ("6s 6c 6d 6h 7s 7c 8s 8c 9s 9c", 2),
    ("7s 7c 7d 7h 8s 8c 9s 9c Ts Tc", 2),
    ("8s 8c 8d 8h 9s 9c Ts Tc Js Jc", 2),
    ("9s 9c 9d 9h Ts Tc Js Jc Qs Qc", 2),
    ("Ts Tc Td Th Js Jc Qs Qc Ks Kc", 2),
    ("Js Jc Jd Jh Qs Qc Ks Kc As Ac", 2),
    ("Js Jc Jd Jh Qs Qc Ks Kc", 1),
    ("Ts Tc Js Jc Jd Jh Qs Qc", 1),
    ("Ts Tc Td Th Jd Jh Qs Qc Ks Kh", 2),
    ("Ts Tc Th Jd Qs Qc Ks Kh", 0),
    ("8s Ts Tc Jd Qs Qc Ks Kh", 0),
])
def test_count_n_distinct_special_case(reward, input, expected):
    player_card = tuple(Card.new(elem) for elem in input.split())
    assert reward.count_n_distinct_special_case(player_card) == expected


@pytest.mark.parametrize("input, expected", 
[
    ([(2,), (3,), (), ()], 1),
    ([(2,), (3,), (4,), ()], 2),
    ([(2,), (3,), (4,), (5,)], 3),
    ([(2, 10), (3,), (), ()], 1),
    ([(2, 12), (3,), (4,), ()], 2),
    ([(2, 20), (3,), (4,), (5, 6, 7)], 3),
    ([(), (3,), (), ()], 1),
    ([(), (3,), (4,), ()], 2),
    ([(), (3,), (4,), (5,)], 3),
    ([(), (3,), (4,), (5, 6, 7)], 3),
])
def test_cal_n_other_player_playing(reward, input, expected):
    assert reward.cal_n_other_player_playing(input) == expected


@pytest.mark.parametrize("input, expected", 
[
    (["2s", "2c", "2d 2h"], 4),
    (["2s 4s 4c 4d 4h", "2c", "2d 2h"], 5),
    (["2s 4s 4c 5d 5h 6s 6h", "2c 2h", "2d 8s 8c 8d 8h"], 6),
    (["5d 5h 6s 6h 7s 7d", "3c 4d 5h", "3s 4s Ah"], 1),
    (["As Ad Ah", "3c 4d 5h", "5d 5h 6s 6h 7s 7d"], 1),
    (["As Ad Ah", "5d 5h 6s 6h 7s 7d", "Ks Kh"], 1),
    (["4s", "5s", "8s"], 0),
    (["", "", ""], 0),
    (["4s", "", "8s"], 0),
    (["", "", "8s"], 0),
    (["4s", "", ""], 0),
    (["5c", "6h", ""], 0),
])
def test_count_n_deuce_special_case_other_player(reward, input, expected):
    other_player_card = [tuple(Card.new(elem) for elem in card_str.split()) for card_str in input]
    assert reward.count_n_deuce_special_case_other_player(other_player_card) == expected


@pytest.mark.parametrize("input, expected", 
[
    (["2s", "2c", "2d 2h"], True),
    (["2s 4s 4c 4d 4h", "2c", "2d 2h"], True),
    (["2s 4s 4c 5d 5h 6s 6h", "2c 2h", "2d 8s 8c 8d 8h"], True),
    (["5d 5h 6s 6h 7s 7d", "3c 4d 5h", "3s 4s Ah"], True),
    (["As Ad Ah", "3c 4d 5h", "5d 5h 6s 6h 7s 7d"], True),
    (["As Ad Ah", "5d 5h 6s 6h 7s 7d", "Ks Kh"], True),
    (["4s", "5s", "8s"], False),
    (["", "", ""], False),
    (["4s", "", "8s"], False),
    (["", "", "8s"], False),
    (["4s", "", ""], False),
    (["5c", "6h", ""], False),
])
def test_exist_deuce_special_case_other_player(reward, input, expected):
    other_player_card = [tuple(Card.new(elem) for elem in card_str.split()) for card_str in input]
    assert reward.exist_deuce_special_case_other_player(other_player_card) == expected


@pytest.mark.parametrize("input, expected", 
[
    ([(15, 27, 29, 38), (), (32,), ()], 0),
    ([(3, 19, 26, 33, 39), (0, 2, 5, 6, 12, 15), (), ()], 0),
    ([(), (41,), (5, 6, 20, 40), ()], 2),
    ([(), (1, 4, 11, 15, 17, 19, 22, 25, 31, 41, 43, 51), (8, 10, 23, 26, 29, 35, 37, 38, 44, 46), (2, 9, 12, 16, 21, 36, 42, 45, 47, 48, 50)], 4),
    ([(9, 20, 24, 25, 30), (), (), ()], 0),
    ([(9, 20, 24, 25, 30, 48), (), (), ()], -1),
    ([(9, 10, 13, 15, 16, 17), (), (), ()], -1),
])
def test_get_reward_more_than_2_players(reward, input, expected):
    assert reward.get_reward_more_than_2_players(input) == expected