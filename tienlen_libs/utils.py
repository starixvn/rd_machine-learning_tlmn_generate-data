from .card import Card
from .constant import ComboType
from collections import defaultdict


class Utils:

    mapping_len_to_type = {2: ComboType.PAIR, 3: ComboType.TRIPLET, 4: ComboType.QUARTET}
    mapping_len_to_double_sequence = {6: ComboType.DOUBLE_SEQUENCE_THREE, 
                                      8: ComboType.DOUBLE_SEQUENCE_FOUR}

    def __init__(self):

        self.compare_two_combo_function = {
            ComboType.SINGLE: self.compare_two_single_card,
            ComboType.SINGLE_DEUCE: self.compare_special_card_with_single_deuce,
            ComboType.PAIR: self.compare_two_pair_cards,
            ComboType.PAIR_DEUCE: self.compare_special_card_with_pair_deuce,
            ComboType.TRIPLET: self.compare_two_triplet_quartet_cards,
            ComboType.QUARTET: self.compare_special_card_with_quartet,
            ComboType.SEQUENCE: self.compare_two_sequence,
            ComboType.DOUBLE_SEQUENCE_THREE: self.compare_special_card_with_double_sequence_three,
            ComboType.DOUBLE_SEQUENCE_FOUR: self.compare_special_card_with_double_sequence_four,
            ComboType.PASS: self.compare_two_pass,
        }

    @staticmethod
    def sort_cards(cards):
        return sorted(cards)
    
    @staticmethod
    def get_combo_type(cards):
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
                return Utils.mapping_len_to_type[n_cards]
        else:
            if n_unique_rank == n_cards:
                return ComboType.SEQUENCE
            else:
                assert 2 * n_unique_rank == n_cards, \
                    f"Invalid number of unique rank: {n_unique_rank} for {cards}"
                return Utils.mapping_len_to_double_sequence[n_cards]

    @staticmethod
    def stats_frequency_of_card(board):
        frequency_stats = defaultdict(list)
        for card_int in board:
            rank_int = Card.get_rank_int(card_int)
            frequency_stats[rank_int].append(card_int)       
        return frequency_stats

    @staticmethod
    def compare_two_single_card(single_card_1: tuple[Card], single_card_2: tuple[Card]) -> bool:
        assert len(single_card_1) == len(single_card_2) == 1, \
            f"Single card must be a single card {single_card_1} and {single_card_2}"
        return single_card_1[0] > single_card_2[0]

    @staticmethod
    def compare_special_card_with_single_deuce(special_card: tuple[Card], single_deuce: tuple[Card]) -> bool:
        assert Utils.get_combo_type(special_card) in [ComboType.SINGLE, ComboType.SINGLE_DEUCE,
                                                      ComboType.QUARTET, ComboType.DOUBLE_SEQUENCE_THREE,
                                                      ComboType.DOUBLE_SEQUENCE_FOUR], \
            f"Special card invalid: {special_card}"
        if len(special_card) == 1: 
            return Utils.compare_two_single_card(special_card, single_deuce)
        return True
    
    @staticmethod
    def compare_special_card_with_pair_deuce(special_card: tuple[Card], pair_deuce: tuple[Card]) -> bool:
        assert Utils.get_combo_type(special_card) in [ComboType.PAIR, ComboType.PAIR_DEUCE,
                                                      ComboType.QUARTET, ComboType.DOUBLE_SEQUENCE_FOUR], \
            f"Special card invalid: {special_card}"
        if len(special_card) == 2:
            return Utils.compare_two_pair_cards(special_card, pair_deuce)
        return True

    @staticmethod
    def compare_two_pair_cards(pair_1: tuple[Card], pair_2: tuple[Card]) -> bool:
        assert len(pair_1) == len(pair_2) == 2, \
            f"Pair cards must be a pair of cards {pair_1} and {pair_2}"
        assert max(pair_1) == pair_1[-1] and max(pair_2) == pair_2[-1]
        return pair_1[-1] > pair_2[-1]

    @staticmethod
    def compare_two_triplet_quartet_cards(cards_1: tuple[Card], cards_2: tuple[Card]) -> bool:
        assert len(cards_1) == len(cards_2) == 3 or len(cards_1) == len(cards_2) == 4
        return cards_1[0] > cards_2[0]

    @staticmethod
    def compare_special_card_with_quartet(special_card: tuple[Card], quartet: tuple[Card]) -> bool:
        assert Utils.get_combo_type(special_card) in [ComboType.QUARTET, ComboType.DOUBLE_SEQUENCE_FOUR], \
            f"Special card invalid: {special_card}"
        if len(special_card) == 4:
            return Utils.compare_two_triplet_quartet_cards(special_card, quartet)
        return True

    @staticmethod
    def compare_two_sequence(cards_1: tuple[Card], cards_2: tuple[Card]) -> bool:
        if len(cards_1) != len(cards_2): return False
        assert max(cards_1) == cards_1[-1] and max(cards_2) == cards_2[-1]
        return cards_1[-1] > cards_2[-1]
    
    @staticmethod
    def compare_special_card_with_double_sequence_three(special_card: tuple[Card], 
                                                        double_sequence_three: tuple[Card]) -> bool:
        assert Utils.get_combo_type(special_card) in [ComboType.QUARTET, ComboType.DOUBLE_SEQUENCE_THREE,
                                                      ComboType.DOUBLE_SEQUENCE_FOUR], \
            f"Special card invalid: {special_card}"
        if len(special_card) == 6:
            return Utils.compare_two_sequence(special_card, double_sequence_three)
        return True

    @staticmethod
    def compare_special_card_with_double_sequence_four(special_card: tuple[Card], 
                                                       double_sequence_four: tuple[Card]) -> bool:
        assert Utils.get_combo_type(special_card) == ComboType.DOUBLE_SEQUENCE_FOUR
        return Utils.compare_two_sequence(special_card, double_sequence_four)

    @staticmethod
    def compare_two_pass(*args) -> bool:
        return True

    def compare(self, cards_1: tuple[Card], cards_2: tuple[Card], combo_type: ComboType) -> bool:
        return self.compare_two_combo_function[combo_type](cards_1, cards_2)
