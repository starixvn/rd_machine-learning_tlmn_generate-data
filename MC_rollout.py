from tienlen_libs.env import TienLenEnv
from tienlen_libs import ActionGenerator, Reward, NaturalWin, Utils
import pickle
from more_itertools import split_into
import numpy as np
from os.path import join, dirname


class MC_Rollout(object):
    def __init__(self):
        self.env = TienLenEnv()
        self.action_generator = ActionGenerator()
        self.reward = Reward()
        self.utils = Utils()
        self.natural_win = NaturalWin()

        self.n_simulation = 5000

    def decode_state_data(self, state_data):
        n_player = self.env.n_player
        assert len(state_data) == 3 * n_player

        player_card = list(state_data[:n_player])
        player_action = [()] + list(state_data[n_player:2*n_player-1])
        player_skip = list(state_data[2*n_player-1:3*n_player-1])
        turn = state_data[-1]

        assert all(isinstance(x, bool) for x in player_skip), f"{player_skip}"
        assert 0 <= turn < n_player, f"{turn}"

        return self.env.STATE(player_card=player_card, player_action=player_action,
                                player_skip=player_skip, turn=turn)

    def run_episode_from_state(self, state):
        total_bomb_beat = 0

        while True:
            action_player0 = self.env.get_player_action(
                0, state.player_card, state.player_action, state.player_skip, state.turn)

            state, step_info = self.env.step(state, action_player0)
            total_bomb_beat += step_info.bomb_beat

            if step_info.done:
                return step_info.win_rank, total_bomb_beat

    def get_state_and_actions_from_data(self, data):
        assert len(data) == 1
        state_data = list(data.keys())[0]
        state = self.decode_state_data(state_data)
        valid_actions = list(data[state_data].keys())
        return state, valid_actions

    def generate_random_card_for_each_remain_player(self, cur_player_card, origin_player_card, max_n_iter):
        n_player = len(origin_player_card)
        deck_remain = list(sum(cur_player_card[1:n_player], ()))
        len_other_player_card = tuple([len(cur_player_card[i]) for i in range(1, n_player)])
        assert all(0 <= length <= 13 for length in len_other_player_card), f"{len_other_player_card}" 

        other_player_action_cards = [
            tuple(set(origin_player_card[i]) - set(cur_player_card[i])) for i in range(1, n_player)
        ]
        assert all(len(other_player_action_cards[i]) + len_other_player_card[i] == 13 
                    for i in range(n_player-1))

        n_combination = self.utils.cal_total_n_combination(len(deck_remain), len_other_player_card)
        if n_combination >= (2*max_n_iter):
            n_yield = 0
            while n_yield < max_n_iter:
                np.random.shuffle(deck_remain)
                other_player_card = [tuple(sorted(x)) for x in split_into(deck_remain, len_other_player_card)]
                if any(self.natural_win.detect_natural_win(sorted(other_player_card[i] + other_player_action_cards[i])) 
                        for i in range(n_player-1)): 
                    continue
                yield other_player_card
                n_yield += 1
        else:
            for partition in self.utils.partition_by_sizes(deck_remain, len_other_player_card):
                other_player_card = [tuple(sorted(x)) for x in partition]
                if any(self.natural_win.detect_natural_win(sorted(other_player_card[i] + other_player_action_cards[i])) 
                        for i in range(n_player-1)): 
                    continue
                yield other_player_card

    def create_state_with_other_player_card(self, state, other_player_card):
        assert all(len(state.player_card[i+1]) == len(other_player_card[i]) 
                    for i in range(self.env.n_player-1)), f"{state}"
        return self.env.STATE(
                    player_card=[state.player_card[0]] + other_player_card,
                    player_action=state.player_action.copy(),
                    player_skip=state.player_skip.copy(),
                    turn=state.turn
                )

    def run_simulation(self, data, origin_player_card):
        state, valid_actions = self.get_state_and_actions_from_data(data)
        assert len(valid_actions) >= 2

        list_other_player_card = list(self.generate_random_card_for_each_remain_player(
                            state.player_card, origin_player_card, self.n_simulation))
        
        stats_res = {}
        for action in valid_actions:

            simu_result = {"win_rank": [], "bomb_beat": []}
            for other_player_card in list_other_player_card:
                state_new = self.create_state_with_other_player_card(state, other_player_card)

                next_state, step1_info = self.env.step(state_new, action)
                if step1_info.done:
                    simu_result["win_rank"].append(step1_info.win_rank)
                    simu_result["bomb_beat"].append(step1_info.bomb_beat)
                else:
                    win_rank, total_bomb_beat = self.run_episode_from_state(next_state)
                    simu_result["win_rank"].append(win_rank)
                    simu_result["bomb_beat"].append(step1_info.bomb_beat + total_bomb_beat)

            stats_res[action] = {k: float(np.mean(v)) for k, v in simu_result.items()}
        return stats_res

    def cal_and_save_stats_of_state(self, data_dir, result_dir):
        # print(f"\nProcessing {data_dir} => {result_dir} ...")
        with open(data_dir, "rb") as f:
            data = pickle.load(f)
        
        initial_game_info_dir = join(dirname(data_dir), "initial_game_info.pkl")
        with open(initial_game_info_dir, "rb") as f:
            initial_game_info = pickle.load(f)
        origin_player_card = initial_game_info["player_card"]

        stats_result = self.run_simulation(data, origin_player_card)
        assert len(data) == 1
        stats_data = (list(data.keys())[0], stats_result)

        with open(result_dir, "wb") as f:
            pickle.dump(stats_data, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    pass