import random

from . import cards

colors = 'kwrgb'

class Player(object):
    def __init__(self, game):
        self.game = game
        self.chips = {c:0 for c in colors+'x'}
        self.bonus = {c:0 for c in colors}
        self.cards = []
        self.reserve = []
        self.points = 0

    def can_draw_three(self, **kwargs):
        if self.game.players[self.game.current_player] is not self:
            return False
        if sum(kwargs.values()) > 3:
            return False
        for c in colors:
            n = kwargs.get(c, 0)
            if n < 0 or n > 1 or n > self.game.chips[c]:
                return False
        return True

    def draw_three(self, **kwargs):
        assert self.can_draw_three(**kwargs)
        for c in colors:
            n = kwargs.get(c, 0)
            self.chips[c] += n
            self.game.chips[c] -= n
        self.game.end_turn()

    def can_draw_two(self, color):
        if self.game.players[self.game.current_player] is not self:
            return False
        if self.game.chips[color] < 4:
            return False
        return True

    def draw_two(self, color):
        assert self.can_draw_two(color)
        self.chips[color] += 2
        self.game.chips[color] -= 2
        self.game.end_turn()

    def can_reserve_card(self, card):
        if len(self.reserve) >= 3:
            return False
        if not self.game.is_in_tableau(card):
            return False
        return True

    def reserve_card(self, card):
        assert self.can_reserve_card(card)
        self.reserve.append(card)
        self.game.remove_card(card)
        self.game.end_turn()

    def can_play(self, card):
        if not self.game.is_in_tableau(card) and card not in self.reserve:
            return False
        for c in colors:
            cost = getattr(card, c)
            if self.chips[c] + self.bonus[c] < cost:
                return False
        return True

    def play(self, card):
        assert self.can_play(card)
        self.cards.append(card)
        if card in self.reserve:
            self.reserve.remove(card)
        else:
            self.game.remove_card(card)
        for c in colors:
            cost = getattr(card, c)
            self.chips[c] -= min(cost - self.bonus[c], 0)
        self.bonus[card.bonus] += 1
        self.points += card.points
        if self.points >= 15:
            self.game.end_game = True
        self.game.end_turn()

    def valid_actions(self):
        actions = []
        for level in [3, 2, 1]:
            for card in self.game.tableau[level]:
                if card is not None:
                    if self.can_play(card):
                        actions.append((self.play, dict(card=card)))
        for card in self.reserve:
            if self.can_play(card):
                actions.append((self.play, dict(card=card)))
        for c1 in colors:
            if self.game.chips[c1] == 0:
                continue
            for c2 in colors:
                if c1 == c2 or self.game.chips[c2] == 0:
                    continue
                for c3 in colors:
                    if c1 == c3 or c2 == c3 or self.game.chips[c3] == 0:
                        continue
                    actions.append((self.draw_three, {c1:1, c2:1, c3:1}))
        for c in colors:
            if self.game.chips[c] >= 4:
                actions.append((self.draw_two, dict(color=c)))
        if len(self.reserve) < 3:
            for level in [3, 2, 1]:
                for card in self.game.tableau[level]:
                    if card is not None:
                        actions.append((self.reserve_card, dict(card=card)))
        return actions


class Splendor(object):
    def __init__(self, n_players, seed):
        self.players = [Player(self) for i in range(n_players)]
        rng = random.Random()
        rng.seed(seed)
        all_cards = cards.generate()
        rng.shuffle(all_cards)
        self.levels = {}
        self.tableau = {}
        for level in [1, 2, 3]:
            self.levels[level] = [x for x in all_cards if x.level==level]
            self.tableau[level] = [self.draw(level) for j in range(4)]

        self.first_player = rng.randrange(n_players)
        self.current_player = self.first_player
        self.end_game = False
        self.winners = None
        self.pass_count = 0

        n_chips = 7 if n_players > 2 else 4
        self.chips = dict(k=n_chips, w=n_chips, r=n_chips,
                          g=n_chips, b=n_chips, x=5)

    def draw(self, level):
        if len(self.levels[level]) == 0:
            return None
        return self.levels[level].pop()

    def is_in_tableau(self, card):
        for level in [1, 2, 3]:
            if card in self.tableau[level]:
                return True
        return False

    def remove_card(self, card):
        for level in [1, 2, 3]:
            if card in self.tableau[level]:
                self.tableau[level].remove(card)
                self.tableau[level].append(self.draw(level))
                return
        raise Exception('removed unknown card')

    def pass_turn(self):
        self.pass_count += 1
        if self.pass_count == len(self.players):
            self.winners = []
            self.current_player = None
        else:
            self.end_turn(reset_pass=False)

    def end_turn(self, reset_pass=True):
        if reset_pass:
            self.pass_count = 0
        self.current_player = ((self.current_player + 1) % len(self.players))
        if self.end_game and self.current_player == self.first_player:
            max_points = max([p.points for p in self.players])
            self.winners = [p for p in self.players if p.points == max_points]
            self.current_player = None










        


