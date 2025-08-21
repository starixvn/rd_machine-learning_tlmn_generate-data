from agent_bot.TL_AI_bot import Bot_TL_AI
from agent_bot.bot_2_players_honestly import Bot_2_players_honestly
import numpy as np
import random
from tienlen_libs import Card, NaturalWin, Reward
import time


class Game(object):
    def __init__(self):
        self.reward = Reward()
        self.tl_ai_bot = Bot_TL_AI()
        self.medium_bot = Bot_2_players_honestly()
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
        player1_card = [card for card in player1_card if card not in player1_action]
        # print(f"Player {who_play_first} plays first")
        # print(f"\nPlayer 1 action: ", end=""); Card.print_pretty_cards(player1_action)
        actions_card_player1 = list(player1_action)
        deck_remain_player1 = [card for card in deck_remain_player1 if card not in player1_action]
        assert len(deck_remain_player1) == 39 - len(player1_action)
        cumsum_bomb_beat = 0

        while 1:
            state = (tuple(player2_card), tuple(player1_action), tuple(actions_card_player1), 
                    tuple(actions_card_player2), tuple(deck_remain_player1), len(player1_card))
            player2_play_first = 1 if who_play_first == 2 else 0
            # print(f"state = {state}")
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
                 
    
    def medium_vs_tl_ai(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player2_action", "player1_card")})

    def tl_ai_vs_tl_ai(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player1_action", "player2_card")},
                                bot1_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player2_action", "player1_card")})
    
    def medium_vs_medium(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player2_play_first")},
                                bot1_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})
    def tl_ai_vs_medium(self, player1_card, player2_card, who_play_first):
        return self._bot_vs_bot(player1_card, player2_card, who_play_first, 
                                bot2_kargs = {"func": self.tl_ai_bot.run_rule_based_bot, 
                                              "args": ("player1_action", "player2_card")},
                                bot1_kargs = {"func": self.medium_bot.choose_best_action_with_max_Q_value, 
                                              "args": ("state", "player1_play_first")})

    def run_one_game(self):
        full_deck = list(range(52))
        np.random.shuffle(full_deck)
        player1_card = full_deck[:13]; player1_card.sort()
        player2_card = full_deck[13:26]; player2_card.sort()
        # print("Player1 cards: ", end=""); Card.print_pretty_cards(player1_card)
        # print("Player2 cards: ", end=""); Card.print_pretty_cards(player2_card)
        if self.natural_win.detect_natural_win(player1_card) or self.natural_win.detect_natural_win(player2_card):
            # print("Natural Win Detected: SKIPPING this game!!!")
            return {
                "medium_bot_versus_tl_ai_bot": 0,
                "tl_ai_bot_versus_tl_ai_bot": 0,
                "medium_bot_versus_medium_bot": 0,
                "tl_ai_bot_versus_medium_bot": 0,
            }
        
        who_play_first = random.choice([1, 2])
        res_1 = self.medium_vs_tl_ai(player1_card.copy(), player2_card.copy(), who_play_first)
        res_2 = self.tl_ai_vs_tl_ai(player1_card.copy(), player2_card.copy(), who_play_first)
        res_3 = self.medium_vs_medium(player1_card.copy(), player2_card.copy(), who_play_first)
        res_4 = self.tl_ai_vs_medium(player1_card.copy(), player2_card.copy(), who_play_first)
        # print(f"Result of medium bot versus tl ai bot: {res_1}")
        # print(f"Result of tl ai bot versus tl ai bot: {res_2}")
        # print(f"Result of medium bot versus medium bot: {res_3}")
        # print(f"Result of tl ai bot versus medium bot: {res_4}")
        return {
            "medium_bot_versus_tl_ai_bot": res_1,
            "tl_ai_bot_versus_tl_ai_bot": res_2,
            "medium_bot_versus_medium_bot": res_3,
            "tl_ai_bot_versus_medium_bot": res_4
        }
        

if __name__ == "__main__":
    game = Game()
    summary_res = {
        "medium_bot_versus_tl_ai_bot": 0,
        "tl_ai_bot_versus_tl_ai_bot": 0,
        "medium_bot_versus_medium_bot": 0,
        "tl_ai_bot_versus_medium_bot": 0
    }
    for i in range(10000):
        print(f"\nGame {i+1}")
        res = game.run_one_game()
        for k in summary_res:
            summary_res[k] += res[k]
    print(f"Summary result of medium bot versus tl ai bot: {summary_res['medium_bot_versus_tl_ai_bot']}")
    print(f"Summary result of tl ai bot versus tl ai bot: {summary_res['tl_ai_bot_versus_tl_ai_bot']}")
    print(f"Summary result of medium bot versus medium bot: {summary_res['medium_bot_versus_medium_bot']}")
    print(f"Summary result of tl ai bot versus medium bot: {summary_res['tl_ai_bot_versus_medium_bot']}")