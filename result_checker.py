#!/usr/bin/python
## coding=utf-8

import codecs
import sys
from card import Card
from hand import Hand, TYPE_NAME


class GameLogParser:
    def __init__(self, filename):
        self.filename = filename

    def read_line(self):
        self.cline = self.file.readline()

    def parse(self, *games):
        with codecs.open(self.filename, 'r', encoding='UTF-8') as self.file:
            self.read_line()

            # read until eof
            while self.cline:
                game_line = self.cline.strip()
                for game in games:
                    if game.check_title(self.cline):
                        print game_line
                        game.process(self)

                self.read_line()

        for game in games:
            game.print_coverage()

    def search_until(self, *search):
        while True:
            for pair in search:
                if pair[0] in self.cline:
                    return pair[1]
            self.read_line()

    def read_until(self, search):
        while search not in self.cline:
            self.read_line()

    def before(self, end_char):
        return self.cline[:self.cline.index(end_char)]

    def between(self, start_char, end_char):
        return self.cline[self.cline.index(start_char) + 1: self.cline.index(end_char)]


class GameLogic:
    game_name = "???"

    def __init__(self):
        # create two dimensional array (list of lists) to hold counters for different hand comparisons
        self.coverage = [[0 for y in range(11)] for x in range(11)]
        self.coverage_count = 0

    def update_coverage(self, hands):
        """
        Combine winning hand with every other hand and increment comparison counters
        """
        winner = max(hands)
        for hand in hands:
            if hand != winner:
                self.coverage[winner[0].type][hand[0].type] += 1
                self.coverage_count += 1

    def print_coverage(self):
        """
        Print debug information
        """
        print "%s coverage report (%d hands compared)" % (self.game_name, self.coverage_count)
        print ' ' * 14, ''.join(map(lambda tn: tn.center(14), TYPE_NAME))
        for type_name, counts in zip(TYPE_NAME, self.coverage):
            print type_name.rjust(14), ''.join(map(lambda count: str(count).center(14), counts))

    def check_title(self, line):
        """
        Return True if line starts game-log for accepted type of game
        """
        raise NotImplementedError("Please Implement this method")

    def process(self, parser):
        """
        Process the game-log and return True if log declares correct winner(s)
        """
        raise NotImplementedError("Please Implement this method")

    def print_error(self, hands, winners, winners_by_log):
        """
        Helper method to declare dispute in subclasses process()
        """
        print "  ERROR"
        for hand in hands:
            print "  {player}: [{hand}] {ipj}{chk}".format(
                player=str(hand[1]),
                hand=str(hand[0]),
                ipj='(ipj)' if hand[1] in winners_by_log else '',
                chk='(chk)' if hand[1] in winners else '',
            )


class SokoLogic(GameLogic):
    game_name = "Sökö"

    def __init__(self):
        GameLogic.__init__(self)

    def check_title(self, line):
        return u'GAME #' in line and u'Sökö' in line

    def process(self, parser):
        # read all hands in showdown
        hands = self.parse_showdown(parser)

        if not hands:
            return True

        self.update_coverage(hands)

        # collect all players whose hand is equal to the best hand
        winners = [hand[1] for hand in hands if hand[0] == max(hands)[0]]

        # who is the winner in log?
        winners_by_log = self.parse_summary(parser)

        if set(winners_by_log) == set(winners):
            return True
        else:
            self.print_error(hands, winners, winners_by_log)
            return False

    def parse_showdown(self, parser):
        # search for showdown title
        if not parser.search_until((u'*** SHOW DOWN ***', True), (u'*** SUMMARY ***', False)):
            parser.read_line()
            return []

        # showdown title line processed -> advance to next line
        parser.read_line()

        hands = []

        # read until summary title concludes the showdown
        while u'*** SUMMARY ***' not in parser.cline:
            # skip mucked hands
            if u'(mucked)' not in parser.cline:
                try:
                    player = parser.before(':')

                    cards = parser.between('[', ']')
                    hand = Hand.from_str(cards)

                    hands.append((hand, player))
                except ValueError:
                    pass

            # hand processed -> advance to next line
            parser.read_line()

        return hands

    def parse_summary(self, parser):
        winners = []
        parser.read_until(u'wins')

        while u'wins' in parser.cline:
            winners.append(parser.before(':'))
            # winner processed -> advance to next line
            parser.read_line()

        return winners


class HoldemLogic(GameLogic):
    game_name = "Holdem"

    def __init__(self):
        GameLogic.__init__(self)

    def check_title(self, line):
        return u'GAME #' in line and u'Holdem' in line

    def process(self, parser):
        # read table cards
        river = self.parse_river(parser)

        # read all hands in showdown
        hands = self.parse_showdown(parser, river)
        self.update_coverage(hands)

        # collect all players whose hand is equal to the best hand
        winners = [hand[1] for hand in hands if hand[0] == max(hands)[0]]

        # who is the winner in log?
        winners_by_log = self.parse_summary(parser)

        if set(winners_by_log) == set(winners):
            return True
        else:
            self.print_error(hands, winners, winners_by_log)
            return False

    def parse_river(self, parser):
        # search for river title
        parser.read_until(u'*** RIVER ***')
        cards = Card.from_str(parser.between('[', ']'))
        parser.read_line()
        return cards

    def parse_showdown(self, parser, river):
        # search for showdown title
        parser.read_until(u'*** SHOW DOWN ***')

        # showdown title line processed -> advance to next line
        parser.read_line()

        hands = []

        # read until summary title concludes the showdown
        while u'*** SUMMARY ***' not in parser.cline:
            # skip mucked hands
            if u'(mucked)' not in parser.cline:
                try:
                    player = parser.before(':')

                    cards = Card.from_str(parser.between('[', ']'))
                    hand = Hand.from_cards(river + cards)

                    hands.append((hand, player))
                except ValueError:
                    pass

            # hand processed -> advance to next line
            parser.read_line()

        return hands

    def parse_summary(self, parser):
        winners = []
        parser.read_until(u'wins')

        while u'wins' in parser.cline:
            winners.append(parser.before(':'))
            # winner processed -> advance to next line
            parser.read_line()

        return winners

if __name__ == "__main__":
    parser = GameLogParser(sys.argv[1])
    parser.parse(SokoLogic(), HoldemLogic())
