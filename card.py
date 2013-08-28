TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE = range(2, 15)

DIAMONDS, HEARTS, CLUBS, SPADES = range(4)

RANK_ABBR = '??23456789TJQKA'
SUIT_ABBR = 'dhcs'

RANK_NAME = ['?', '?', 'two', 'three', 'four', 'five', 'six', 'seven',
             'eight', 'nine', 'ten', 'jack', 'queen', 'king', 'ace']

SUIT_NAME = ['diamonds', 'hearts', 'clubs', 'spades']


class CardFormatException(Exception):
    """Invalid string representation; cannot convert to Card"""
    pass


class Card(object):
    """A playing card; e.g. ace of hearts, queen of spades, etc."""

    @classmethod
    def from_str(cls, s):
        return [Card(part) for part in s.split()]

    def __init__(self, s):
        s = s.strip().lower()

        if len(s) < 2:
            raise CardFormatException("need string with two characters")

        if '2' in s:
            self.rank = 2
        elif '3' in s:
            self.rank = 3
        elif '4' in s:
            self.rank = 4
        elif '5' in s:
            self.rank = 5
        elif '6' in s:
            self.rank = 6
        elif '7' in s:
            self.rank = 7
        elif '8' in s:
            self.rank = 8
        elif '9' in s:
            self.rank = 9
        elif '10' in s:
            self.rank = TEN
        elif 't' in s:
            self.rank = TEN
        elif 'j' in s:
            self.rank = JACK
        elif 'q' in s:
            self.rank = QUEEN
        elif 'k' in s:
            self.rank = KING
        elif 'a' in s:
            self.rank = ACE
        elif '1' in s:
            self.rank = ACE
        else:
            raise CardFormatException("unknown card rank '%s'" % s)

        if 's' in s:
            self.suit = SPADES
        elif 'c' in s:
            self.suit = CLUBS
        elif 'd' in s:
            self.suit = DIAMONDS
        elif 'h' in s:
            self.suit = HEARTS
        else:
            raise CardFormatException("unknown card suit '%s'" % s)

    def __cmp__(self, other):
        """Cards are compared by their rank alone"""
        return cmp(self.rank, other.rank)

    def __str__(self):
        return SUIT_ABBR[self.suit] + RANK_ABBR[self.rank]

    def describe(self):
        """return description of card. If long_fmt is True then this returns
           something like 'ace of clubs' (cf. 'As')."""
        return '%s of %s' % (RANK_NAME[self.rank], SUIT_NAME[self.suit])
