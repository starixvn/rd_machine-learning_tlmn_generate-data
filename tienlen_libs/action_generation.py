from .card import Card
from .utils import Utils
from .constant import ComboType
import time
import random
from itertools import chain

class ActionGenerator(object):
    
    def __init__(self):

        self.func_get_list_possible_action = {
            ComboType.SINGLE: self.get_only_single_card,
            ComboType.SINGLE_DEUCE: self.get_single_quartet_double_sequence,
            ComboType.PAIR: self.get_only_pair_card,
            ComboType.PAIR_DEUCE: self.get_pair_quartet_double_sequence_four,
            ComboType.TRIPLET: self.get_only_triplet_card,
            ComboType.QUARTET: self.get_quartet_double_sequence_four,
            ComboType.SEQUENCE: self.get_only_sequence,
            ComboType.DOUBLE_SEQUENCE_THREE: self.get_quartet_double_sequence,
            ComboType.DOUBLE_SEQUENCE_FOUR: self.get_only_double_sequence_four,
            ComboType.PASS: self.get_all_possible_combo,
        }

        self.utils = Utils()

    @staticmethod
    def detect_sequence_based_on_rank(list_rank):
        assert len(list_rank) == len(set(list_rank)), "List contains duplicate elements"
        list_rank.sort()    #Preprocessing
        n = len(list_rank)

        for i in range(n - 2):
            start = list_rank[i]
            for j in range(i + 3, n + 1):
                end = list_rank[j - 1]
                if end - start != j - i - 1:
                    break
                yield list_rank[i:j]

    @staticmethod
    def is_double_sequence_n(rank_sequence_card, n=None):
        if n is not None and len(rank_sequence_card) != n: 
            return False
        for cards in rank_sequence_card:
            if len(cards) < 2:
                return False
        return True

    @staticmethod
    def generate_double_sequence(rank_sequence_cards):
        assert all(sorted(elem) == elem for elem in rank_sequence_cards)
        return tuple([card for cards in rank_sequence_cards 
                                for card in (cards[0], cards[1])])

    @classmethod
    def generate_regular_sequence(cls, rank_sequence_cards):
        tmp = list(chain.from_iterable(rank_sequence_cards))
        assert tmp == sorted(tmp)
        sequence = [cards[0] for cards in rank_sequence_cards[:-1]]
        max_rank_cards = rank_sequence_cards[-1]
        for single_card in cls.get_single_card(max_rank_cards, len(max_rank_cards)):
            yield tuple(sequence + [single_card])

    @classmethod
    def get_sequence_double_sequence(cls, frequency_stats, 
                                     get_sequence=True, 
                                     get_double_sequence_three=True,
                                     get_double_sequence_four=True):
        list_rank = [rank for rank in frequency_stats.keys() if rank != 12]

        for rank_sequence in cls.detect_sequence_based_on_rank(list_rank):
            rank_sequence_cards = [frequency_stats[rank] for rank in rank_sequence]
            
            if get_double_sequence_three:
                if cls.is_double_sequence_n(rank_sequence_cards, 3):
                    yield cls.generate_double_sequence(rank_sequence_cards)

            if get_double_sequence_four:
                if cls.is_double_sequence_n(rank_sequence_cards, 4):
                    yield cls.generate_double_sequence(rank_sequence_cards)
                
            if get_sequence:
                yield from cls.generate_regular_sequence(rank_sequence_cards)

    @classmethod
    def get_only_sequence(cls, frequency_stats):
        yield from cls.get_sequence_double_sequence(frequency_stats, get_sequence=True, 
                                                                    get_double_sequence_three=False, 
                                                                    get_double_sequence_four=False)

    @classmethod
    def get_only_double_sequence_four(cls, frequency_stats):
        yield from cls.get_sequence_double_sequence(frequency_stats, get_sequence=False, 
                                                                    get_double_sequence_three=False, 
                                                                    get_double_sequence_four=True)
        
    @classmethod
    def get_double_sequence_three_and_four(cls, frequency_stats):
        yield from cls.get_sequence_double_sequence(frequency_stats, get_sequence=False, 
                                                                    get_double_sequence_three=True, 
                                                                    get_double_sequence_four=True)

    @staticmethod
    def get_single_card_from_pair(cards):
        if cards[1] - cards[0] == 1:
            yield cards[0]
        else:
            for card in cards:
                yield card

    @staticmethod
    def get_single_card_from_triplet(cards):
        max_min_diff = cards[2] - cards[0]
        if max_min_diff == 2:
            yield cards[0]
        else:
            assert max_min_diff == 3, f"Invalid cards: {cards}"
            if cards[1] - cards[0] == 1:
                yield cards[0]
                yield cards[2]
            else:
                yield cards[0]
                yield cards[1]

    @classmethod
    def get_single_card(cls, cards, n_cards):
        if n_cards in [1, 4]:
            yield cards[0]
        elif n_cards == 2:
            yield from cls.get_single_card_from_pair(cards)
        elif n_cards == 3:
            yield from cls.get_single_card_from_triplet(cards)
        else:
            raise ValueError(f"Invalid cards: {cards}")

    @classmethod
    def get_single_pair_triplet_quartet(cls, frequency_stats, get_single=True, 
                                                            get_pair=True, 
                                                            get_triplet=True, 
                                                            get_quartet=True):        
        for cards in frequency_stats.values():
            assert cards == sorted(cards)
            cards = tuple(cards)
            n_cards = len(cards)

            if get_single:
                for single_card in cls.get_single_card(cards, n_cards):
                    yield (single_card,)
            
            if get_quartet:
                if n_cards == 4:
                    yield cards

            if get_pair:
                if n_cards >= 2:
                    yield cards[:2]

            if get_triplet:
                if n_cards >= 3:
                    yield cards[:3]

    @classmethod
    def get_only_single_card(cls, frequency_stats):
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=True, 
                                                                        get_pair=False, 
                                                                        get_triplet=False, 
                                                                        get_quartet=False)

    @classmethod
    def get_single_quartet_double_sequence(cls, frequency_stats):
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=True, 
                                                                        get_pair=False, 
                                                                        get_triplet=False, 
                                                                        get_quartet=True)
        yield from cls.get_double_sequence_three_and_four(frequency_stats)

    @classmethod
    def get_only_pair_card(cls, frequency_stats):
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=False, 
                                                                        get_pair=True, 
                                                                        get_triplet=False, 
                                                                        get_quartet=False)

    @classmethod
    def get_pair_quartet_double_sequence_four(cls, frequency_stats):
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=False, 
                                                                        get_pair=True, 
                                                                        get_triplet=False, 
                                                                        get_quartet=True)
        yield from cls.get_only_double_sequence_four(frequency_stats)

    @classmethod
    def get_only_triplet_card(cls, frequency_stats):
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=False, 
                                                                        get_pair=False, 
                                                                        get_triplet=True, 
                                                                        get_quartet=False)

    @classmethod
    def get_only_quartet_card(cls, frequency_stats):
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=False, 
                                                                        get_pair=False, 
                                                                        get_triplet=False, 
                                                                        get_quartet=True)

    @classmethod
    def get_quartet_double_sequence_four(cls, frequency_stats):
        yield from cls.get_only_quartet_card(frequency_stats)
        yield from cls.get_only_double_sequence_four(frequency_stats)

    @classmethod
    def get_quartet_double_sequence(cls, frequency_stats):
        yield from cls.get_only_quartet_card(frequency_stats)
        yield from cls.get_double_sequence_three_and_four(frequency_stats)

    @classmethod
    def get_all_possible_combo(cls, frequency_stats):
        yield from cls.get_sequence_double_sequence(frequency_stats, get_sequence=True, 
                                                                    get_double_sequence_three=True,
                                                                    get_double_sequence_four=True)
        yield from cls.get_single_pair_triplet_quartet(frequency_stats, get_single=True, 
                                                                        get_pair=True, 
                                                                        get_triplet=True, 
                                                                        get_quartet=True)

    def get_list_valid_action(self, my_card, opponent_move_card):
        opponent_move_card = tuple(opponent_move_card)
        frequency_stats = self.utils.stats_frequency_of_card(my_card)
        opponent_combo_type = self.utils.get_combo_type(opponent_move_card)

        list_possible_action = self.func_get_list_possible_action[opponent_combo_type](frequency_stats)
        list_valid_action = [action for action in list_possible_action 
                        if self.utils.compare(action, opponent_move_card, opponent_combo_type)]
        if len(opponent_move_card) > 0: list_valid_action.append(tuple())
        return list_valid_action
    
    def choose_random_valid_action(self, my_card, opponent_move_card):
        list_valid_action = self.get_list_valid_action(my_card, opponent_move_card)
        return random.choice(list_valid_action)
          

if __name__ == "__main__":
    start_time = time.time()

    pass

    end_time = time.time()
    print(f"Elasped time: {end_time - start_time} seconds")