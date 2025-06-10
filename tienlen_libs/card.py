from typing import Sequence

class Card:
    """
    Static class that handles cards. We represent cards as integers from 0 to 51
    with order of [3s, 3c, 3d, 3h, 4s, 4c,...,As,2s,2c,...,2h]
    """

    # the basics
    STR_RANKS: str = '3456789TJQKA2'
    INT_RANKS: range = range(13)

    # conversion from string => int
    CHAR_RANK_TO_INT_RANK: dict[str, int] = dict(zip(list(STR_RANKS), INT_RANKS))
    CHAR_SUIT_TO_INT_SUIT: dict[str, int] = {
        's': 0,  # spades
        'c': 1,  # clubs
        'd': 2,  # diamonds
        'h': 3,  # hearts
    }
    INT_SUIT_TO_CHAR_SUIT: str = 'scdh'

    # for pretty printing
    PRETTY_SUITS: dict[int, str] = {
        0: chr(9824),   # spades
        1: chr(9827),   # clubs 
        2: chr(9830),   # diamonds
        3: chr(9829)    # hearts 
    }

    SUIT_COLORS: dict[int, str] = {
        1: "green",
        2: "blue",
        3: "red"
    }

    @staticmethod
    def new(string: str) -> int:
        """
        Converts Card string to integer representation of card:
        """
        rank_char = string[0]
        suit_char = string[1]
        rank_int = Card.CHAR_RANK_TO_INT_RANK[rank_char]
        suit_int = Card.CHAR_SUIT_TO_INT_SUIT[suit_char]
        return (4 * rank_int) + suit_int

    @staticmethod
    def int_to_str(card_int: int) -> str:
        rank_int = Card.get_rank_int(card_int)
        suit_int = Card.get_suit_int(card_int)
        return Card.STR_RANKS[rank_int] + Card.INT_SUIT_TO_CHAR_SUIT[suit_int]

    @staticmethod
    def get_rank_int(card_int: int) -> int:
        return card_int // 4

    @staticmethod
    def get_suit_int(card_int: int) -> int:
        return card_int % 4

    @staticmethod
    def int_to_pretty_str(card_int: int) -> str:
        """
        Prints a single card 
        """
        
        color = False
        try:
            from termcolor import colored
            # for mac, linux: http://pypi.python.org/pypi/termcolor
            # can use for windows: http://pypi.python.org/pypi/colorama
            color = True
        except ImportError: 
            pass

        # suit and rank
        suit_int = Card.get_suit_int(card_int)
        rank_int = Card.get_rank_int(card_int)

        # color
        s = Card.PRETTY_SUITS[suit_int]
        if color and suit_int in Card.SUIT_COLORS:
            s = colored(s, Card.SUIT_COLORS[suit_int])

        r = Card.STR_RANKS[rank_int]

        return "[{}{}]".format(r,s)

    @staticmethod
    def print_pretty_card(card_int: int) -> None:
        """
        Expects a single integer as input
        """
        print(Card.int_to_pretty_str(card_int))

    @staticmethod
    def ints_to_pretty_str(card_ints: Sequence[int]) -> str:
        """
        Expects a list of cards in integer form.
        """
        output = " "
        for i in range(len(card_ints)):
            c = card_ints[i]
            if i != len(card_ints) - 1:
                output += str(Card.int_to_pretty_str(c)) + ","
            else:
                output += str(Card.int_to_pretty_str(c)) + " "
    
        return output

    @staticmethod
    def print_pretty_cards(card_ints: Sequence[int], end: str = "\n") -> None:
        """
        Expects a list of cards in integer form.
        """
        print(Card.ints_to_pretty_str(card_ints), end=end)

if __name__ == "__main__":
    list_of_cards = [Card.new("Ad"), Card.new("Kh"), Card.new("2c"), Card.new("5d"), Card.new("Th"), Card.new("3s"), Card.new("4c"), Card.new("6h")]
    for card in list_of_cards:
        rank = Card.get_rank_int(card)
        suit = Card.get_suit_int(card)
        print(f"Card: {Card.int_to_pretty_str(card)}, Rank: {rank}, Suit: {suit}")