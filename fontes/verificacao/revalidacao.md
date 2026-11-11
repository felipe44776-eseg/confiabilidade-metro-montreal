# Revalidação do simulador contra o histórico (spec 020)

Gerado por `app/relatorios/revalidacao.relatorio.ts`: cada um dos 364 dias de 2025 simulado 6 vezes (semente 20261110), sem políticas, com o tipo de dia, a estação, o clima e os eventos de cada hora daquele dia (painel do modelo, spec 005) e a taxa-base do ano 2025. As greves não entram: o simulador roda o serviço normal nesses dias. Parâmetros revistos: `sha256-scripts:489914bafbbe991e` (contrato v2); v1.1.0: `sha256-scripts:70cf9c002aa2ba0a`. Observado: o ano de 2025 (o ano-base dos parâmetros), com IC 95% por blocos semanais (1.000 reamostras); a média de 2019 a 2025 fica como contexto, porque a mistura de frotas mudou (a Verde tinha 61% de MR-73 em 2019 e 15% em 2025). Tolerância declarada antes: até 15% da média observada (a da spec 009). O IC do observado aparece para dar a escala da variação de um ano.

**Critério da spec 020 (dentro do IC 95% do observado em 2025):** revisto 25 de 28; v1.1.0 21 de 28. **A até 15% do observado (critério da spec 009):** revisto 12 de 28.

| Linha | Medida por ano | Observado em 2025 (IC 95%) | Média 2019–2025 | Revisto | v1.1.0 | Revisto no IC | v1.1.0 no IC | Revisto a até 15% |
|---|---|---|---|---|---|---|---|---|
| verde | falhas_MR | 138,0 (101,0–179,0) | 201,1 | 128,8 | 177,7 | sim | sim | sim |
| verde | falhas_EF | 162,0 (126,0–200,0) | 177,0 | 141,2 | 167,0 | sim | sim | sim |
| verde | falhas_CC | 10,0 (3,0–18,0) | 4,0 | 4,5 | 4,5 | sim | sim | não |
| verde | minutos_MR | 585,0 (420,0–746,0) | 849,4 | 541,5 | 793,5 | sim | não | sim |
| verde | minutos_EF | 630,0 (311,0–1.022,0) | 739,1 | 592,2 | 775,8 | sim | sim | sim |
| verde | minutos_CC | 150,0 (12,0–368,0) | 97,6 | 75,4 | 75,4 | sim | sim | não |
| verde | falhas_5_ou_mais | 81,0 (61,0–101,0) | 103,4 | 70,5 | 99,0 | sim | sim | sim |
| laranja | falhas_MR | 127,0 (96,0–164,0) | 121,7 | 122,3 | 104,8 | sim | sim | sim |
| laranja | falhas_EF | 279,0 (231,0–333,0) | 292,6 | 232,7 | 263,0 | sim | sim | não |
| laranja | falhas_CC | 11,0 (4,0–19,0) | 5,6 | 6,3 | 6,3 | sim | sim | não |
| laranja | minutos_MR | 269,0 (148,0–449,0) | 493,1 | 435,8 | 418,5 | sim | sim | não |
| laranja | minutos_EF | 742,0 (461,0–1.077,0) | 987,3 | 643,7 | 1.027,1 | sim | sim | sim |
| laranja | minutos_CC | 150,0 (12,0–368,0) | 132,1 | 105,9 | 106,4 | sim | sim | não |
| laranja | falhas_5_ou_mais | 61,0 (48,0–75,0) | 85,6 | 74,3 | 79,7 | sim | não | não |
| amarela | falhas_MR | 60,0 (43,0–76,0) | 73,1 | 59,3 | 52,5 | sim | sim | sim |
| amarela | falhas_EF | 19,0 (9,0–32,0) | 82,6 | 40,5 | 59,8 | não | não | não |
| amarela | falhas_CC | 4,0 (0,0–10,0) | 2,3 | 2,7 | 2,7 | sim | sim | não |
| amarela | minutos_MR | 252,0 (160,0–352,0) | 209,1 | 189,6 | 124,5 | sim | não | não |
| amarela | minutos_EF | 44,0 (8,0–98,0) | 238,3 | 143,3 | 178,5 | não | não | não |
| amarela | minutos_CC | 11,0 (0,0–26,0) | 56,1 | 19,0 | 19,0 | sim | sim | não |
| amarela | falhas_5_ou_mais | 25,0 (15,0–36,0) | 33,9 | 23,7 | 22,2 | sim | sim | sim |
| azul | falhas_MR | 113,0 (82,0–147,0) | 133,1 | 135,8 | 118,3 | sim | sim | não |
| azul | falhas_EF | 42,0 (29,0–57,0) | 61,0 | 44,8 | 53,0 | sim | sim | sim |
| azul | falhas_CC | 2,0 (0,0–5,0) | 2,7 | 3,2 | 3,2 | sim | sim | não |
| azul | minutos_MR | 517,0 (345,0–709,0) | 554,7 | 541,0 | 521,9 | sim | sim | sim |
| azul | minutos_EF | 141,0 (55,0–266,0) | 351,0 | 98,0 | 908,8 | sim | não | não |
| azul | minutos_CC | 2,0 (0,0–6,0) | 59,0 | 48,2 | 48,7 | não | não | não |
| azul | falhas_5_ou_mais | 48,0 (32,0–66,0) | 50,9 | 50,5 | 47,5 | sim | sim | sim |

## Dispersão das falhas por dia (dias úteis)

Variância ÷ média das falhas por dia de cada linha × família. Poisson dá 1; o histórico tem agrupamento (spec 006). Somar fontes independentes tende a dar dispersão menor que a observada. Critério da spec 019: a simulada dentro do IC 95% da observada, por blocos semanais (1.000 reamostras das semanas de dias úteis de 2025); abaixo dele, o critério pede um fator diário comum por família. A dispersão por mês (12 meses num ano) não foi calculada.

**Revisto dentro do IC:** 9 de 12 (abaixo: verde EF). **v1.1.0 dentro do IC:** 11 de 12.

| Linha | Família | Observado (dias úteis de 2025; IC 95%) | Revisto | v1.1.0 | Revisto no IC |
|---|---|---|---|---|---|
| verde | MR | 1,28 (0,93–1,73) | 1,25 | 1,25 | sim |
| verde | EF | 1,31 (1,14–1,47) | 1,06 | 1,30 | não, abaixo |
| verde | CC | 1,26 (0,97–1,66) | 0,99 | 0,99 | sim |
| laranja | MR | 1,44 (1,17–1,70) | 1,30 | 1,30 | sim |
| laranja | EF | 1,56 (1,22–1,94) | 1,34 | 1,63 | sim |
| laranja | CC | 1,48 (0,98–1,86) | 0,98 | 0,98 | sim |
| amarela | MR | 1,11 (0,93–1,29) | 1,36 | 1,16 | não, acima |
| amarela | EF | 1,08 (0,93–1,35) | 1,64 | 2,06 | não, acima |
| amarela | CC | 0,99 (0,98–1,00) | 0,99 | 0,99 | sim |
| azul | MR | 1,28 (1,01–1,60) | 1,29 | 1,37 | sim |
| azul | EF | 1,11 (0,88–1,42) | 1,15 | 1,27 | sim |
| azul | CC | 1,00 (0,98–1,00) | 0,99 | 0,99 | sim |

## Indicador de 5 minutos ou mais por milhão de km-carro

Só falhas técnicas e causa comum (o indicador da STM conta todas as causas, inclusive clientela). Km-carro de 2025: 83,8 milhões.

- Simulado (revisto): 2,61 por milhão de km-carro (219 por ano).
- Dados abertos de 2025, faixa oficial: 2,46 (206 falhas técnicas de uma linha).
- Publicado pela STM, todas as causas: 2019: 10,60; 2020: 9,20; 2021: 9,40; 2022: 10,40; 2023: 13,20; 2024: 13,00; 2025: 11,66.

### Por ano: dados abertos contra o publicado

Incidentes de 5 min ou mais pela faixa oficial ("Incident en minutes") do CSV de incidentes, por ano civil, divididos pelo km-carro do km real no mesmo ano. A STM não publica a regra de contagem do indicador; a diferença que sobra fica declarada como exceção da spec 020 e é uma das perguntas do pedido à STM.

| Ano | Km-carro (milhões) | Dados abertos, todas as causas | Dados abertos, só técnicas | Publicado pela STM | Dados abertos ÷ publicado |
|---|---|---|---|---|---|
| 2019 | 90,9 | 9,09 | 3,16 | 10,60 | 0,857 |
| 2020 | 87,0 | 8,16 | 2,79 | 9,20 | 0,887 |
| 2021 | 85,4 | 7,99 | 3,02 | 9,40 | 0,850 |
| 2022 | 85,8 | 8,89 | 3,02 | 10,40 | 0,855 |
| 2023 | 83,3 | 11,34 | 3,49 | 13,20 | 0,859 |
| 2024 | 86,1 | 11,10 | 3,63 | 13,00 | 0,854 |
| 2025 | 83,8 | 9,89 | 2,51 | 11,66 | 0,848 |

Razão entre os dados abertos de todas as causas e o publicado: de 0,848 a 0,887. As falhas técnicas são de 25% a 38% dos incidentes de 5 min ou mais.
