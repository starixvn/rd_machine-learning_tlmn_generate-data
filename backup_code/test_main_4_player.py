from collections import defaultdict
import time
from tienlen_libs import Card, ActionGenerator, Utils, NaturalWin, Reward
from tienlen_libs.constant import ComboType
import pickle
from multiprocessing import Pool, freeze_support
import os
import platform
import psutil
from datetime import datetime
import sys
import numpy as np
import random
from py_mini_racer import py_mini_racer
from py_rule_based import rule_based_json_code
from deep_Q_learning import value_iteration_RAM_optimize, extract_optimal_Q_table_RAM_optimize
from copy import deepcopy
import gc
from preprocessing_data_4_player import create_polars_table_of_state_action_return_encode


class Bot_Simulation(object):
    def __init__(self):
        self.action_generator = ActionGenerator()
        self.utils = Utils()
        self.tuple_rule_based_bot_input = self.__create_tuple_rule_based_bot_input()
        self.map_rule_based_bot_input_to_card = self.__create_mapping_rule_based_bot_input_to_card()
        self.ctx = self.compile_rule_based_json_code_with_V8_engine()
        self.test_rule_based_bot()
        self.reward = Reward()
        self.n_player = 4
        self.skip_int_encode = -1
        
    def __create_tuple_rule_based_bot_input(self):
        tuple_rule_based_bot_input = tuple(f"anh/{i:02}{j}" for i in list(range(3, 15)) + [16] 
                                                                for j in ["a", "b", "c", "d"])
        assert len(tuple_rule_based_bot_input) == 52
        assert all(len(x) == 7 for x in tuple_rule_based_bot_input)
        return tuple_rule_based_bot_input
    
    def __create_mapping_rule_based_bot_input_to_card(self):
        tuple_rule_based_bot_input = self.__create_tuple_rule_based_bot_input()
        map_rule_based_bot_input_to_card = {bot_input: idx 
                                    for idx, bot_input in enumerate(tuple_rule_based_bot_input)}
        return map_rule_based_bot_input_to_card
    
    def compile_rule_based_json_code_with_V8_engine(self):
        ctx = py_mini_racer.MiniRacer()
        ctx.eval(rule_based_json_code)
        return ctx

    def test_rule_based_bot(self):
        result = self.ctx.call("AI", ["anh/14a"], 
                                ["anh/14b", "anh/14c", "anh/16a", "anh/16b"])
        assert set(result) == set(["anh/14c"])

        result = self.ctx.call("AI", [], 
                               ["anh/03a", "anh/04a", "anh/05a", "anh/06a", "anh/07a"])
        assert set(result) == set(["anh/03a", "anh/04a", "anh/05a", "anh/06a", "anh/07a"])

        result = self.ctx.call("AI", ["anh/10a", "anh/10b"], 
                               ["anh/11c", "anh/11d", "anh/12a", "anh/12b", "anh/12c", "anh/13c", 
                                "anh/14a", "anh/14b", "anh/15a", "anh/15b", "anh/16a", "anh/16b"])
        assert set(result) == set(["anh/12a", "anh/12c"])

        result = self.ctx.call("AI", ["anh/03a", "anh/04b", "anh/05c"], 
                               ["anh/07a", "anh/08b", "anh/09c", "anh/10a", "anh/11b"])
        assert set(result) == set(["anh/07a", "anh/08b", "anh/09c"])

        result = self.ctx.call("AI", ["anh/07a", "anh/07b", "anh/07c"], 
                               ["anh/09a", "anh/09b", "anh/09c", "anh/11d"])
        assert set(result) == set(["anh/09a", "anh/09b", "anh/09c"])

        result = self.ctx.call("AI", ["anh/04a", "anh/05b", "anh/06c", "anh/07d", "anh/08a"], 
                               ["anh/09b", "anh/10c", "anh/11d", "anh/12a", "anh/13b"])
        assert set(result) == set(["anh/09b", "anh/10c", "anh/11d", "anh/12a", "anh/13b"])

        result = self.ctx.call("AI", ["anh/03a"], 
                               ["anh/03b", "anh/04a", "anh/05c", "anh/06c", "anh/07b", "anh/08d", "anh/09a", 
                                "anh/10d", "anh/11b", "anh/12c", "anh/13a", "anh/14d", "anh/16b"])
        assert set(result) == set(["anh/16b"])
    
    def convert_list_card_to_rule_based_bot_list_input(self, list_card):
        return [self.tuple_rule_based_bot_input[card] for card in list_card]
    
    def convert_rule_based_bot_list_input_to_list_card(self, bot_list_input):
        return [self.map_rule_based_bot_input_to_card[bot_input] for bot_input in bot_list_input]

    def run_rule_based_bot(self, opponent_move, my_card):
        assert list(opponent_move) == sorted(opponent_move)
        assert my_card == sorted(my_card)
        opponent_move_bot_input = self.convert_list_card_to_rule_based_bot_list_input(opponent_move)
        my_card_bot_input = self.convert_list_card_to_rule_based_bot_list_input(my_card)
        our_move_bot_format = self.ctx.call("AI", opponent_move_bot_input, my_card_bot_input)
        our_move = self.convert_rule_based_bot_list_input_to_list_card(our_move_bot_format)
        our_move.sort()
        return our_move

    def reset_player_skip(self):
        return {i: False for i in range(1, self.n_player + 1)}

    def get_player_action(self, player_id, player_id_card, last_action, turn):
        if turn == player_id:
            player_action = self.run_rule_based_bot([], player_id_card)
        else:
            player_action = self.run_rule_based_bot(last_action, player_id_card)
        return player_action

    def remove_list_card_from_player_card(self, player_card, list_card_to_remove):
        return [card for card in player_card if card not in list_card_to_remove]

    def update_player_card_and_player_skip(self, player_card, player_skip, 
                                           player_id, player_id_action):
        if len(player_id_action) > 0:                
            player_card[player_id] = self.remove_list_card_from_player_card(
                                        player_card[player_id], player_id_action)
            player_skip[player_id] = False
        else:
            player_skip[player_id] = True

    def update_turn(self, player_id, player_id_action, current_turn):
        turn = current_turn
        if len(player_id_action) > 0:
            turn = player_id
        return turn

    def get_list_valid_action_of_player(self, player_id, player_id_card, last_action, turn):
        if turn == player_id:
            list_valid_action = self.action_generator.get_list_valid_action(player_id_card, [])
        else:
            list_valid_action = self.action_generator.get_list_valid_action(player_id_card, last_action)
        return list_valid_action
    
    def is_deuce_or_pair_deuce(self, player_id_action):
        return self.utils.get_combo_type(player_id_action) in [ComboType.SINGLE_DEUCE, ComboType.PAIR_DEUCE]
    
    def get_list_valid_action_in_skip_condition(self, player_id, player_id_card, last_action, turn):
        assert turn != player_id, f"turn = {turn}, player_id = {player_id}"
        list_possible_action = []
        if self.is_deuce_or_pair_deuce(last_action):
            list_valid_action = self.get_list_valid_action_of_player(player_id, player_id_card, last_action, turn)
            for valid_action in list_valid_action:
                if self.utils.get_combo_type(valid_action) == ComboType.DOUBLE_SEQUENCE_FOUR:
                    list_possible_action.append(valid_action)
        list_possible_action.append(self.skip_int_encode)
        return list_possible_action

    def get_player_action_in_skip_condition(self, player_id, player_id_card, last_action, turn):
        assert turn != player_id, f"turn = {turn}, player_id = {player_id}"
        if self.is_deuce_or_pair_deuce(last_action):
            player_id_action = self.get_player_action(player_id, player_id_card, last_action, turn)
            if self.utils.get_combo_type(player_id_action) == ComboType.DOUBLE_SEQUENCE_FOUR:
                return player_id_action
        return self.skip_int_encode

    def run_round_for_other_players(self, player_card, player_action, player_skip, turn, ignore, player_id_start=2):
        for player_id in range(player_id_start, self.n_player + 1):
            if ignore:
                player_action[player_id] = self.skip_int_encode
                player_skip[player_id] = True
                continue

            if not player_skip[player_id]:
                if turn == player_id: player_skip = self.reset_player_skip()
                player_action[player_id] = self.get_player_action(
                                            player_id, player_card[player_id], player_action[turn], turn)
            else:
                player_action[player_id] = self.get_player_action_in_skip_condition(
                                            player_id, player_card[player_id], player_action[turn], turn)
            
            if player_action[player_id] != self.skip_int_encode:
                self.update_player_card_and_player_skip(player_card, player_skip, player_id, player_action[player_id])
                turn = self.update_turn(player_id, player_action[player_id], turn)

            if len(player_card[player_id]) == 0:
                ignore = True
        return player_card, player_action, player_skip, turn
    
    def encode_state(self, player_card, player_action, player_skip, turn):
        player_card_encode = tuple(tuple(player_card[i]) for i in range(1, self.n_player + 1))
        player_action_encode = tuple(
            tuple(player_action[i]) if player_action[i] != self.skip_int_encode else self.skip_int_encode
            for i in range(2, self.n_player + 1)
        )
        # player_skip_encode = tuple(player_skip[i] for i in range(1, self.n_player + 1))
        state = (player_card_encode, player_action_encode, turn)
        return state

    def recursive_depth_first_search(self, env, player_card, player_action, player_skip, turn):
        if any(len(player_card[i]) == 0 for i in range(1, self.n_player + 1)):
            assert sum(len(x) == 0 for x in player_card.values()) == 1
            return
        state = self.encode_state(player_card, player_action, player_skip, turn)
        if state in env: return
        
        if not player_skip[1]:
            if turn == 1: player_skip = self.reset_player_skip()
            list_valid_action_player1 = self.get_list_valid_action_of_player(1, player_card[1], player_action[turn], turn)
        else:
            list_valid_action_player1 = self.get_list_valid_action_in_skip_condition(1, player_card[1], player_action[turn], turn)
            assert self.skip_int_encode in list_valid_action_player1
        for valid_action_player1 in list_valid_action_player1:
            next_player_card = deepcopy(player_card)
            next_player_action = deepcopy(player_action)
            next_player_skip = deepcopy(player_skip)
            next_turn = turn

            next_player_action[1] = valid_action_player1
            if valid_action_player1 != self.skip_int_encode:
                self.update_player_card_and_player_skip(next_player_card, next_player_skip, 1, next_player_action[1])
                next_turn = self.update_turn(1, next_player_action[1], next_turn)
            ignore = (len(next_player_card[1]) == 0)

            next_player_card, next_player_action, next_player_skip, next_turn = self.run_round_for_other_players(
                                                next_player_card, next_player_action, next_player_skip, next_turn, ignore)
            
            next_state = self.encode_state(next_player_card, next_player_action, next_player_skip, next_turn)
            reward = self.reward.get_reward_more_than_2_players(next_player_card)
            env[state][valid_action_player1] = (next_state, reward)
            self.recursive_depth_first_search(env, next_player_card, next_player_action, next_player_skip, next_turn)
 
    def build_env(self, player_card, who_play_first):
        player_action = {i: [] for i in range(1, self.n_player + 1)}
        player_skip = self.reset_player_skip()
        turn = who_play_first
        if who_play_first != 1:
            player_card, player_action, player_skip, turn = self.run_round_for_other_players(
                                        player_card, player_action, player_skip, turn, False, player_id_start=who_play_first)

        env = defaultdict(dict)
        self.recursive_depth_first_search(env, player_card, player_action, player_skip, turn)
        return env


def write_data_to_file(src_data, idx_game, df_table):
    if len(df_table) == 0:
        return

    computer_name = platform.node()
    computer_name = computer_name.replace("-", "")

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d-%H-%M-%S")

    process_id = os.getpid()

    filename = f"TLMN_{formatted_now}_{computer_name}_{process_id}_{idx_game}.parquet"
    path_to_file = os.path.join(src_data, filename)
    
    df_table.write_parquet(path_to_file)

def calculate_optimal_Q_table(env):
    value_table = value_iteration_RAM_optimize(env)
    optimal_Q_table = extract_optimal_Q_table_RAM_optimize(value_table, env)
    return optimal_Q_table

def run_bot_simulation(src_data):
    bot_simulation = Bot_Simulation()
    natural_win = NaturalWin()

    for idx_game in range(10**6):
        try:
            full_deck = list(range(52))
            np.random.shuffle(full_deck)
            player1_card = full_deck[:13]; player1_card.sort()
            player2_card = full_deck[13:26]; player2_card.sort()
            player3_card = full_deck[26:39]; player3_card.sort()
            player4_card = full_deck[39:]; player4_card.sort()
            if natural_win.detect_natural_win(player1_card) or \
                natural_win.detect_natural_win(player2_card) or \
                natural_win.detect_natural_win(player3_card) or \
                natural_win.detect_natural_win(player4_card):
                # print("Natural Win Detected: SKIPPING this game!!!")
                continue
            player_card = {1: player1_card, 2: player2_card, 
                           3: player3_card, 4: player4_card}
            assert len(player_card) == bot_simulation.n_player
            who_play_first = random.choice(list(range(1, bot_simulation.n_player + 1)))
            env = bot_simulation.build_env(deepcopy(player_card), who_play_first)
            optimal_Q_table = calculate_optimal_Q_table(env)
            del env; gc.collect()
            game_data = {
                "Q_table": optimal_Q_table,
                "player_card": player_card,
                "who_play_first": who_play_first,
            }
            df_table = create_polars_table_of_state_action_return_encode(game_data)
            del optimal_Q_table, game_data; gc.collect()
            write_data_to_file(src_data, idx_game, df_table)
            del df_table; gc.collect()
        except Exception as e:
            print(f"\nThe ERRRRRRRROOOOOOOOOOOORRRRRRRRRR occurs:", e)
            for i in range(1, len(player_card) + 1):
                print(f"Player {i} cards: ", end=""); Card.print_pretty_cards(player_card[i])
            print(f"Player {who_play_first} plays first")

if __name__ == "__main__":
    n_process = psutil.cpu_count(logical=False) - 4
    src_data = r"\\10.5.10.44\data_see_opponent_card_4_players"

    print(f"The number of running process: {n_process}")
    print(f"Finding src_data status: {os.path.exists(src_data)}")
    if not os.path.exists(src_data):
        os.makedirs(src_data)
    if sys.platform.startswith('win'):
        freeze_support()
    with Pool(processes=n_process) as pool:
        pool.map(run_bot_simulation, [src_data] * n_process)