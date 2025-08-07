import time
from tienlen_libs import Card, ActionGenerator, Utils
from tienlen_libs.constant import ComboType
import os
import numpy as np
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from keras.models import load_model


class Bot_2_players_honestly(object):
    def __init__(self,
                 model_dir=r"agent_bot/Bot_TLMN_solo_medium_level.keras"):
        self.action_generator = ActionGenerator()
        self.model_dir = model_dir
        self.MLP_model = load_model(self.model_dir)
     
    def generate_one_hot_encoding(self, cards: tuple[int], dimension: int = 52):
        return tuple(1 if i in cards else 0 for i in range(dimension))
    
    def encode_pair_deuce_color(self, action):
        """
        If Pair Deuce is Black Pair Deuce then return (1, 0, 0)
        If Pair Deuce is Red Pair Deuce then return (0, 1, 0)
        If Pair Deuce is Black Red Pair Deuce then return (0, 0, 1)
        """
        set_action = set(action)
        if set_action == {48, 49}:
            return (1, 0, 0)
        elif set_action == {50, 51}:
            return (0, 1, 0)
        else:
            assert set_action == {48, 50} or set_action == {48, 51} \
                or set_action == {49, 50} or set_action == {49, 51}
            return (0, 0, 1)

    def generate_action_encoding(self, action: tuple[int]):
        action_int_combo_type = Utils.get_int_combo_type(action)
        action_int_combo_type_encoding = self.generate_one_hot_encoding((action_int_combo_type,),
                                                                        dimension=19)
        assert action_int_combo_type_encoding.count(1) == 1        
        if len(action) > 0:
            max_card = max(action)
            max_card_encoding = self.generate_one_hot_encoding((max_card,))
            assert max_card_encoding.count(1) == 1
        else:
            max_card_encoding = tuple(0 for _ in range(52))

        if Utils.get_combo_type(action) == ComboType.PAIR_DEUCE:
            pair_deuce_color_encoding = self.encode_pair_deuce_color(action)
            assert pair_deuce_color_encoding.count(1) == 1
        else:
            pair_deuce_color_encoding = (0, 0, 0)

        return action_int_combo_type_encoding + max_card_encoding + pair_deuce_color_encoding
    
    def encode_state(self, state):
        player2_card, player1_action, actions_card_player1, actions_card_player2, deck_remain, len_player1_card = state
        player2_card_encoding = self.generate_one_hot_encoding(player2_card)
        player1_action_encoding = self.generate_action_encoding(player1_action)
        actions_card_player1_encoding = self.generate_one_hot_encoding(actions_card_player1)
        actions_card_player2_encoding = self.generate_one_hot_encoding(actions_card_player2)
        deck_remain_encoding = self.generate_one_hot_encoding(deck_remain)
        len_player1_card_encoding = self.generate_one_hot_encoding((len_player1_card-1,), dimension=13)

        state_encode = player2_card_encoding + player1_action_encoding + \
                    actions_card_player1_encoding + actions_card_player2_encoding + \
                    deck_remain_encoding + len_player1_card_encoding 
                    # action_encoding + (player2_play_first, expected_return)
        return state_encode
    
    def predict_Q_value(self, list_state_action_encode):
        state_action_array = np.array(list_state_action_encode, dtype=np.float64)
        assert all(x in [0, 1] for x in state_action_array.flatten()), "Input must contain only 0s and 1s"
        Q_values = self.MLP_model.predict(state_action_array, verbose=1).flatten()
        return Q_values
    
    def print_list_valid_action_player2(self, list_valid_action_player2):
        print(f"List valid action: ", end="")
        for action in list_valid_action_player2:
            if len(action) == 0:
                print("PASS", end="; ")
            else:
                Card.print_pretty_cards(action, end="; ")
        print()

    def choose_best_action_with_max_Q_value(self, state, I_play_first):
        state_encoding = self.encode_state(state)
        assert I_play_first in [1, 0]
        player2_play_first = I_play_first

        player2_card, player1_action, _, _, _, _ = state
        list_valid_action_player2 = self.action_generator.get_list_valid_action(player2_card, player1_action)
        # self.print_list_valid_action_player2(list_valid_action_player2)
        if len(list_valid_action_player2) == 1: return list_valid_action_player2[0]
        list_state_action_encode = []
        for action in list_valid_action_player2:
            action_encoding = self.generate_action_encoding(action)
            state_action_encode = state_encoding + action_encoding + (player2_play_first,)
            assert len(state_action_encode) == 370
            list_state_action_encode.append(state_action_encode)

        Q_values = self.predict_Q_value(list_state_action_encode)
        action_to_Q_value = dict(zip(list_valid_action_player2, Q_values))
        for action, Q_value in action_to_Q_value.items():
            print("Action: ", end=""); Card.print_pretty_cards(action, end=" => ")            
            print(f"Q_value = {float(Q_value)}")
        player2_action = max(action_to_Q_value.items(), key=lambda x: x[1])[0]
        return player2_action


if __name__ == "__main__":
    pass