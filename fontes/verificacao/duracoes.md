# Duração das interrupções: amostra observada contra lognormal

Gerado por `pipeline/parametros.py`. Média das durações positivas observadas contra a média exp(μ + σ²/2) da lognormal ajustada às mesmas durações (`fontes/verificacao/distribuicoes.md`). Razão acima de 1: a lognormal subestima a média, por isso o simulador sorteia da amostra observada.

| Linha e causa | Durações positivas | Média observada (min) | Média da lognormal (min) | Razão |
|---|---|---|---|---|
| verde · MR | 1138 | 5,59 | 5,26 | 1,062 |
| verde · EF | 551 | 9,69 | 8,26 | 1,173 |
| laranja · MR | 531 | 6,77 | 5,49 | 1,234 |
| laranja · EF | 779 | 9,82 | 7,90 | 1,244 |
| amarela · MR | 327 | 4,73 | 4,49 | 1,053 |
| amarela · EF | 200 | 9,88 | 9,39 | 1,052 |
| azul · MR | 816 | 5,22 | 5,00 | 1,043 |
| azul · EF | 181 | 14,79 | 7,25 | 2,039 |
