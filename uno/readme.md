# Uno card game simulations

Questões de interesse:

1. Existe vantagem em começar jogando?

Sim. Os arquivos `randomness_check*` comparam a proporção de vitórias
segundo as simulações do jogo (`game_winners` em `uno.py`)
versus o caso em que um vencedor aleatório
é escolhido (`simu_winners` em `uno.py`).

Os gráficos mostram a distribuição desta proporção em 100 réplicas de Monte
Carlo de uma simulação de 1000 jogos (ou amostras aleatórias de jogadores).
Neste caso, os dados do csv foram gerados com o comando `python uno.py 1000 100`.

O sufixo `rand` significa que o primeiro jogador foi escolhido aleatoriamente
e `0` significa que o jogador 0 começa. A vantagem é de cerca aproximadament
2 pontos percentuais na probabilidade de vitória.

