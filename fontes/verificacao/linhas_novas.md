# Linhas novas numa viagem (spec 016)

Gerado por `app/relatorios/linhas_novas.relatorio.ts` com o `parametros.json` real (código sha256-scripts:70cf9c002aa2ba0a). Cenário padrão (dia útil, condições de referência do modelo), 1.000 dias por caso, semente 20261021: os mesmos dias da aba "Muitos dias" com essa semente. Média e intervalo de 95%.

Cada dia é simulado uma vez e medido duas vezes: na rede atual e na rede com a linha nova. A linha nova tem falhas e trens próprios, num fluxo de sorteio separado; as falhas da rede atual são as mesmas nas duas medidas. Por isso a diferença tem intervalo pareado, mais estreito que o de cada valor.

Escala: perto de 100%, a disponibilidade esconde as diferenças. Ao lado dela vão o tempo sem caminho por dia, o número de noves (−log₁₀ da indisponibilidade: 99% são 2 noves, 99,9% são 3) e a razão do tempo sem caminho contra a rede atual.

## Atwater → Université-de-Montréal, com uma ligação desenhada entre as duas

A melhor ligação nova da busca da spec 014 (a Azul hoje só se liga à rede pela Laranja). A ligação vira o caminho de sempre: uma linha só, no lugar de Verde, Laranja e Azul.

### sem rota alternativa; linha nova independente

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 98,463% (98,064% a 98,861%) | 99,860% (99,696% a 100,000%) | +1,398 pp (+0,966 pp a +1,830 pp) |
| Tempo sem caminho (min por dia) | 18,42 (13,64 a 23,19) | 1,67 (0,00 a 3,64) | -16,74 (-21,92 a -11,57) |
| Noves (−log₁₀ da indisponibilidade) | 1,81 (1,71 a 1,94) | 2,85 (2,52 a ∞) | +1,04 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,091 (0,000 a 0,200) |
| Chance de chegar mais de 5 min atrasado | 1,11% (0,71% a 1,51%) | 0,18% (0,01% a 0,35%) | -0,93 pp (-1,37 pp a -0,49 pp) |
| Atraso médio por viagem (min) | 3,41 (0,80 a 6,01) | 0,02 (0,01 a 0,02) | -3,39 (-5,99 a -0,79) |
| Tempo médio da saída à chegada, com as falhas (min) | 30,8 (28,2 a 33,4) | 8,3 (8,3 a 8,4) | -22,45 (-25,05 a -19,85) |
| Falhas da linha nova por dia | | 0,197 (0,170 a 0,224) | |

3,8 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### sem rota alternativa; linha nova divide a causa comum com as linhas em que encosta

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 98,463% (98,064% a 98,861%) | 99,835% (99,670% a 100,000%) | +1,373 pp (+0,941 pp a +1,805 pp) |
| Tempo sem caminho (min por dia) | 18,42 (13,64 a 23,19) | 1,97 (0,00 a 3,95) | -16,45 (-21,62 a -11,27) |
| Noves (−log₁₀ da indisponibilidade) | 1,81 (1,71 a 1,94) | 2,78 (2,48 a ∞) | +0,97 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,107 (0,000 a 0,218) |
| Chance de chegar mais de 5 min atrasado | 1,11% (0,71% a 1,51%) | 0,21% (0,04% a 0,38%) | -0,90 pp (-1,34 pp a -0,46 pp) |
| Atraso médio por viagem (min) | 3,41 (0,80 a 6,01) | 0,02 (0,01 a 0,04) | -3,38 (-5,99 a -0,78) |
| Tempo médio da saída à chegada, com as falhas (min) | 30,8 (28,2 a 33,4) | 8,4 (8,3 a 8,4) | -22,44 (-25,05 a -19,84) |
| Falhas da linha nova por dia | | 0,197 (0,170 a 0,224) | |

5,4 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova para junto com as linhas em que encosta; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa; linha nova independente

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 98,463% (98,064% a 98,861%) | 99,999% (99,997% a 100,000%) | +1,536 pp (+1,138 pp a +1,934 pp) |
| Tempo sem caminho (min por dia) | 18,42 (13,64 a 23,19) | 0,02 (0,00 a 0,04) | -18,40 (-23,17 a -13,63) |
| Noves (−log₁₀ da indisponibilidade) | 1,81 (1,71 a 1,94) | 4,84 (4,50 a ∞) | +3,03 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,001 (0,000 a 0,002) |
| Chance de chegar mais de 5 min atrasado | 1,10% (0,70% a 1,51%) | 0,18% (0,01% a 0,35%) | -0,92 pp (-1,36 pp a -0,48 pp) |
| Atraso médio por viagem (min) | 3,38 (0,78 a 5,98) | 0,03 (0,00 a 0,06) | -3,35 (-5,95 a -0,75) |
| Tempo médio da saída à chegada, com as falhas (min) | 30,7 (28,1 a 33,3) | 8,4 (8,3 a 8,4) | -22,37 (-24,97 a -19,77) |
| Falhas da linha nova por dia | | 0,197 (0,170 a 0,224) | |

13,2 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa; linha nova divide a causa comum com as linhas em que encosta

| Medida | Rede atual | Com Linha desenhada 1 (Atwater – Université De Montreal) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Lionel-Groulx, Laranja até Snowdon, Azul até Université De Montreal | linha desenhada até Université De Montreal | |
| Tempo programado do caminho (min) | 20,0 | 5,9 | -14,1 |
| Disponibilidade da viagem | 98,463% (98,064% a 98,861%) | 99,974% (99,954% a 99,994%) | +1,511 pp (+1,113 pp a +1,909 pp) |
| Tempo sem caminho (min por dia) | 18,42 (13,64 a 23,19) | 0,31 (0,07 a 0,55) | -18,10 (-22,87 a -13,33) |
| Noves (−log₁₀ da indisponibilidade) | 1,81 (1,71 a 1,94) | 3,58 (3,33 a 4,21) | +1,77 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,017 (0,003 a 0,031) |
| Chance de chegar mais de 5 min atrasado | 1,10% (0,70% a 1,51%) | 0,21% (0,04% a 0,38%) | -0,89 pp (-1,33 pp a -0,46 pp) |
| Atraso médio por viagem (min) | 3,38 (0,78 a 5,98) | 0,04 (0,00 a 0,07) | -3,34 (-5,94 a -0,74) |
| Tempo médio da saída à chegada, com as falhas (min) | 30,7 (28,1 a 33,3) | 8,4 (8,3 a 8,4) | -22,36 (-24,96 a -19,76) |
| Falhas da linha nova por dia | | 0,197 (0,170 a 0,224) | |

12,8 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Atwater – Université De Montreal): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Atwater – Université De Montreal): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha verde, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova para junto com as linhas em que encosta; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Côte-Vertu → Montmorency, com o anel da Laranja (ARTM, 2019)

Hoje a viagem dá a volta pela Laranja inteira; o anel liga as duas pontas por Laval.

### sem rota alternativa

| Medida | Rede atual | Com Anel da Laranja (ARTM, 2019) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Snowdon, Azul até Jean-Talon, Laranja até Montmorency | Anel da Laranja (ARTM, 2019) até Montmorency | |
| Tempo programado do caminho (min) | 40,0 | 16,5 | -23,5 |
| Disponibilidade da viagem | 98,899% (98,510% a 99,289%) | 99,905% (99,873% a 99,937%) | +1,005 pp (+0,615 pp a +1,396 pp) |
| Tempo sem caminho (min por dia) | 13,18 (8,52 a 17,85) | 1,14 (0,76 a 1,52) | -12,05 (-16,73 a -7,36) |
| Noves (−log₁₀ da indisponibilidade) | 1,96 (1,83 a 2,15) | 3,02 (2,90 a 3,20) | +1,06 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,086 (0,044 a 0,129) |
| Chance de chegar mais de 5 min atrasado | 0,71% (0,45% a 0,96%) | 0,17% (0,12% a 0,21%) | -0,54 pp (-0,80 pp a -0,28 pp) |
| Atraso médio por viagem (min) | 0,60 (0,00 a 1,29) | 0,04 (0,01 a 0,06) | -0,57 (-1,26 a +0,12) |
| Tempo médio da saída à chegada, com as falhas (min) | 49,3 (48,6 a 49,9) | 19,2 (19,2 a 19,2) | -30,06 (-30,75 a -29,37) |
| Falhas da linha nova por dia | | 0,416 (0,374 a 0,458) | |

5,5 s para 1.000 dias nesta máquina (um processo). Hipóteses: Anel da Laranja (ARTM, 2019): traçado hipótese de traçado (https://web.archive.org/web/20191010182703/https://montrealgazette.com/news/local-news/completing-montreal-metros-orange-line-loop-will-cost-an-estimated-4-3b); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Anel da Laranja (ARTM, 2019): taxas por km da linha laranja, durações da linha laranja; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa

| Medida | Rede atual | Com Anel da Laranja (ARTM, 2019) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Snowdon, Azul até Jean-Talon, Laranja até Montmorency | Anel da Laranja (ARTM, 2019) até Montmorency | |
| Tempo programado do caminho (min) | 40,0 | 16,5 | -23,5 |
| Disponibilidade da viagem | 99,457% (99,280% a 99,634%) | 100,000% (99,999% a 100,000%) | +0,542 pp (+0,366 pp a +0,719 pp) |
| Tempo sem caminho (min por dia) | 6,50 (4,38 a 8,62) | 0,01 (0,00 a 0,01) | -6,50 (-8,61 a -4,38) |
| Noves (−log₁₀ da indisponibilidade) | 2,27 (2,14 a 2,44) | 5,38 (4,91 a ∞) | +3,11 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,001 (0,000 a 0,002) |
| Chance de chegar mais de 5 min atrasado | 0,71% (0,45% a 0,96%) | 0,17% (0,12% a 0,21%) | -0,54 pp (-0,80 pp a -0,28 pp) |
| Atraso médio por viagem (min) | 0,60 (0,00 a 1,29) | 0,02 (0,01 a 0,03) | -0,58 (-1,27 a +0,11) |
| Tempo médio da saída à chegada, com as falhas (min) | 49,3 (48,6 a 49,9) | 19,2 (19,2 a 19,2) | -30,07 (-30,77 a -29,38) |
| Falhas da linha nova por dia | | 0,416 (0,374 a 0,458) | |

14,3 s para 1.000 dias nesta máquina (um processo). Hipóteses: Anel da Laranja (ARTM, 2019): traçado hipótese de traçado (https://web.archive.org/web/20191010182703/https://montrealgazette.com/news/local-news/completing-montreal-metros-orange-line-loop-will-cost-an-estimated-4-3b); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Anel da Laranja (ARTM, 2019): taxas por km da linha laranja, durações da linha laranja; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Vendôme → Place-des-Arts, com a Linha Rosa (proposta de 2017)

A Rosa encosta na Laranja em Vendôme e em Mont-Royal e na Verde em Place-des-Arts.

### sem rota alternativa

| Medida | Rede atual | Com Linha Rosa (proposta de 2017) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Lionel-Groulx, Verde até Place Des Arts | Linha Rosa (proposta de 2017) até Place Des Arts | |
| Tempo programado do caminho (min) | 14,0 | 11,5 | -2,5 |
| Disponibilidade da viagem | 99,016% (98,817% a 99,216%) | 99,195% (98,919% a 99,471%) | +0,179 pp (-0,160 pp a +0,518 pp) |
| Tempo sem caminho (min por dia) | 11,78 (9,40 a 14,17) | 9,64 (6,33 a 12,95) | -2,14 (-6,20 a +1,92) |
| Noves (−log₁₀ da indisponibilidade) | 2,01 (1,93 a 2,11) | 2,09 (1,97 a 2,28) | +0,09 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,818 (0,493 a 1,143) |
| Chance de chegar mais de 5 min atrasado | 0,49% (0,28% a 0,70%) | 1,30% (1,01% a 1,58%) | +0,80 pp (+0,45 pp a +1,16 pp) |
| Atraso médio por viagem (min) | 0,62 (0,00 a 1,33) | 0,19 (0,13 a 0,26) | -0,43 (-1,14 a +0,28) |
| Tempo médio da saída à chegada, com as falhas (min) | 18,8 (18,1 a 19,5) | 14,4 (14,3 a 14,5) | -4,39 (-5,10 a -3,68) |
| Falhas da linha nova por dia | | 1,834 (1,750 a 1,918) | |

5,4 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha Rosa (proposta de 2017): traçado hipótese de traçado (https://ici.radio-canada.ca/nouvelle/1065916/stations-ligne-rose-metro-localisation-projet-montreal-plante-ouellet); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha Rosa (proposta de 2017): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa

| Medida | Rede atual | Com Linha Rosa (proposta de 2017) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Laranja até Lionel-Groulx, Verde até Place Des Arts | Linha Rosa (proposta de 2017) até Place Des Arts | |
| Tempo programado do caminho (min) | 14,0 | 11,5 | -2,5 |
| Disponibilidade da viagem | 99,016% (98,817% a 99,216%) | 99,991% (99,987% a 99,996%) | +0,975 pp (+0,776 pp a +1,174 pp) |
| Tempo sem caminho (min por dia) | 11,78 (9,40 a 14,17) | 0,11 (0,05 a 0,16) | -11,68 (-14,06 a -9,30) |
| Noves (−log₁₀ da indisponibilidade) | 2,01 (1,93 a 2,11) | 4,06 (3,88 a 4,36) | +2,05 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,009 (0,004 a 0,013) |
| Chance de chegar mais de 5 min atrasado | 0,44% (0,24% a 0,65%) | 0,45% (0,36% a 0,55%) | +0,01 pp (-0,22 pp a +0,24 pp) |
| Atraso médio por viagem (min) | 0,60 (0,00 a 1,30) | 0,06 (0,05 a 0,08) | -0,54 (-1,24 a +0,17) |
| Tempo médio da saída à chegada, com as falhas (min) | 18,7 (18,0 a 19,4) | 14,1 (14,0 a 14,1) | -4,68 (-5,38 a -3,97) |
| Falhas da linha nova por dia | | 1,834 (1,750 a 1,918) | |

14,4 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha Rosa (proposta de 2017): traçado hipótese de traçado (https://ici.radio-canada.ca/nouvelle/1065916/stations-ligne-rose-metro-localisation-projet-montreal-plante-ouellet); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha Rosa (proposta de 2017): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Angrignon → Saint-Michel (a viagem padrão), com uma ligação desenhada Angrignon–Snowdon

A ligação troca três linhas em série (Verde, Laranja, Azul) por duas (a ligação e a Azul).

### sem rota alternativa

| Medida | Rede atual | Com Linha desenhada 1 (Angrignon – Snowdon) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Berri-Uqam, Laranja até Jean-Talon, Azul até Saint-Michel | linha desenhada até Snowdon, Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 40,0 | 27,4 | -12,6 |
| Disponibilidade da viagem | 98,463% (98,064% a 98,861%) | 99,223% (98,828% a 99,619%) | +0,761 pp (+0,487 pp a +1,034 pp) |
| Tempo sem caminho (min por dia) | 18,42 (13,64 a 23,19) | 9,31 (4,57 a 14,05) | -9,11 (-12,39 a -5,84) |
| Noves (−log₁₀ da indisponibilidade) | 1,81 (1,71 a 1,94) | 2,11 (1,93 a 2,42) | +0,30 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,505 (0,327 a 0,684) |
| Chance de chegar mais de 5 min atrasado | 1,29% (0,84% a 1,74%) | 0,79% (0,39% a 1,20%) | -0,50 pp (-0,83 pp a -0,16 pp) |
| Atraso médio por viagem (min) | 3,27 (0,87 a 5,67) | 2,88 (0,29 a 5,46) | -0,39 (-1,27 a +0,48) |
| Tempo médio da saída à chegada, com as falhas (min) | 51,5 (49,1 a 53,8) | 38,4 (35,9 a 41,0) | -13,02 (-13,89 a -12,14) |
| Falhas da linha nova por dia | | 0,307 (0,272 a 0,342) | |

4,9 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Angrignon – Snowdon): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Angrignon – Snowdon): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### com rota alternativa

| Medida | Rede atual | Com Linha desenhada 1 (Angrignon – Snowdon) | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Verde até Berri-Uqam, Laranja até Jean-Talon, Azul até Saint-Michel | linha desenhada até Snowdon, Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 40,0 | 27,4 | -12,6 |
| Disponibilidade da viagem | 98,463% (98,064% a 98,861%) | 99,424% (99,075% a 99,774%) | +0,962 pp (+0,763 pp a +1,161 pp) |
| Tempo sem caminho (min por dia) | 18,42 (13,64 a 23,19) | 6,90 (2,71 a 11,08) | -11,52 (-13,91 a -9,14) |
| Noves (−log₁₀ da indisponibilidade) | 1,81 (1,71 a 1,94) | 2,24 (2,03 a 2,65) | +0,43 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 0,374 (0,223 a 0,526) |
| Chance de chegar mais de 5 min atrasado | 1,08% (0,66% a 1,51%) | 0,79% (0,39% a 1,19%) | -0,29 pp (-0,59 pp a -0,00 pp) |
| Atraso médio por viagem (min) | 3,17 (0,79 a 5,56) | 2,58 (0,31 a 4,85) | -0,59 (-1,28 a +0,10) |
| Tempo médio da saída à chegada, com as falhas (min) | 50,1 (47,7 a 52,5) | 38,1 (35,9 a 40,4) | -11,97 (-12,65 a -11,28) |
| Falhas da linha nova por dia | | 0,307 (0,272 a 0,342) | |

8,9 s para 1.000 dias nesta máquina (um processo). Hipóteses: Linha desenhada 1 (Angrignon – Snowdon): traçado livre; km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; Linha desenhada 1 (Angrignon – Snowdon): taxas por km da média da rede, durações das linhas atuais, com peso pela taxa; partidas por hora da linha laranja, espaçadas por igual; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

## Snowdon → Saint-Michel, com o prolongamento da Azul até Anjou

A viagem não usa o trecho novo. Sem retorno parcial, uma falha no prolongamento para a Azul inteira; com retorno parcial, Saint-Michel continua ponto de retorno.

### sem rota alternativa

| Medida | Rede atual | Com Prolongamento da Azul até Anjou | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Azul até Saint-Michel | Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 14,0 | 14,0 | 0,0 |
| Disponibilidade da viagem | 99,425% (99,076% a 99,775%) | 99,211% (98,825% a 99,597%) | -0,214 pp (-0,380 pp a -0,049 pp) |
| Tempo sem caminho (min por dia) | 6,89 (2,70 a 11,07) | 9,45 (4,83 a 14,08) | +2,57 (+0,58 a +4,55) |
| Noves (−log₁₀ da indisponibilidade) | 2,24 (2,03 a 2,65) | 2,10 (1,93 a 2,39) | -0,14 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 1,373 (1,005 a 1,741) |
| Chance de chegar mais de 5 min atrasado | 0,50% (0,15% a 0,85%) | 0,81% (0,42% a 1,20%) | +0,31 pp (+0,14 pp a +0,48 pp) |
| Atraso médio por viagem (min) | 2,82 (0,26 a 5,38) | 2,85 (0,29 a 5,41) | +0,03 (+0,02 a +0,04) |
| Tempo médio da saída à chegada, com as falhas (min) | 21,8 (19,2 a 24,3) | 21,8 (19,2 a 24,4) | +0,03 (+0,02 a +0,04) |
| Falhas da linha nova por dia | | 0,365 (0,325 a 0,405) | |

2,6 s para 1.000 dias nesta máquina (um processo). Hipóteses: Prolongamento da Azul até Anjou: traçado em obras (OSM) (https://montreal.ca/communiques-de-presse/les-femmes-et-les-communautes-seront-honorees-sur-le-futur-troncon-de-la-ligne-bleue); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; azul: o trecho novo falha com as taxas por km e as durações observadas da própria linha, e as viagens do horário seguem por ele; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; sem retorno parcial: um trecho parado para a linha inteira, inclusive o prolongamento.

### sem rota alternativa; com retorno parcial

| Medida | Rede atual | Com Prolongamento da Azul até Anjou | Com − atual (IC 95%, mesmo dia) |
|---|---|---|---|
| Caminho de sempre | Azul até Saint-Michel | Azul até Saint-Michel | |
| Tempo programado do caminho (min) | 14,0 | 14,0 | 0,0 |
| Disponibilidade da viagem | 99,490% (99,140% a 99,839%) | 99,490% (99,140% a 99,839%) | 0,000 pp (0,000 pp a 0,000 pp) |
| Tempo sem caminho (min por dia) | 6,11 (1,93 a 10,30) | 6,11 (1,93 a 10,30) | 0,00 (0,00 a 0,00) |
| Noves (−log₁₀ da indisponibilidade) | 2,29 (2,07 a 2,79) | 2,29 (2,07 a 2,79) | 0,00 |
| Tempo sem caminho com a linha nova ÷ rede atual | | | 1,000 (1,000 a 1,000) |
| Chance de chegar mais de 5 min atrasado | 0,50% (0,15% a 0,85%) | 0,50% (0,15% a 0,85%) | 0,00 pp (0,00 pp a 0,00 pp) |
| Atraso médio por viagem (min) | 2,82 (0,26 a 5,38) | 2,82 (0,26 a 5,38) | 0,00 (0,00 a 0,00) |
| Tempo médio da saída à chegada, com as falhas (min) | 21,8 (19,2 a 24,3) | 21,8 (19,2 a 24,3) | 0,00 (0,00 a 0,00) |
| Falhas da linha nova por dia | | 0,365 (0,325 a 0,405) | |

3,8 s para 1.000 dias nesta máquina (um processo). Hipóteses: Prolongamento da Azul até Anjou: traçado em obras (OSM) (https://montreal.ca/communiques-de-presse/les-femmes-et-les-communautes-seront-honorees-sur-le-futur-troncon-de-la-ligne-bleue); km = linha reta × 1.2; velocidade comercial dos trechos novos: 36 km/h; azul: o trecho novo falha com as taxas por km e as durações observadas da própria linha, e as viagens do horário seguem por ele; trens das linhas novas seguem o horário depois de cada interrupção, sem fila; causa comum: a linha nova é independente das linhas atuais; retorno parcial ligado (pontas de viagem do horário e os terminais antigos).

## Como ler

- A linha nova ajuda de dois jeitos: quando vira o caminho de sempre (menos linhas em série, viagem mais curta) e, com a rota alternativa, como caminho em paralelo.
- Sem a rota alternativa, a pessoa usa só o caminho de sempre: se ele passa pela linha nova, a viagem passa a depender das falhas dela.
- Um prolongamento que a viagem não usa não ajuda e, sem retorno parcial, piora: a falha no trecho novo para a linha inteira.
- A linha nova herda as taxas por km e as durações das linhas atuais: não é mais confiável que elas por hipótese.

Tempo de execução total: 1,6 min (um processo).
