import polars as pl
from tienlen_libs import Utils


def generate_one_hot_encoding(cards: tuple[int], dimension: int = 52):
    return tuple(True if i in cards else False for i in range(dimension))

def generate_action_encoding(action: tuple[int]):
    skip_int_encode = -1
    if action == skip_int_encode:
        action_int_combo_type = 19
    else:
        action_int_combo_type = Utils.get_int_combo_type(action)
        assert action_int_combo_type < 19
    action_int_combo_type_encoding = generate_one_hot_encoding((action_int_combo_type,),
                                                               dimension=20)
    assert action_int_combo_type_encoding.count(True) == 1        
    max_card = max(action) if (action != skip_int_encode and len(action) > 0) else -1
    return action_int_combo_type_encoding + (max_card,)

def generate_player_card_encoding(player_card: tuple[tuple[int]]):
    return tuple(
        encoding
        for player_id_card in player_card
        for encoding in generate_one_hot_encoding(player_id_card)
    )

def generate_player_action_encoding(player_action: tuple[tuple[int]]):
    return tuple(
        encoding
        for player_id_action in player_action
        for encoding in generate_action_encoding(player_id_action)
    )

def generate_actions_card_player_encoding(player_card, initial_player_card):
    n_player = len(initial_player_card)
    actions_card_player_encoding = tuple()
    for i in range(n_player):
        player_id_card = player_card[i]
        initial_player_id_card = initial_player_card[i+1]
        actions_card_player_id = tuple([
            card for card in initial_player_id_card if card not in player_id_card
        ])
        assert len(player_id_card) + len(actions_card_player_id) == 13
        assert set(player_id_card).union(set(actions_card_player_id)) == set(initial_player_id_card)
        actions_card_player_encoding += generate_one_hot_encoding(actions_card_player_id)
    return actions_card_player_encoding

def determine_early_mid_end_game_stage(player_card):
    """
    Determine the early, mid, or end game stage of the game.
    Return 0 if the game is in the early game stage.
    Return 1 if the game is in the mid game stage.
    Return 2 if the game is in the end game stage.
    """
    assert len(player_card) == 3 and isinstance(player_card, tuple)
    len_player2_card = len(player_card[1])
    len_player3_card = len(player_card[2])
    if len_player2_card >= 9 and len_player3_card >= 9:
        return 0
    elif len_player2_card <= 5 and len_player3_card <= 5:
        return 2
    else:
        return 1

def generate_list_state_action_return_encode(game_data):
    Q_table = game_data["Q_table"]
    who_play_first = game_data["who_play_first"]
    initial_player_card = game_data["player_card"]
    n_player = len(initial_player_card)
    assert who_play_first in range(1, n_player + 1)
    assert all(len(initial_player_card[i]) == 13 for i in range(1, n_player + 1))
    who_play_first_encoding = generate_one_hot_encoding((who_play_first-1,), 
                                                        dimension=n_player)
    assert who_play_first_encoding.count(True) == 1

    for state in Q_table:
        if len(Q_table[state]) <= 1: continue
        player_card, player_action, turn = state
        assert len(player_card) == n_player
        assert len(player_action) == n_player - 1
        assert turn in range(1, n_player + 1)

        player_card_encoding = generate_player_card_encoding(player_card)
        player_action_encoding = generate_player_action_encoding(player_action)
        actions_card_player_encoding = generate_actions_card_player_encoding(
                                                player_card, initial_player_card)
        turn_encoding = generate_one_hot_encoding((turn-1,), dimension=n_player)
        assert turn_encoding.count(True) == 1
        game_stage = determine_early_mid_end_game_stage(player_card)
        assert game_stage in [0, 1, 2]

        for action in Q_table[state]:
            expected_return = Q_table[state][action]
            assert expected_return in [-1, 1]
            if expected_return == -1: expected_return = 0

            action_encoding = generate_action_encoding(action)

            state_action_return_encode = player_card_encoding + player_action_encoding + \
                                        actions_card_player_encoding + turn_encoding + action_encoding + \
                                        who_play_first_encoding + (game_stage, expected_return)
            yield state_action_return_encode

def undersample_df_table_for_mid_end_game_stage(df_table: pl.DataFrame):
    n_early_game_stage_sample = (df_table.get_column('game_stage') == 0).sum()
    n_mid_game_stage_sample = (df_table.get_column('game_stage') == 1).sum()
    n_mid_game_stage_sample = min(n_early_game_stage_sample * 2, n_mid_game_stage_sample)
    n_end_game_stage_sample = (df_table.get_column('game_stage') == 2).sum()
    n_end_game_stage_sample = min(n_early_game_stage_sample * 2, n_end_game_stage_sample)

    df_early_game_stage = df_table.filter(pl.col('game_stage') == 0).sample(n=n_early_game_stage_sample)
    df_mid_game_stage = df_table.filter(pl.col('game_stage') == 1).sample(n=n_mid_game_stage_sample)
    df_end_game_stage = df_table.filter(pl.col('game_stage') == 2).sample(n=n_end_game_stage_sample)

    df_undersampled = pl.concat([df_early_game_stage, df_mid_game_stage, df_end_game_stage])
    assert df_undersampled.shape[1] == df_early_game_stage.shape[1]
    return df_undersampled.drop('game_stage')

def create_polars_table_of_state_action_return_encode(game_data):
    n_player = 3
    schema_columns = [(f"player1_card_{i}", pl.Boolean) for i in range(52)] + \
                    [(f"player2_card_{i}", pl.Boolean) for i in range(52)] + \
                    [(f"player3_card_{i}", pl.Boolean) for i in range(52)] + \
                    [(f"player2_action_combo_type_{i}", pl.Boolean) for i in range(20)] + \
                    [(f"player2_action_max_card", pl.Int8)] + \
                    [(f"player3_action_combo_type_{i}", pl.Boolean) for i in range(20)] + \
                    [(f"player3_action_max_card", pl.Int8)] + \
                    [(f"actions_card_player1_{i}", pl.Boolean) for i in range(52)] + \
                    [(f"actions_card_player2_{i}", pl.Boolean) for i in range(52)] + \
                    [(f"actions_card_player3_{i}", pl.Boolean) for i in range(52)] + \
                    [(f"turn_player{i}", pl.Boolean) for i in range(1, n_player + 1)] + \
                    [(f"action_combo_type_{i}", pl.Boolean) for i in range(20)] + \
                    [(f"action_max_card", pl.Int8)] + \
                    [(f"player{i}_play_first", pl.Boolean) for i in range(1, n_player + 1)] + \
                    [(f"game_stage", pl.Int8)] + \
                    [(f"expected_return", pl.Int8)]
    df_table = pl.DataFrame(generate_list_state_action_return_encode(game_data), 
                            schema=schema_columns)
    df_table = undersample_df_table_for_mid_end_game_stage(df_table)
    return df_table