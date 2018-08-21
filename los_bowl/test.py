'''
Created on Aug 20, 2018

@author: carlos
'''
from itertools import count
import logging
import unittest

from bowling import BowlingGame
from short_bowl import ShortRules


class TestGameListInput(unittest.TestCase):
    """
    simple unnitest Test Case to test Bowling Game code
    """
    _log_id = count()

    def setUp(self):
        unittest.TestCase.setUp(self)
        logging.disable(logging.DEBUG)
        self.log_name = 'Bowling_game_log_%i' % self._log_id.next()  # make sure every test get it's own log for clean access...

    def test_perfect_game(self):
        """
        test perfect game score
        12 rolls of 10 pins
        """
        rolls = [10] * 12
        game = BowlingGame(log_name=self.log_name)
        score = game.play_from_list(rolls)
        self.assertTrue(score == 300, 'score is %i' % score)

    def test_nine_one_split_game(self):
        """
        this test simulates a game full of 9,1 splits with 10 pin score on the last frame (bonus)
        """
        rolls = []
        for _ in xrange(10):
            rolls.extend([9, 1])

        # last frame is a strike
        rolls.append(10)

        game = BowlingGame(log_name=self.log_name)
        score = game.play_from_list(rolls)
        self.assertTrue(score == 191, 'score is %i' % score)

    def test_mixed_score(self):
        """
        test mix scores here's just a random list i ran through an online bowling score calculator
        assuming that the calculator was correct our game logic should be too :D 
        """
        rolls = [0, 0,
                 1, 2,
                 5, 4,
                 3, 1,
                 10,
                 9, 1,
                 0, 4,
                 6, 1,
                 4, 6,
                 5, 1]

        game = BowlingGame(log_name=self.log_name)
        score = game.play_from_list(rolls)
        self.assertTrue(score == 78, 'score = %s' % score)

    def test_excemption_roll_value(self):
        """
        let's do some basic checking for input like that we don't let people score more frames that pins per frame
        """
        rolls = [20] * 12
        game = BowlingGame(log_name=self.log_name)

        with self.assertRaises(ValueError):
            game.play_from_list(rolls)

    def test_excemption_not_enough_rolls(self):
        """
        let's make sure that the catch if the user didn't input enough rolls
        """
        rolls = [3, 2, 1]
        game = BowlingGame(log_name=self.log_name)
        with self.assertRaises(ValueError):
            game.play_from_list(rolls)

    def test_rule_change(self):
        """
        test new rule change implementation (shortgame)
        """
        game = BowlingGame(rules=ShortRules(), log_name=self.log_name)
        short_list = [10] * 7  # 5 strikes and 2 extra rolls
        score = game.play_from_list(short_list)
        self.assertTrue(score == 150)


if __name__ == '__main__':
    unittest.main()
