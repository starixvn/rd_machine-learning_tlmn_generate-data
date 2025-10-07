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
from math import comb
from more_itertools import split_into
from itertools import combinations, islice
from math import ceil
import gc
from agent_bot.TL_AI_bot import Bot_TL_AI


class Bot_Simulation(object):
    def __init__(self, n_player=4):
        self.action_generator = ActionGenerator()
        self.utils = Utils()
        self.reward = Reward()
        self.n_player = n_player
        self.skip_int_encode = -1
        self.finish_int_encode = -2
        self.tl_ai_bot = Bot_TL_AI()

    def reset_player_skip(self, player_skip, player_action):
        for i in range(self.n_player):
            if player_action[i] != self.finish_int_encode:
                player_skip[i] = False

    def get_player_action(self, player_id, player_id_card, last_action, turn):
        if turn == player_id:
            player_action = self.tl_ai_bot.run_rule_based_bot((), player_id_card)
        else:
            player_action = self.tl_ai_bot.run_rule_based_bot(last_action, player_id_card)
        return player_action

    def remove_list_card_from_player_card(self, player_card, list_card_to_remove):
        return tuple([card for card in player_card if card not in list_card_to_remove])

    def update_player_card_and_player_skip(self, player_card, player_skip, 
                                           player_id, player_id_action):
        if player_id_action:                
            player_card[player_id] = self.remove_list_card_from_player_card(
                                        player_card[player_id], player_id_action)
            player_skip[player_id] = False
        else:
            player_skip[player_id] = True

    def get_list_valid_action_of_player(self, player_id, player_id_card, last_action, turn):
        if turn == player_id:
            list_valid_action = self.action_generator.get_list_valid_action(player_id_card, ())
        else:
            list_valid_action = self.action_generator.get_list_valid_action(player_id_card, last_action)
        return list_valid_action
    
    def is_deuce_or_pair_deuce(self, player_id_action):
        n = len(player_id_action)
        return (n == 1 or n == 2) and Card.get_rank_int(player_id_action[0]) == 12
    
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

    def get_list_valid_action_of_first_player(self, first_player_id, first_player_card, 
                                            player_action, turn, player_skip):
        if not player_skip[first_player_id]:
            if turn == first_player_id: self.reset_player_skip(player_skip, player_action)
            list_valid_action_first_player = self.get_list_valid_action_of_player(
                                            first_player_id, first_player_card, player_action[turn], turn)
        else:
            list_valid_action_first_player = self.get_list_valid_action_in_skip_condition(
                                            first_player_id, first_player_card, player_action[turn], turn)
            assert self.skip_int_encode in list_valid_action_first_player
        return list_valid_action_first_player

    def get_player_action_in_skip_condition(self, player_id, player_id_card, last_action, turn):
        assert turn != player_id, f"turn = {turn}, player_id = {player_id}"
        if self.is_deuce_or_pair_deuce(last_action):
            player_id_action = self.get_player_action(player_id, player_id_card, last_action, turn)
            if self.utils.get_combo_type(player_id_action) == ComboType.DOUBLE_SEQUENCE_FOUR:
                return player_id_action
        return self.skip_int_encode

    def update_player_card_action_skip_turn(self, player_card, player_action, player_skip, turn,
                                            player_id, player_id_action):
        player_action[player_id] = player_id_action
        if player_id_action != self.skip_int_encode:
            self.update_player_card_and_player_skip(player_card, player_skip, player_id, player_id_action)
            if player_id_action:
                turn = player_id
        return turn

    def move_to_next_turn(self, turn):
        return (turn + 1) % self.n_player

    def run_round_for_other_players(self, player_card, player_action, player_skip, turn, player_id_start=1):
        bomb_beat_other_player = 0
        for player_id in range(player_id_start, self.n_player):
            if not player_card[player_id]:
                player_action[player_id] = self.finish_int_encode
                player_skip[player_id] = True
                if turn == player_id:
                    turn = self.move_to_next_turn(turn)
                    player_skip[turn] = False
                continue

            if not player_card[0]:
                player_action[player_id] = self.skip_int_encode
                player_skip[player_id] = True
                continue

            if not player_skip[player_id]:
                if turn == player_id: self.reset_player_skip(player_skip, player_action)
                player_id_action = self.get_player_action(
                                        player_id, player_card[player_id], player_action[turn], turn)
            else:
                player_id_action = self.get_player_action_in_skip_condition(
                                        player_id, player_card[player_id], player_action[turn], turn)
            
            if turn == 0:
                bomb_beat_other_player -= self.get_bomb_beating_penalty_4_players(turn, player_action[turn], 
                                                                                player_id, player_id_action)
            turn = self.update_player_card_action_skip_turn(player_card, player_action, player_skip, turn,
                                                            player_id, player_id_action)

        return turn, bomb_beat_other_player
    
    def encode_state(self, player_card, player_action, player_skip, turn):
        return (*player_card,
                *islice(player_action, 1, None),
                *player_skip,
                turn)

    def decode_state(self, state):
        assert len(state) == 3 * self.n_player
        player_card = list(state[:self.n_player])
        player_action = [()] + list(state[self.n_player:2*self.n_player-1])
        player_skip = list(state[2*self.n_player-1:3*self.n_player-1])
        turn = state[-1]
        assert all(isinstance(x, bool) for x in player_skip), \
                f"player_skip must be all boolean: {player_skip}"
        assert 0 <= turn < self.n_player, f"turn must be in range [0,{self.n_player}): {turn}"
        return player_card, player_action, player_skip, turn

    def is_terminated(self, player_card):
        if not player_card[0]:
            return True
        for i in range(1, self.n_player):
            if player_card[i]:  # non-empty hand
                return False
        return True

    def get_bomb_beating_penalty_4_players(self, previous_player_id, previous_action, 
                                                    current_player_id, current_action):
        if previous_player_id == current_player_id:
            return 0
        if isinstance(previous_action, int) or isinstance(current_action, int):
            return 0
        bomb_beating_penalty = self.reward.get_bomb_beating_penalty(previous_action, current_action)
        assert bomb_beating_penalty >= 0
        return 4 if bomb_beating_penalty > 0 else 0

    def env_transition(self, player_card, player_action, player_skip, turn, valid_action_player0):
        next_player_card = player_card.copy()
        next_player_action = player_action.copy()
        next_player_skip = player_skip.copy()

        bomb_beat_player0 = self.get_bomb_beating_penalty_4_players(turn, player_action[turn],
                                                                    0, valid_action_player0)
        next_turn = self.update_player_card_action_skip_turn(next_player_card, next_player_action, 
                                                            next_player_skip, turn,
                                                            0, valid_action_player0)

        next_turn, bomb_beat_other_player = self.run_round_for_other_players(
                                    next_player_card, next_player_action, next_player_skip, next_turn)
        bomb_beat_in_round = bomb_beat_player0 + bomb_beat_other_player
        return next_player_card, next_player_action, next_player_skip, next_turn, bomb_beat_in_round

    def recursive_depth_first_search(self, env, player_card, player_action, player_skip, turn,
                                    reward_info, traverse_all, cumsum_bomb_beat):
        if not traverse_all and reward_info["max"] == reward_info["upper_limit"]:
            # print("Found the path to win ==> Return")
            return
        if self.is_terminated(player_card):
            reward = self.reward.get_reward_more_than_2_players(player_card) + cumsum_bomb_beat
            if not traverse_all:
                assert reward <= reward_info["upper_limit"], \
                    f'reward = {reward}, upper_limit = {reward_info["upper_limit"]}'
            reward_info["max"] = max(reward_info["max"], reward)
            return
        state = self.encode_state(player_card, player_action, player_skip, turn)
        if state in env: return
        
        list_valid_action_player0 = self.get_list_valid_action_of_first_player(
                                        0, player_card[0], player_action, turn, player_skip)
        for valid_action_player0 in list_valid_action_player0:
            next_player_card, next_player_action, next_player_skip, next_turn, bomb_beat_in_round = \
                self.env_transition(player_card, player_action, player_skip, turn, valid_action_player0)

            next_cumsum_bomb_beat = cumsum_bomb_beat + bomb_beat_in_round

            if not traverse_all:
                next_state = self.encode_state(next_player_card, next_player_action, next_player_skip, next_turn)
                reward = self.reward.get_reward_more_than_2_players(next_player_card) + bomb_beat_in_round
                env[state][valid_action_player0] = (next_state, reward)
            else:
                env.add(state)
            self.recursive_depth_first_search(env, next_player_card, next_player_action, next_player_skip, next_turn,
                                            reward_info, traverse_all, next_cumsum_bomb_beat)

    def is_last_action_is_deuce_or_special_case(self, last_action, turn):
        if turn == 0:
            return False
        
        return Utils.get_combo_type(last_action) in [ComboType.SINGLE_DEUCE, ComboType.PAIR_DEUCE,
                                                    ComboType.QUARTET,
                                                    ComboType.DOUBLE_SEQUENCE_THREE, 
                                                    ComboType.DOUBLE_SEQUENCE_FOUR]

    def cal_upper_limit_of_reward(self, player_card, last_action, turn):
        n_other_player_playing = self.reward.cal_n_other_player_playing(player_card)
        n_deuce_special_case_other_player = self.reward.count_n_deuce_special_case_other_player(player_card[1:])
        last_action_deuce_special_case = int(self.is_last_action_is_deuce_or_special_case(last_action, turn))
        n_special_case_player0 = self.reward.count_n_distinct_special_case(player_card[0])
        assert n_special_case_player0 <= 2 and last_action_deuce_special_case in [0, 1]

        penalized_bomb_beat = min(n_special_case_player0, 
                                n_deuce_special_case_other_player + last_action_deuce_special_case)
                
        if n_deuce_special_case_other_player > max(n_special_case_player0 - last_action_deuce_special_case, 0):
            penalized_stuck = 1
        else:
            penalized_stuck = 0

        upper_limit = n_other_player_playing + (penalized_bomb_beat * 4) + penalized_stuck

        return upper_limit

    def compute_value(self, state, env, memo, upper_limit):
        if state in memo:
            return memo[state]

        if self.is_terminated(state):
            return 0

        max_return = float('-inf')
        if state in env:
            for action_step_info in env[state].values():
                next_state, reward = action_step_info
                total_return = reward + self.compute_value(next_state, env, memo, upper_limit)
                max_return = max(max_return, total_return)
                assert max_return <= upper_limit
                if max_return == upper_limit:
                    memo[state] = upper_limit
                    return upper_limit

        memo[state] = max_return
        return max_return

    def calculte_max_reward_for_all_actions_of_state(self, state, other_player_card):
        player_card, player_action, player_skip, turn = self.decode_state(state)
        player_card[1:] = other_player_card
        list_valid_action_player0 = self.get_list_valid_action_of_first_player(
                                        0, player_card[0], player_action, turn, player_skip)
        if len(list_valid_action_player0) == 1: return {}
        actions_max_reward = {}
        env = defaultdict(dict)
        for valid_action_player0 in list_valid_action_player0:
            next_player_card, next_player_action, next_player_skip, next_turn, bomb_beat_in_round = \
                self.env_transition(player_card, player_action, player_skip, turn, valid_action_player0)

            next_state = self.encode_state(next_player_card, next_player_action, next_player_skip, next_turn)
            reward = self.reward.get_reward_more_than_2_players(next_player_card) + bomb_beat_in_round
            env[state][valid_action_player0] = (next_state, reward)

            reward_info = {"max": float('-inf'),
                           "upper_limit": self.cal_upper_limit_of_reward(
                            next_player_card, next_player_action[next_turn], next_turn) + bomb_beat_in_round}
                        
            try:
                self.recursive_depth_first_search(env, next_player_card, next_player_action,
                                                    next_player_skip, next_turn,
                                                    reward_info, traverse_all=False,
                                                    cumsum_bomb_beat=bomb_beat_in_round)
                if reward_info["max"] != reward_info["upper_limit"]:
                    reward_info["max"] = reward + self.compute_value(next_state, env, {}, 
                                                                     reward_info["upper_limit"] - reward)
            except Exception as e:
                print(f"ERROR at {e}")
                print(f"state = {state}")
                print(f"other_player_card = {other_player_card}")
                return {key_tmp: float('-inf') for key_tmp in list_valid_action_player0}
            actions_max_reward[valid_action_player0] = reward_info["max"]
        return actions_max_reward

    def build_env(self, player_card, who_play_first):
        player_action = [()] * self.n_player
        player_skip = [False] * self.n_player
        turn = who_play_first
        if who_play_first != 0:
            turn, _ = self.run_round_for_other_players(
                        player_card, player_action, player_skip, turn, player_id_start=who_play_first)

        env = set()
        reward_info = {"max": float('-inf'),
                       "upper_limit": float('-inf')}
        self.recursive_depth_first_search(env, player_card, player_action, player_skip, turn,
                                        reward_info, traverse_all=True, cumsum_bomb_beat=0)
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

def save_the_initial_game_info(path_to_folder, player_card, who_play_first):
    assert all(len(cards) == 13 for cards in player_card) and who_play_first <= 3
    path_to_file = os.path.join(path_to_folder, "initial_game_info.pkl")
    initial_game_info = {
        "player_card": player_card,
        "who_play_first": who_play_first,
        "version": "medium_mode",
    }
    with open(path_to_file, "wb") as f:
        pickle.dump(initial_game_info, f, protocol=pickle.HIGHEST_PROTOCOL)

def write_data_to_file(path_to_folder, state_index, state, actions_average_max_reward):
    path_to_file = os.path.join(path_to_folder, f"state_{state_index}.pkl")
    if os.path.exists(path_to_file): print(f"[ERRRRRRORRRRRRR] {path_to_file} is existing")
    game_data = {state: actions_average_max_reward}
    with open(path_to_file, "wb") as f:
        pickle.dump(game_data, f, protocol=pickle.HIGHEST_PROTOCOL)

def cal_total_n_combination(len_deck_remain, len_other_player_card):
    n = len_deck_remain
    assert sum(len_other_player_card) == n, \
            f"len_other_player_card = {len_other_player_card}, n = {n}"
    result = 1
    for k in len_other_player_card[:-1]:
        result *= comb(n, k)
        n -= k
    return result

def partition_by_sizes(iterable, sizes): 
    if not sizes:
        yield []
        return

    first_size, *rest_sizes = sizes
    for first_group in combinations(iterable, first_size):
        remaining = set(iterable) - set(first_group)
        for rest_partition in partition_by_sizes(remaining, rest_sizes):
            yield [first_group] + rest_partition

def generate_random_card_for_each_remain_player(state, origin_player_card):
    n_player = len(origin_player_card)
    deck_remain = list(sum(state[1:n_player], ()))
    len_other_player_card = tuple([len(state[i]) for i in range(1, n_player)])
    assert all(0 <= length <= 13 for length in len_other_player_card), \
        f"Player card lengths must be between 0 and 13: {len_other_player_card}" 

    other_player_action_cards = [
        tuple(set(origin_player_card[i]) - set(state[i])) for i in range(1, n_player)
    ]
    assert all(len(other_player_action_cards[i]) + len_other_player_card[i] == 13 
                for i in range(n_player-1))

    natural_win = NaturalWin()
    max_n_iter = 1000
    n_iter = min(max_n_iter, cal_total_n_combination(len(deck_remain), len_other_player_card))
    if n_iter == max_n_iter:
        n_yield = 0
        while n_yield < max_n_iter:
            np.random.shuffle(deck_remain)
            other_player_card = [tuple(sorted(x)) for x in split_into(deck_remain, len_other_player_card)]
            if any(natural_win.detect_natural_win(other_player_card[i] + other_player_action_cards[i]) 
                    for i in range(n_player-1)): 
                continue
            yield other_player_card
            n_yield += 1
    else:
        for partition in partition_by_sizes(deck_remain, len_other_player_card):
            other_player_card = [tuple(sorted(x)) for x in partition]
            if any(natural_win.detect_natural_win(other_player_card[i] + other_player_action_cards[i]) 
                    for i in range(n_player-1)): 
                continue
            yield other_player_card

def generate_average_max_reward_for_all_actions_of_state(state, bot_simulation, origin_player_card):
    actions_list_max_reward = defaultdict(list)
    for idx, other_player_card in enumerate(generate_random_card_for_each_remain_player(
                                                                        state, origin_player_card)):
        # print(f"idx other player card = {idx}")
        actions_max_reward = bot_simulation.calculte_max_reward_for_all_actions_of_state(state, other_player_card)
        if actions_max_reward == {}: return None
        for action, max_reward in actions_max_reward.items():
            actions_list_max_reward[action].append(max_reward)

        bot_simulation.tl_ai_bot.run_rule_based_bot.cache_clear()

    assert len(set(map(len, actions_list_max_reward.values()))) == 1
    actions_average_max_reward = {action: sum(rewards) / len(rewards) 
                                for action, rewards in actions_list_max_reward.items()}
    return actions_average_max_reward

def filter_state_for_src_data(src_data, env, n_player):
    src_data_split = src_data.split("_")
    start_range_idx, end_range_idx = int(src_data_split[-1]), int(src_data_split[-2])
    set_states = []
    for key_state in env:
        len_player_card = [len(key_state[i]) for i in range(n_player)]
        if min(len_player_card) in range(start_range_idx, end_range_idx+1):
            set_states.append(key_state)
    return set_states

def run_bot_simulation(src_data):
    bot_simulation = Bot_Simulation()
    natural_win = NaturalWin()

    for idx_game in range(10**6):
        try:
            full_deck = list(range(52))
            np.random.shuffle(full_deck)
            player_card = [
                tuple(sorted(full_deck[i * 13:(i + 1) * 13]))
                for i in range(bot_simulation.n_player)
            ]
            if any(natural_win.detect_natural_win(cards) for cards in player_card):
                # print("Natural Win Detected: SKIPPING this game!!!")
                continue
                
            assert len(player_card) == bot_simulation.n_player
            who_play_first = random.choice(list(range(bot_simulation.n_player)))
            assert who_play_first <= 3
            env = bot_simulation.build_env(player_card.copy(), who_play_first)

            set_states = filter_state_for_src_data(src_data, env, bot_simulation.n_player)
            max_n_state = 10**4
            if len(set_states) > max_n_state:
                set_states = random.sample(set_states, max_n_state)
            else:
                random.shuffle(set_states)
            del env; gc.collect()
            
            path_to_folder = create_folder_contain_one_game_data(src_data, idx_game)
            save_the_initial_game_info(path_to_folder, player_card, who_play_first)
            for state_index, state in enumerate(set_states):
                start_time_cal = time.time()
                actions_average_max_reward = generate_average_max_reward_for_all_actions_of_state(state, 
                                                                            bot_simulation, player_card)
                end_time_cal = time.time()
                if actions_average_max_reward is None: continue
                # print(f"\nstate = {state}")
                # print(f"player_card = {player_card}")
                # print(f"{actions_average_max_reward}")
                # print(f"The time taken is: {end_time_cal-start_time_cal} seconds")
                write_data_to_file(path_to_folder, state_index, state, actions_average_max_reward)

        except Exception as e:
            print(f"\nThe ERRRRRRRROOOOOOOOOOOORRRRRRRRRR occurs:", e)
            for i in range(len(player_card)):
                print(f"Player {i} cards: ", end=""); Card.print_pretty_cards(player_card[i])
            print(f"Player {who_play_first} plays first")


if __name__ == "__main__":
    def divide_job(n_process, src_data):
        n_src_data_idx_0 = int(0.5 * n_process)
        n_src_data_idx_1 = ceil(0.5 * (n_process - n_src_data_idx_0))
        n_src_data_idx_2 = n_process - n_src_data_idx_0 - n_src_data_idx_1
        return n_src_data_idx_0 * [src_data[0]] + \
                n_src_data_idx_1 * [src_data[1]] + \
                n_src_data_idx_2 * [src_data[2]]

    n_process = psutil.cpu_count(logical=False) - 1
    src_data = [r"\\10.18.200.241\public\aibot\data_full_13_11",
                r"\\10.18.200.241\public\aibot\data_full_10_8",
                r"\\10.18.200.241\public\aibot\data_full_7_5"]

    print(f"The number of running process: {n_process}")
    if sys.platform.startswith('win'):
        freeze_support()
    with Pool(processes=n_process) as pool:
        pool.map(run_bot_simulation, divide_job(n_process, src_data))