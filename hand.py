from itertools import combinations
from card import *

HIGHCARD, PAIR, FOUR_STRAIGHT, FOUR_FLUSH, TWOPAIR, SET, STRAIGHT, FLUSH, FULLHOUSE, QUADS, STRAIGHTFLUSH = range(11)

TYPE_NAME = ['HIGHCARD', 'PAIR', 'FOUR_STRAIGHT', 'FOUR_FLUSH', 'TWOPAIR', 'SET', 'STRAIGHT', 'FLUSH', 'FULLHOUSE', 'QUADS', 'STRAIGHTFLUSH']


class HandFormatException(Exception):
    pass


class Hand(object):
    """A set of cards with support for determining which poker hand
       the cards form.  Also supports comparing two hands for determining
       who 'wins' in a showdown. Note that the analysis performed searches
       for the *best* possible poker hand.  Poker games that score 'low'
       hands over 'high' hands are not currently supported."""

    @classmethod
    def from_cards(cls, cards):
        return max(Hand(combination) for combination in combinations(cards, 5))

    @classmethod
    def from_str(cls, s):
        cards = Card.from_str(s)
        return Hand.from_cards(cards)

    def __init__(self, cards):
        if len(cards) < 5:
            raise HandFormatException('>= 5 cards required')

        self.cards = sorted(cards, reverse=True)
        self._analyze()

    def __str__(self):
        return ' '.join([str(card) for card in self.cards])

    def __cmp__(self, other):
        """compare hands following standard poker hand rankings, 
           including kickers."""
        n = cmp(self.type, other.type)
        if n != 0:
            return n

        if self.ranks > other.ranks:
            return 1
        if self.ranks < other.ranks:
            return -1
        return 0

    # determine the best hand possible given the current set of cards
    def _analyze(self):
        if self._find_straightflush():
            self.type = STRAIGHTFLUSH
            if self.ranks[0].rank == ACE:
                self.desc = 'royal flush'
            else:
                self.desc = '%s-high straight flush' % RANK_NAME[self.ranks[0].rank]
        elif self._find_same(4):
            self.type = QUADS
            self.desc = 'four of a kind (%s)' % self._pluralize_rank(RANK_NAME[self.ranks[0].rank])
        elif self._find_fullhouse():
            self.type = FULLHOUSE
            self.desc = 'full house (%s over %s)' % \
                        (self._pluralize_rank(RANK_NAME[max(self.ranks[0].rank, self.ranks[3].rank)]),
                         self._pluralize_rank(RANK_NAME[min(self.ranks[0].rank, self.ranks[3].rank)]))
        elif self._find_flush(5):
            self.type = FLUSH
            self.desc = '%s-high flush' % RANK_NAME[self.ranks[0].rank]
        elif self._find_straight(5):
            self.type = STRAIGHT
            self.desc = '%s-high straight' % RANK_NAME[self.ranks[0].rank]
        elif self._find_same(3):
            self.type = SET
            self.desc = 'three of a kind (%s)' % self._pluralize_rank(RANK_NAME[self.ranks[0].rank])
        elif self._find_twopair():
            self.type = TWOPAIR
            self.desc = 'two pair (%s and %s)' % (self._pluralize_rank(RANK_NAME[self.ranks[0].rank]),
                                                  self._pluralize_rank(RANK_NAME[self.ranks[2].rank]))
        elif self._find_flush(4):
            self.type = FOUR_FLUSH
            self.desc = '%s-high four flush' % RANK_NAME[self.ranks[0].rank]
        elif self._find_straight(4):
            self.type = FOUR_STRAIGHT
            self.desc = '%s-high four straight' % RANK_NAME[self.ranks[0].rank]
        elif self._find_same(2):
            self.type = PAIR
            self.desc = 'pair of %s' % self._pluralize_rank(RANK_NAME[self.ranks[0].rank])
        else:
            self.type = HIGHCARD
            self.ranks = self.cards
            self.desc = '%s-high' % RANK_NAME[self.ranks[0].rank]

        self.ranks += self._find_kickers(self.ranks)

    def _find_straightflush(self):
        return self._find_straight(5) and self._find_flush(5)

    def _find_same(self, length, ignore=()):
        for rank in range(ACE, 0, -1):
            ranks = self._find_ranks(rank, ignore)
            if len(ranks) == length:
                self.ranks = ranks
                return True

        return False

    def _find_fullhouse(self):
        if not self._find_same(3):
            return False

        trip = self.ranks

        if not self._find_same(2, trip):
            return False

        pair = self.ranks

        self.ranks = trip + pair
        return True

    def _find_flush(self, length):
        for suit in range(4):
            ranks = self._find_suits(suit)
            if len(ranks) == length:
                self.ranks = ranks
                return True

        return False

    def _find_straight(self, length):
        ranks = []
        for rank in range(ACE, 0, -1):
            card = self._find_rank(rank, ranks)
            if card:
                ranks.append(card)
                if len(ranks) == length:
                    self.ranks = ranks
                    return True
            elif ranks:
                ranks = []

        return False

    def _find_twopair(self):
        if not self._find_same(2):
            return False

        pair_h = self.ranks

        if not self._find_same(2, pair_h):
            return False

        pair_l = self.ranks

        self.ranks = pair_h + pair_l
        return True

    # LOW level helper functions
    def _find_kickers(self, ignore=()):
        return [card for card in self.cards if id(card) not in map(id, ignore)]

    def _find_suits(self, suit):
        return [card for card in self.cards if card.suit == suit]

    def _find_ranks(self, rank, ignore=()):
        return [card for card in self.cards if (card.rank == rank or (card.rank == ACE and rank == 1)) and id(card) not in map(id, ignore)]

    def _find_rank(self, rank, ignore=()):
        return next((card for card in self.cards if (card.rank == rank or (card.rank == ACE and rank == 1)) and id(card) not in map(id, ignore)), False)

    def _find_highest_rank(self, ignore=()):
        return max([card for card in self.cards if id(card) not in map(id, ignore)])

    def _pluralize_rank(self, r_str):
        if r_str == 'six':
            return r_str + 'es'
        return r_str + 's'
