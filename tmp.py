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
from deep_Q_learning import value_iteration_RAM_optimize, extract_optimal_Q_table_RAM_optimize
from agent_bot.TL_AI_bot import Bot_TL_AI


class Bot_Simulation_Test(object):
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
            turn = self.update_turn(player_id, player_id_action, turn)
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
        player_card_encode = tuple(cards for cards in player_card)
        player_action_encode = tuple(cards for cards in player_action[1:])
        state = player_card_encode + player_action_encode + tuple(player_skip) + (turn,)
        return state

    def get_bomb_beating_penalty_4_players(self, previous_player_id, previous_action, 
                                                    current_player_id, current_action):
        if previous_player_id == current_player_id:
            return 0
        if isinstance(previous_action, int) or isinstance(current_action, int):
            return 0
        bomb_beating_penalty = self.reward.get_bomb_beating_penalty(previous_action, current_action)
        return 4 if bomb_beating_penalty > 0 else 0

    def recursive_depth_first_search(self, env, player_card, player_action, player_skip, turn):
        if not player_card[0] or all(not cards for cards in player_card[1:]):
            return
        state = self.encode_state(player_card, player_action, player_skip, turn)
        if state in env: return
        
        list_valid_action_player0 = self.get_list_valid_action_of_first_player(
                                        0, player_card[0], player_action, turn, player_skip)
        for valid_action_player0 in list_valid_action_player0:
            next_player_card = player_card.copy()
            next_player_action = player_action.copy()
            next_player_skip = player_skip.copy()

            bomb_beat_player0 = self.get_bomb_beating_penalty_4_players(turn, player_action[turn],
                                                                        0, valid_action_player0)

            next_turn = self.update_player_card_action_skip_turn(next_player_card, next_player_action, next_player_skip, 
                                                                turn, 0, valid_action_player0)

            next_turn, bomb_beat_other_player = self.run_round_for_other_players(
                            next_player_card, next_player_action, next_player_skip, next_turn)
            
            next_state = self.encode_state(next_player_card, next_player_action, next_player_skip, next_turn)
            reward = self.reward.get_reward_more_than_2_players(next_player_card) + \
                        bomb_beat_player0 + bomb_beat_other_player
            terminated = not next_player_card[0] or all(not cards for cards in next_player_card[1:])
            env[state][valid_action_player0] = (next_state, reward, terminated)
            self.recursive_depth_first_search(env, next_player_card, next_player_action, next_player_skip, next_turn)
 
    # def build_env(self, player_card, who_play_first):
    #     player_action = [()] * self.n_player
    #     player_skip = [False] * self.n_player
    #     turn = who_play_first
    #     if who_play_first != 0:
    #         turn = self.run_round_for_other_players(
    #                     player_card, player_action, player_skip, turn, player_id_start=who_play_first)

    #     env = defaultdict(dict)
    #     self.recursive_depth_first_search(env, player_card, player_action, player_skip, turn)
    #     return env

    def decode_state(self, state):
        assert len(state) == 3 * self.n_player
        player_card = list(state[:self.n_player])
        player_action = [()] + list(state[self.n_player:2*self.n_player-1])
        player_skip = list(state[2*self.n_player-1:3*self.n_player-1])
        turn = state[-1]
        assert all(isinstance(x, bool) for x in player_skip), \
                f"player_skip must be all boolean: {player_skip}"
        assert 0 <= turn < 4, f"turn must be in range [0,4): {turn}"
        return player_card, player_action, player_skip, turn

    def build_env(self, state, other_player_card):
        player_card, player_action, player_skip, turn = self.decode_state(state)
        player_card[1:] = other_player_card

        env = defaultdict(dict)
        self.recursive_depth_first_search(env, player_card, player_action, player_skip, turn)
        optimal_Q_table = calculate_optimal_Q_table(env)
        return optimal_Q_table


def calculate_optimal_Q_table(env):
    value_table = value_iteration_RAM_optimize(env)
    optimal_Q_table = extract_optimal_Q_table_RAM_optimize(value_table, env)
    return optimal_Q_table


if __name__ == "__main__":
    pass