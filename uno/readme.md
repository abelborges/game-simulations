# Uno card game simulation

### Baseline strategy

1. If the player has at least 1 non-joker card (jokers include
"+4" and "choose a color"), choose one of them at random;
if the player has only jokers, choose one at random
2. When the player plays a joker, she selects a random card
from her hand from the set of cards with a defined color;
if only jokers are left, she picks a random color.
3. If the player is "attacked" by a +2 card, he'll always
play another +2 in case he has at least 1 card with this type;
if he has more than one +2, he chooses one at random.

This means (I guess) that
(A) jokers are chosen only
when no other card is available,
(B) it's always preferred to avoid buying
cards, if you can do so, and
(C) it's believed that asking for a color
that it's common in the player's hand
increases the likelihood of being able
to play in the next round.

### Questions of interest

Assuming all players use the baseline strategy:

> Does playing first increases the likelihood of winning?

Apparently, yes.

![](https://raw.githubusercontent.com/abelborges/game-simulations/master/uno/randomness_check.png)

The image above compare the proportion of winnings
for each player according to
the Uno game simulations (`uno.game_winners`)
versus sampling a random winner (`uno.simu_winners`).

The boxplots display the distribution of 1000 proportions of victory,
each one of them being estimated through 1000 independent
simulations, for both the game and pick-a-random-winner cases.
In this case, the csv files were generated with `python uno.py 1000 1000`.

The median of player 0 when she always starts playing
(bottom-left plot) is approximately 2 percentage points
greater than in the random-first-player case.
Curiously enough, those victories are taken from
the other players in such a way that `Prob(winner=k) > Prob(winner=k+1)`.
That can be explained by the fact that it's more likely that
the game starts and stays in the direction 0->1->2->3 most of the time
so that player 3 is the last to play in the round and thus it's more
likely that someone else wins before him.

