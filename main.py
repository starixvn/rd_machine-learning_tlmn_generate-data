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
from math import comb
from itertools import combinations
import gc
from agent_bot.bot_2_players_honestly import Bot_2_players_honestly


class Bot_Simulation(object):
    def __init__(self):
        self.action_generator = ActionGenerator()
        self.utils = Utils()
        self.reward = Reward()
        self.who_play_first = -1
        self.medium_bot_reinforcement = Bot_2_players_honestly()
        
    def cal_upper_limit_of_reward(self, opponent_card):
        return 1 + self.reward.get_penalized_deuce_quartet_double_sequence(tuple(opponent_card))

    def recursive_depth_first_search_reward(self, env, player1_card, player2_card, player1_action, 
                                                 actions_card_player1, actions_card_player2,
                                                 deck_remain_player1, deck_remain_player2,
                                                 reward_info, traverse_all,
                                                 cumsum_bomb_beat):
        if traverse_all == False and reward_info["max"] == reward_info["upper_limit"]:
            # print("Found the path to win ==> Return")
            return
        if len(player1_card) == 0 or len(player2_card) == 0:
            reward = self.reward.get_reward(player1_card, player2_card) + cumsum_bomb_beat
            if traverse_all == False:
                assert reward <= reward_info["upper_limit"], \
                    f'reward = {reward}, upper_limit = {reward_info["upper_limit"]}'
            reward_info["max"] = max(reward_info["max"], reward)
            return
        state = (tuple(player2_card), tuple(player1_action), tuple(actions_card_player1), 
                 tuple(actions_card_player2), tuple(deck_remain_player1), len(player1_card))
        if state in env:
            return
        
        list_valid_action_player2 = self.action_generator.get_list_valid_action(state[0], state[1])
        for player2_action in list_valid_action_player2:

            next_player2_card = [card for card in player2_card if card not in player2_action]
            next_actions_card_player2 = actions_card_player2 + list(player2_action)
            next_actions_card_player2.sort()
            next_deck_remain_player2 = [card for card in deck_remain_player2 if card not in player2_action]

            if len(next_player2_card) > 0:
                # next_player1_action = self.run_rule_based_bot(player2_action, player1_card)
                medium_bot_state = (tuple(player1_card), tuple(player2_action), tuple(next_actions_card_player2),
                                    tuple(actions_card_player1), tuple(next_deck_remain_player2), len(next_player2_card))
                player1_play_first = 1 if self.who_play_first == 1 else 0
                next_player1_action = self.medium_bot_reinforcement.choose_best_action_with_max_Q_value(
                    medium_bot_state, player1_play_first
                )
            else:
                next_player1_action = tuple()

            next_player1_card = [card for card in player1_card if card not in next_player1_action]
            next_actions_card_player1 = actions_card_player1 + list(next_player1_action)
            next_actions_card_player1.sort()
            next_deck_remain_player1 = [card for card in deck_remain_player1 if card not in next_player1_action]

            bomb_beat_2_versus_1 = self.reward.get_bomb_beating_penalty(player1_action, player2_action)
            bomb_beat_1_versus_2 = -1 * self.reward.get_bomb_beating_penalty(player2_action, next_player1_action)
            next_cumsum_bomb_beat = cumsum_bomb_beat + bomb_beat_2_versus_1 + bomb_beat_1_versus_2

            next_state = (tuple(next_player2_card), tuple(next_player1_action), tuple(next_actions_card_player1), 
                         tuple(next_actions_card_player2), tuple(next_deck_remain_player1), len(next_player1_card))
            reward = self.reward.get_reward(next_player1_card, next_player2_card) + \
                        bomb_beat_2_versus_1 + bomb_beat_1_versus_2
            terminated = len(next_player1_card) == 0 or len(next_player2_card) == 0
            env[state][player2_action] = (next_state, reward, terminated)

            self.recursive_depth_first_search_reward(env, next_player1_card, 
                                                     next_player2_card, next_player1_action, 
                                                     next_actions_card_player1, next_actions_card_player2,
                                                     next_deck_remain_player1, next_deck_remain_player2,
                                                     reward_info, traverse_all,
                                                     next_cumsum_bomb_beat)

    def compute_value(self, state, terminated, env, memo, upper_limit):
        if state in memo:
            return memo[state]

        if terminated:
            return 0

        max_return = float('-inf')
        if state in env:
            for action_step_info in env[state].values():
                next_state, reward, next_terminated = action_step_info
                total_return = reward + self.compute_value(next_state, next_terminated, env, memo, upper_limit)
                max_return = max(max_return, total_return)
                assert max_return <= upper_limit
                if max_return == upper_limit:
                    memo[state] = upper_limit
                    return upper_limit

        memo[state] = max_return
        return max_return

    def calculte_max_reward_for_all_actions_of_state(self, state, player1_card):
        assert self.who_play_first in [1, 2]
        player2_card, player1_action, actions_card_player1, actions_card_player2, deck_remain_player1, _ = state
        deck_remain_player2 = list(set(range(52)) - set(player1_card) \
                                   - set(actions_card_player1) - set(actions_card_player2))
        list_valid_action_player2 = self.action_generator.get_list_valid_action(player2_card, player1_action)
        if len(list_valid_action_player2) == 1: return {}
        actions_max_reward = {}
        env = defaultdict(dict)
        for player2_action in list_valid_action_player2:

            next_player2_card = [card for card in player2_card if card not in player2_action]
            next_actions_card_player2 = list(actions_card_player2) + list(player2_action)
            next_actions_card_player2.sort()
            next_deck_remain_player2 = [card for card in deck_remain_player2 if card not in player2_action]

            if len(next_player2_card) > 0:
                # next_player1_action = self.run_rule_based_bot(player2_action, player1_card)
                medium_bot_state = (tuple(player1_card), tuple(player2_action), tuple(next_actions_card_player2),
                                    tuple(actions_card_player1), tuple(next_deck_remain_player2), len(next_player2_card))
                player1_play_first = 1 if self.who_play_first == 1 else 0
                next_player1_action = self.medium_bot_reinforcement.choose_best_action_with_max_Q_value(
                    medium_bot_state, player1_play_first
                )
            else:
                next_player1_action = tuple()
                
            next_player1_card = [card for card in player1_card if card not in next_player1_action]
            next_actions_card_player1 = list(actions_card_player1) + list(next_player1_action)
            next_actions_card_player1.sort()
            next_deck_remain_player1 = [card for card in deck_remain_player1 if card not in next_player1_action]

            bomb_beat_2_versus_1 = self.reward.get_bomb_beating_penalty(player1_action, player2_action)
            bomb_beat_1_versus_2 = -1 * self.reward.get_bomb_beating_penalty(player2_action, next_player1_action)
            next_cumsum_bomb_beat = bomb_beat_2_versus_1 + bomb_beat_1_versus_2

            next_state = (tuple(next_player2_card), tuple(next_player1_action), tuple(next_actions_card_player1), 
                         tuple(next_actions_card_player2), tuple(next_deck_remain_player1), len(next_player1_card))
            reward = self.reward.get_reward(next_player1_card, next_player2_card) + \
                        bomb_beat_2_versus_1 + bomb_beat_1_versus_2
            terminated = len(next_player1_card) == 0 or len(next_player2_card) == 0
            env[state][player2_action] = (next_state, reward, terminated)

            reward_info = {"max": float('-inf'), 
                           "upper_limit": self.cal_upper_limit_of_reward(player1_card) + next_cumsum_bomb_beat}
            try:
                self.recursive_depth_first_search_reward(env, next_player1_card, 
                                                        next_player2_card, next_player1_action, 
                                                        next_actions_card_player1, next_actions_card_player2,
                                                        next_deck_remain_player1, next_deck_remain_player2,
                                                        reward_info, traverse_all=False,
                                                        cumsum_bomb_beat=next_cumsum_bomb_beat)
                if reward_info["max"] != reward_info["upper_limit"]:
                    reward_info["max"] = reward + self.compute_value(next_state, terminated, env, {}, 
                                                                     reward_info["upper_limit"] - reward)
            except Exception as e:
                print(f"ERROR at {e}")
                print(f"state = {state}")
                print(f"player1_card = {player1_card}")
                return {key_tmp: float('-inf') for key_tmp in list_valid_action_player2}
            actions_max_reward[player2_action] = reward_info["max"]
        return actions_max_reward

    def build_env(self, player1_card, player2_card):
        full_deck = list(range(52))
        actions_card_player1 = []
        actions_card_player2 = []
        deck_remain_player1 = [card for card in full_deck if card not in player2_card]
        deck_remain_player2 = [card for card in full_deck if card not in player1_card]

        if self.who_play_first == 1:
            # player1_action = self.run_rule_based_bot([], player1_card)
            medium_bot_state = (tuple(player1_card), tuple(), tuple(actions_card_player2),
                                tuple(actions_card_player1), tuple(deck_remain_player2), len(player2_card))
            assert medium_bot_state[-1] == 13 and len(medium_bot_state[-2]) == 39
            player1_play_first = 1 if self.who_play_first == 1 else 0
            player1_action = self.medium_bot_reinforcement.choose_best_action_with_max_Q_value(
                medium_bot_state, player1_play_first
            )
        else:
            player1_action = tuple()
        player1_card = [card for card in player1_card if card not in player1_action]
        actions_card_player1 = list(player1_action)
        deck_remain_player1 = [card for card in deck_remain_player1 if card not in player1_action]
        assert set(deck_remain_player1 + list(player1_action) + player2_card) == set(full_deck)
        assert len(deck_remain_player2) == 39
    
        env = defaultdict(dict)
        reward_info = {"max": float('-inf'),
                       "upper_limit": float('-inf')}
        self.recursive_depth_first_search_reward(env, player1_card, player2_card, player1_action, 
                                                 actions_card_player1, actions_card_player2,
                                                 deck_remain_player1, deck_remain_player2,
                                                 reward_info, traverse_all=True,
                                                 cumsum_bomb_beat=0)
        return env


def create_folder_contain_one_game_data(src_data, idx_game):
    computer_name = platform.node()
    computer_name = computer_name.replace("-", "")

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d-%H-%M-%S")

    process_id = os.getpid()

    foldername = f"TLMN_{formatted_now}_{computer_name}_{process_id}_{idx_game}"
    path_to_folder = os.path.join(src_data, foldername)
    os.makedirs(path_to_folder)
    return path_to_folder

def save_the_initial_game_info(path_to_folder, player1_card, player2_card, who_play_first):
    assert len(player1_card) == 13 and len(player2_card) == 13 and who_play_first in [1, 2]
    path_to_file = os.path.join(path_to_folder, "initial_game_info.pkl")
    initial_game_info = {
        "player1_card": tuple(player1_card),
        "player2_card": tuple(player2_card), 
        "who_play_first": who_play_first,
        "version": "hard_mode",
    }
    with open(path_to_file, "wb") as f:
        pickle.dump(initial_game_info, f, protocol=pickle.HIGHEST_PROTOCOL)

def write_data_to_file(path_to_folder, state_index, state, actions_average_max_reward):
    path_to_file = os.path.join(path_to_folder, f"state_{state_index}.pkl")
    if os.path.exists(path_to_file): print(f"[ERRRRRRORRRRRRR] {path_to_file} is existing")
    game_data = {state: actions_average_max_reward}
    with open(path_to_file, "wb") as f:
        pickle.dump(game_data, f, protocol=pickle.HIGHEST_PROTOCOL)

def generate_random_player1_card_from_deck_remain(deck_remain, len_player1_card, origin_player2_card):
    player1_action_cards = [card for card in range(52) 
                            if card not in origin_player2_card and card not in deck_remain]
    assert len(player1_action_cards) + len_player1_card == 13 and len(origin_player2_card) == 13

    natural_win = NaturalWin()
    deck_remain_shuffled = list(deck_remain)
    max_n_iter = 1000
    n_iter = min(max_n_iter, comb(len(deck_remain), len_player1_card))
    if n_iter == max_n_iter:
        for _ in range(n_iter):
            np.random.shuffle(deck_remain_shuffled)
            player1_card = deck_remain_shuffled[:len_player1_card]
            if natural_win.detect_natural_win(player1_card + player1_action_cards): 
                continue
            yield sorted(player1_card)
    else:
        for player1_card in combinations(deck_remain, len_player1_card):
            player1_card = list(player1_card)
            if natural_win.detect_natural_win(player1_card + player1_action_cards): 
                continue
            yield sorted(player1_card)

def generate_average_max_reward_for_all_actions_of_state(state, bot_simulation, origin_player2_card):
    _, _, _, _, deck_remain, len_player1_card = state
    actions_list_max_reward = defaultdict(list)
    for player1_card in generate_random_player1_card_from_deck_remain(deck_remain, len_player1_card, 
                                                                      origin_player2_card):
        actions_max_reward = bot_simulation.calculte_max_reward_for_all_actions_of_state(state, player1_card)
        if actions_max_reward == {}: return None
        for action, max_reward in actions_max_reward.items():
            actions_list_max_reward[action].append(max_reward)

        bot_simulation.medium_bot_reinforcement.generate_one_hot_encoding.cache_clear()
        bot_simulation.action_generator.get_list_valid_action.cache_clear()
        bot_simulation.reward.get_penalized_deuce_quartet_double_sequence.cache_clear()
    bot_simulation.medium_bot_reinforcement.generate_action_encoding.cache_clear()

    lengths = [len(rewards) for rewards in actions_list_max_reward.values()]
    assert all(x == lengths[0] for x in lengths), "All reward lists must have equal length"
    actions_average_max_reward = {action: sum(rewards) / len(rewards) 
                                for action, rewards in actions_list_max_reward.items()}
    return actions_average_max_reward

def run_bot_simulation(src_data):
    bot_simulation = Bot_Simulation()
    natural_win = NaturalWin()

    for idx_game in range(10**6):
        full_deck = list(range(52))
        np.random.shuffle(full_deck)
        player1_card = full_deck[:13]; player1_card.sort()
        player2_card = full_deck[13:26]; player2_card.sort()
        if natural_win.detect_natural_win(player1_card) or natural_win.detect_natural_win(player2_card):
            # print("Natural Win Detected: SKIPPING this game!!!")
            continue
        who_play_first = random.choice([1, 2])
        bot_simulation.who_play_first = who_play_first
        env = bot_simulation.build_env(player1_card, player2_card)
        set_states = set(env.keys())
        del env; gc.collect()
        # print("\nPlayer1 cards: ", end=""); Card.print_pretty_cards(player1_card)
        # print("Player2 cards: ", end=""); Card.print_pretty_cards(player2_card)
        # print(f"The number of state: {len(set_states)}")
        path_to_folder = create_folder_contain_one_game_data(src_data, idx_game)
        save_the_initial_game_info(path_to_folder, player1_card, player2_card, who_play_first)
        for state_index, state in enumerate(set_states):
            assert type(state[-1]) == int
            if state[-1] not in [2, 1]: continue
            start_time_cal = time.time()
            actions_average_max_reward = generate_average_max_reward_for_all_actions_of_state(state, 
                                                                        bot_simulation, player2_card)
            end_time_cal = time.time()
            if actions_average_max_reward is None: continue
            # print(f"\nstate: {state}")
            # print(f"{actions_average_max_reward}")
            # print(f"The time taken is: {end_time_cal-start_time_cal} seconds")
            write_data_to_file(path_to_folder, state_index, state, actions_average_max_reward)


if __name__ == "__main__":
    n_process = psutil.cpu_count(logical=False)
    src_data = r"C:\Users\justin.pham\Downloads\tmp"

    print(f"The number of running process: {n_process}")
    print(f"Finding src_data status: {os.path.exists(src_data)}")
    if not os.path.exists(src_data):
        os.makedirs(src_data)
    if sys.platform.startswith('win'):
        freeze_support()
    with Pool(processes=n_process) as pool:
        pool.map(run_bot_simulation, [src_data] * n_process)