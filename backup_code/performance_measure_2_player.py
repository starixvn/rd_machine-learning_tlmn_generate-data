from agent_bot.TL_AI_bot import Bot_TL_AI
from agent_bot.bot_2_players_honestly import Bot_2_players_honestly
import numpy as np
import random
from tienlen_libs import Card, NaturalWin, Reward
from multiprocessing import Pool
import psutil
from tqdm import tqdm
import time


class Game(object):
    def __init__(self):
        self.reward = Reward()
        self.tl_ai_bot = Bot_TL_AI()
        self.hard_bot = Bot_2_players_honestly(
            model_dir=r"C:\Users\justin.pham\OneDrive\Documents\Code\TLMN\bot-see-opponent-cards\src\models\Bot_TLMN_solo_hard_level.keras")
        self.medium_bot = Bot_2_players_honestly(
            model_dir=r"C:\Users\justin.pham\OneDrive\Documents\Code\TLMN\bot-see-opponent-cards\src\models\Bot_TLMN_solo_medium_level.keras")
        self.natural_win = NaturalWin()

    def _check_medium_bot_state(self, medium_bot_state, I_play_first):
        our_card, opponent_action, opponent_actions_card, \
                our_actions_card, deck_remain, len_opponent_card = medium_bot_state

        assert len(set(our_card).union(set(our_actions_card))) == 13, "Union of our_card and our_actions_card must equal our_initial_card"
        assert not set(our_card).intersection(set(our_actions_card)), "our_card and our_actions_card must be disjoint"
        assert set(opponent_action).issubset(set(opponent_actions_card)), "Opponent action must be subset of opponent actions card"
        assert len(deck_remain) == 39 - len(opponent_actions_card), "Length of deck_remain must be equal to 39 - len(opponent_actions_card)"
        assert not set(deck_remain).intersection(set(our_card)), "deck_remain must not intersect with our_card"
        assert not set(deck_remain).intersection(set(our_actions_card)), "deck_remain must not intersect with our_actions_card"
        assert not set(deck_remain).intersection(set(opponent_actions_card)), "deck_remain must not intersect with opponent_actions_card"
        assert isinstance(len_opponent_card, int), "len_opponent_card must be an integer"
        assert 1 <= len_opponent_card <= 13, "len_opponent_card must be between 1 and 13"
        assert I_play_first in [0, 1], "I_play_first must be 0 or 1"

    # def hard_and_medium_choose_best_action_with_max_Q_value(self, state, I_play_first):
    #     hard_res = self.hard_bot.predict_Q_value_of_all_action(state, I_play_first)
    #     medium_res = self.medium_bot.predict_Q_value_of_all_action(state, I_play_first)
    #     assert set(hard_res.keys()) == set(medium_res.keys())
    #     avg_res = {}
    #     for key in hard_res:
    #         avg_res[key] = (0.3*hard_res[key]) + (0.7*medium_res[key])
    #     print(f"hard_res = {hard_res}")
    #     print(f"medium_res = {medium_res}")
    #     print(f"avg_res = {avg_res}")
    #     return max(avg_res.items(), key=lambda x: x[1])[0]

    def _bot_vs_bot(self, player1_card, player2_card, who_play_first, bot2_kargs, bot1_kargs):
        assert len(player1_card) == 13 and len(player2_card) == 13, "Length of player1_card and player2_card must be 13"
        full_deck = list(range(52))
        actions_card_player1 = []
        actions_card_player2 = []
        deck_remain_player1 = [card for card in full_deck if card not in player2_card]
        deck_remain_player2 = [card for card in full_deck if card not in player1_card]

        if who_play_first == 1:
            state = (tuple(player1_card), tuple(), tuple(actions_card_player2),
                    tuple(actions_card_player1), tuple(deck_remain_player2), len(player2_card))
            assert state[-1] == 13 and len(state[-2]) == 39
            player1_play_first = 1 if who_play_first == 1 else 0
            player2_action = tuple()
            bot_1_args = (eval(bot1_kargs["args"][0]), eval(bot1_kargs["args"][1]))
            player1_action = bot1_kargs["func"](*bot_1_args)
        else:
            player1_action = tuple()
        # print(f"\nPlayer 1 card: ", end=""); Card.print_pretty_cards(player1_card)
        player1_card = [card for card in player1_card if card not in player1_action]
        # print(f"Player {who_play_first} plays first")
        # print(f"Player 1 action: ", end=""); Card.print_pretty_cards(player1_action)
        actions_card_player1 = list(player1_action)
        deck_remain_player1 = [card for card in deck_remain_player1 if card not in player1_action]
        assert len(deck_remain_player1) == 39 - len(player1_action)
        cumsum_bomb_beat = 0

        while 1:
            state = (tuple(player2_card), tuple(player1_action), tuple(actions_card_player1), 
                    tuple(actions_card_player2), tuple(deck_remain_player1), len(player1_card))
            player2_play_first = 1 if who_play_first == 2 else 0
            # print(f"state = {state}")
            # print(f"player2_play_first = {player2_play_first}")
            self._check_medium_bot_state(state, player2_play_first)

            #Player 2 turn
            # print(f"Player 2 card: ", end=""); Card.print_pretty_cards(player2_card)
            bot_2_args = (eval(bot2_kargs["args"][0]), eval(bot2_kargs["args"][1]))
            player2_action = bot2_kargs["func"](*bot_2_args)
            # print(f"Player 2 action: ", end=""); Card.print_pretty_cards(player2_action)
            player2_card = [card for card in player2_card if card not in player2_action]
            actions_card_player2 = actions_card_player2 + list(player2_action)
            actions_card_player2.sort()
            deck_remain_player2 = [card for card in deck_remain_player2 if card not in player2_action]
            cumsum_bomb_beat += self.reward.get_bomb_beating_penalty(player1_action, player2_action)
            if len(player2_card) == 0:
                # print("Player 2 win !!!")
                return self.reward.get_reward(player1_card, player2_card) + cumsum_bomb_beat

            #Player 1 turn
            # print(f"\nPlayer 1 card: ", end=""); Card.print_pretty_cards(player1_card)
            state = (tuple(player1_card), tuple(player2_action), tuple(actions_card_player2),
                    tuple(actions_card_player1), tuple(deck_remain_player2), len(player2_card))
            player1_play_first = 1 if who_play_first == 1 else 0
            self._check_medium_bot_state(state, player1_play_first)
            bot_1_args = (eval(bot1_kargs["args"][0]), eval(bot1_kargs["args"][1]))
            player1_action = bot1_kargs["func"](*bot_1_args)
            # print(f"Player 1 action: ", end=""); Card.print_pretty_cards(player1_action)
            player1_card = [card for card in player1_card if card not in player1_action]
            actions_card_player1 = actions_card_player1 + list(player1_action)
            actions_card_player1.sort()
            deck_remain_player1 = [card for card in deck_remain_player1 if card not in player1_action]
            cumsum_bomb_beat += (-1 * self.reward.get_bomb_beating_penalty(player2_action, player1_action))
            if len(player1_card) == 0:
                # print("Player 1 win !!!")
                return self.reward.get_reward(player1_card, player2_card) + cumsum_bomb_beat

    def medium_vs_medium(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})

    def hard_vs_medium(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.hard_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})

    def tl_ai_vs_medium(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player1_action", "player2_card")},
                                bot1_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})

    def medium_vs_hard(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.hard_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})

    def hard_vs_hard(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.hard_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.hard_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})

    def tl_ai_vs_hard(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player1_action", "player2_card")},
                                bot1_kargs = {"func": self.hard_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})
    
    def medium_vs_tl_ai(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player2_action", "player1_card")})
    
    def hard_vs_tl_ai(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.hard_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player2_action", "player1_card")})
    
    def tl_ai_vs_tl_ai(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player1_action", "player2_card")},
                                bot1_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player2_action", "player1_card")})

    def run_one_game(self):
        full_deck = list(range(52))
        np.random.shuffle(full_deck)
        player1_card = full_deck[:13]; player1_card.sort()
        player2_card = full_deck[13:26]; player2_card.sort()
        # print("Player1 cards: ", end=""); Card.print_pretty_cards(player1_card)
        # print("Player2 cards: ", end=""); Card.print_pretty_cards(player2_card)
        who_play_first = random.choice([1, 2])

        MATCH_TYPES = [
            (self.medium_vs_medium.__name__, self.medium_vs_medium),
            (self.hard_vs_medium.__name__, self.hard_vs_medium),
            (self.tl_ai_vs_medium.__name__, self.tl_ai_vs_medium), 
            (self.medium_vs_hard.__name__, self.medium_vs_hard),
            (self.hard_vs_hard.__name__, self.hard_vs_hard),
            (self.tl_ai_vs_hard.__name__, self.tl_ai_vs_hard),
            (self.medium_vs_tl_ai.__name__, self.medium_vs_tl_ai),
            (self.hard_vs_tl_ai.__name__, self.hard_vs_tl_ai),
            (self.tl_ai_vs_tl_ai.__name__, self.tl_ai_vs_tl_ai)
        ]

        if self.natural_win.detect_natural_win(player1_card) or self.natural_win.detect_natural_win(player2_card):
            return None
        
        results = {}
        for tolerance_pass in [1.5]:
            self.hard_bot.tolerance_pass = tolerance_pass
            self.medium_bot.tolerance_pass = tolerance_pass
            results_tolerance_pass = {}
            for match_type, match_func in MATCH_TYPES:
                results_tolerance_pass[match_type] = match_func(player1_card.copy(), player2_card.copy(), who_play_first)
            results[tolerance_pass] = results_tolerance_pass
        return results

def process_computer(n_iter):
    game = Game()
    while 1:
        summary_res = game.run_one_game()
        if summary_res is not None: break
    
    for i in tqdm(range(n_iter)):
        # print(f"\nGame {i+1}")
        res = game.run_one_game()
        if res is None: continue
        for tolerance_pass in res:
            for match_type in res[tolerance_pass]:
                summary_res[tolerance_pass][match_type] += res[tolerance_pass][match_type]
    return summary_res        

if __name__ == "__main__":
    n_process = 10
    with Pool(processes=n_process) as pool:
        list_summary_res = pool.map(process_computer, [1000] * n_process)

    final_summary = list_summary_res[0]
    for res in list_summary_res[1:]:
        for tolerance_pass in res:
            for match_type in res[tolerance_pass]:
                final_summary[tolerance_pass][match_type] += res[tolerance_pass][match_type] 

    for tolerance_pass in final_summary:
        print()
        for match_type in final_summary[tolerance_pass]:
            print(f"[TOLERANCE {tolerance_pass}] Summary result of {match_type}: {final_summary[tolerance_pass][match_type]}")