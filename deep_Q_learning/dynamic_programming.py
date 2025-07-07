import random
from copy import deepcopy
from tqdm import tqdm


def value_iteration(env, observation_space):
    # print("\nRunning Value Iteration...")
    num_iterations = 10000
    threshold = 1e-20
    gamma = 1.0
    
    value_table = {state: 0.0 for state in observation_space}
    for i in range(num_iterations):
        updated_value_table = deepcopy(value_table)
        for state in observation_space:
            Q_values = []
            for action in env[state]:
                next_state, reward = env[state][action]
                Q_values.append(reward + gamma * updated_value_table[next_state])
            if len(Q_values) > 0:
                value_table[state] = max(Q_values)
        if sum(abs(updated_value_table[state] - value_table[state]) for state in observation_space) < threshold:
            break
    return value_table

def is_terminal_state(state):
    player_card = state[0]
    return any(len(cards) == 0 for cards in player_card)

def value_iteration_RAM_optimize(env):
    # print("\nRunning Value Iteration...")
    num_iterations = 10000
    threshold = 1e-20
    gamma = 1.0
    
    value_table = {state: 0.0 for state in env}
    for i in range(num_iterations):
        updated_value_table = deepcopy(value_table)
        for state in env:
            Q_values = []
            for action in env[state]:
                next_state, reward = env[state][action]
                if is_terminal_state(next_state):
                    assert reward in [-1, 1], f"Reward = {reward}"
                    Q_values.append(reward)
                else:
                    Q_values.append(reward + gamma * updated_value_table[next_state])
            value_table[state] = max(Q_values)
        if sum(abs(updated_value_table[state] - value_table[state]) for state in env) < threshold:
            break
    return value_table

def extract_policy(value_table, env, observation_space):
    print("\nExtracting Optimal Policy from Optimal Value Table...")
    gamma = 1.0
    policy = {}
    
    for state in observation_space:
        Q_values = {}
        for action in env[state]:
            next_state, reward = env[state][action]
            Q_values[action] = reward + gamma * value_table[next_state]
        if len(Q_values) > 0:
            # policy[state] = max(Q_values, key=Q_values.get)
            max_Q_value = max(Q_values.values())
            max_Q_value_keys = [key for key, value in Q_values.items() if value == max_Q_value]
            policy[state] = random.choice(max_Q_value_keys)
            policy[state] = Q_values

    return policy

def extract_optimal_Q_table(value_table, env, observation_space):
    # print("\nExtracting Optimal Q Table from Optimal Value Table...")
    gamma = 1.0
    Q_table = {}
    
    for state in observation_space:
        if len(env[state]) == 0: continue
        Q_table[state] = {}
        for action in env[state]:
            next_state, reward = env[state][action]
            Q_table[state][action] = reward + gamma * value_table[next_state]

    return Q_table

def extract_optimal_Q_table_RAM_optimize(value_table, env):
    # print("\nExtracting Optimal Q Table from Optimal Value Table...")
    gamma = 1.0
    Q_table = {}
    
    for state in env:
        Q_table[state] = {}
        for action in env[state]:
            next_state, reward = env[state][action]
            if is_terminal_state(next_state):
                assert reward in [-1, 1], f"Reward = {reward}"
                Q_table[state][action] = reward
            else:
                Q_table[state][action] = reward + gamma * value_table[next_state]
    return Q_table