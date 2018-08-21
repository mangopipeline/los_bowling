'''
Created on Aug 20, 2018

@author: carlos anguiano

doc strings follow sphinx auto doc convention
styling is pep8
'''

import logging


class Rules(object):
    """
    class containing basic rules of the game we can make varition of the rules by inherting and reimplenting property or method of the class
    """
    frames = 10
    pins_per_frame = 10
    rolls_per_frame = 2
    points_per_pin = 1
    strike_min_rolls = 1
    strike_bonus_rolls = 2
    spare_bonus_rolls = 1

    def is_frame_strike(self, frame):
        """
        test that defines weather the rolls of a frame can be considered a strike or not

        :param Frame frame:
        """
        if not frame.rolls:
            return False
        rolls = [roll for roll in frame.rolls if not roll.extra]
        if len(rolls) <= self.strike_min_rolls and frame.get_dead_pins(ex_extra=True) == self.pins_per_frame:
            return True

        return False

    def is_frame_spare(self, frame):
        """
        test that defines weather the rolls of a frame con be considred a spear or not

        :param frame:
        """
        if not frame.rolls:
            return False

        rolls = [roll for roll in frame.rolls if not roll.extra]

        if rolls <= self.strike_min_rolls:
            return False

        if frame.get_dead_pins(ex_extra=True) != self.pins_per_frame:
            return False

        return True


class Frame(object):
    """
    this class is a holder for frames played
    """

    def __init__(self, game):
        """

        :param  Game game: pass the insatance of the game the frame belongs too
        """
        self.game = game
        self.id = len(self.game.frames)
        self.game.frames.append(self)
        self.log = self.game.log
        self.rules = self.game.rules
        self.rolls = []
        self._play_frame_rolls()

    def _play_frame_rolls(self):
        frame_nmb = self.id + 1
        self.log.debug('Playing frame %s now!', frame_nmb)
        roll = None  # we will use this later :D
        for index in xrange(self.rules.rolls_per_frame):
            self.log.debug('\troll %s of frame %s', (index + 1), frame_nmb)
            roll = Roll(self)
            roll_score = self.game.get_score_from_roll_list(roll.id)
            roll.set_score(roll_score)

            if roll.strike or roll.spare:
                break

        # let's check if this is the last frame so we can add extra rolls :D
        if (self.id + 1) != self.rules.frames:
            return

        if not roll.strike and not roll.spare:
            return

        bonus_rolls = self.rules.strike_bonus_rolls

        if roll.spare:
            bonus_rolls = self.rules.spare_bonus_rolls

        dead_pins = 0
        for index in xrange(bonus_rolls):
            self.log.debug('\t\tBonus Roll %s on the way!!!' % index)
            broll = Roll(self, extra=True)
            score = self.game.get_score_from_roll_list(broll.id)
            broll.set_score(score, dead_pins=dead_pins)

            if score == self.rules.pins_per_frame:
                continue
            # in case of spare with more bonus frames left
            dead_pins = score

    def is_strike(self):
        """
        test did the user bowl are strike on this frame
        """
        return self.rules.is_frame_strike(self)

    def is_spare(self):
        """
        test did the user bowl a spare on this frame
        """
        return self.rules.is_frame_spare(self)

    def get_dead_pins(self, ex_extra=False):
        """
        list the number of pins that have been knocked down so far
        """
        if not self.rolls:
            return 0
        if ex_extra:
            return sum([roll.get_score() for roll in self.rolls if not roll.extra and roll.get_score()])
        return sum([roll.get_score() for roll in self.rolls if roll.get_score()])

    def get_score(self):
        """
        tally up score for given frame
        """
        frame_score = self.get_dead_pins()
        # if it's the last frame things are eazy jut get a raw score...
        if (self.id + 1) == self.rules.frames:
            return frame_score

        lframe_id = self.rolls[-1].id
        bonus_rolls = 0

        if self.is_strike():
            bonus_rolls = self.rules.strike_bonus_rolls
        elif self.is_spare():
            bonus_rolls = self.rules.spare_bonus_rolls
        else:
            return frame_score

        # assume if it can be tallied up for now (might be incomplete)

        for index in xrange(bonus_rolls):
            frame_score += self.game.rolls[lframe_id + index + 1].get_score()

        return frame_score


class Roll(object):
    """
    this class is a holder for rolls played in a game plus their relationship to frames
    """

    def __init__(self, frame, extra=False):
        """

        :param Frame frame: instance of the frame the roll will belong too
        :param extra: if this is an "extra" roll on the last frame  set this to true
        """
        self.frame = frame
        self.game = self.frame.game
        self.rules = self.game.rules
        self.id = len(self.game.rolls)
        self.game.rolls.append(self)
        self.fid = len(self.frame.rolls)
        self.frame.rolls.append(self)
        self._score = None
        self._strike = False
        self._spare = False
        self._extra = extra

    @property
    def strike(self):
        """
        use this property to retrieve if the roll is a strike or not
        """
        return self._strike

    @property
    def spare(self):
        """
        use this property to retrieve if the roll is a spare or not
        """
        return self._spare

    @property
    def extra(self):
        return self._extra

    def get_score(self):
        """
        get the score for the roll
        """
        return self._score

    def set_score(self, value, dead_pins=None):
        """
        get the score for the roll

        :param value:
        """

        # TODO: this was a property like the others but my logic got a little weird on the extra frame mechanism some i did this instead
        # i would revisit this for consistency at some point maybe use a miss of property for retrieval but only allow for the score to be set via a method

        if dead_pins is None:
            dead_pins = self.frame.get_dead_pins()

        if not isinstance(value, int):
            raise ValueError('score most be integer')
        if value < 0 or value > self.rules.pins_per_frame:
            raise ValueError('roll score needs to be between 0 and %s' % self.rules.pins_per_frame)

        live_pins = self.rules.pins_per_frame - dead_pins

        if value > live_pins:
            raise ValueError('you cant score more pins than what is left for the frame (%s pins left in frame)' % live_pins)

        self._score = value

        # only worry about marking strikes and spares in none extra frames
        if self.extra:
            return

        if self.frame.is_strike():
            self._strike = True
        elif self.frame.is_spare():
            self._spare = True


class BowlingGame(object):
    """
    main class holding our game logic
    """

    def __init__(self, rules=None, log_name=None):
        """

        :param Rules rules: instance of class rules you like to follow (you can implement your own)
        :param str log_name: name space for the logger this is a lazy way to get better loging in the unnit test
        """
        self._roll_list = None
        self.rules = rules or Rules()
        self.frames = []
        self.rolls = []
        self.log = self.setup_logging(log_name=log_name)

    @staticmethod
    def setup_logging(log_name=None):
        """
        method for setting up a simple logging object
        """
        log_name = log_name or 'Bowling Game'
        log = logging.getLogger(log_name)
        log.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        log.addHandler(handler)
        return log

    @staticmethod
    def _valdiate_roll_list(roll_list):
        """
        simple method for adding validations and error catching for invalid input list

        :param [int] _roll_list: list of values you like to test
        """
        bad_vals = [val for val in roll_list if not isinstance(val, int)]
        if bad_vals:
            raise ValueError('sorry bob your list needs to be made up of integer values :(')

        return roll_list

    def _output_game_score(self):
        """
        this method does all our end of game scoring and stats :D
        """
        self.log.info('========final-game=======')
        final = 0
        for frame in self.frames:
            fid = frame.id + 1
            score = frame.get_score()
            fstat = 'Open'
            final += score
            frolls = ','.join([str(roll.get_score()) for roll in frame.rolls])
            if frame.is_strike():
                fstat = 'Strike'
            elif frame.is_spare():
                fstat = 'Spare'

            self.log.info('Frame %s score is %s (%s) [%s]', fid, score, fstat, frolls)

        self.log.info('Final Game Score is %i', final)
        return final

    def get_score_from_roll_list(self, roll_id):
        """
        throws an exception if the index being request is outside the scope of the list

        :param _roll_list: list with roll/pin values
        :roll_id index: index which you would like retrive
        """
        if roll_id >= len(self._roll_list):
            raise ValueError('there is not enough rolls in your list')

        return self._roll_list[roll_id]

    def play_from_list(self, roll_list):
        """
        this method uses as an input a list of rolls, it will then simulate the game and return the score

        :param list _roll_list: list containing an integer describing how many pins were knocked down per roll
        """
        self._roll_list = self._valdiate_roll_list(roll_list)

        for _ in xrange(self.rules.frames):
            Frame(self)

        return self._output_game_score()


if __name__ == '__main__':
    # easy test to get started with perfect game... unit test will have more in depth testing...
    GAME = BowlingGame()
    GAME.play_from_list([10] * 12)
