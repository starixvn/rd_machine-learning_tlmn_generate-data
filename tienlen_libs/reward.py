from .utils import Utils
from .action_generation import ActionGenerator
from .constant import ComboType
from functools import lru_cache

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
    def count_n_quartet(frequency_stats):
        n_quartet = 0
        for cards in frequency_stats.values():
            if len(cards) == 4:
                n_quartet += 1
        return n_quartet
    
    @staticmethod
    def count_n_double_sequence_three_and_four(frequency_stats):
        n_double_sequence_three = 0
        
        for double_sequence in ActionGenerator.get_double_sequence_three_and_four(frequency_stats):
            if len(double_sequence) == 6:
                n_double_sequence_three += 1
            elif len(double_sequence) == 8:
                return 0, 1
            
        return n_double_sequence_three, 0
    
    @staticmethod
    def count_n_long_sequence(frequency_stats, expected_len_long_sequence):
        n_long_sequence = 0
        for sequence in ActionGenerator.get_only_sequence(frequency_stats):
            if len(sequence) == expected_len_long_sequence:
                n_long_sequence += 1
        return n_long_sequence
    
    @staticmethod
    def detect_quartet_in_card(player_card):
        frequency_stats = Utils.stats_frequency_of_card(player_card)
        n_quartet = Reward.count_n_quartet(frequency_stats)
        assert n_quartet <= 1
        return (n_quartet > 0)
    
    @staticmethod
    def detect_double_sequence_three_in_card(player_card):
        frequency_stats = Utils.stats_frequency_of_card(player_card)
        n_double_sequence_three, _ = Reward.count_n_double_sequence_three_and_four(frequency_stats)
        return (n_double_sequence_three > 0)
    
    @staticmethod
    def detect_double_sequence_four_in_card(player_card):
        frequency_stats = Utils.stats_frequency_of_card(player_card)
        _, n_double_sequence_four = Reward.count_n_double_sequence_three_and_four(frequency_stats)
        return (n_double_sequence_four > 0)
    
    @staticmethod
    def detect_long_sequence_in_card(player_card, expected_len_long_sequence):
        frequency_stats = Utils.stats_frequency_of_card(player_card)
        n_long_sequence = Reward.count_n_long_sequence(frequency_stats, expected_len_long_sequence)
        if any(Reward.count_n_long_sequence(frequency_stats, exceed_expected_len) > 0 
            for exceed_expected_len in range(expected_len_long_sequence + 1, 13)):
            n_long_sequence = 0
        return (n_long_sequence > 0)

    @classmethod
    @lru_cache(maxsize=None)
    def get_penalized_deuce_quartet_double_sequence(cls, player_card):
        assert list(player_card) == sorted(player_card)
        assert len(player_card) > 0
        len_player_card = len(player_card)

        penalized = 0    
        if 48 in player_card:
            penalized += cls.BOMB_PENALTY['BLACK_DEUCE']
        if 49 in player_card:
            penalized += cls.BOMB_PENALTY['BLACK_DEUCE']
        if 50 in player_card:
            penalized += cls.BOMB_PENALTY['RED_DEUCE']
        if 51 in player_card:
            penalized += cls.BOMB_PENALTY['RED_DEUCE']
        
        if len_player_card >= 4:
            frequency_stats = Utils.stats_frequency_of_card(player_card)
            n_quartet = cls.count_n_quartet(frequency_stats)
            penalized += (cls.BOMB_PENALTY[ComboType.QUARTET] * n_quartet) 
        
            if len_player_card >= 6:
                n_double_sequence_three, n_double_sequence_four = \
                    Reward.count_n_double_sequence_three_and_four(frequency_stats)
                penalized += (cls.BOMB_PENALTY[ComboType.DOUBLE_SEQUENCE_THREE] * n_double_sequence_three)
                penalized += (cls.BOMB_PENALTY[ComboType.DOUBLE_SEQUENCE_FOUR] * n_double_sequence_four)

        return penalized
    
    @classmethod
    def get_reward(cls, player1_card, player2_card):
        len_player1_card = len(player1_card)
        len_player2_card = len(player2_card)

        if len_player2_card == 0:
            player1_penalized = cls.get_penalized_deuce_quartet_double_sequence(tuple(player1_card))
            return 1 + player1_penalized
        elif len_player1_card == 0:
            player2_penalized = cls.get_penalized_deuce_quartet_double_sequence(tuple(player2_card))
            return -1 * (1 + player2_penalized)
        else:
            return 0
                
    def get_reward_more_than_2_players(self, player_card):
        len_player1_card = len(player_card[1])
        other_player_lens = [len(player_card[player_id]) 
                            for player_id in player_card if player_id != 1]
        assert len(other_player_lens) == len(player_card) - 1

        if len_player1_card == 0:
            assert all(l > 0 for l in other_player_lens)
            return 1
        elif any(l == 0 for l in other_player_lens):
            assert len_player1_card > 0
            assert sum([l == 0 for l in other_player_lens]) == 1
            return -1
        else:
            assert len_player1_card > 0 and all(l > 0 for l in other_player_lens)
            return 0

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
    def cal_total_bomb_beating_reward(list_bomb_beat_reward):
        total_reward = 0
        i = 0
        n = len(list_bomb_beat_reward)

        while i < n:
            if list_bomb_beat_reward[i] == 0:
                i += 1
                continue

            temporary_reward, last_nonzero = 0, 0
            while i < n:
                cur_reward = list_bomb_beat_reward[i]
                i += 1
                if cur_reward != 0:
                    temporary_reward += abs(cur_reward)
                    last_nonzero = cur_reward
                else:
                    break
            
            assert last_nonzero != 0
            total_reward += (temporary_reward * (1 if last_nonzero > 0 else -1))
        return total_reward