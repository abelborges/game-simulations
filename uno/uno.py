from math import floor
import random
import pandas
import sys
import multiprocessing as mp

CARDS_BASIC = "basic"
CARDS_PLUS_2 = "plus2"
CARDS_DIRECTION = "direction"
CARDS_SKIP = "skip"
CARDS_COLOR = "color"
CARDS_PLUS_4 = "plus4"

CARDS_SIMPLE = [CARDS_BASIC, CARDS_DIRECTION, CARDS_SKIP]
CARDS_JOKERS = [CARDS_COLOR, CARDS_PLUS_4]
CARDS_BUY = [CARDS_PLUS_2, CARDS_PLUS_4]

LENGTHS = {
    CARDS_BASIC: 76,
    CARDS_PLUS_2: 8,
    CARDS_DIRECTION: 8,
    CARDS_SKIP: 8,
    CARDS_COLOR: 4,
    CARDS_PLUS_4: 4,
}

COLORS = ["red", "green", "blue", "yellow"]

N_CARDS = sum(LENGTHS.values())
N_COLORS = 4
CARDS_PER_PLAYER = 7
CARDS_PER_COLOR = 2

def buys(card):
    return {CARDS_PLUS_2: 2, CARDS_PLUS_4: 4}.get(card.type, 0)

class Card:
    
    """
    4 colors (a,b,c,d)

    1a,1b,1c,1d,1a,1b,1c,1d,2a,2b,...,9a,9b,9c,9d:
    18 cards per color, with numbers from 1 to 9

    a,b,c,d:
    4 "ZERO" cards, 1 per color

    a,b,c,d,a,b,c,d:
    8 "+2" cards, 2 per color
    8 "invert the order" cards, 2 per color
    8 "skip next player" cards, 2 per color

    4 "COLOR" jokers
    4 "+4" jokers
    1 "deck exchange" card
    """
    
    def __init__(self, id):
        self.id = id
        self.type = self._type()
        self.color = self._color()
        self.number = self._number()
    
    def _type(self):
        n = 0
        for _, card_type in enumerate(LENGTHS):
            n += LENGTHS[card_type]
            if self.id < n:
                return card_type
    
    def _color(self):
        if self.is_joker():
            return None
        else:
            return COLORS[self.id % N_COLORS]
    
    def _number(self):
        if self.id < N_COLORS:
            return 0
        elif self.type == CARDS_BASIC:
            return floor(self.id / (N_COLORS * CARDS_PER_COLOR)) + 1
        else:
            return None
    
    def is_joker(self):
        return self.type in CARDS_JOKERS
    
    def is_playable(self, table, color=None):
        if self.is_joker():
            return True
        elif table.type == CARDS_BASIC:
            return table.color == self.color or table.number == self.number
        elif table.type in [CARDS_DIRECTION, CARDS_SKIP]:
            return table.color == self.color or table.type == self.type
        elif table.type in CARDS_JOKERS:
            return self.color == color
        elif table.type == CARDS_PLUS_2:
            return self.type == CARDS_PLUS_2 or self.color == table.color
    
    def __str__(self):
        return "_".join([str(a) for a in \
            (self.type if self.type != CARDS_BASIC else None, \
            self.color, self.number) if a is not None])

class Player:
    
    def __init__(self, id, cards):
        self.id = id
        self.cards = cards
    
    def uno(self): return not bool(self.cards)
    
    def buy(self, cards):
        for card in cards: self.cards.append(card)
    
    def playable(self, table, color):
        return [c for c in self.cards if c.is_playable(table, color)]
    
    def play(self, table, color=None):
        """
        If no card is playable, return None.
        If there's at least 1 non-joker playable card, sample from this set;
        otherwise, sample from the playable jokers.
        """
        
        playable = self.playable(table, color)
        if not playable: return None
        
        playable.sort(key=lambda c: c.is_joker())
        if not playable[0].is_joker():
            cards = [c for c in playable if not c.is_joker()]
        else:
            cards = playable
        card = random.choice(cards)
        self.cards.remove(card)
        return card
    
    def play_plus2(self):
        plus2 = [c for c in self.cards if c.type == CARDS_PLUS_2]
        if not plus2: return None
        else:
            p2 = random.choice(plus2)
            self.cards.remove(p2)
            return p2
    
    def pick_color(self):
        colors = [c.color for c in self.cards if c.color is not None]
        if not colors: colors = COLORS
        return random.choice(colors)
    
    def __str__(self):
        return ",".join([str(c) for c in self.cards])

class Game:
    
    def __init__(self, n_players=4, debug=True, first_player=None):
        cards = [Card(i) for i in range(N_CARDS)]
        random.shuffle(cards)
        
        players = []
        for player_id in range(n_players):
            player_cards = []
            for _ in range(CARDS_PER_PLAYER):
                player_cards.append(cards.pop())
            players.append(Player(player_id, player_cards))
        table = cards.pop()
        
        rand_first = random.choice([i for i in range(n_players)])
        
        self.cards = cards
        self.players = players
        self.player_id = first_player if first_player is not None else rand_first
        self.table = [table]
        
        self.buy = 0
        self.color = None
        self.direction = 1
        self.finished = False
        
        self.debug = debug
        self.history = [{
            "pid": -1,
            "cid": table.id,
            "cty": table.type,
            "ccol": table.color if table.color is not None else "",
            "cnum": table.number if table.number is not None else -1,
            "col": "" if self.color is None else self.color,
            "ns": self._n_cards()
        }]
    
    @property
    def n_players(self): return len(self.players)
    
    @property
    def table_top(self): return self.table[-1]
        
    @property
    def player(self): return self.players[self.player_id]
    
    def update_table(self):
        old_table = self.table.copy()
        top_card = old_table.pop()
        random.shuffle(old_table)
        self.cards = old_table
        self.table = [top_card]
    
    def buy_cards(self):
        bought = []
        for _ in range(self.buy):
            bought.append(self.cards.pop())
            if not self.cards: self.update_table()
        
        self.player.buy(bought)
        self.buy = 0
        return bought
    
    def update_player(self, plus=1):
        self.player_id = (self.player_id + self.direction*plus) % self.n_players

    def play(self, card):
        self.direction *= (-1 if card.type == CARDS_DIRECTION else 1)
        plus = 2 if card.type == CARDS_SKIP else 1
        self.table.append(card)
        self.buy = buys(card)
        self.color = self.player.pick_color() if card.is_joker() else None
        self.update_player(plus)
    
    def play_simple(self):
        card = self.player.play(self.table_top, self.color)
        
        if card is None:
            self.buy = 1
            bought_card = self.buy_cards().pop()
            if bought_card.is_playable(self.table_top, self.color):
                self.player.cards.pop()
                self.play(bought_card)
                card = bought_card
            else: self.update_player()
        else: self.play(card)
        return card
    
    def play_plus2(self):
        player = self.player
        
        if self.buy:
            card = player.play_plus2()
            if card is not None:
                self.table.append(card)
                self.buy += 2
            else: self.buy_cards()
            self.update_player()
        else: card = self.play_simple()
        return card
    
    def play_plus4(self):
        if self.buy:
            card = None
            self.buy_cards()
            self.update_player()
        else:
            card = self.play_simple()
        return card
    
    def round(self):
        if self.finished:
            return
        
        t = self.table_top
        player = self.player
        
        if t.type == CARDS_PLUS_2: card = self.play_plus2()
        elif t.type == CARDS_PLUS_4: card = self.play_plus4()
        else: card = self.play_simple()
        
        self.finished = player.uno()
        if self.finished: return player.id
        
        self.history.append({
            "pid": player.id,
            "cid": card.id if card is not None else -1,
            "cty": card.type if card is not None else None,
            "ccol": card.color if card is not None else None,
            "cnum": -1 if card is None else \
                (card.number if card.number is not None else -1),
            "col": "" if self.color is None else self.color,
            "ns": self._n_cards()
        })
        
        if self.debug:
            print(self._h())
            print("\n")
            for player in self.players:
                print(str(player.id) + ": " + str(player))
    
    def _h(self): return pandas.DataFrame(self.history)
    
    def _n_cards(self):
        return ",".join([str(len(p.cards)) for p in self.players])


def hist(x):
    t = []
    s = set(x)
    for e in s: t.append((e, x.count(e)/len(x)))
    return t

def simu_winners(n, k=4):
    players = [p for p in range(k)]
    ids = []
    for _ in range(n): ids.append(random.choice(players))
    return hist(ids)

def game_winners(n, first=None):
    ids = []
    for _ in range(N):
        g = Game(debug=False, first_player=first)
        while True:
            player_id = g.round()
            if player_id is not None: break
        ids.append(player_id)
    return hist(ids)

def randomness_check(N, first=None):
    game = game_winners(N, first)
    simu = simu_winners(N)
    n_players = len(game)
    h = dict()
    for i in range(n_players):
        h["game_p_" + str(i)] = game[i][1]
        h["simu_p_" + str(i)] = simu[i][1]
    return h

if __name__ == "__main__":
    N, K = int(sys.argv[1]), int(sys.argv[2])
    pool = mp.Pool(processes=4)

    future_rand = [pool.apply_async(randomness_check, (N, None)) for _ in range(K)]
    future_0 = [pool.apply_async(randomness_check, (N, 0)) for _ in range(K)]
    
    res_rand = [f.get() for f in future_rand]
    res_0 = [f.get() for f in future_0]

    pandas.DataFrame(res_rand).to_csv("randomness_check_rand.csv", index=False)
    pandas.DataFrame(res_0).to_csv("randomness_check_0.csv", index=False)
