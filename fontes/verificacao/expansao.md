# Expansão da rede: que linha construir (spec 014)

Gerado por `app/relatorios/expansao.relatorio.ts` com o motor do simulador e o `parametros.json` real (sha256-scripts:e05a311efcb01915). Método de estados: 200.000 sorteios do estado de cada trecho (aberto ou bloqueado, pela taxa de falha e pela duração), semente 20261021, dia útil. A disponibilidade origem-destino é a fração dos pares de estações atuais com caminho, ponderada pela oferta de hoje; o ganho de cada candidata é pareado com a rede atual.

Rede atual: disponibilidade origem-destino 99,2360 (99,2029 a 99,2692)%; minutos de par interrompido por ano 3.341 (3.196 a 3.485).

## Validação: método de estados contra a camada diária (critério: até 0,1 p.p.)

| Linha | Camada diária (4.000 dias úteis) | Método de estados | Diferença (p.p.) |
|---|---|---|---|
| verde | 99,504% | 99,524% | 0,020 |
| laranja | 99,545% | 99,536% | -0,009 |
| amarela | 99,892% | 99,903% | 0,010 |
| azul | 99,635% | 99,540% | -0,095 |

## Candidatas oficiais e propostas, sem retorno parcial (trecho bloqueado para a linha inteira)

| Candidata | Status do traçado | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum compartilhada | Ganho por km (p.p./km) | Minutos de par evitados por ano |
|---|---|---|---|---|---|---|
| Linha Rosa (proposta de 2017) | hipótese de traçado | 35,4 | 0,0208 (0,0197 a 0,0219) | 0,0206 (0,0195 a 0,0217) | 0,00059 | 91 (86 a 96) |
| Linha Rosa (proposta de 2017) com prolongamento da Azul até Anjou | hipótese de traçado | 42,3 | 0,0028 (-0,0059 a 0,0116) | 0,0019 (-0,0069 a 0,0107) | 0,00007 | 12 (-26 a 51) |
| Anel da Laranja (ARTM, 2019) | hipótese de traçado | 9,9 | 0,0002 (0,0002 a 0,0002) | 0,0002 (0,0002 a 0,0002) | 0,00002 | 1 (1 a 1) |
| Prolongamento da Amarela em Longueuil | hipótese de traçado | 7,2 | -0,0054 (-0,0062 a -0,0047) | -0,0054 (-0,0062 a -0,0047) | -0,00075 | -24 (-27 a -20) |
| Prolongamento da Laranja até Bois-Franc | hipótese de traçado | 3,0 | -0,0347 (-0,0420 a -0,0273) | -0,0347 (-0,0420 a -0,0273) | -0,01162 | -152 (-184 a -120) |
| Prolongamento da Azul até Anjou | em obras (OSM) | 6,9 | -0,0753 (-0,0811 a -0,0695) | -0,0753 (-0,0811 a -0,0695) | -0,01098 | -329 (-355 a -304) |

## Candidatas oficiais e propostas, com retorno parcial nas pontas de viagem (hipótese)

| Candidata | Status do traçado | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum compartilhada | Ganho por km (p.p./km) | Minutos de par evitados por ano |
|---|---|---|---|---|---|---|
| Linha Rosa (proposta de 2017) com prolongamento da Azul até Anjou | hipótese de traçado | 42,3 | 0,0528 (0,0496 a 0,0559) | 0,0519 (0,0487 a 0,0551) | 0,00125 | 231 (217 a 244) |
| Anel da Laranja (ARTM, 2019) | hipótese de traçado | 9,9 | 0,0186 (0,0162 a 0,0210) | 0,0186 (0,0162 a 0,0210) | 0,00188 | 81 (71 a 92) |
| Linha Rosa (proposta de 2017) | hipótese de traçado | 35,4 | 0,0112 (0,0105 a 0,0120) | 0,0110 (0,0103 a 0,0118) | 0,00032 | 49 (46 a 52) |
| Prolongamento da Azul até Anjou | em obras (OSM) | 6,9 | 0,0000 (0,0000 a 0,0000) | 0,0000 (0,0000 a 0,0000) | 0,00000 | 0 (0 a 0) |
| Prolongamento da Amarela em Longueuil | hipótese de traçado | 7,2 | 0,0000 (0,0000 a 0,0000) | 0,0000 (0,0000 a 0,0000) | 0,00000 | 0 (0 a 0) |
| Prolongamento da Laranja até Bois-Franc | hipótese de traçado | 3,0 | 0,0000 (0,0000 a 0,0000) | 0,0000 (0,0000 a 0,0000) | 0,00000 | 0 (0 a 0) |

## Busca exaustiva: ligações diretas entre estações atuais até 3 km em linha reta

298 ligações avaliadas com 50.000 sorteios cada (sem retorno parcial). As 15 melhores por ganho:

| Ligação | km (aprox.) | Ganho de disponibilidade OD, p.p. (IC 95%) | Com causa comum | Ganho por km |
|---|---|---|---|---|
| Atwater – Université De Montreal | 3,6 | 0,0850 (0,0771 a 0,0930) | 0,0849 (0,0769 a 0,0929) | 0,02387 |
| Monk – Vendôme | 3,2 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00482 |
| Monk – Place St-Henri | 3,6 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00432 |
| Verdun – Vendôme | 3,6 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00430 |
| Lasalle – Vendôme | 3,5 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00434 |
| Lasalle – Place St-Henri | 2,1 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00736 |
| Charlevoix – Vendôme | 3,3 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00468 |
| Charlevoix – Place St-Henri | 1,6 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00959 |
| Charlevoix – Georges-Vanier | 1,5 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00992 |
| Charlevoix – Lucien-L'Allier | 2,2 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00702 |
| Charlevoix – Square Victoria-Oaci | 3,2 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00484 |
| Atwater – Villa-Maria | 3,5 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00442 |
| Atwater – Place St-Henri | 1,7 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,00908 |
| Atwater – Georges-Vanier | 0,9 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,01743 |
| Atwater – Lucien-L'Allier | 1,5 | 0,0154 (0,0138 a 0,0169) | 0,0153 (0,0137 a 0,0168) | 0,01024 |

As 15 melhores por ganho por km:

| Ligação | km (aprox.) | Ganho por km (p.p./km) | Ganho (p.p.) |
|---|---|---|---|
| Atwater – Université De Montreal | 3,6 | 0,02387 | 0,0850 (0,0771 a 0,0930) |
| Guy-Concordia – Lucien-L'Allier | 0,8 | 0,02020 | 0,0154 (0,0138 a 0,0169) |
| St-Laurent – Place D'Armes | 0,8 | 0,01937 | 0,0154 (0,0138 a 0,0169) |
| Peel – Bonaventure | 0,8 | 0,01911 | 0,0154 (0,0138 a 0,0169) |
| St-Laurent – Champs De Mars | 0,8 | 0,01843 | 0,0154 (0,0138 a 0,0169) |
| Mcgill – Square Victoria-Oaci | 0,9 | 0,01788 | 0,0154 (0,0138 a 0,0169) |
| Place Des Arts – Place D'Armes | 0,9 | 0,01783 | 0,0154 (0,0138 a 0,0169) |
| Peel – Lucien-L'Allier | 0,9 | 0,01756 | 0,0154 (0,0138 a 0,0169) |
| Atwater – Georges-Vanier | 0,9 | 0,01743 | 0,0154 (0,0138 a 0,0169) |
| Mcgill – Bonaventure | 0,9 | 0,01667 | 0,0154 (0,0138 a 0,0169) |
| Guy-Concordia – Georges-Vanier | 0,9 | 0,01642 | 0,0154 (0,0138 a 0,0169) |
| Place Des Arts – Square Victoria-Oaci | 1,0 | 0,01588 | 0,0154 (0,0138 a 0,0169) |
| St-Laurent – Sherbrooke | 1,1 | 0,01425 | 0,0154 (0,0138 a 0,0169) |
| Peel – Square Victoria-Oaci | 1,1 | 0,01415 | 0,0154 (0,0138 a 0,0169) |
| Place Des Arts – Champs De Mars | 1,1 | 0,01353 | 0,0154 (0,0138 a 0,0169) |

## Como ler

- Ganho = disponibilidade origem-destino com a candidata menos a da rede atual, nos pares de estações que já existem. Uma ligação vale pelos caminhos alternativos que cria.
- Um ramal (prolongamento que não fecha ciclo) não cria caminho alternativo e acrescenta trechos que podem falhar. Sem retorno parcial, uma falha no prolongamento para a linha inteira, e por isso o ganho pode ser negativo. A cobertura de bairros novos não entra: não há dado de passageiros.
- "Com causa comum compartilhada": a candidata divide alimentação e controle com as linhas em que encosta e para junto nos eventos de causa comum.
- km: linha reta × fator de traçado (1,2, hipótese). A busca exaustiva filtra pela distância em linha reta (até 3 km), por isso aparecem ligações com mais de 3 km de via.
- Pesos: cada par de estações pesa pela oferta das linhas que o servem. Como quase todas as viagens percorrem a linha inteira, as estações de uma mesma linha pesam igual, e ligações que unem as mesmas duas linhas dão o mesmo ganho.
- A ligação Atwater (Verde) – Université-de-Montréal (Azul) lidera porque hoje a Azul só se liga ao resto da rede pela Laranja (Snowdon e Jean-Talon): quando a Laranja para, a Azul fica isolada. Uma ligação direta da Azul com outra linha remove esse ponto único de falha.
- Hipóteses: traçado aproximado (linha reta × fator de traçado), velocidade comercial, taxas de falha por km herdadas da linha ou da média da rede. Ver a coluna de hipóteses em `dados/derivados/simulador/expansao.json`.

