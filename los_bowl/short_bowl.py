'''
Created on Aug 20, 2018

@author: carlos

this is a simple example of rule encapsulation and inheritance to implement the game with new rules

'''
from bowling import Rules


class ShortRules(Rules):
    frames = 5


if __name__ == '__main__':
    from bowling import BowlingGame
    GAME = BowlingGame(rules=ShortRules())
    HALFROLLS = [10] * 7  # 5 strikes and 2 extra rolls
    GAME.play_from_list(HALFROLLS)
