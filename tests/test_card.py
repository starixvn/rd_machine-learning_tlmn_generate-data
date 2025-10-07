from tienlen_libs import Card
import pytest

@pytest.mark.parametrize("card_int, expected", 
[
    (0, 0), (1, 0), (2, 0), (3, 0),
    (4, 1), (5, 1), (6, 1), (7, 1),
    (8, 2), (9, 2), (10, 2), (11, 2),
    (12, 3), (13, 3), (14, 3), (15, 3),
    (16, 4), (17, 4), (18, 4), (19, 4),
    (20, 5), (21, 5), (22, 5), (23, 5),
    (24, 6), (25, 6), (26, 6), (27, 6),
    (28, 7), (29, 7), (30, 7), (31, 7),
    (32, 8), (33, 8), (34, 8), (35, 8),
    (36, 9), (37, 9), (38, 9), (39, 9),
    (40, 10), (41, 10), (42, 10), (43, 10),
    (44, 11), (45, 11), (46, 11), (47, 11),
    (48, 12), (49, 12), (50, 12), (51, 12),
])
def test_get_rank_int(card_int, expected):
    assert Card.get_rank_int(card_int) == expected


@pytest.mark.parametrize("card_int, expected", 
[
    (0, 0), (1, 1), (2, 2), (3, 3),
    (4, 0), (5, 1), (6, 2), (7, 3),
    (8, 0), (9, 1), (10, 2), (11, 3),
    (12, 0), (13, 1), (14, 2), (15, 3),
    (16, 0), (17, 1), (18, 2), (19, 3),
    (20, 0), (21, 1), (22, 2), (23, 3),
    (24, 0), (25, 1), (26, 2), (27, 3),
    (28, 0), (29, 1), (30, 2), (31, 3),
    (32, 0), (33, 1), (34, 2), (35, 3),
    (36, 0), (37, 1), (38, 2), (39, 3),
    (40, 0), (41, 1), (42, 2), (43, 3),
    (44, 0), (45, 1), (46, 2), (47, 3),
    (48, 0), (49, 1), (50, 2), (51, 3),
])
def test_get_suit_int(card_int, expected):
    assert Card.get_suit_int(card_int) == expected


@pytest.mark.parametrize("card_int", list(range(52)))
def test_get_rank_and_suit_int(card_int):
    assert Card.get_rank_int(card_int)*4 + Card.get_suit_int(card_int) == card_int