from collections import defaultdict
import time
from tienlen_libs import Card, ActionGenerator, Utils, NaturalWin, Reward
from tienlen_libs.constant import ComboType
import pickle
from multiprocessing import Pool, freeze_support
import os
import psutil
from datetime import datetime
import sys
import numpy as np
import random
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

    def reset_player_skip(self, player_skip):
        for i in range(self.n_player):
            player_skip[i] = False

    def get_player_action(self, player_id, player_id_card, last_action, turn):
        if turn == player_id:
            player_action = self.tl_ai_bot.run_rule_based_bot([], player_id_card)
        else:
            player_action = self.tl_ai_bot.run_rule_based_bot(last_action, player_id_card)
        return player_action

    def remove_list_card_from_player_card(self, player_card, list_card_to_remove):
        return tuple([card for card in player_card if card not in list_card_to_remove])

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
            list_valid_action = self.action_generator.get_list_valid_action(player_id_card, tuple())
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

    def get_list_valid_action_of_first_player(self, first_player_id, first_player_card, 
                                            last_action, turn, player_skip):
        if not player_skip[first_player_id]:
            if turn == first_player_id: self.reset_player_skip(player_skip)
            list_valid_action_first_player = self.get_list_valid_action_of_player(
                                            first_player_id, first_player_card, last_action, turn)
        else:
            list_valid_action_first_player = self.get_list_valid_action_in_skip_condition(
                                            first_player_id, first_player_card, last_action, turn)
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
            turn = self.update_turn(player_id, player_id_action, turn)
        return turn

    def move_to_next_turn(self, turn):
        return (turn + 1) % self.n_player

    def run_round_for_other_players(self, player_card, player_action, player_skip, turn, player_id_start=1):
        for player_id in range(player_id_start, self.n_player):
            if not player_card[player_id]:
                player_action[player_id] = self.finish_int_encode
                if turn == player_id:
                    turn = self.move_to_next_turn(turn)
                    player_skip[turn] = False
                continue

            if not player_card[0]:
                player_action[player_id] = self.skip_int_encode
                continue

            if not player_skip[player_id]:
                if turn == player_id: self.reset_player_skip(player_skip)
                player_id_action = self.get_player_action(
                                        player_id, player_card[player_id], player_action[turn], turn)
            else:
                player_id_action = self.get_player_action_in_skip_condition(
                                        player_id, player_card[player_id], player_action[turn], turn)
            
            turn = self.update_player_card_action_skip_turn(player_card, player_action, player_skip, turn,
                                                            player_id, player_id_action)

        return turn
    
    def encode_state(self, player_card, player_action, player_skip, turn):
        player_card_encode = tuple(cards for cards in player_card)
        player_action_encode = tuple(cards for cards in player_action[1:])
        # player_skip_encode = tuple(player_skip[i] for i in range(1, self.n_player + 1))
        # state = (player_card_encode, player_action_encode, turn)
        state = player_card_encode + player_action_encode + (turn,)
        return state

    def recursive_depth_first_search(self, env, player_card, player_action, player_skip, turn):
        if not player_card[0] or all(not cards for cards in player_card[1:]):
            return
        state = self.encode_state(player_card, player_action, player_skip, turn)
        if state in env: return
        
        list_valid_action_player0 = self.get_list_valid_action_of_first_player(
                                        0, player_card[0], player_action[turn], turn, player_skip)
        for valid_action_player0 in list_valid_action_player0:
            next_player_card = player_card.copy()
            next_player_action = player_action.copy()
            next_player_skip = player_skip.copy()

            next_turn = self.update_player_card_action_skip_turn(next_player_card, next_player_action, next_player_skip, 
                                                                turn, 0, valid_action_player0)

            next_turn = self.run_round_for_other_players(
                            next_player_card, next_player_action, next_player_skip, next_turn)
            
            next_state = self.encode_state(next_player_card, next_player_action, next_player_skip, next_turn)
            reward = self.reward.get_reward_more_than_2_players(next_player_card)
            env[state][valid_action_player0] = (next_state, reward)
            self.recursive_depth_first_search(env, next_player_card, next_player_action, next_player_skip, next_turn)
 
    def build_env(self, player_card, who_play_first):
        player_action = [()] * self.n_player
        player_skip = [False] * self.n_player
        turn = who_play_first
        if who_play_first != 0:
            turn = self.run_round_for_other_players(
                        player_card, player_action, player_skip, turn, player_id_start=who_play_first)

        env = defaultdict(dict)
        self.recursive_depth_first_search(env, player_card, player_action, player_skip, turn)
        return env


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
            bot_simulation.action_generator.get_list_valid_action.cache_clear()
            print(f"The length of the env: {len(env):,}")
        except Exception as e:
            print(f"\nThe ERRRRRRRROOOOOOOOOOOORRRRRRRRRR occurs:", e)
            for i in range(len(player_card)):
                print(f"Player {i} cards: ", end=""); Card.print_pretty_cards(player_card[i])
            print(f"Player {who_play_first} plays first")

if __name__ == "__main__":
    n_process = psutil.cpu_count(logical=False) - 1
    src_data = r"C:\Users\justin.pham\Downloads\tmp"

    print(f"The number of running process: {n_process}")
    print(f"Finding src_data status: {os.path.exists(src_data)}")
    os.makedirs(src_data, exist_ok=True)
    if sys.platform.startswith('win'):
        freeze_support()
    with Pool(processes=n_process) as pool:
        pool.map(run_bot_simulation, [src_data] * n_process)