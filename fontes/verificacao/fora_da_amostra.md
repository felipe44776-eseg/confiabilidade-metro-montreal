# Um ano de fora: modelo da v1.1.0 contra o modelo por fonte (spec 018)

Gerado por `pipeline/fora_da_amostra.py`. Cada ano de 2019 a 2025 é tirado do ajuste e previsto com a exposição, o clima e o calendário observados; o efeito do ano ausente é a média dos anos do treino. Erro = log(observado ÷ esperado) por linha no ano tirado. Medido fora da amostra, para não premiar o modelo com mais parâmetros.

| Família | Raiz do erro quadrático, v1.1.0 | Raiz do erro quadrático, por fonte | Casos |
|---|---|---|---|
| MR | 0,308 | 0,247 | 28 |
| EF | 0,646 | 0,589 | 28 |

## Por linha e ano (observado ÷ esperado)

| Ano | Linha | Família | Observado | v1.1.0 | Por fonte |
|---|---|---|---|---|---|
| 2019 | verde | MR | 373 | 2,044 | 0,941 |
| 2019 | verde | EF | 165 | 0,906 | 0,964 |
| 2019 | laranja | MR | 159 | 1,282 | 1,295 |
| 2019 | laranja | EF | 290 | 0,975 | 1,109 |
| 2019 | amarela | MR | 135 | 2,180 | 2,169 |
| 2019 | amarela | EF | 51 | 0,656 | 0,942 |
| 2019 | azul | MR | 166 | 1,180 | 1,176 |
| 2019 | azul | EF | 66 | 1,121 | 1,224 |
| 2020 | verde | MR | 277 | 1,490 | 0,870 |
| 2020 | verde | EF | 107 | 0,586 | 0,629 |
| 2020 | laranja | MR | 145 | 1,236 | 1,234 |
| 2020 | laranja | EF | 231 | 0,798 | 0,916 |
| 2020 | amarela | MR | 56 | 0,815 | 0,801 |
| 2020 | amarela | EF | 18 | 0,234 | 0,341 |
| 2020 | azul | MR | 136 | 0,998 | 0,975 |
| 2020 | azul | EF | 31 | 0,507 | 0,559 |
| 2021 | verde | MR | 145 | 0,721 | 0,848 |
| 2021 | verde | EF | 194 | 1,156 | 1,245 |
| 2021 | laranja | MR | 132 | 1,126 | 1,130 |
| 2021 | laranja | EF | 222 | 0,757 | 0,874 |
| 2021 | amarela | MR | 43 | 0,626 | 0,613 |
| 2021 | amarela | EF | 43 | 0,589 | 0,852 |
| 2021 | azul | MR | 111 | 0,821 | 0,799 |
| 2021 | azul | EF | 42 | 0,716 | 0,790 |
| 2022 | verde | MR | 182 | 0,938 | 1,142 |
| 2022 | verde | EF | 156 | 0,904 | 0,975 |
| 2022 | laranja | MR | 80 | 0,645 | 0,642 |
| 2022 | laranja | EF | 303 | 1,093 | 1,265 |
| 2022 | amarela | MR | 76 | 1,112 | 1,083 |
| 2022 | amarela | EF | 53 | 0,697 | 1,052 |
| 2022 | azul | MR | 151 | 1,187 | 1,147 |
| 2022 | azul | EF | 53 | 0,945 | 1,052 |
| 2023 | verde | MR | 157 | 0,869 | 0,889 |
| 2023 | verde | EF | 209 | 1,387 | 1,487 |
| 2023 | laranja | MR | 120 | 1,055 | 1,059 |
| 2023 | laranja | EF | 292 | 1,080 | 1,240 |
| 2023 | amarela | MR | 66 | 0,726 | 0,711 |
| 2023 | amarela | EF | 63 | 0,646 | 0,953 |
| 2023 | azul | MR | 137 | 1,085 | 1,055 |
| 2023 | azul | EF | 52 | 0,945 | 1,044 |
| 2024 | verde | MR | 132 | 0,672 | 1,052 |
| 2024 | verde | EF | 209 | 1,267 | 1,347 |
| 2024 | laranja | MR | 89 | 0,741 | 0,734 |
| 2024 | laranja | EF | 400 | 1,504 | 1,654 |
| 2024 | amarela | MR | 75 | 1,073 | 1,044 |
| 2024 | amarela | EF | 328 | 7,928 | 9,208 |
| 2024 | azul | MR | 116 | 0,897 | 0,868 |
| 2024 | azul | EF | 128 | 2,787 | 2,969 |
| 2025 | verde | MR | 135 | 0,690 | 1,036 |
| 2025 | verde | EF | 153 | 0,926 | 0,996 |
| 2025 | laranja | MR | 125 | 1,096 | 1,101 |
| 2025 | laranja | EF | 263 | 0,974 | 1,125 |
| 2025 | amarela | MR | 60 | 0,866 | 0,846 |
| 2025 | amarela | EF | 19 | 0,244 | 0,367 |
| 2025 | azul | MR | 112 | 0,861 | 0,836 |
| 2025 | azul | EF | 41 | 0,740 | 0,826 |
