from .utils import Utils
from .action_generation import ActionGenerator

class Reward(object):
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

    def get_penalized_deuce_quartet_double_sequence(self, player_card):
        assert list(player_card) == sorted(player_card)
        assert len(player_card) > 0
        len_player_card = len(player_card)

        penalized = 0    
        if 48 in player_card:
            penalized += 2
        if 49 in player_card:
            penalized += 2
        if 50 in player_card:
            penalized += 4
        if 51 in player_card:
            penalized += 4
        
        if len_player_card >= 4:
            frequency_stats = self.utils.stats_frequency_of_card(player_card)
            penalized += (8 * Reward.count_n_quartet(frequency_stats)) 
        
            if len_player_card >= 6:
                n_double_sequence_three, n_double_sequence_four = \
                    Reward.count_n_double_sequence_three_and_four(frequency_stats)
                penalized += (4 * n_double_sequence_three)
                penalized += (8 * n_double_sequence_four)

        return penalized
    
    def get_reward(self, player1_card, player2_card):
        len_player1_card = len(player1_card)
        len_player2_card = len(player2_card)

        if len_player2_card == 0:
            # player1_penalized = self.get_penalized_deuce_quartet_double_sequence(player1_card)
            # return len_player1_card + player1_penalized
            return 1
        elif len_player1_card == 0:
            # player2_penalized = self.get_penalized_deuce_quartet_double_sequence(player2_card)
            # return -1 * (len_player2_card + player2_penalized)
            return 0
        else:
            # return 0
            raise ValueError("Invalid result for reward!!!")
                
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