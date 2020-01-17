from math import floor
import random
import pandas

CARDS_BASIC = "basic"
CARDS_PLUS_2 = "plus-2"
CARDS_DIRECTION = "change-direction"
CARDS_SKIP = "skip-next-player"
CARDS_COLOR = "color"
CARDS_PLUS_4 = "plus-4"

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

COLORS = ['red', 'green', 'blue', 'yellow']

N_CARDS = sum(LENGTHS.values())
N_COLORS = 4
CARDS_PER_PLAYER = 7
CARDS_PER_COLOR = 2
NEXT_PLAYER = {
    CARDS_DIRECTION: -1,
    CARDS_SKIP: 2
}

BUYS = {
    CARDS_PLUS_2: 2,
    CARDS_PLUS_4: 4
}

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
    
    def playable(self, table, color=None):
        if self.is_joker():
            return True
        elif table.type == CARDS_BASIC:
            return table.color == self.color or table.number == self.number
        elif table.type in [CARDS_DIRECTION, CARDS_SKIP]:
            return table.color == self.color
        elif table.type in CARDS_JOKERS:
            return self.color == color
        elif table.type == CARDS_PLUS_2:
            return self.type == CARDS_PLUS_2 or self.color == table.color

class Player:
    
    def __init__(self, id, cards):
        self.id = id
        self.cards = cards
    
    def uno(self):
        return len(self.cards) == 0
    
    def buy(self, cards):
        for card in cards:
            self.cards.append(card)
    
    def playable(self, table, color):
        return [c for c in self.cards if c.playable(table, color)]
    
    def play(self, table, color=None):
        """
        If no card is playable, return None.
        If there's at least 1 non-joker playable card, sample from this set;
        otherwise, sample from the playable jokers.
        """
        
        playable = self.playable(table, color)
        if not playable:
            return None
        
        criteria = lambda c: c.is_joker()
        playable.sort(key=criteria)
        if not playable[0].is_joker():
            cards = [c for c in playable if not c.is_joker()]
        else:
            cards = playable
        card = random.choice(cards)
        self.cards.remove(card)
        return card
    
    def play_plus2(self):
        plus2 = [c for c in self.cards if c.type == CARDS_PLUS_2]
        if not plus2:
            return None
        else:
            p2 = random.choice(plus2)
            self.cards.remove(p2)
            return p2
    
    def pick_color(self):
        colors = [c.color for c in self.cards if c.color is not None]
        if not colors:
            colors = [i for i in range(N_COLORS)]
        return random.choice(colors)

class Game:
    
    def __init__(self, n_players=4, debug=False):
        cards = [Card(i) for i in range(N_CARDS)]
        random.shuffle(cards)
        
        players = []
        for player_id in range(n_players):
            player_cards = []
            for _ in range(CARDS_PER_PLAYER):
                player_cards.append(cards.pop())
            players.append(Player(player_id, player_cards))
        table = cards.pop()
        
        self.cards = cards
        self.players = players
        self.table = [table]
        self.player_id = 0
        self.buy = 0
        self.color = None
        self.n_players = n_players
        
        # debug
        self.debug = debug
        self.history = [{
            "player_id": -1,
            "card_id": table.id,
            "card_type": table.type,
            "card_color": table.color if table.color is not None else None,
            "card_number": table.number if table.number is not None else -1,
            "color": "" if self.color is None else self.color,
            "n_cards": self.n_cards
        }]
    
    @property
    def h(self):
        return pandas.DataFrame(self.history)
    
    @property
    def n_cards(self):
        return ','.join([str(len(p.cards)) for p in self.players])
    
    def table_top(self):
        return self.table[-1]
    
    def player(self):
        return self.players[self.player_id]
    
    def buy_cards(self):
        bought = []
        for _ in range(self.buy):
            bought.append(self.cards.pop())
            if not self.cards:
                old_table = self.table.copy()
                random.shuffle(old_table)
                self.cards = old_table
                new_table = self.cards.pop()
                self.table = [new_table]
        
        player = self.player()
        player.buy(bought)
        self.buy = 0
    
    def update_player(self, plus=1):
        self.player_id = (self.player_id + plus) % self.n_players
    
    def play_simple(self):
        player = self.player()
        card = player.play(self.table_top(), self.color)
        
        if card is None:
            self.buy = 1
            self.buy_cards()
            
            self.update_player()
        else:
            self.table.append(card)
            self.update_player(NEXT_PLAYER.get(card.type, 1))
            self.buy = BUYS.get(card.type, 0)
            self.color = player.pick_color() if card.is_joker() else None
        return card
    
    def play_plus2(self):
        player = self.player()
        
        if self.buy:
            card = player.play_plus2()
            if card is not None:
                self.table.append(card)
                self.buy += 2
            else:
                self.buy_cards()
            self.update_player()
        else:
            card = self.play_simple()
        return card
    
    def play_plus4(self):
        player = self.player()
        
        if self.buy:
            card = None
            self.buy_cards()
            self.update_player()
        else:
            card = self.play_simple()
        return card
    
    def uno(self):
        player = self.player()
        return player.uno()
    
    def round(self):
        """
        - se carta simples, OK
        - se +2
            - se buy
                - se tem outro +2
                    - jogue
                - else
                    - compra 2
            - se not buy
                - age igual a carta simples
        - se +4
            - se buy
                - compra 4
            - else
                - age igual a carta simples com color especificada
        - se cor
            - age igual a carta simples com color especificada
        """
        
        if self.uno():
            return
        
        t = self.table_top()
        player = self.player()
        
        if t.type == CARDS_PLUS_2:
            card = self.play_plus2()
        elif t.type == CARDS_PLUS_4:
            card = self.play_plus4()
        else:
            card = self.play_simple()
        
        # ---------- debug -------------------
        self.history.append({
            "player_id": player.id,
            "card_id": card.id if card is not None else -1,
            "card_type": card.type if card is not None else None,
            "card_color": card.color if card is not None else None,
            "card_number": -1 if card is None else \
                (card.number if card.number is not None else -1),
            "color": "" if self.color is None else self.color,
            "n_cards": self.n_cards
        })
        # ------------------------------------
        
        if self.debug: print(self.h)
        #return self.uno()
