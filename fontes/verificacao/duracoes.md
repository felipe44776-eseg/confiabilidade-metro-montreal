# Duração das interrupções: amostra observada contra lognormal

Gerado por `pipeline/parametros.py`. Média das durações positivas observadas contra a média exp(μ + σ²/2) da lognormal ajustada às mesmas durações (`fontes/verificacao/distribuicoes.md`). Razão acima de 1: a lognormal subestima a média, por isso o simulador sorteia da amostra observada.

| Linha e causa | Durações positivas | Média observada (min) | Média da lognormal (min) | Razão |
|---|---|---|---|---|
| verde · MR | 1139 | 5,83 | 5,48 | 1,064 |
| verde · EF | 555 | 12,07 | 9,56 | 1,262 |
| laranja · MR | 531 | 6,96 | 5,67 | 1,228 |
| laranja · EF | 786 | 11,48 | 8,89 | 1,291 |
| amarela · MR | 328 | 4,79 | 4,56 | 1,052 |
| amarela · EF | 200 | 10,46 | 9,83 | 1,065 |
| azul · MR | 816 | 5,36 | 5,12 | 1,046 |
| azul · EF | 190 | 51,97 | 15,36 | 3,384 |
