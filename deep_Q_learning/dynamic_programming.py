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

def value_iteration_RAM_optimize(env):
    # print("\nRunning Value Iteration...")
    num_iterations = 10000
    threshold = 1e-20
    gamma = 1.0
    
    value_table = {state: 0.0 for state in env}
    for i in range(num_iterations):
        updated_value_table = value_table.copy()
        for state, state_info in env.items():
            Q_values = []
            for action_info in state_info.values():
                next_state, reward, terminated = action_info
                if terminated:
                    assert reward != 0, f"Reward = {reward}"
                    Q_values.append(reward)
                else:
                    Q_values.append(reward + gamma * updated_value_table[next_state])
            value_table[state] = max(Q_values)
        if sum(abs(updated_value_table[state] - value_table[state]) for state in env) < threshold:
            break
    return value_table

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
    
    for state, state_info in env.items():
        action_Q_value = {}
        for action, action_info in state_info.items():
            next_state, reward, terminated = action_info
            if terminated:
                assert reward != 0, f"Reward = {reward}"
                action_Q_value[action] = reward
            else:
                action_Q_value[action] = reward + gamma * value_table[next_state]
        Q_table[state] = action_Q_value
    return Q_table