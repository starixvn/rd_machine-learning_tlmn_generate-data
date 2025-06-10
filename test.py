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
from deep_Q_learning import value_iteration, extract_optimal_Q_table
from copy import deepcopy
import gc
from test_main_3_player import Bot_Simulation, calculate_optimal_Q_table

bot_simulation = Bot_Simulation()
full_deck = list(range(52))
np.random.shuffle(full_deck)
player1_card = full_deck[:13]; player1_card.sort()
player2_card = full_deck[13:26]; player2_card.sort()
player3_card = full_deck[26:39]; player3_card.sort()
player_card = {1: player1_card, 2: player2_card, 3: player3_card}
assert len(player_card) == bot_simulation.n_player
who_play_first = random.choice(list(range(1, bot_simulation.n_player + 1)))
env = bot_simulation.build_env(deepcopy(player_card), who_play_first)
optimal_Q_table = calculate_optimal_Q_table(env)

def print_action(action, end="\n"):
    print(f"Action: ", end="")
    if action == bot_simulation.skip_int_encode:
        print("SKIP", end=end)
    elif len(action) == 0:
        print("PASS", end=end)
    else:
        Card.print_pretty_cards(action, end=end)

def print_state(state):
    for player_id in range(1, bot_simulation.n_player + 1):
        player_id_card = state[0][player_id-1]
        print(f"Player {player_id} card [len={len(player_id_card)}]: ", end="")
        Card.print_pretty_cards(player_id_card, end="; ")
        if player_id > 1:
            player_id_action = state[1][player_id-2]
            print_action(player_id_action)
        else:
            print()
    print(f"Turn = {state[2]}")

start_state = list(env.keys())[0]
print(f"Player {who_play_first} play first")
print_state(start_state)
while 1:
    if len(start_state[0][0]) == 0 or len(start_state[0][1]) == 0 or len(start_state[0][2]) == 0:
        print("TERMINATED")
        break
    print(f"Full Q value start_state:")
    for action in env[start_state]:
        print_action(action, end=" => ")
        print(optimal_Q_table[start_state][action])
    # random_action = random.choice(list(env[start_state].keys()))
    random_action = input("Choose action: ")
    try:
        random_action = tuple(Card.new(elem) for elem in random_action.split())
    except:
        random_action = -1
    print_action(random_action)
    next_state, reward = env[start_state][random_action]
    print_state(next_state)
    if reward != 0:
        print(f"Reward = {reward}")
    else:
        print(f"Optimal Q value = {optimal_Q_table[start_state][random_action]}")
    print()
    start_state = next_state