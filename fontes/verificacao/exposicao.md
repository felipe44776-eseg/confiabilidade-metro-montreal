# Exposição (spec 004)

Gerado por `pipeline/exposicao.py` a partir do GTFS da STM (moldes de dia útil, sábado e domingo) e do km real republicado pela STM em 2026-10-23 (usado até 2026-06-30, o fim dos incidentes; até a v1.1.0, o km real ia de 2019-01 a 2023-09).

## Trens em viagem às 08:00 de um dia útil

| Linha | GTFS | Esperado | Dentro da tolerância de 1 trem |
|---|---|---|---|
| verde | 26 | 26 | sim |
| laranja | 31 | 32 | sim |
| amarela | 2 | 2 | sim |
| azul | 9 | 9 | sim |

## Erro mensal do km estimado contra o km real

356 meses-linha comparados; 6 acima de 10% (98.3% dentro); erro absoluto mediano de 0.50%.

| Linha | Mês | Erro |
|---|---|---|
| verde | 2020-04 | +17.6% |
| azul | 2020-04 | +16.2% |
| laranja | 2020-04 | +16.1% |
| verde | 2020-05 | -11.7% |
| azul | 2020-05 | -11.1% |
| laranja | 2020-05 | -10.8% |

Exceção registrada na v1.1.0 (220 meses, 2019-01 a 2023-09): abril de 2020 (primeiro mês da pandemia, com oferta cortada no meio do mês) nas três linhas grandes e junho de 2019 na Amarela. O km real republicado preencheu o período de exploração de cerca de 80 mil registros que estavam com "#", o que muda os fatores de calibração por linha e período, e estende a comparação até o fim dos incidentes; os meses acima de 10% passam a ser os da tabela. Em dia de greve, o km estimado conta só as horas com serviço (D63). O critério não foi afrouxado.

## Km real por frota

| Frota | Registros | km-carro |
|---|---|---|
| MPM-10 | 583.173 | 497.122.545,6 |
| MR-63 | 26 | 21,9 |
| MR-73 | 341.442 | 169.445.418,2 |

Total: 666,57 milhões de km-carro. O total menos MR-73 e MPM-10 dá 21,90 km, que são os 26 registros do material tipo 63.

## Status

- 10852 dias-linha com fator medido (km real) e 100 estimados (sem km real no dia).
- 25 dias de greve em 2025: a exposição de cada hora é multiplicada pela fração da hora com serviço, com o fator típico da linha e do tipo de dia (D63). O km real desses dias é de 0,93 a 2,26 vezes o km do horário só nas faixas com serviço (mediana 1,36): houve serviço fora das faixas, que o modelo não representa (as falhas fora das faixas ficam fora, como na v1.1.0).
- Parcela de cada frota por linha e dia em `frota_diaria.csv` e por mês em `frota_mensal.csv`, medida pelo km real em todo o período (spec 018; na v1.1.0, medida até 2023-09 e suposta igual à do último ano depois).
