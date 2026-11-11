# Taxa de falha por fonte (spec 018)

Gerado por `pipeline/modelo_taxa.py`. Mesmo painel horário, deslocamento e bootstrap em blocos semanais da spec 005 (B = 200, semente 20261021, as mesmas semanas para todas as fontes). Exposição medida em todo o período (km real de 2019-01 a 2026-09). Fontes da spec 017; modelo próprio com 400 falhas ou mais; abaixo, reduzido (linha e faixa do dia; abaixo de 100, só a linha), com o clima, o tipo de dia, os eventos e o ano da família como deslocamento, réplica a réplica.

## Material rodante: as duas frotas num modelo só

Uma linha do painel por linha × dia × hora × frota, com deslocamento log(trens-hora × parcela da frota no km do dia). Covariáveis da spec 005 mais a frota e a tendência anual própria do MR-73. A Verde é a única linha com as duas frotas: a razão entre elas sai de lá.

- Binomial negativa contra Poisson: AIC 38.689,4 contra 38.546,0; α = 2,034; p = 8,7e-34.
- A linha ainda pesa dentro de cada frota? Razão de verossimilhança 131,5 com 3 graus de liberdade, p = 2,5e-28.
- Falhas sem exposição da frota no dia nem no mês (ficam fora): {'mpm10': 0, 'mr73': 0}.

| Ano | MR-73 ÷ MPM-10 (por trem-hora da frota, IC 95%) |
|---|---|
| 2019 | 7,09 (5,70–9,03) |
| 2020 | 6,06 (4,75–8,02) |
| 2021 | 6,50 (5,06–8,64) |
| 2022 | 15,54 (12,19–19,28) |
| 2023 | 9,33 (7,28–11,87) |
| 2024 | 14,41 (10,86–19,96) |
| 2025 | 8,89 (6,61–11,23) |
| 2026 | 8,73 (5,82–12,26) |

| Linha × frota | Falhas por trem-hora da frota em 2025, condições de referência (IC 95%) | Parcela da frota em 2025 |
|---|---|---|
| verde · MPM-10 | 0,000520 (0,000366–0,000691) | 0,853 |
| laranja · MPM-10 | 0,000784 (0,000576–0,001046) | 0,996 |
| verde · MR-73 | 0,004620 (0,003565–0,005857) | 0,147 |
| amarela · MR-73 | 0,004381 (0,003322–0,005517) | 1,000 |
| azul · MR-73 | 0,003058 (0,002371–0,003824) | 0,995 |

## Modelo de cada fonte

| Fonte | Família | Falhas | Modelo | α | Poisson contra binomial negativa (AIC) |
|---|---|---|---|---|---|
| `mpm10` | MR | 1.190 | empilhado por frota (MPM-10) | 2,034 | ver acima |
| `mr73` | MR | 2.736 | empilhado por frota (MR-73) | 2,034 | ver acima |
| `aux_stations` | EF | 388 | reduzido: linha e faixa; clima, dia, eventos e ano da família EF | 0,227 | 5.349,3 contra 5.351,2 |
| `aux_trains_sintoma_fixo` | EF | 1.500 | próprio | 6,922 | 17.037,2 contra 16.865,0 |
| `aux_trains_sintoma_trem` | EF | 694 | próprio | 19,990 | 8.985,6 contra 8.445,3 |
| `mr_outros` | MR | 40 | reduzido: linha; clima, dia, eventos e ano da família MR | 0,010 | 774,8 contra 776,8 |
| `tcpe` | EF | 132 | reduzido: linha e faixa; clima, dia, eventos e ano da família EF | 0,010 | 2.160,4 contra 2.162,4 |
| `voie_sintoma_fixo` | EF | 924 | próprio | 2,849 | 11.543,4 contra 11.533,3 |
| `voie_sintoma_trem` | EF | 785 | próprio | 15,701 | 8.233,1 contra 7.691,9 |

## De onde vem cada efeito

Multiplicador (IC 95%) nas fontes com modelo próprio e no material rodante empilhado; em negrito quando o intervalo não contém 1. As fontes com modelo reduzido herdam esses fatores da família.

| Fator | Família MR | Família EF | MR empilhado | `aux_trains_sintoma_fixo` | `aux_trains_sintoma_trem` | `voie_sintoma_fixo` | `voie_sintoma_trem` |
|---|---|---|---|---|---|---|---|
| Abertura (5 a 6 h) | **2,64 (2,36–2,92)** | **3,59 (3,14–4,03)** | **2,64 (2,37–2,91)** | **3,13 (2,60–3,69)** | **3,80 (2,96–4,78)** | **3,43 (2,53–4,43)** | **3,74 (2,56–5,06)** |
| Pico da manhã | **1,35 (1,23–1,48)** | **1,26 (1,14–1,37)** | **1,37 (1,24–1,50)** | **1,29 (1,10–1,49)** | **1,46 (1,09–1,88)** | 0,92 (0,74–1,10) | **1,62 (1,23–2,09)** |
| Pico da tarde | **0,85 (0,77–0,93)** | **0,61 (0,55–0,68)** | **0,86 (0,78–0,93)** | **0,61 (0,50–0,75)** | 0,91 (0,70–1,16) | **0,39 (0,30–0,48)** | 0,89 (0,67–1,20) |
| 25 °C ou mais | 1,07 (0,83–1,34) | **1,84 (1,29–2,33)** | 1,08 (0,84–1,36) | **1,39 (1,04–1,90)** | 1,30 (0,70–1,99) | **2,23 (1,17–3,52)** | **2,70 (1,17–5,80)** |
| Abaixo de −15 °C | 0,94 (0,72–1,26) | 1,07 (0,73–1,59) | 0,96 (0,74–1,28) | 1,33 (0,77–2,21) | 0,64 (0,25–1,26) | 0,93 (0,43–1,59) | 1,11 (0,00–3,35) |
| Mais de 10 cm de neve no solo | **1,37 (1,09–1,67)** | **1,37 (1,09–1,69)** | **1,31 (1,02–1,62)** | 1,30 (1,00–1,80) | 1,56 (0,86–3,07) | 1,44 (0,93–2,20) | 1,45 (0,41–4,38) |
| Neve | 0,87 (0,75–1,02) | **0,75 (0,62–0,91)** | 0,88 (0,75–1,02) | **0,66 (0,51–0,87)** | 1,09 (0,66–1,77) | 0,73 (0,53–1,02) | 0,84 (0,25–1,55) |
| Jogo do Canadiens | **1,26 (1,01–1,59)** | 0,91 (0,65–1,15) | 1,25 (0,98–1,59) | 1,07 (0,60–1,55) | 0,56 (0,18–1,19) | 1,03 (0,54–1,61) | 0,95 (0,45–1,79) |

## Faixa do dia nas fontes com modelo reduzido

- `aux_stations` (388 falhas): abertura 2,05 (1,45–2,94).
- `mr_outros` (40 falhas): só a linha.
- `tcpe` (132 falhas): abertura 8,53 (5,39–13,67).
