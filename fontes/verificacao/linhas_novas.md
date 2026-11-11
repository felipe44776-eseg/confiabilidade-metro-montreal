# Linhas novas numa viagem (spec 016)

Gerado por `app/relatorios/linhas_novas.relatorio.ts` com o `parametros.json` real (código sha256-scripts:a0ff551bd3d56c35). Cenário padrão (dia útil, condições de referência do modelo), 1.000 dias por caso, semente 20261021: os mesmos dias da aba "Muitos dias" com essa semente. Média e intervalo de 95%.

Cada dia é simulado uma vez e medido duas vezes: na rede atual e na rede com a linha nova. A linha nova tem falhas e trens próprios, num fluxo de sorteio separado; as falhas da rede atual são as mesmas nas duas medidas. Por isso a diferença tem intervalo pareado, mais estreito que o de cada valor.

Escala: perto de 100%, a disponibilidade esconde as diferenças. Ao lado dela vão o tempo sem caminho por dia, o número de noves (−log₁₀ da indisponibilidade: 99% são 2 noves, 99,9% são 3) e a razão do tempo sem caminho contra a rede atual.

## Atwater → Université-de-Montréal, com uma ligação desenhada entre as duas

A melhor ligação nova da busca da spec 014 (a Azul hoje só se liga à rede pela Laranja). A ligação vira o caminho de sempre: uma linha só, no lugar de Verde, Laranja e Azul.

### sem rota alternativa; linha nova independente

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 99,282% (99,198% a 99,366%) | 99,945% (99,925% a 99,965%) | +0,663 pp (+0,576 pp a +0,750 pp) |
| Tempo sem caminho (min por dia) | 8,60 (7,59 a 9,61) | 0,66 (0,42 a 0,90) | -7,94 (-8,98 a -6,90) |
| Noves (−log₁₀ da indisponibilidade) | 2,14 (2,10 a 2,20) | 3,26 (3,12 a 3,46) | +1,12 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,077 (0,047 a 0,106) |
| Chance de chegar mais de 5 min atrasado | 0,37% (0,29% a 0,45%) | 0,09% (0,06% a 0,11%) | -0,28 pp (-0,36 pp a -0,20 pp) |
| Atraso médio por viagem (min) | 0,11 (0,02 a 0,20) | 0,01 (0,01 a 0,02) | -0,09 (-0,18 a -0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 27,5 (27,4 a 27,6) | 8,3 (8,3 a 8,3) | -19,15 (-19,24 a -19,07) |
| Falhas da linha nova por dia | | 0,175 (0,149 a 0,201) | |

3,2 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### sem rota alternativa; linha nova divide a causa comum com as linhas em que encosta

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 99,282% (99,198% a 99,366%) | 99,920% (99,892% a 99,949%) | +0,638 pp (+0,553 pp a +0,723 pp) |
| Tempo sem caminho (min por dia) | 8,60 (7,59 a 9,61) | 0,96 (0,62 a 1,29) | -7,65 (-8,67 a -6,63) |
| Noves (−log₁₀ da indisponibilidade) | 2,14 (2,10 a 2,20) | 3,10 (2,97 a 3,29) | +0,95 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,111 (0,071 a 0,151) |
| Chance de chegar mais de 5 min atrasado | 0,37% (0,29% a 0,45%) | 0,11% (0,08% a 0,15%) | -0,25 pp (-0,33 pp a -0,18 pp) |
| Atraso médio por viagem (min) | 0,11 (0,02 a 0,20) | 0,02 (0,01 a 0,03) | -0,08 (-0,17 a +0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 27,5 (27,4 a 27,6) | 8,4 (8,3 a 8,4) | -19,14 (-19,23 a -19,06) |
| Falhas da linha nova por dia | | 0,175 (0,149 a 0,201) | |

2,8 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova para junto com as linhas em que encosta; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa; linha nova independente

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 99,282% (99,198% a 99,366%) | 100,000% (100,000% a 100,000%) | +0,718 pp (+0,634 pp a +0,802 pp) |
| Tempo sem caminho (min por dia) | 8,60 (7,59 a 9,61) | 0,00 (0,00 a 0,00) | -8,60 (-9,61 a -7,59) |
| Noves (−log₁₀ da indisponibilidade) | 2,14 (2,10 a 2,20) | ∞ (∞ a ∞) | +∞ |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,000 (0,000 a 0,000) |
| Chance de chegar mais de 5 min atrasado | 0,35% (0,27% a 0,43%) | 0,09% (0,06% a 0,11%) | -0,26 pp (-0,34 pp a -0,18 pp) |
| Atraso médio por viagem (min) | 0,10 (0,01 a 0,19) | 0,01 (0,01 a 0,01) | -0,09 (-0,18 a -0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 27,5 (27,4 a 27,5) | 8,3 (8,3 a 8,3) | -19,12 (-19,20 a -19,03) |
| Falhas da linha nova por dia | | 0,175 (0,149 a 0,201) | |

7,6 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa; linha nova divide a causa comum com as linhas em que encosta

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 99,282% (99,198% a 99,366%) | 99,975% (99,955% a 99,995%) | +0,693 pp (+0,611 pp a +0,776 pp) |
| Tempo sem caminho (min por dia) | 8,60 (7,59 a 9,61) | 0,30 (0,06 a 0,53) | -8,31 (-9,29 a -7,32) |
| Noves (−log₁₀ da indisponibilidade) | 2,14 (2,10 a 2,20) | 3,61 (3,35 a 4,33) | +1,46 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,034 (0,007 a 0,062) |
| Chance de chegar mais de 5 min atrasado | 0,35% (0,27% a 0,43%) | 0,11% (0,08% a 0,15%) | -0,24 pp (-0,31 pp a -0,16 pp) |
| Atraso médio por viagem (min) | 0,10 (0,01 a 0,19) | 0,02 (0,01 a 0,03) | -0,08 (-0,17 a +0,01) |
| Tempo médio da saída à chegada, com as falhas (min) | 27,5 (27,4 a 27,5) | 8,3 (8,3 a 8,4) | -19,11 (-19,19 a -19,02) |
| Falhas da linha nova por dia | | 0,175 (0,149 a 0,201) | |

7,5 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova para junto com as linhas em que encosta; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Côte-Vertu → Montmorency, com o anel da Laranja (ARTM, 2019)

Hoje a viagem dá a volta pela Laranja inteira; o anel liga as duas pontas por Laval.

### sem rota alternativa

| Medida | Rede atual | Com Anel da Laranja (ARTM, 2019) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Snowdon, Azul até Jean-Talon, Laranja até Montmorency | Anel da Laranja (ARTM, 2019) até Montmorency | |
| Tempo programado do caminho (min) | 40,0 | 16,5 | -23,5 |
| Disponibilidade da viagem | 99,527% (99,450% a 99,605%) | 99,909% (99,881% a 99,936%) | +0,381 pp (+0,299 pp a +0,464 pp) |
| Tempo sem caminho (min por dia) | 5,66 (4,73 a 6,59) | 1,10 (0,76 a 1,43) | -4,57 (-5,56 a -3,58) |
| Noves (−log₁₀ da indisponibilidade) | 2,33 (2,26 a 2,40) | 3,04 (2,92 a 3,20) | +0,71 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,193 (0,127 a 0,260) |
| Chance de chegar mais de 5 min atrasado | 0,28% (0,20% a 0,36%) | 0,16% (0,12% a 0,20%) | -0,12 pp (-0,21 pp a -0,03 pp) |
| Atraso médio por viagem (min) | 0,07 (0,04 a 0,09) | 0,03 (0,02 a 0,04) | -0,04 (-0,07 a -0,01) |
| Tempo médio da saída à chegada, com as falhas (min) | 48,7 (48,7 a 48,7) | 19,2 (19,2 a 19,2) | -29,53 (-29,56 a -29,50) |
| Falhas da linha nova por dia | | 0,361 (0,322 a 0,400) | |

3,1 s para 1.000 dias nesta máquina (um processo). Hipóteses: Anel da Laranja (ARTM, 2019): traçado hipótese de traçado (https://web.archive.org/web/20191010182703/https://montrealgazette.com/news/local-news/completing-montreal-metros-orange-line-loop-will-cost-an-estimated-4-3b); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Anel da Laranja (ARTM, 2019): taxas por km da linha laranja, durações da linha laranja; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa

| Medida | Rede atual | Com Anel da Laranja (ARTM, 2019) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Snowdon, Azul até Jean-Talon, Laranja até Montmorency | Anel da Laranja (ARTM, 2019) até Montmorency | |
| Tempo programado do caminho (min) | 40,0 | 16,5 | -23,5 |
| Disponibilidade da viagem | 99,707% (99,660% a 99,754%) | 100,000% (100,000% a 100,000%) | +0,293 pp (+0,246 pp a +0,340 pp) |
| Tempo sem caminho (min por dia) | 3,51 (2,95 a 4,07) | 0,00 (0,00 a 0,00) | -3,51 (-4,07 a -2,95) |
| Noves (−log₁₀ da indisponibilidade) | 2,53 (2,47 a 2,61) | ∞ (∞ a ∞) | +∞ |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,000 (0,000 a 0,000) |
| Chance de chegar mais de 5 min atrasado | 0,28% (0,20% a 0,36%) | 0,16% (0,12% a 0,20%) | -0,12 pp (-0,21 pp a -0,03 pp) |
| Atraso médio por viagem (min) | 0,07 (0,04 a 0,09) | 0,02 (0,01 a 0,03) | -0,04 (-0,07 a -0,02) |
| Tempo médio da saída à chegada, com as falhas (min) | 48,7 (48,7 a 48,7) | 19,2 (19,2 a 19,2) | -29,54 (-29,57 a -29,51) |
| Falhas da linha nova por dia | | 0,361 (0,322 a 0,400) | |

8,4 s para 1.000 dias nesta máquina (um processo). Hipóteses: Anel da Laranja (ARTM, 2019): traçado hipótese de traçado (https://web.archive.org/web/20191010182703/https://montrealgazette.com/news/local-news/completing-montreal-metros-orange-line-loop-will-cost-an-estimated-4-3b); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Anel da Laranja (ARTM, 2019): taxas por km da linha laranja, durações da linha laranja; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Vendôme → Place-des-Arts, com a Linha Rosa (proposta de 2017)

A Rosa encosta na Laranja em Vendôme e em Mont-Royal e na Verde em Place-des-Arts.

### sem rota alternativa

| Medida | Rede atual | Com Linha Rosa (proposta de 2017) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Lionel-Groulx, Verde até Place Des Arts | Linha Rosa (proposta de 2017) até Place Des Arts | |
| Tempo programado do caminho (min) | 14,0 | 11,5 | -2,5 |
| Disponibilidade da viagem | 99,460% (99,402% a 99,518%) | 99,486% (99,373% a 99,600%) | +0,026 pp (-0,101 pp a +0,153 pp) |
| Tempo sem caminho (min por dia) | 6,47 (5,77 a 7,17) | 6,16 (4,80 a 7,52) | -0,31 (-1,83 a +1,21) |
| Noves (−log₁₀ da indisponibilidade) | 2,27 (2,22 a 2,32) | 2,29 (2,20 a 2,40) | +0,02 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,951 (0,719 a 1,184) |
| Chance de chegar mais de 5 min atrasado | 0,17% (0,12% a 0,22%) | 0,94% (0,81% a 1,08%) | +0,78 pp (+0,64 pp a +0,91 pp) |
| Atraso médio por viagem (min) | 0,04 (0,02 a 0,06) | 0,14 (0,12 a 0,17) | +0,10 (+0,07 a +0,14) |
| Tempo médio da saída à chegada, com as falhas (min) | 18,2 (18,2 a 18,2) | 14,4 (14,3 a 14,4) | -3,86 (-3,89 a -3,83) |
| Falhas da linha nova por dia | | 1,575 (1,497 a 1,653) | |

2,8 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha Rosa (proposta de 2017): traçado hipótese de traçado (https://ici.radio-canada.ca/nouvelle/1065916/stations-ligne-rose-metro-localisation-projet-montreal-plante-ouellet); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha Rosa (proposta de 2017): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa

| Medida | Rede atual | Com Linha Rosa (proposta de 2017) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Lionel-Groulx, Verde até Place Des Arts | Linha Rosa (proposta de 2017) até Place Des Arts | |
| Tempo programado do caminho (min) | 14,0 | 11,5 | -2,5 |
| Disponibilidade da viagem | 99,460% (99,402% a 99,518%) | 99,997% (99,995% a 99,999%) | +0,537 pp (+0,479 pp a +0,595 pp) |
| Tempo sem caminho (min por dia) | 6,47 (5,77 a 7,17) | 0,03 (0,01 a 0,06) | -6,44 (-7,13 a -5,74) |
| Noves (−log₁₀ da indisponibilidade) | 2,27 (2,22 a 2,32) | 4,57 (4,33 a 5,16) | +2,30 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,005 (0,001 a 0,009) |
| Chance de chegar mais de 5 min atrasado | 0,14% (0,09% a 0,18%) | 0,37% (0,31% a 0,43%) | +0,23 pp (+0,15 pp a +0,30 pp) |
| Atraso médio por viagem (min) | 0,03 (0,02 a 0,05) | 0,05 (0,04 a 0,05) | +0,02 (-0,00 a +0,03) |
| Tempo médio da saída à chegada, com as falhas (min) | 18,2 (18,2 a 18,2) | 14,0 (14,0 a 14,0) | -4,13 (-4,14 a -4,11) |
| Falhas da linha nova por dia | | 1,575 (1,497 a 1,653) | |

8,4 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha Rosa (proposta de 2017): traçado hipótese de traçado (https://ici.radio-canada.ca/nouvelle/1065916/stations-ligne-rose-metro-localisation-projet-montreal-plante-ouellet); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha Rosa (proposta de 2017): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Angrignon → Saint-Michel (a viagem padrão), com uma ligação desenhada Angrignon–Snowdon

A ligação troca três linhas em série (Verde, Laranja, Azul) por duas (a ligação e a Azul).

### sem rota alternativa

| Medida | Rede atual | Com Linha desenhada 1 (Angrignon – Snowdon) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Berri-Uqam, Laranja até Jean-Talon, Azul até Saint-Michel | linha desenhada até Snowdon, Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 40,0 | 27,4 | -12,6 |
| Disponibilidade da viagem | 99,282% (99,198% a 99,366%) | 99,728% (99,660% a 99,796%) | +0,446 pp (+0,385 pp a +0,507 pp) |
| Tempo sem caminho (min por dia) | 8,60 (7,59 a 9,61) | 3,26 (2,45 a 4,07) | -5,34 (-6,07 a -4,61) |
| Noves (−log₁₀ da indisponibilidade) | 2,14 (2,10 a 2,20) | 2,56 (2,47 a 2,69) | +0,42 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,379 (0,308 a 0,450) |
| Chance de chegar mais de 5 min atrasado | 0,40% (0,30% a 0,50%) | 0,29% (0,20% a 0,38%) | -0,11 pp (-0,20 pp a -0,02 pp) |
| Atraso médio por viagem (min) | 0,13 (0,03 a 0,24) | 0,11 (0,00 a 0,22) | -0,03 (-0,05 a +0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 48,3 (48,2 a 48,4) | 35,7 (35,6 a 35,8) | -12,65 (-12,68 a -12,62) |
| Falhas da linha nova por dia | | 0,267 (0,235 a 0,299) | |

3,5 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Angrignon – Snowdon): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Angrignon – Snowdon): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa

| Medida | Rede atual | Com Linha desenhada 1 (Angrignon – Snowdon) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Berri-Uqam, Laranja até Jean-Talon, Azul até Saint-Michel | linha desenhada até Snowdon, Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 40,0 | 27,4 | -12,6 |
| Disponibilidade da viagem | 99,282% (99,198% a 99,366%) | 99,805% (99,741% a 99,869%) | +0,523 pp (+0,467 pp a +0,579 pp) |
| Tempo sem caminho (min por dia) | 8,60 (7,59 a 9,61) | 2,34 (1,57 a 3,11) | -6,27 (-6,94 a -5,59) |
| Noves (−log₁₀ da indisponibilidade) | 2,14 (2,10 a 2,20) | 2,71 (2,59 a 2,88) | +0,57 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,272 (0,202 a 0,341) |
| Chance de chegar mais de 5 min atrasado | 0,29% (0,20% a 0,38%) | 0,29% (0,20% a 0,38%) | +0,00 pp (-0,07 pp a +0,07 pp) |
| Atraso médio por viagem (min) | 0,11 (0,00 a 0,21) | 0,09 (0,00 a 0,20) | -0,01 (-0,03 a +0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 47,0 (46,9 a 47,1) | 35,7 (35,5 a 35,8) | -11,39 (-11,41 a -11,37) |
| Falhas da linha nova por dia | | 0,267 (0,235 a 0,299) | |

8,5 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Angrignon – Snowdon): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Angrignon – Snowdon): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Snowdon → Saint-Michel, com o prolongamento da Azul até Anjou

A viagem não usa o trecho novo. Sem retorno parcial, uma falha no prolongamento para a Azul inteira; com retorno parcial, Saint-Michel continua ponto de retorno.

### sem rota alternativa

| Medida | Rede atual | Com Prolongamento da Azul até Anjou | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Azul até Saint-Michel | Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 14,0 | 14,0 | 0,0 |
| Disponibilidade da viagem | 99,806% (99,742% a 99,870%) | 99,695% (99,627% a 99,764%) | -0,111 pp (-0,134 pp a -0,088 pp) |
| Tempo sem caminho (min por dia) | 2,32 (1,55 a 3,09) | 3,65 (2,83 a 4,47) | +1,33 (+1,05 a +1,60) |
| Noves (−log₁₀ da indisponibilidade) | 2,71 (2,59 a 2,89) | 2,52 (2,43 a 2,63) | -0,20 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 1,571 (1,348 a 1,794) |
| Chance de chegar mais de 5 min atrasado | 0,13% (0,06% a 0,21%) | 0,33% (0,25% a 0,42%) | +0,20 pp (+0,16 pp a +0,24 pp) |
| Atraso médio por viagem (min) | 0,08 (0,00 a 0,18) | 0,11 (0,00 a 0,21) | +0,03 (+0,02 a +0,04) |
| Tempo médio da saída à chegada, com as falhas (min) | 19,0 (18,9 a 19,1) | 19,1 (18,9 a 19,2) | +0,03 (+0,02 a +0,04) |
| Falhas da linha nova por dia | | 0,340 (0,301 a 0,379) | |

2,5 s para 1.000 dias nesta máquina (um processo). Hipóteses: Prolongamento da Azul até Anjou: traçado em obras (OSM) (https://montreal.ca/communiques-de-presse/les-femmes-et-les-communautes-seront-honorees-sur-le-futur-troncon-de-la-ligne-bleue); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; azul: o trecho novo falha com as taxas por km e as durações observadas da própria linha, e as viagens do horário seguem por ele; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### sem rota alternativa; com retorno parcial

| Medida | Rede atual | Com Prolongamento da Azul até Anjou | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Azul até Saint-Michel | Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 14,0 | 14,0 | 0,0 |
| Disponibilidade da viagem | 99,856% (99,793% a 99,919%) | 99,856% (99,793% a 99,919%) | 0,000 pp (0,000 pp a 0,000 pp) |
| Tempo sem caminho (min por dia) | 1,72 (0,97 a 2,48) | 1,72 (0,97 a 2,48) | 0,00 (0,00 a 0,00) |
| Noves (−log₁₀ da indisponibilidade) | 2,84 (2,68 a 3,09) | 2,84 (2,68 a 3,09) | 0,00 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 1,000 (1,000 a 1,000) |
| Chance de chegar mais de 5 min atrasado | 0,13% (0,06% a 0,21%) | 0,13% (0,06% a 0,21%) | 0,00 pp (0,00 pp a 0,00 pp) |
| Atraso médio por viagem (min) | 0,08 (0,00 a 0,18) | 0,08 (0,00 a 0,18) | 0,00 (0,00 a 0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 19,0 (18,9 a 19,1) | 19,0 (18,9 a 19,1) | 0,00 (0,00 a 0,00) |
| Falhas da linha nova por dia | | 0,340 (0,301 a 0,379) | |

2,5 s para 1.000 dias nesta máquina (um processo). Hipóteses: Prolongamento da Azul até Anjou: traçado em obras (OSM) (https://montreal.ca/communiques-de-presse/les-femmes-et-les-communautes-seront-honorees-sur-le-futur-troncon-de-la-ligne-bleue); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; azul: o trecho novo falha com as taxas por km e as durações observadas da própria linha, e as viagens do horário seguem por ele; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; retorno parcial ligado (pontas de viagem do horário e os terminais antigos).

## Como ler

- A linha nova ajuda de dois jeitos: quando vira o caminho de sempre (menos linhas em série, viagem mais curta) e, com a rota alternativa, como caminho em paralelo.
- Sem a rota alternativa, a pessoa usa só o caminho de sempre: se ele passa pela linha nova, a viagem passa a depender das falhas dela.
- Um prolongamento que a viagem não usa não ajuda e, sem retorno parcial, piora: a falha no trecho novo para a linha inteira.
- A linha nova herda as taxas por km e as durações das linhas atuais: não é mais confiável que elas por hipótese.

Tempo de execução total: 1,0 min (um processo).
