# Fontes de falha e durações pela faixa oficial (spec 017)

Gerado por `pipeline/normaliza.py`, com a regra de duração de `pipeline/duracao.py` (D55) e as fontes da D56. Falhas técnicas de uma linha, de 2019-01-01 a 2026-06-30.

## Falhas por fonte e linha

| Fonte | verde | laranja | amarela | azul | Rede |
|---|---|---|---|---|---|
| `aux_stations` | 226 | 161 | 10 | 23 | 420 |
| `aux_trains_sintoma_fixo` | 480 | 804 | 96 | 154 | 1.534 |
| `aux_trains_sintoma_trem` | 146 | 370 | 97 | 82 | 695 |
| `mpm10` | 306 | 885 | 0 | 0 | 1.191 |
| `mr73` | 1.188 | 0 | 543 | 1.009 | 2.740 |
| `mr_outros` | 8 | 32 | 1 | 10 | 51 |
| `tcpe` | 57 | 54 | 13 | 18 | 142 |
| `voie_sintoma_fixo` | 330 | 430 | 92 | 117 | 969 |
| `voie_sintoma_trem` | 85 | 352 | 294 | 57 | 788 |

Causa comum (45 eventos): `aux_stations` 12, `aux_trains_sintoma_fixo` 7, `aux_trains_sintoma_trem` 1, `mpm10` 3, `mr73` 2, `tcpe` 11, `voie_sintoma_fixo` 8, `voie_sintoma_trem` 1.

## Divisão dos setores pelo sintoma

Um setor se divide em sintoma de trem (atribuído na hora a material rodante) e sintoma fixo quando cada parte tem 400 falhas ou mais na rede.

| Setor | Sintoma de trem | Sintoma fixo | Dividido |
|---|---|---|---|
| `voie` | 788 | 969 | sim |
| `aux_trains` | 695 | 1.534 | sim |
| `aux_stations` | 0 | 420 | não |
| `tcpe` | 7 | 135 | não |

## Frota: causa secundária contra "Type de matériel"

| Causa secundária | 73 | 10 | Non affecté |
|---|---|---|---|
| MR-73 | 2761 | 0 | 0 |
| MPM-10 | 0 | 1196 | 0 |
| Véhicules de travaux | 0 | 0 | 22 |
| Matériel roulant | 0 | 0 | 3 |

## Durações

Exceção: duração calculada fora da faixa oficial e da vizinha. Nela, vale a faixa (sorteio entre as durações coerentes da mesma faixa e família, semente pelo número do incidente). "Ponto médio" é a sensibilidade com o centro da faixa.

| Linha | Família | Falhas | Exceções | Minutos calculados | Minutos pela regra | Minutos com o ponto médio | Minutos das exceções (calculados → regra) |
|---|---|---|---|---|---|---|---|
| verde | MR | 1.502 | 22 | 6.645 | 6.358 | 6.372 | 390 → 103 |
| verde | EF | 1.324 | 19 | 6.697 | 5.338 | 5.354 | 1.479 → 120 |
| laranja | MR | 917 | 9 | 3.694 | 3.596 | 3.608 | 165 → 67 |
| laranja | EF | 2.171 | 21 | 9.025 | 7.654 | 7.672 | 1.472 → 101 |
| amarela | MR | 544 | 3 | 1.572 | 1.547 | 1.550 | 33 → 8 |
| amarela | EF | 602 | 7 | 2.093 | 1.976 | 1.969 | 217 → 100 |
| azul | MR | 1.019 | 8 | 4.371 | 4.258 | 4.262 | 166 → 53 |
| azul | EF | 451 | 11 | 9.874 | 2.677 | 2.690 | 7.207 → 10 |

Total: 43.971 minutos calculados, 33.404 pela regra, 33.476 com o ponto médio. As 100 exceções (1,2% das falhas) tinham 11.129 minutos calculados (25,3% do total) e ficam com 562 pela regra.

Retomada no dia civil seguinte: 27 falhas, 19 coerentes com a faixa (cruzam a meia-noite) e 8 exceções.

### Falhas de 300 minutos ou mais depois da regra

| Incidente | Linha | Fonte | Início | Minutos | Faixa oficial | Local |
|---|---|---|---|---|---|---|
| T04102403 | azul | `voie_sintoma_fixo` | 2024-10-04T05:30 | 1.170 | 30 min et plus | STATION ST-MICHEL |
| T12042406 | laranja | `voie_sintoma_fixo` | 2024-04-12T10:27 | 880 | 30 min et plus | INTER.JARRY/CREMAZIE |
| T03102413 | azul | `voie_sintoma_fixo` | 2024-10-03T19:19 | 341 | 30 min et plus | STATION ST-MICHEL |

## Gravidade (D58)

Classes pelos limites da STM: o indicador conta 5 min ou mais; aviso aos usuários acima de 10 min; ônibus substituto acima de 30 min.

| Fonte | menos_de_5 | 5_a_10 | 10_a_30 | 30_ou_mais | 5 min ou mais (pela regra) | 5 min ou mais (faixa oficial) |
|---|---|---|---|---|---|---|
| `aux_stations` | 396 | 4 | 9 | 11 | 24 | 24 |
| `aux_trains_sintoma_fixo` | 1.314 | 125 | 65 | 30 | 220 | 215 |
| `aux_trains_sintoma_trem` | 628 | 32 | 30 | 5 | 67 | 66 |
| `mpm10` | 929 | 188 | 52 | 22 | 262 | 256 |
| `mr73` | 1.949 | 571 | 200 | 20 | 791 | 776 |
| `mr_outros` | 36 | 8 | 6 | 1 | 15 | 16 |
| `tcpe` | 110 | 16 | 10 | 6 | 32 | 32 |
| `voie_sintoma_fixo` | 450 | 370 | 110 | 39 | 519 | 518 |
| `voie_sintoma_trem` | 735 | 29 | 19 | 5 | 53 | 53 |
