from py_mini_racer import py_mini_racer
from agent_bot.py_rule_based import rule_based_json_code


class Bot_TL_AI(object):
    def __init__(self):
        self.tuple_rule_based_bot_input = self.__create_tuple_rule_based_bot_input()
        self.map_rule_based_bot_input_to_card = self.__create_mapping_rule_based_bot_input_to_card()
        self.ctx = self.compile_rule_based_json_code_with_V8_engine()
        self.test_rule_based_bot()
        
    def __create_tuple_rule_based_bot_input(self):
        tuple_rule_based_bot_input = tuple(f"anh/{i:02}{j}" for i in list(range(3, 15)) + [16] 
                                                                for j in ["a", "b", "c", "d"])
        assert len(tuple_rule_based_bot_input) == 52
        assert all(len(x) == 7 for x in tuple_rule_based_bot_input)
        return tuple_rule_based_bot_input
    
    def __create_mapping_rule_based_bot_input_to_card(self):
        tuple_rule_based_bot_input = self.__create_tuple_rule_based_bot_input()
        map_rule_based_bot_input_to_card = {bot_input: idx 
                                    for idx, bot_input in enumerate(tuple_rule_based_bot_input)}
        return map_rule_based_bot_input_to_card
    
    def compile_rule_based_json_code_with_V8_engine(self):
        ctx = py_mini_racer.MiniRacer()
        ctx.eval(rule_based_json_code)
        return ctx

    def test_rule_based_bot(self):
        result = self.ctx.call("AI", ["anh/14a"], 
                                ["anh/14b", "anh/14c", "anh/16a", "anh/16b"])
        assert set(result) == set(["anh/14c"])
        # print("Test 1 PASSED")

        result = self.ctx.call("AI", [], 
                               ["anh/03a", "anh/04a", "anh/05a", "anh/06a", "anh/07a"])
        assert set(result) == set(["anh/03a", "anh/04a", "anh/05a", "anh/06a", "anh/07a"])
        # print("Test 2 PASSED")

        result = self.ctx.call("AI", ["anh/10a", "anh/10b"], 
                               ["anh/11c", "anh/11d", "anh/12a", "anh/12b", "anh/12c", "anh/13c", 
                                "anh/14a", "anh/14b", "anh/15a", "anh/15b", "anh/16a", "anh/16b"])
        assert set(result) == set(["anh/12a", "anh/12c"])
        # print("Test 3 PASSED")

        result = self.ctx.call("AI", ["anh/03a", "anh/04b", "anh/05c"], 
                               ["anh/07a", "anh/08b", "anh/09c", "anh/10a", "anh/11b"])
        assert set(result) == set(["anh/07a", "anh/08b", "anh/09c"])
        # print("Test 4 PASSED")

        result = self.ctx.call("AI", ["anh/07a", "anh/07b", "anh/07c"], 
                               ["anh/09a", "anh/09b", "anh/09c", "anh/11d"])
        assert set(result) == set(["anh/09a", "anh/09b", "anh/09c"])
        # print("Test 5 PASSED")

        result = self.ctx.call("AI", ["anh/04a", "anh/05b", "anh/06c", "anh/07d", "anh/08a"], 
                               ["anh/09b", "anh/10c", "anh/11d", "anh/12a", "anh/13b"])
        assert set(result) == set(["anh/09b", "anh/10c", "anh/11d", "anh/12a", "anh/13b"])
        # print("Test 6 PASSED")

        result = self.ctx.call("AI", ["anh/03a"], 
                               ["anh/03b", "anh/04a", "anh/05c", "anh/06c", "anh/07b", "anh/08d", "anh/09a", 
                                "anh/10d", "anh/11b", "anh/12c", "anh/13a", "anh/14d", "anh/16b"])
        assert set(result) == set(["anh/16b"])
        # print("Test 7 PASSED")
    
    def convert_list_card_to_rule_based_bot_list_input(self, list_card):
        return [self.tuple_rule_based_bot_input[card] for card in list_card]
    
    def convert_rule_based_bot_list_input_to_list_card(self, bot_list_input):
        return [self.map_rule_based_bot_input_to_card[bot_input] for bot_input in bot_list_input]

    def run_rule_based_bot(self, opponent_move, my_card):
        assert list(opponent_move) == sorted(opponent_move)
        assert list(my_card) == sorted(my_card)
        opponent_move_bot_input = self.convert_list_card_to_rule_based_bot_list_input(opponent_move)
        my_card_bot_input = self.convert_list_card_to_rule_based_bot_list_input(my_card)
        our_move_bot_format = self.ctx.call("AI", opponent_move_bot_input, my_card_bot_input)
        our_move = self.convert_rule_based_bot_list_input_to_list_card(our_move_bot_format)
        our_move.sort()
        return tuple(our_move)
