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
from deep_Q_learning import value_iteration_RAM_optimize, extract_optimal_Q_table_RAM_optimize
from agent_bot.bot_2_players_honestly import Bot_2_players_honestly
import gc
import polars as pl
from functools import lru_cache


class Preprocessing_2_player(object):
    def __init__(self):
        pass

    def generate_one_hot_encoding(self, cards: tuple[int], dimension: int = 52):
        return tuple(True if i in cards else False for i in range(dimension))

    def encode_pair_deuce_color(self, action):
        """
        If Pair Deuce is Black Pair Deuce then return (True, False, False)
        If Pair Deuce is Red Pair Deuce then return (False, True, False)
        If Pair Deuce is Black Red Pair Deuce then return (False, False, True)
        """
        set_action = set(action)
        if set_action == {48, 49}:
            return (True, False, False)
        elif set_action == {50, 51}:
            return (False, True, False)
        else:
            assert set_action == {48, 50} or set_action == {48, 51} \
                or set_action == {49, 50} or set_action == {49, 51}
            return (False, False, True)

    @lru_cache(maxsize=None)
    def generate_action_encoding(self, action: tuple[int]):
        action_int_combo_type = Utils.get_int_combo_type(action)
        action_int_combo_type_encoding = self.generate_one_hot_encoding((action_int_combo_type,),
                                                                dimension=19)
        assert action_int_combo_type_encoding.count(True) == 1        
        if len(action) > 0:
            max_card = max(action)
            max_card_encoding = self.generate_one_hot_encoding((max_card,))
            assert max_card_encoding.count(True) == 1
        else:
            max_card_encoding = tuple(False for _ in range(52))

        if Utils.get_combo_type(action) == ComboType.PAIR_DEUCE:
            pair_deuce_color_encoding = self.encode_pair_deuce_color(action)
            assert pair_deuce_color_encoding.count(True) == 1
        else:
            pair_deuce_color_encoding = (False, False, False)

        return action_int_combo_type_encoding + max_card_encoding + pair_deuce_color_encoding

    def generate_list_state_action_return_encode(self, Q_table, who_play_first):
        player2_play_first = True if who_play_first == 2 else False
        for state in Q_table:
            if len(Q_table[state]) <= 1: continue
            player2_card, player1_action, actions_card_player1, actions_card_player2, player1_card = state

            player2_card_encoding = self.generate_one_hot_encoding(player2_card)
            player1_action_encoding = self.generate_action_encoding(player1_action)
            actions_card_player1_encoding = self.generate_one_hot_encoding(actions_card_player1)
            actions_card_player2_encoding = self.generate_one_hot_encoding(actions_card_player2)
            player1_card_encoding = self.generate_one_hot_encoding(player1_card)

            for action in Q_table[state]:
                expected_return = Q_table[state][action]
                assert -100 <= expected_return <= 100

                action_encoding = self.generate_action_encoding(action)

                state_action_return_encode = player2_card_encoding + player1_action_encoding + \
                                            actions_card_player1_encoding + actions_card_player2_encoding + \
                                            player1_card_encoding + action_encoding + \
                                            (player2_play_first, expected_return)
                yield state_action_return_encode

    def create_polars_table_of_state_action_return_encode(self, Q_table, who_play_first):
        schema_columns = [(f"player2_card_{i}", pl.Boolean) for i in range(52)] + \
                        [(f"player1_action_combo_type_{i}", pl.Boolean) for i in range(19)] + \
                        [(f"player1_action_max_card_{i}", pl.Boolean) for i in range(52)] + \
                        [(f"player1_action_black_pair_deuce", pl.Boolean)] + \
                        [(f"player1_action_red_pair_deuce", pl.Boolean)] + \
                        [(f"player1_action_mixed_pair_deuce", pl.Boolean)] + \
                        [(f"actions_card_player1_{i}", pl.Boolean) for i in range(52)] + \
                        [(f"actions_card_player2_{i}", pl.Boolean) for i in range(52)] + \
                        [(f"player1_card_{i}", pl.Boolean) for i in range(52)] + \
                        [(f"action_combo_type_{i}", pl.Boolean) for i in range(19)] + \
                        [(f"action_max_card_{i}", pl.Boolean) for i in range(52)] + \
                        [(f"action_black_pair_deuce", pl.Boolean)] + \
                        [(f"action_red_pair_deuce", pl.Boolean)] + \
                        [(f"action_mixed_pair_deuce", pl.Boolean)] + \
                        [(f"player2_play_first", pl.Boolean)] + \
                        [(f"expected_return", pl.Int8)]
        df_table = pl.DataFrame(self.generate_list_state_action_return_encode(Q_table, who_play_first), 
                                schema=schema_columns)
        self.generate_action_encoding.cache_clear()
        return df_table


class Bot_Simulation(object):
    def __init__(self):
        self.action_generator = ActionGenerator()
        self.utils = Utils()
        self.reward = Reward()
        self.medium_bot_reinforcement = Bot_2_players_honestly()
        
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

    def recursive_depth_first_search_reward(self, env, player1_card, player2_card, player1_action, 
                                                 actions_card_player1, actions_card_player2,
                                                 deck_remain_player2):
        if len(player1_card) == 0 or len(player2_card) == 0:
            return
        state = (tuple(player2_card), tuple(player1_action), tuple(actions_card_player1), 
                 tuple(actions_card_player2), tuple(player1_card))
        if state in env:
            return
        
        list_valid_action_player2 = self.action_generator.get_list_valid_action(state[0], state[1])
        for player2_action in list_valid_action_player2:

            next_player2_card = [card for card in player2_card if card not in player2_action]
            next_actions_card_player2 = actions_card_player2 + list(player2_action)
            next_actions_card_player2.sort()
            next_deck_remain_player2 = [card for card in deck_remain_player2 if card not in player2_action]

            if len(next_player2_card) > 0:
                medium_bot_state = (tuple(player1_card), tuple(player2_action), tuple(next_actions_card_player2),
                                    tuple(actions_card_player1), tuple(next_deck_remain_player2), len(next_player2_card))
                player1_play_first = 1 if self.who_play_first == 1 else 0
                self.__check_medium_bot_state(medium_bot_state, player1_play_first)
                next_player1_action = self.medium_bot_reinforcement.choose_best_action_with_max_Q_value(
                    medium_bot_state, player1_play_first
                )
            else:
                next_player1_action = tuple()

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

            self.recursive_depth_first_search_reward(env, next_player1_card, 
                                                     next_player2_card, next_player1_action, 
                                                     next_actions_card_player1, next_actions_card_player2,
                                                     next_deck_remain_player2)
            
    def build_env(self, player1_card, player2_card):
        full_deck = list(range(52))
        actions_card_player1 = []
        actions_card_player2 = []
        deck_remain_player2 = [card for card in full_deck if card not in player1_card]

        if self.who_play_first == 1:
            medium_bot_state = (tuple(player1_card), tuple(), tuple(actions_card_player2),
                                tuple(actions_card_player1), tuple(deck_remain_player2), len(player2_card))
            assert medium_bot_state[-1] == 13 and len(medium_bot_state[-2]) == 39
            player1_play_first = 1 if self.who_play_first == 1 else 0
            self.__check_medium_bot_state(medium_bot_state, player1_play_first)
            player1_action = self.medium_bot_reinforcement.choose_best_action_with_max_Q_value(
                medium_bot_state, player1_play_first
            )
        else:
            player1_action = tuple()
        player1_card = [card for card in player1_card if card not in player1_action]
        actions_card_player1 = list(player1_action)
        assert len(deck_remain_player2) == 39
    
        env = defaultdict(dict)
        self.recursive_depth_first_search_reward(env, player1_card, player2_card, player1_action, 
                                                 actions_card_player1, actions_card_player2,
                                                 deck_remain_player2)
        return env


def write_data_to_file(src_data, idx_game, df_table):
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
    preprocess_2_player = Preprocessing_2_player()

    for idx_game in range(10**6):
        full_deck = list(range(52))
        np.random.shuffle(full_deck)
        player1_card = full_deck[:13]; player1_card.sort()
        player2_card = full_deck[13:26]; player2_card.sort()
        print("\nPlayer1 cards: ", end=""); Card.print_pretty_cards(player1_card)
        print("Player2 cards: ", end=""); Card.print_pretty_cards(player2_card)
        if natural_win.detect_natural_win(player1_card) or natural_win.detect_natural_win(player2_card):
            print("Natural Win Detected: SKIPPING this game!!!")
            continue
        who_play_first = random.choice([1, 2])
        bot_simulation.who_play_first = who_play_first
        env = bot_simulation.build_env(player1_card, player2_card)
        print(f"The number of state: {len(env):,}")
        bot_simulation.medium_bot_reinforcement.generate_one_hot_encoding.cache_clear()
        bot_simulation.action_generator.get_list_valid_action.cache_clear()
        bot_simulation.reward.get_penalized_deuce_quartet_double_sequence.cache_clear()
        bot_simulation.medium_bot_reinforcement.generate_action_encoding.cache_clear()
        optimal_Q_table = calculate_optimal_Q_table(env)
        del env; gc.collect()
        df_table = preprocess_2_player.create_polars_table_of_state_action_return_encode(
            optimal_Q_table, who_play_first
        )
        del optimal_Q_table; gc.collect()
        write_data_to_file(src_data, idx_game, df_table)
        del df_table; gc.collect()


if __name__ == "__main__":
    n_process = psutil.cpu_count(logical=False) - 1
    src_data = r"\\10.5.10.44\TLMN_see_opponent_cards_2_players\hard_1"

    print(f"The number of running process: {n_process}")
    print(f"Finding src_data status: {os.path.exists(src_data)}")
    os.makedirs(src_data, exist_ok=True)
    if sys.platform.startswith('win'):
        freeze_support()
    with Pool(processes=n_process) as pool:
        pool.map(run_bot_simulation, [src_data] * n_process)