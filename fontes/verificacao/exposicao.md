# Exposição (spec 004)

Gerado por `pipeline/exposicao.py` a partir do GTFS da STM (moldes de dia útil, sábado e domingo) e do km real (2019-01 a 2023-09).

## Trens em viagem às 08:00 de um dia útil

| Linha | GTFS | Esperado | Dentro da tolerância de 1 trem |
|---|---|---|---|
| verde | 26 | 26 | sim |
| laranja | 31 | 32 | sim |
| amarela | 2 | 2 | sim |
| azul | 9 | 9 | sim |

## Erro mensal do km estimado contra o km real

220 meses-linha comparados; 4 acima de 10% (98.2% dentro); erro absoluto mediano de 0.44%.

| Linha | Mês | Erro |
|---|---|---|
| verde | 2020-04 | +17.2% |
| azul | 2020-04 | +15.9% |
| laranja | 2020-04 | +15.7% |
| amarela | 2019-06 | -10.8% |

Exceção registrada: abril de 2020 (primeiro mês da pandemia, com oferta cortada no meio do mês) nas três linhas grandes e junho de 2019 na Amarela. O critério não foi afrouxado.

## Km real por frota

| Frota | Registros | km-carro |
|---|---|---|
| MPM-10 | 342.261 | 294.258.032,7 |
| MR-63 | 22 | 15,7 |
| MR-73 | 217.266 | 117.373.473,9 |

Total: 411,63 milhões de km-carro. O total menos MR-73 e MPM-10 dá 15,72 km, que são os 22 registros do material tipo 63.

## Status

- 6936 dias-linha com fator medido (km real) e 4016 estimados (depois de 2023-09 ou sem km no dia).
- 25 dias de greve em 2025: a exposição de cada hora é multiplicada pela fração da hora com serviço.
- Parcela de cada frota por linha e mês em `frota_mensal.csv`: medida até 2023-09, estimada depois.
