from .utils import Utils
from .action_generation import ActionGenerator


class Reward(object):
    def __init__(self):
        self.action_generator = ActionGenerator()
        self.utils = Utils()

    def __count_n_quartet(self, frequency_stats):
        n_quartet = 0
        for cards in frequency_stats.values():
            if len(cards) == 4:
                n_quartet += 1
        return n_quartet
    
    def __count_n_double_sequence_three_and_four(self, frequency_stats):
        n_double_sequence_three = 0
        
        for double_sequence in ActionGenerator.get_double_sequence_three_and_four(frequency_stats):
            if len(double_sequence) == 6:
                n_double_sequence_three += 1
            elif len(double_sequence) == 8:
                return 0, 1
            
        return n_double_sequence_three, 0
    
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
            penalized += (8 * self.__count_n_quartet(frequency_stats)) 
        
            if len_player_card >= 6:
                n_double_sequence_three, n_double_sequence_four = \
                    self.__count_n_double_sequence_three_and_four(frequency_stats)
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
        
    def get_reward_3_player(self, player_card):
        len_player1_card = len(player_card[1])
        len_player2_card = len(player_card[2])
        len_player3_card = len(player_card[3])

        if len_player1_card == 0:
            assert len_player2_card > 0 and len_player3_card > 0
            return 1
        elif len_player2_card == 0 or len_player3_card == 0:
            assert len_player1_card > 0
            assert len_player2_card + len_player3_card == max(len_player2_card, len_player3_card)
            return -1
        else:
            assert len_player1_card > 0 and len_player2_card > 0 and len_player3_card > 0
            return 0