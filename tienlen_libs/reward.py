from .utils import Utils
from .action_generation import ActionGenerator
from .constant import ComboType

class Reward(object):
    BOMB_PENALTY = {
        'BLACK_DEUCE': 2,
        'RED_DEUCE': 4, 
        ComboType.DOUBLE_SEQUENCE_THREE: 4,
        ComboType.DOUBLE_SEQUENCE_FOUR: 8,
        ComboType.QUARTET: 8
    }

    def __init__(self):
        self.utils = Utils()
    
    @staticmethod
    def cal_n_other_player_playing(player_card):
        count = 0
        for cards in player_card[1:]:
            if cards:
                count += 1
        return count

    @classmethod    
    def get_deuce_action_bomb_penalty(cls, deuce_action):
        assert set(deuce_action).issubset({48, 49, 50, 51})
        penalty = 0
        for card in deuce_action:
            if card in [48, 49]:
                penalty += cls.BOMB_PENALTY['BLACK_DEUCE']
            else:
                penalty += cls.BOMB_PENALTY['RED_DEUCE']
        return penalty

    @classmethod
    def get_bomb_beating_penalty(cls, previous_action, current_action):
        if len(current_action) not in [4, 6, 8] or len(previous_action) == 0:
            return 0
        
        previous_action_combo_type = Utils.get_combo_type(previous_action)
        if previous_action_combo_type in [ComboType.SINGLE_DEUCE, ComboType.PAIR_DEUCE]:
            return cls.get_deuce_action_bomb_penalty(previous_action)
        return cls.BOMB_PENALTY.get(previous_action_combo_type, 0)

    @staticmethod
    def count_n_deuce_in_card(player_card):
        n_deuce = 0
        for c in player_card:
            if c >= 48:
                n_deuce += 1
        return n_deuce

    @classmethod
    def count_n_distinct_special_case(cls, player_card):
        len_player_card = len(player_card)
        assert len_player_card <= 13
        n_special_case = 0

        if len_player_card >= 4:
            frequency_stats = Utils.stats_frequency_of_card(player_card)

            quartet_rank = next((rank for rank, cards in frequency_stats.items() if len(cards) == 4), None) 
            if quartet_rank is not None:
                n_special_case += 1
                del frequency_stats[quartet_rank]
        
            if len_player_card >= 6:
                n_double_sequence_three, n_double_sequence_four = \
                    cls.count_n_double_sequence_three_and_four(frequency_stats)
                assert n_double_sequence_three + n_double_sequence_four <= 1
                n_special_case += (n_double_sequence_three + n_double_sequence_four)
        return n_special_case