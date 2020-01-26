import uno
import pandas
import sys

def plus4s(cards):
    return set([c for c in cards if c.type == uno.CARDS_PLUS_4])

def plus4_impact(n_players=4):
    g = uno.Game(debug=False)
    status = [plus4s(p.cards) for p in g.players]
    while True:
        winner = g.round()
        if winner is not None: break
        status = [s.union(plus4s(p.cards)) for s, p in zip(status, g.players)]
    return [len(s) for s in status], winner

def sim_plus4_impact(K, n_players=4, progress=True):
    df = []
    for i in range(K):
        if progress and not i % 100: print(i/K)

        status, winner = plus4_impact(n_players)
        d = dict()
        d["replicate_id"] = i
        d["winner"] = winner
        for j in range(n_players): d["plus4s_" + str(j)] = status[j]
        df.append(d)
    return pandas.DataFrame(df)

if __name__ == "__main__":
    K = int(sys.argv[1])
    df = sim_plus4_impact(K, progress=True)
    df.to_csv("plus4_impact.csv", index=False)
