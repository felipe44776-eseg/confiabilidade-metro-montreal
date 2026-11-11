# Expansão da rede: que linha construir (spec 014)

Gerado por `app/relatorios/expansao.relatorio.ts` com o motor do simulador e o `parametros.json` real (sha256-scripts:489914bafbbe991e). Método de estados: 200.000 sorteios do estado de cada trecho (aberto ou bloqueado, pela taxa de falha e pela duração), semente 20261021, dia útil. A disponibilidade origem-destino é a fração dos pares de estações atuais com caminho, ponderada pela oferta de hoje; o ganho de cada candidata é pareado com a rede atual.

Rede atual: disponibilidade origem-destino 99,4248 (99,3970 a 99,4526)%; minutos de par interrompido por ano 2.515 (2.393 a 2.637).

## Validação: método de estados contra a camada diária (critério: até 0,1 p.p.)

| Linha | Camada diária (4.000 dias úteis) | Método de estados | Diferença (p.p.) |
|---|---|---|---|
| verde | 99,673% | 99,661% | -0,013 |
| laranja | 99,652% | 99,589% | -0,063 |
| amarela | 99,905% | 99,887% | -0,018 |
| azul | 99,818% | 99,793% | -0,025 |

## Candidatas oficiais e propostas, sem retorno parcial (trecho bloqueado para a linha inteira)

| Candidata | Status do traçado | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum compartilhada | Ganho por km (p.p./km) | Minutos de par evitados por ano |
|---|---|---|---|---|---|---|
| Linha Rosa (proposta de 2017) com prolongamento da Azul até Anjou | hipótese de traçado | 42,3 | 0,0361 (0,0295 a 0,0427) | 0,0348 (0,0282 a 0,0414) | 0,00085 | 158 (129 a 187) |
| Linha Rosa (proposta de 2017) | hipótese de traçado | 35,4 | 0,0165 (0,0156 a 0,0175) | 0,0162 (0,0152 a 0,0172) | 0,00047 | 72 (68 a 77) |
| Anel da Laranja (ARTM, 2019) | hipótese de traçado | 9,9 | 0,0002 (0,0001 a 0,0002) | 0,0001 (0,0001 a 0,0002) | 0,00002 | 1 (1 a 1) |
| Prolongamento da Amarela em Longueuil | hipótese de traçado | 7,2 | -0,0053 (-0,0060 a -0,0046) | -0,0053 (-0,0060 a -0,0046) | -0,00073 | -23 (-26 a -20) |
| Prolongamento da Laranja até Bois-Franc | hipótese de traçado | 3,0 | -0,0288 (-0,0359 a -0,0218) | -0,0288 (-0,0359 a -0,0218) | -0,00966 | -126 (-157 a -95) |
| Prolongamento da Azul até Anjou | em obras (OSM) | 6,9 | -0,0323 (-0,0362 a -0,0283) | -0,0323 (-0,0362 a -0,0283) | -0,00470 | -141 (-158 a -124) |

## Candidatas oficiais e propostas, com retorno parcial nas pontas de viagem (hipótese)

| Candidata | Status do traçado | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum compartilhada | Ganho por km (p.p./km) | Minutos de par evitados por ano |
|---|---|---|---|---|---|---|
| Linha Rosa (proposta de 2017) com prolongamento da Azul até Anjou | hipótese de traçado | 42,3 | 0,0381 (0,0348 a 0,0414) | 0,0368 (0,0334 a 0,0401) | 0,00090 | 167 (152 a 181) |
| Anel da Laranja (ARTM, 2019) | hipótese de traçado | 9,9 | 0,0211 (0,0191 a 0,0231) | 0,0211 (0,0191 a 0,0231) | 0,00214 | 92 (84 a 101) |
| Linha Rosa (proposta de 2017) | hipótese de traçado | 35,4 | 0,0084 (0,0077 a 0,0091) | 0,0081 (0,0074 a 0,0087) | 0,00024 | 37 (34 a 40) |
| Prolongamento da Azul até Anjou | em obras (OSM) | 6,9 | 0,0000 (0,0000 a 0,0000) | 0,0000 (0,0000 a 0,0000) | 0,00000 | 0 (0 a 0) |
| Prolongamento da Amarela em Longueuil | hipótese de traçado | 7,2 | 0,0000 (0,0000 a 0,0000) | 0,0000 (0,0000 a 0,0000) | 0,00000 | 0 (0 a 0) |
| Prolongamento da Laranja até Bois-Franc | hipótese de traçado | 3,0 | 0,0000 (0,0000 a 0,0000) | 0,0000 (0,0000 a 0,0000) | 0,00000 | 0 (0 a 0) |

## Busca exaustiva: ligações diretas entre estações atuais até 3 km em linha reta

298 ligações avaliadas com 50.000 sorteios cada (sem retorno parcial). As 15 melhores por ganho:

| Ligação | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum | Ganho por km |
|---|---|---|---|---|
| Atwater – Université De Montreal | 3,6 | 0,0629 (0,0541 a 0,0716) | 0,0627 (0,0540 a 0,0715) | 0,01765 |
| Monk – Place St-Henri | 3,6 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00327 |
| Jolicoeur – Vendôme | 3,1 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00380 |
| Jolicoeur – Place St-Henri | 2,8 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00419 |
| Verdun – Vendôme | 3,6 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00325 |
| Verdun – Place St-Henri | 2,8 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00421 |
| De L'Église – Place St-Henri | 2,7 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00424 |
| Lasalle – Vendôme | 3,5 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00328 |
| Lasalle – Place St-Henri | 2,1 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00557 |
| Lasalle – Georges-Vanier | 2,6 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00443 |
| Charlevoix – Place St-Henri | 1,6 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00726 |
| Charlevoix – Georges-Vanier | 1,5 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00751 |
| Charlevoix – Lucien-L'Allier | 2,2 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00531 |
| Charlevoix – Bonaventure | 2,6 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00443 |
| Atwater – Villa-Maria | 3,5 | 0,0116 (0,0104 a 0,0128) | 0,0114 (0,0102 a 0,0126) | 0,00334 |

As 15 melhores por ganho por km:

| Ligação | km (aprox.) | Ganho por km (p.p./km) | Ganho (p.p.) |
|---|---|---|---|
| Atwater – Université De Montreal | 3,6 | 0,01765 | 0,0629 (0,0541 a 0,0716) |
| Guy-Concordia – Lucien-L'Allier | 0,8 | 0,01529 | 0,0116 (0,0104 a 0,0128) |
| St-Laurent – Place D'Armes | 0,8 | 0,01466 | 0,0116 (0,0104 a 0,0128) |
| Peel – Bonaventure | 0,8 | 0,01446 | 0,0116 (0,0104 a 0,0128) |
| St-Laurent – Champs De Mars | 0,8 | 0,01395 | 0,0116 (0,0104 a 0,0128) |
| Mcgill – Square Victoria-Oaci | 0,9 | 0,01353 | 0,0116 (0,0104 a 0,0128) |
| Place Des Arts – Place D'Armes | 0,9 | 0,01349 | 0,0116 (0,0104 a 0,0128) |
| Peel – Lucien-L'Allier | 0,9 | 0,01329 | 0,0116 (0,0104 a 0,0128) |
| Atwater – Georges-Vanier | 0,9 | 0,01319 | 0,0116 (0,0104 a 0,0128) |
| Mcgill – Bonaventure | 0,9 | 0,01262 | 0,0116 (0,0104 a 0,0128) |
| Guy-Concordia – Georges-Vanier | 0,9 | 0,01242 | 0,0116 (0,0104 a 0,0128) |
| Place Des Arts – Square Victoria-Oaci | 1,0 | 0,01202 | 0,0116 (0,0104 a 0,0128) |
| St-Laurent – Sherbrooke | 1,1 | 0,01078 | 0,0116 (0,0104 a 0,0128) |
| Peel – Square Victoria-Oaci | 1,1 | 0,01071 | 0,0116 (0,0104 a 0,0128) |
| Place Des Arts – Champs De Mars | 1,1 | 0,01024 | 0,0116 (0,0104 a 0,0128) |

## Como ler

- Ganho = disponibilidade origem-destino com a candidata menos a da rede atual, nos pares de estações que já existem. Uma ligação vale pelos caminhos alternativos que cria.
- Um ramal (prolongamento que não fecha ciclo) não cria caminho alternativo e acrescenta trechos que podem falhar. Sem retorno parcial, uma falha no prolongamento para a linha inteira, e por isso o ganho pode ser negativo. A cobertura de bairros novos não entra: não há dado de passageiros.
- "Com causa comum compartilhada": a candidata divide alimentação e controle com as linhas em que encosta e para junto nos eventos de causa comum.
- km: linha reta × fator de traçado (1,2, hipótese). A busca exaustiva filtra pela distância em linha reta (até 3 km), por isso aparecem ligações com mais de 3 km de via.
- Pesos: cada par de estações pesa pela oferta das linhas que o servem. Como quase todas as viagens percorrem a linha inteira, as estações de uma mesma linha pesam igual, e ligações que unem as mesmas duas linhas dão o mesmo ganho.
- A ligação Atwater (Verde) – Université-de-Montréal (Azul) lidera porque hoje a Azul só se liga ao resto da rede pela Laranja (Snowdon e Jean-Talon): quando a Laranja para, a Azul fica isolada. Uma ligação direta da Azul com outra linha remove esse ponto único de falha.
- Hipóteses: traçado aproximado (linha reta × fator de traçado), velocidade comercial, taxas de falha por km herdadas da linha ou da média da rede. Ver a coluna de hipóteses em `dados/derivados/simulador/expansao.json`.

