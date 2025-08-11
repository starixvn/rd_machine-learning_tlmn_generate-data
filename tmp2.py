from collections import defaultdict
import time
from tienlen_libs import Card, ActionGenerator, Utils, NaturalWin, Reward
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
from agent_bot.bot_2_players_honestly import Bot_2_players_honestly


class Bot_Simulation(object):
    def __init__(self):
        self.action_generator = ActionGenerator()
        self.utils = Utils()
        self.tuple_rule_based_bot_input = self.__create_tuple_rule_based_bot_input()
        self.map_rule_based_bot_input_to_card = self.__create_mapping_rule_based_bot_input_to_card()
        self.ctx = self.compile_rule_based_json_code_with_V8_engine()
        self.test_rule_based_bot()
        self.reward = Reward()
        self.medium_bot_reinforcement = Bot_2_players_honestly()
        
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
        print("Test 1 PASSED")

        result = self.ctx.call("AI", [], 
                               ["anh/03a", "anh/04a", "anh/05a", "anh/06a", "anh/07a"])
        assert set(result) == set(["anh/03a", "anh/04a", "anh/05a", "anh/06a", "anh/07a"])
        print("Test 2 PASSED")

        result = self.ctx.call("AI", ["anh/10a", "anh/10b"], 
                               ["anh/11c", "anh/11d", "anh/12a", "anh/12b", "anh/12c", "anh/13c", 
                                "anh/14a", "anh/14b", "anh/15a", "anh/15b", "anh/16a", "anh/16b"])
        assert set(result) == set(["anh/12a", "anh/12c"])
        print("Test 3 PASSED")

        result = self.ctx.call("AI", ["anh/03a", "anh/04b", "anh/05c"], 
                               ["anh/07a", "anh/08b", "anh/09c", "anh/10a", "anh/11b"])
        assert set(result) == set(["anh/07a", "anh/08b", "anh/09c"])
        print("Test 4 PASSED")

        result = self.ctx.call("AI", ["anh/07a", "anh/07b", "anh/07c"], 
                               ["anh/09a", "anh/09b", "anh/09c", "anh/11d"])
        assert set(result) == set(["anh/09a", "anh/09b", "anh/09c"])
        print("Test 5 PASSED")

        result = self.ctx.call("AI", ["anh/04a", "anh/05b", "anh/06c", "anh/07d", "anh/08a"], 
                               ["anh/09b", "anh/10c", "anh/11d", "anh/12a", "anh/13b"])
        assert set(result) == set(["anh/09b", "anh/10c", "anh/11d", "anh/12a", "anh/13b"])
        print("Test 6 PASSED")

        result = self.ctx.call("AI", ["anh/03a"], 
                               ["anh/03b", "anh/04a", "anh/05c", "anh/06c", "anh/07b", "anh/08d", "anh/09a", 
                                "anh/10d", "anh/11b", "anh/12c", "anh/13a", "anh/14d", "anh/16b"])
        assert set(result) == set(["anh/16b"])
        print("Test 7 PASSED")
    
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

    def __check_medium_bot_state(self, medium_bot_state, player1_play_first):
        our_card, opponent_action, opponent_actions_card, \
                our_actions_card, deck_remain_, len_opponent_card = medium_bot_state

        assert len(set(our_card).union(set(our_actions_card))) == 13, "Union of our_card and our_actions_card must equal length 13"
        assert not set(our_card).intersection(set(our_actions_card)), "our_card and our_actions_card must be disjoint"
        assert set(opponent_action).issubset(set(opponent_actions_card)), "Opponent action must be subset of opponent actions card"
        assert len(deck_remain_) == 39 - len(opponent_actions_card), "Length of deck_remain must be equal to 39 - len(opponent_actions_card)"
        assert not set(deck_remain_).intersection(set(our_card)), "deck_remain must not intersect with our_card"
        assert not set(deck_remain_).intersection(set(our_actions_card)), "deck_remain must not intersect with our_actions_card"
        assert not set(deck_remain_).intersection(set(opponent_actions_card)), "deck_remain must not intersect with opponent_actions_card"
        assert isinstance(len_opponent_card, int), "len_opponent_card must be an integer"
        assert 1 <= len_opponent_card <= 13, "len_opponent_card must be between 1 and 13"
        assert player1_play_first in [0, 1], "player1_play_first must be 0 or 1"

    def recursive_depth_first_search(self, env, player1_card, player2_card, player1_action, 
                                     actions_card_player1, actions_card_player2, 
                                     deck_remain, player1_play_first):
        if len(player1_card) == 0 or len(player2_card) == 0:
            return
        state = (tuple(player2_card), tuple(player1_action), tuple(actions_card_player1), 
                 tuple(actions_card_player2), tuple(player1_card))
        if state in env: return
        
        list_valid_action_player2 = self.action_generator.get_list_valid_action(state[0], state[1])
        for player2_action in list_valid_action_player2:
            next_player2_card = [card for card in player2_card if card not in player2_action]
            next_actions_card_player2 = actions_card_player2 + list(player2_action)
            next_actions_card_player2.sort()
            next_deck_remain = [card for card in deck_remain if card not in player2_action]

            if len(next_player2_card) > 0:
                medium_bot_state = (tuple(player1_card), tuple(player2_action), tuple(next_actions_card_player2),
                                    tuple(actions_card_player1), tuple(next_deck_remain), len(next_player2_card))
                self.__check_medium_bot_state(medium_bot_state, player1_play_first)
                next_player1_action = self.medium_bot_reinforcement.choose_best_action_with_max_Q_value(
                    medium_bot_state, player1_play_first
                )
            else:
                next_player1_action = []

            next_player1_card = [card for card in player1_card if card not in next_player1_action]
            next_actions_card_player1 = actions_card_player1 + list(next_player1_action)
            next_actions_card_player1.sort()

            bomb_beat_2_versus_1 = self.reward.get_bomb_beating_penalty(player1_action, player2_action)
            bomb_beat_1_versus_2 = -1 * self.reward.get_bomb_beating_penalty(player2_action, next_player1_action)

            next_state = (tuple(next_player2_card), tuple(next_player1_action), tuple(next_actions_card_player1), 
                         tuple(next_actions_card_player2), tuple(next_player1_card))
            reward = self.reward.get_reward(next_player1_card, next_player2_card) + \
                        bomb_beat_2_versus_1 + bomb_beat_1_versus_2
            terminated = len(next_player1_card) == 0 or len(next_player2_card) == 0
            env[state][player2_action] = (next_state, reward, terminated)
            
            self.recursive_depth_first_search(env, next_player1_card, next_player2_card, next_player1_action, 
                                              next_actions_card_player1, next_actions_card_player2, 
                                              next_deck_remain, player1_play_first)
            
    def build_env(self, player1_card, player2_card, who_play_first):
        full_deck = list(range(52))
        deck_remain = [card for card in full_deck if card not in player1_card]
        assert len(deck_remain) == 39
        player1_action = self.run_rule_based_bot([], player1_card) if who_play_first == 1 else []
        print(f"Player {who_play_first} plays first", end=" ==> ")
        print(f"Player1 action: ", end=""); Card.print_pretty_cards(player1_action)
        player1_card = [card for card in player1_card if card not in player1_action]
        actions_card_player1 = list(player1_action)
        actions_card_player2 = []
        player1_play_first = 1 if who_play_first == 1 else 0
        
        env = defaultdict(dict)
        self.recursive_depth_first_search(env, player1_card, player2_card, player1_action, 
                                          actions_card_player1, actions_card_player2, 
                                          deck_remain, player1_play_first)
        return env


def write_data_to_file(src_data, idx_game, optimal_Q_table, 
                       player1_card, player2_card, who_play_first):
    computer_name = platform.node()
    computer_name = computer_name.replace("-", "")

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d-%H-%M-%S")

    process_id = os.getpid()

    filename = f"TLMN_{formatted_now}_{computer_name}_{process_id}_{idx_game}.pkl"
    path_to_file = os.path.join(src_data, filename)

    game_data = {
        "Q_table": optimal_Q_table,
        "player1_card": player1_card,
        "player2_card": player2_card,
        "who_play_first": who_play_first,
    }
    with open(path_to_file, "wb") as f:
        pickle.dump(game_data, f, protocol=pickle.HIGHEST_PROTOCOL)

def calculate_optimal_Q_table(env):
    value_table = value_iteration_RAM_optimize(env)
    optimal_Q_table = extract_optimal_Q_table_RAM_optimize(value_table, env)
    return optimal_Q_table

def run_bot_simulation(src_data):
    bot_simulation = Bot_Simulation()
    natural_win = NaturalWin()

    for idx_game in range(1):
        full_deck = list(range(52))
        np.random.shuffle(full_deck)
        player1_card = full_deck[:13]; player1_card.sort()
        player2_card = full_deck[13:26]; player2_card.sort()
        # player1_card = "3d 4c 5c 6s 6c 6d 6h 8s 9s 9d Td Jd Ah"
        # player1_card = [Card.new(elem) for elem in player1_card.split()]
        # player2_card = "3h 5d 5h 7s 7c 8d 8h 9c Qs Qh Ad 2s 2h"
        # player2_card = [Card.new(elem) for elem in player2_card.split()]
        print("\nPlayer1 cards: ", end=""); Card.print_pretty_cards(player1_card)
        print("Player2 cards: ", end=""); Card.print_pretty_cards(player2_card)
        if natural_win.detect_natural_win(player1_card) or natural_win.detect_natural_win(player2_card):
            print("Natural Win Detected: SKIPPING this game!!!")
            continue
        who_play_first = random.choice([2])
        env = bot_simulation.build_env(player1_card, player2_card, who_play_first)
        optimal_Q_table = calculate_optimal_Q_table(env)
        write_data_to_file(src_data, idx_game, optimal_Q_table, 
                           player1_card, player2_card, who_play_first)


if __name__ == "__main__":
    import cProfile
    src_data = r"C:\Users\justin.pham\Downloads\tmp"
    start_time = time.time()
    cProfile.run('run_bot_simulation(src_data)')
    # run_bot_simulation(src_data)
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")