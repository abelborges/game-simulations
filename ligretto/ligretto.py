from math import floor, ceil
from random import shuffle, expovariate as rexp
from functools import reduce
import sys

CARDS_TOTAL = 40
CARDS_PER_COLOR = 10
CARDS_IN_ROW = 3
CARDS_IN_PILE = 10
CARDS_PER_HAND_NEXT = 3
MOVE_NEXT = 'next'
MOVE_NEXT_AND_SHUFFLE = 'next_and_shuffle'
MOVE_PLAY_ROW_ONES = 'play_row_ones'
MOVE_PLAY_HAND = 'play_hand'
MOVE_PLAY_ROW = 'play_row'
DECK_ROW = 'row'
DECK_PILE = 'pile'
DECK_HAND = 'hand'

class Card:
    
    def __init__(self, id):
        self.id = id
        self.color = floor(self.id / CARDS_PER_COLOR)
        self.number = self.id % CARDS_PER_COLOR + 1
    
    def equals(self, card):
        return self.id == card.id
    
    def is_next(self, card):
        has_same_color = self.color == card.color
        is_next_number = self.number == card.number + 1
        return has_same_color and is_next_number
    
    def next(self):
        if self.number == 10:
            return None
        else:
            return Card(self.id + 1)

def deck_init(n_total=CARDS_TOTAL, n_row=CARDS_IN_ROW, n_pile=CARDS_IN_PILE):
    deck = [Card(i) for i in range(n_total)]
    shuffle(deck)
    i = n_row + n_pile
    row = deck[:n_row]
    pile = deck[n_row:i]
    hand = deck[i:]
    return row, pile, hand

def best_to_play(cards):
    if len(cards) < 1 or cards is None:
        return None
    reducer = lambda acc, card: card if card.number >= acc.number else acc
    return reduce(reducer, cards)

class Player:
    
    def __init__(self, id, rate_next, rate_shuffle, rate_realize, rate_replace):
        self.id = id
        self.deltat = {
            MOVE_PLAY_ROW_ONES: lambda: 0.0,
            MOVE_NEXT: lambda: rexp(rate_next),
            MOVE_NEXT_AND_SHUFFLE: lambda: rexp(rate_next) + rexp(rate_shuffle),
            MOVE_PLAY_ROW: lambda: rexp(rate_realize) + rexp(rate_replace),
            MOVE_PLAY_HAND: lambda: rexp(rate_realize)
        }
        self.history = []
        self.row, self.pile, self.hand = deck_init()
        self.hand_idx = -1
    
    @property
    def hand_top(self):
        return self.hand[self.hand_idx]
    
    def ligretto(self):
        return len(self.ten) == 0
    
    def track(self, move, card):
        self.history.append({
            'time': self.history[-1].time + self.deltat.get(move)(),
            'move': move,
            'card': card
        })
    
    def play_row_ones(self):
        row = self.row.copy()
        ones = []
        for idx, card in enumerate(self.row):
            if card.number == 1:
                ones.append(row.pop(idx))
                self.track(MOVE_PLAY_ROW_ONES, card)
        
        for one in ones:
            row.append(self.ten.pop())
        
        self.row = row
        return ones
    
    def hand_next(self):
        if self.hand_idx == len(self.hand) - 1:
            shuffle(self.hand)
            idx = CARDS_PER_HAND_NEXT - 1
            move = MOVE_NEXT_AND_SHUFFLE
        else:
            idx = self.hand_idx + CARDS_PER_HAND_NEXT
            idx = idx if idx < len(self.hand) else len(self.hand) - 1
            move = MOVE_NEXT
        self.hand_idx = idx
        self.track(move, self.hand_top)
        return self.hand_top
    
    def playable(self, table):
        row = [c for c in self.row if c.number == 1 or \
            len([t for t in table if c.is_next(t)]) > 0]
        
        hand_is_playable = False
        for card in table:
            if self.hand_top.is_next(card):
                hand_is_playable = True
                break
        
        return row, (self.hand_top if hand_is_playable else None)
    
    def play(self, table):
        row, hand = self.playable(table)
        
        if len(row) > 0:
            card = best_to_play(row)
            idx = [c.id for c in self.row].index(card.id)
            self.track(MOVE_PLAY_ROW, self.row.pop(idx))
            self.row.append(self.ten.pop())
            return DECK_ROW, card
        elif hand is not None:
            card = self.hand.pop(self.hand_idx)
            self.track(MOVE_PLAY_HAND, card)
            self.hand_next()
            return DECK_HAND, card
        else:
            return None, None

class Pile:
    
    def __init__(self, color):
        self.card = Card(color * CARDS_PER_COLOR)
    
    def __len__(self):
        return self.card.number
    
    @property
    def color(self):
        return self.card.color
    
    @property
    def number(self):
        return self.card.number
    
    @property
    def is_open(self):
        return self.card.number < CARDS_PER_COLOR
    
    def update(self):
        if self.is_open:
            self.card.id += 1

class Table:
    
    def __init__(self):
        self.piles = []
    
    def __len__(self):
        return len(self.piles)
    
    @property
    def cards(self):
        def reducer(acc, pile):
            if pile.is_open:
                acc.append(pile.card)
            return acc
        reduce(reducer, self.piles, [])
    
    def create_pile(self, color):
        self.piles.append(Pile(color))
    
    def add_card_to(self, pile_id):
        pile = self.piles[pile_id]
        pile.update()
        self.piles[pile_id] = pile

class Game:
    
    def __init__(self, players):
        self.players = players
        self.table = Table()
        self.history = []
    
    @property
    def ligretto(self):
        for player in self.players:
            if player.ligretto:
                return True
        return False

def game_play(players):
    game = Game(players)
    
    # start: play "1" cards on rows
    for player in players:
        ones = player.play_row_ones()
        if len(ones) > 0:
            for card in ones:
                game.table.create_pile(card.color)
    
    while not game.ligretto:
        for player in players:
            pile_id = player.play(game.table.cards)

if __name__ == '__main__':
    
    players = []
    players.append(Player('A', 0.5, 0.5, 0.5, 0.5))
    players.append(Player('B', 1.0, 1.0, 1.0, 1.0))
    players.append(Player('C', 1.5, 1.5, 1.5, 1.5))
    players.append(Player('D', 2.0, 2.0, 2.0, 2.0))
    
    for player in players:
	    print(player.id)

