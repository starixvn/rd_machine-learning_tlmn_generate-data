from .card import Card
from .constant import ComboType
from collections import defaultdict
from math import comb
from itertools import combinations


class Utils:

    mapping_len_to_type = {2: ComboType.PAIR, 3: ComboType.TRIPLET, 4: ComboType.QUARTET}
    mapping_len_to_double_sequence = {6: ComboType.DOUBLE_SEQUENCE_THREE, 
                                      8: ComboType.DOUBLE_SEQUENCE_FOUR}
    dict_combo_type_to_int = {
        ComboType.PASS: 0,
        ComboType.SINGLE: 1,
        ComboType.SINGLE_DEUCE: 2,
        ComboType.PAIR: 3,
        ComboType.PAIR_DEUCE: 4,
        ComboType.TRIPLET: 5,
        ComboType.QUARTET: 6,
        ComboType.DOUBLE_SEQUENCE_THREE: 7,
        ComboType.DOUBLE_SEQUENCE_FOUR: 8,
        ComboType.SEQUENCE: 9,
    }

    def __init__(self):
        pass

    @staticmethod
    def sort_cards(cards):
        return sorted(cards)
    
    @classmethod
    def get_combo_type(cls, cards):
        n_cards = len(cards)

        if n_cards == 0:
            return ComboType.PASS
        if n_cards == 1:
            if Card.get_rank_int(cards[0]) == 12:
                return ComboType.SINGLE_DEUCE
            else:
                return ComboType.SINGLE
        set_rank_int = {Card.get_rank_int(card) for card in cards}
        n_unique_rank = len(set_rank_int)
        if n_unique_rank == 1:
            if n_cards == 2 and set_rank_int == {12}:
                return ComboType.PAIR_DEUCE
            else:   
                return cls.mapping_len_to_type[n_cards]
        else:
            if n_unique_rank == n_cards:
                return ComboType.SEQUENCE
            else:
                assert 2 * n_unique_rank == n_cards, \
                    f"Invalid number of unique rank: {n_unique_rank} for {cards}"
                return cls.mapping_len_to_double_sequence[n_cards]
            
    @classmethod
    def get_int_combo_type(cls, cards):
        combo_type = cls.get_combo_type(cards)
        if combo_type == ComboType.SEQUENCE:
            return cls.dict_combo_type_to_int[combo_type] + (len(cards) - 3)
        else:
            return cls.dict_combo_type_to_int[combo_type]

    @staticmethod
    def stats_frequency_of_card(board):
        frequency_stats = defaultdict(list)
        for card_int in board:
            rank_int = Card.get_rank_int(card_int)
            frequency_stats[rank_int].append(card_int)       
        return frequency_stats

    @staticmethod
    def is_deuce_or_pair_deuce(action):
        n = len(action)
        return (n == 1 or n == 2) and Card.get_rank_int(action[0]) == 12

    @staticmethod
    def cal_total_n_combination(len_deck_remain, len_other_player_card):
        n = len_deck_remain
        assert sum(len_other_player_card) == n, \
                f"len_other_player_card = {len_other_player_card}, n = {n}"
        result = 1
        for k in len_other_player_card[:-1]:
            result *= comb(n, k)
            n -= k
        return result

    @classmethod
    def partition_by_sizes(cls, iterable, sizes): 
        if not sizes:
            yield []
            return

        first_size, *rest_sizes = sizes
        for first_group in combinations(iterable, first_size):
            remaining = set(iterable) - set(first_group)
            for rest_partition in cls.partition_by_sizes(remaining, rest_sizes):
                yield [first_group] + rest_partition