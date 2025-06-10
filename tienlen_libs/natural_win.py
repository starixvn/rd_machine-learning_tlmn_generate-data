from .card import Card
from collections import defaultdict
from .action_generation import ActionGenerator


class NaturalWin(object):
    def __init__(self):
        self.action_generator = ActionGenerator()

    @staticmethod
    def map_suit_int_to_color_int(suit_int):
        """
        Normalize suit int to color int with the following mapping:
            + spade and club -> 0 (black color)
            + heart and diamond -> 1 (red color)
        """
        return suit_int // 2
    
    @staticmethod
    def is_natural_win_dragon(frequency_stats):
        return len(frequency_stats) == 13

    @staticmethod
    def is_natural_win_concolorous(set_color_int):
        return len(set_color_int) == 1

    def is_special_natural_win_double_sequence(self, frequency_stats):
        list_rank = [rank for rank in frequency_stats.keys() if rank != 12]

        for rank_sequence in self.action_generator.detect_sequence_based_on_rank(list_rank):
            rank_sequence_cards = [frequency_stats[rank] for rank in rank_sequence]

            if self.action_generator.is_double_sequence_n(rank_sequence_cards, n=None):
                if len(rank_sequence_cards) in [5, 6]:
                    return True
                if 0 in rank_sequence and 0 in frequency_stats[0]: # 3 spade in the double sequence
                    return True
        return False
    
    @staticmethod
    def is_natural_win_six_pair_or_two_quartet(frequency_stats):
        n_pair, n_quartet = 0, 0 
        for cards in frequency_stats.values():
            n_pair += (len(cards) // 2)
            n_quartet += (len(cards) // 4)
        return n_pair == 6 or n_quartet == 2
    
    @staticmethod
    def is_natural_win_quartet_2_or_3(board):
        board_set = set(board)
        quartet_3 = {0, 1, 2, 3}
        quartet_2 = {48, 49, 50, 51}
        if quartet_3.issubset(board_set) or quartet_2.issubset(board_set):
            return True
        return False

    def detect_natural_win(self, board):
        assert len(set(board)) == 13
        frequency_stats = defaultdict(list)
        set_color_int = set()

        for card_int in board:
            rank_int = Card.get_rank_int(card_int)
            frequency_stats[rank_int].append(card_int)

            suit_int = Card.get_suit_int(card_int)
            color_int = self.map_suit_int_to_color_int(suit_int)
            set_color_int.add(color_int)

        if self.is_natural_win_dragon(frequency_stats) or \
            self.is_natural_win_concolorous(set_color_int) or \
            self.is_special_natural_win_double_sequence(frequency_stats) or \
            self.is_natural_win_six_pair_or_two_quartet(frequency_stats) or \
            self.is_natural_win_quartet_2_or_3(board):
            return True
        return False
        