from tienlen_libs import ActionGenerator, Utils, Reward
from tienlen_libs.constant import ComboType
from agent_bot.TL_AI_bot import Bot_TL_AI
from collections import namedtuple


class TienLenEnv(object):
    def __init__(self, n_player=4):
        self.n_player = n_player
        self.action_generator = ActionGenerator()
        self.utils = Utils()
        self.reward = Reward()
        self.tl_ai_bot = Bot_TL_AI()
        
        self.skip_int_encode = -1
        self.finish_int_encode = -2

        self.STATE = namedtuple('state', ['player_card', 'player_action', 
                                            'player_skip', 'turn'])
        self.STEP_INFO = namedtuple('step_info', ['done', 'win_rank', 'bomb_beat'])

    def reset_player_skip(self, player_skip, player_action):
        for i in range(self.n_player):
            if player_action[i] != self.finish_int_encode:
                player_skip[i] = False

    def remove_list_card_from_player_card(self, player_card, list_card_to_remove):
        return tuple([card for card in player_card if card not in list_card_to_remove])

    def update_player_card(self, player_card, player_id, player_id_action):
        if player_id_action:                
            player_card[player_id] = self.remove_list_card_from_player_card(
                                        player_card[player_id], player_id_action)
    
    def update_player_skip(self, player_skip, player_id, player_action, turn):
        if player_action[player_id]:
            if turn == player_id: 
                self.reset_player_skip(player_skip, player_action)
            else:
                player_skip[player_id] = False
        else:
            player_skip[player_id] = True
    
    def update_player_card_action_skip_turn(self, player_card, player_action, player_skip, turn,
                                            player_id, player_id_action):
        player_action[player_id] = player_id_action
        if player_id_action != self.skip_int_encode:
            self.update_player_card(player_card, player_id, player_id_action)
            self.update_player_skip(player_skip, player_id, player_action, turn)
            if player_id_action: turn = player_id
        return turn

    def get_player_action_in_normal_condition(self, player_id, player_id_card, last_action, turn):
        if turn == player_id:
            player_action = self.tl_ai_bot.run_rule_based_bot((), player_id_card)
        else:
            player_action = self.tl_ai_bot.run_rule_based_bot(last_action, player_id_card)
        return player_action

    def get_player_action_in_skip_condition(self, player_id, player_id_card, last_action, turn):
        assert turn != player_id, f"turn = {turn}, player_id = {player_id}"

        if self.utils.is_deuce_or_pair_deuce(last_action):
            player_id_action = self.get_player_action_in_normal_condition(
                                                player_id, player_id_card, last_action, turn)
            if self.utils.get_combo_type(player_id_action) == ComboType.DOUBLE_SEQUENCE_FOUR:
                return player_id_action
        return self.skip_int_encode

    def get_player_action(self, player_id, player_card, player_action, player_skip, turn):
        if not player_skip[player_id]:
            player_id_action = self.get_player_action_in_normal_condition(
                                    player_id, player_card[player_id], player_action[turn], turn)
        else:
            player_id_action = self.get_player_action_in_skip_condition(
                                    player_id, player_card[player_id], player_action[turn], turn)
        return player_id_action

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

            player_id_action = self.get_player_action(player_id, player_card, player_action, player_skip, turn)
            
            if turn == 0:
                bomb_beat_other_player -= self.get_bomb_beating_penalty_4_players(turn, player_action[turn], 
                                                                                player_id, player_id_action)
            turn = self.update_player_card_action_skip_turn(player_card, player_action, player_skip, turn,
                                                            player_id, player_id_action)

        return turn, bomb_beat_other_player
    
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
        return 1 if bomb_beating_penalty > 0 else 0

    def step(self, state, action_player0):
        next_player_card = state.player_card.copy()
        next_player_action = state.player_action.copy()
        next_player_skip = state.player_skip.copy()
        turn = state.turn

        bomb_beat_player0 = self.get_bomb_beating_penalty_4_players(turn, next_player_action[turn],
                                                                    0, action_player0)
        next_turn = self.update_player_card_action_skip_turn(next_player_card, next_player_action, 
                                                            next_player_skip, turn,
                                                            0, action_player0)

        next_turn, bomb_beat_other_player = self.run_round_for_other_players(
                                    next_player_card, next_player_action, next_player_skip, next_turn)
        bomb_beat_in_round = bomb_beat_player0 + bomb_beat_other_player

        next_state = self.STATE(player_card=next_player_card,
                                player_action=next_player_action,
                                player_skip=next_player_skip,
                                turn=next_turn)

        done = self.is_terminated(next_player_card)
        win_rank = self.reward.cal_n_other_player_playing(next_player_card) if done else None
        step_info = self.STEP_INFO(done=done, win_rank=win_rank, bomb_beat=bomb_beat_player0)

        return next_state, step_info