# Modelo da taxa horária de falha (spec 005)

Gerado por `pipeline/modelo_taxa.py`. Base: 226658 horas-linha com serviço, de 2019-01-01 a 2026-06-30. Deslocamento: log dos trens-hora (spec 004). Intervalos de 95% por bootstrap em blocos semanais, semente 20261021.

## Poisson contra binomial negativa

| Causa | Falhas no modelo | AIC Poisson | AIC binomial negativa | α | Razão de verossimilhança | p | Escolhido |
|---|---|---|---|---|---|---|---|
| MR | 3966 | 37850.38 | 37709.78 | 1.833019 | 142.604 | 3.6e-33 | binomial negativa |
| EF | 4423 | 41356.78 | 40421.74 | 5.47165 | 937.033 | 4.4e-206 | binomial negativa |

Falhas fora das horas com serviço programado (antes das 05:00 ou em horas sem trem no GTFS): MR 16, EF 125. Ficam fora do modelo e são declaradas.

## Multiplicadores principais (referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação, 2019)

| Fator | Material rodante | Equipamentos fixos |
|---|---|---|
| Pico da manhã | 1.35 (1.23–1.48) | 1.26 (1.14–1.37) |
| Pico da tarde | 0.85 (0.77–0.93) | 0.61 (0.55–0.67) |
| Abertura (5 a 6 h) | 2.64 (2.36–2.92) | 3.59 (3.13–4.03) |
| Abaixo de −15 °C | 0.93 (0.71–1.24) | 1.05 (0.72–1.56) |
| −15 a −5 °C | 1.09 (0.89–1.40) | 0.97 (0.76–1.25) |
| 25 °C ou mais | 1.07 (0.83–1.35) | 1.83 (1.29–2.32) |
| Precipitação acima de 1 mm/h | 0.95 (0.73–1.18) | 1.15 (0.92–1.41) |
| Chuva congelante | 0.89 (0.54–1.40) | 0.69 (0.28–0.99) |
| Neve | 0.87 (0.75–1.03) | 0.75 (0.62–0.91) |
| Mais de 10 cm de neve no solo | 1.37 (1.10–1.67) | 1.38 (1.10–1.70) |
| Jogo do Canadiens | 1.26 (1.00–1.59) | 0.91 (0.65–1.16) |
| Fim de semana do GP | 1.16 (0.59–1.65) | 0.76 (0.36–1.25) |
| Feriado | 0.89 (0.60–1.23) | 1.11 (0.67–1.60) |
| Dia de greve (por exposição) | 1.17 (0.56–2.24) | 1.11 (0.52–1.73) |
| Linha Verde | 2.11 (1.89–2.38) | 0.79 (0.72–0.88) |
| Linha Amarela | 5.05 (4.42–5.77) | 2.14 (1.49–2.78) |
| Linha Azul | 3.74 (3.37–4.22) | 0.66 (0.57–0.76) |

## Material rodante contra equipamentos fixos

Razão entre os multiplicadores das duas causas. As duas usam as mesmas semanas sorteadas, então o intervalo da razão vem do bootstrap pareado.

| Fator | MR | EF | Razão MR/EF (IC 95%) | Conclusão |
|---|---|---|---|---|
| Pico da manhã | 1.35 | 1.26 | 1.08 (0.96–1.23) | sem diferença detectável |
| Pico da tarde | 0.85 | 0.61 | 1.39 (1.22–1.66) | eleva mais o material rodante |
| Abertura (5 a 6 h) | 2.64 | 3.59 | 0.74 (0.63–0.89) | eleva mais os equipamentos fixos |
| Abaixo de −15 °C | 0.93 | 1.05 | 0.88 (0.63–1.28) | sem diferença detectável |
| −15 a −5 °C | 1.09 | 0.97 | 1.12 (0.86–1.51) | sem diferença detectável |
| −5 a 5 °C | 1.07 | 0.91 | 1.18 (0.94–1.43) | sem diferença detectável |
| Mais de 10 cm de neve no solo | 1.37 | 1.38 | 1.00 (0.75–1.36) | sem diferença detectável |
| Precipitação acima de 1 mm/h | 0.95 | 1.15 | 0.83 (0.60–1.13) | sem diferença detectável |
| Neve | 0.87 | 0.75 | 1.16 (0.91–1.46) | sem diferença detectável |
| Chuva congelante | 0.89 | 0.69 | 1.29 (0.63–3.26) | sem diferença detectável |

## Greves

- MR: multiplicador da taxa por trem-hora em dia de greve 1.17 (IC 0.56–2.24). O intervalo contém 1: a greve atua só pela exposição reduzida.
- EF: multiplicador da taxa por trem-hora em dia de greve 1.11 (IC 0.52–1.73). O intervalo contém 1: a greve atua só pela exposição reduzida.

## Resíduos quantílicos e rootograma

- MR: média 0.0004, desvio 1.0003 (esperado 0 e 1), percentis 5% e 95%: -1.648 e 1.643.
  Rootograma (horas com 0, 1, 2 e 3+ falhas, observado/esperado): 0: 222865/222865.0, 1: 3638/3634.8, 2: 140/147.2, 3+: 15/11.0
- EF: média 0.0004, desvio 1.0012 (esperado 0 e 1), percentis 5% e 95%: -1.647 e 1.641.
  Rootograma (horas com 0, 1, 2 e 3+ falhas, observado/esperado): 0: 222654/222670.1, 1: 3688/3571.8, 2: 246/337.6, 3+: 70/78.4

## Defasagem: falha na hora anterior (pergunta em aberto)

- MR: multiplicador 1.9476 (IC do modelo 1.7376–2.183) quando houve falha técnica na mesma linha na hora anterior.
- EF: multiplicador 2.7495 (IC do modelo 2.4663–3.0654) quando houve falha técnica na mesma linha na hora anterior.

## Só o período com km real (2019-01 a 2023-09)

| Fator | MR, período todo | MR, só km real | EF, período todo | EF, só km real |
|---|---|---|---|---|
| faixa=pico_manha | 1.35 | 1.22 | 1.26 | 1.17 |
| temp=abaixo_-15 | 0.93 | 1.07 | 1.05 | 0.91 |
| precip=acima_1mm | 0.95 | 1.01 | 1.15 | 1.16 |
| linha=verde | 2.11 | 2.35 | 0.79 | 0.81 |

## Correlação entre fatores de clima (horas com serviço)

```
{
 "frio_abaixo_-5": {
  "frio_abaixo_-5": 1.0,
  "inverno": 0.606,
  "neve_no_solo": 0.561,
  "precipitacao": 0.009
 },
 "inverno": {
  "frio_abaixo_-5": 0.606,
  "inverno": 1.0,
  "neve_no_solo": 0.706,
  "precipitacao": 0.089
 },
 "neve_no_solo": {
  "frio_abaixo_-5": 0.561,
  "inverno": 0.706,
  "neve_no_solo": 1.0,
  "precipitacao": 0.099
 },
 "precipitacao": {
  "frio_abaixo_-5": 0.009,
  "inverno": 0.089,
  "neve_no_solo": 0.099,
  "precipitacao": 1.0
 }
}
```

