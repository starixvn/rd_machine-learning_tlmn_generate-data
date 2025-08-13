import time
from tienlen_libs import Card, ActionGenerator, Utils
from tienlen_libs.constant import ComboType
import os
import numpy as np
from functools import lru_cache
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path="agent_bot/Bot_TLMN_solo_medium_level_optimize.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
def infer_tflite(x):
    interpreter.set_tensor(input_details[0]['index'], x)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

class Bot_2_players_honestly(object):
    def __init__(self):
        self.action_generator = ActionGenerator()

    @lru_cache(maxsize=None) 
    def generate_one_hot_encoding(self, cards: tuple[int], dimension: int = 52):
        arr = np.zeros(dimension, dtype=np.float32)
        arr[list(cards)] = 1
        return arr

    @lru_cache(maxsize=None)
    def generate_action_encoding(self, action: tuple[int]):
        action_encode = np.zeros(19 + 52 + 3, dtype=np.float32)

        action_int_combo_type = Utils.get_int_combo_type(action)
        action_encode[action_int_combo_type] = 1

        if len(action) > 0:
            max_card = max(action)
            action_encode[19 + max_card] = 1

        if Utils.get_combo_type(action) == ComboType.PAIR_DEUCE:
            set_action = set(action)
            if set_action == {48, 49}:
                action_encode[19 + 52] = 1
            elif set_action == {50, 51}:
                action_encode[19 + 53] = 1
            else:
                action_encode[19 + 54] = 1

        return action_encode
    
    def encode_state(self, state):
        player2_card, player1_action, actions_card_player1, actions_card_player2, deck_remain, len_player1_card = state

        return np.concatenate([
            self.generate_one_hot_encoding(player2_card),
            self.generate_action_encoding(player1_action),
            self.generate_one_hot_encoding(actions_card_player1),
            self.generate_one_hot_encoding(actions_card_player2),
            self.generate_one_hot_encoding(deck_remain),
            self.generate_one_hot_encoding((len_player1_card-1,), dimension=13)
        ])
        
    def print_list_valid_action_player2(self, list_valid_action_player2):
        print(f"List valid action: ", end="")
        for action in list_valid_action_player2:
            if len(action) == 0:
                print("PASS", end="; ")
            else:
                Card.print_pretty_cards(action, end="; ")
        print()

    def predict_Q_value_tflite(self, state_action_array):
        return infer_tflite(state_action_array)[0][0]

    # @lru_cache(maxsize=None)
    def choose_best_action_with_max_Q_value(self, state, I_play_first):
        state_encoding = self.encode_state(state)
        assert I_play_first in [1, 0]

        player2_card, player1_action, _, _, _, _ = state
        list_valid_action_player2 = self.action_generator.get_list_valid_action(player2_card, player1_action)
        # self.print_list_valid_action_player2(list_valid_action_player2)
        if len(list_valid_action_player2) == 1: 
            return list_valid_action_player2[0]

        state_encoding_len = len(state_encoding)
        action_encoding_len = len(self.generate_action_encoding(()))
        state_action_len = state_encoding_len + action_encoding_len + 1  # +1 for I_play_first

        state_action_array = np.empty((1, state_action_len), dtype=np.float32)
        state_action_array[0, :state_encoding_len] = state_encoding
        state_action_array[0, -1] = I_play_first
        
        best_Q_value = -np.inf
        best_action = None
        for action in list_valid_action_player2:
            state_action_array[0, state_encoding_len:-1] = self.generate_action_encoding(action)
            Q_value = self.predict_Q_value_tflite(state_action_array)
            if Q_value > best_Q_value:
                best_Q_value, best_action = Q_value, action
        return best_action


if __name__ == "__main__":
    pass