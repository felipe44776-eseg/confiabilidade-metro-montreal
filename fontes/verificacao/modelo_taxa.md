# Modelo da taxa horária de falha (spec 005)

Gerado por `pipeline/modelo_taxa.py`. Base: 226658 horas-linha com serviço, de 2019-01-01 a 2026-06-30. Deslocamento: log dos trens-hora (spec 004). Intervalos de 95% por bootstrap em blocos semanais, semente 20261021.

## Poisson contra binomial negativa

| Causa | Falhas no modelo | AIC Poisson | AIC binomial negativa | α | Razão de verossimilhança | p | Escolhido |
|---|---|---|---|---|---|---|---|
| MR | 3966 | 37849.54 | 37709.15 | 1.830086 | 142.391 | 4e-33 | binomial negativa |
| EF | 4423 | 41400.99 | 40456.6 | 5.545885 | 946.384 | 4.1e-208 | binomial negativa |

Falhas fora das horas com serviço programado (antes das 05:00 ou em horas sem trem no GTFS): MR 16, EF 125. Ficam fora do modelo e são declaradas.

## Multiplicadores principais (referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação, 2019)

| Fator | Material rodante | Equipamentos fixos |
|---|---|---|
| Pico da manhã | 1.35 (1.23–1.48) | 1.26 (1.14–1.37) |
| Pico da tarde | 0.85 (0.77–0.93) | 0.61 (0.55–0.68) |
| Abertura (5 a 6 h) | 2.64 (2.36–2.92) | 3.59 (3.14–4.03) |
| Abaixo de −15 °C | 0.94 (0.72–1.26) | 1.07 (0.73–1.59) |
| −15 a −5 °C | 1.09 (0.90–1.40) | 0.98 (0.77–1.25) |
| 25 °C ou mais | 1.07 (0.83–1.34) | 1.84 (1.29–2.33) |
| Precipitação acima de 1 mm/h | 0.95 (0.74–1.18) | 1.15 (0.92–1.42) |
| Chuva congelante | 0.89 (0.54–1.40) | 0.69 (0.28–0.99) |
| Neve | 0.87 (0.75–1.02) | 0.75 (0.62–0.91) |
| Mais de 10 cm de neve no solo | 1.37 (1.09–1.67) | 1.37 (1.09–1.69) |
| Jogo do Canadiens | 1.26 (1.01–1.59) | 0.91 (0.65–1.15) |
| Fim de semana do GP | 1.10 (0.55–1.53) | 0.70 (0.32–1.24) |
| Feriado | 0.89 (0.60–1.23) | 1.09 (0.64–1.60) |
| Dia de greve (por exposição) | 1.16 (0.55–2.23) | 1.10 (0.52–1.72) |
| Linha Verde | 2.08 (1.87–2.35) | 0.78 (0.71–0.87) |
| Linha Amarela | 5.44 (4.77–6.22) | 2.37 (1.62–3.08) |
| Linha Azul | 3.76 (3.39–4.23) | 0.66 (0.57–0.77) |

## Material rodante contra equipamentos fixos

Razão entre os multiplicadores das duas causas. As duas usam as mesmas semanas sorteadas, então o intervalo da razão vem do bootstrap pareado.

| Fator | MR | EF | Razão MR/EF (IC 95%) | Conclusão |
|---|---|---|---|---|
| Pico da manhã | 1.35 | 1.26 | 1.08 (0.96–1.23) | sem diferença detectável |
| Pico da tarde | 0.85 | 0.61 | 1.39 (1.22–1.66) | eleva mais o material rodante |
| Abertura (5 a 6 h) | 2.64 | 3.59 | 0.73 (0.63–0.88) | eleva mais os equipamentos fixos |
| Abaixo de −15 °C | 0.94 | 1.07 | 0.88 (0.62–1.27) | sem diferença detectável |
| −15 a −5 °C | 1.09 | 0.98 | 1.12 (0.86–1.51) | sem diferença detectável |
| −5 a 5 °C | 1.07 | 0.91 | 1.18 (0.94–1.43) | sem diferença detectável |
| Mais de 10 cm de neve no solo | 1.37 | 1.37 | 1.00 (0.75–1.36) | sem diferença detectável |
| Precipitação acima de 1 mm/h | 0.95 | 1.15 | 0.83 (0.60–1.13) | sem diferença detectável |
| Neve | 0.87 | 0.75 | 1.16 (0.91–1.46) | sem diferença detectável |
| Chuva congelante | 0.89 | 0.69 | 1.30 (0.64–3.26) | sem diferença detectável |

## Greves

- MR: multiplicador da taxa por trem-hora em dia de greve 1.16 (IC 0.55–2.23). O intervalo contém 1: a greve atua só pela exposição reduzida.
- EF: multiplicador da taxa por trem-hora em dia de greve 1.10 (IC 0.52–1.72). O intervalo contém 1: a greve atua só pela exposição reduzida.

## Resíduos quantílicos e rootograma

- MR: média 0.0004, desvio 1.0003 (esperado 0 e 1), percentis 5% e 95%: -1.648 e 1.643.
  Rootograma (horas com 0, 1, 2 e 3+ falhas, observado/esperado): 0: 222865/222864.8, 1: 3638/3635.3, 2: 140/146.9, 3+: 15/10.9
- EF: média 0.0004, desvio 1.0012 (esperado 0 e 1), percentis 5% e 95%: -1.648 e 1.642.
  Rootograma (horas com 0, 1, 2 e 3+ falhas, observado/esperado): 0: 222654/222670.9, 1: 3688/3566.1, 2: 246/340.4, 3+: 70/80.6

## Defasagem: falha na hora anterior (pergunta em aberto)

- MR: multiplicador 1.9479 (IC do modelo 1.7378–2.1833) quando houve falha técnica na mesma linha na hora anterior.
- EF: multiplicador 2.7616 (IC do modelo 2.4766–3.0793) quando houve falha técnica na mesma linha na hora anterior.

## Só até 2023-09 (o período com km real na v1.1.0)

Na v1.1.0, a exposição depois de 2023-09 era estimada, e esta sensibilidade mostrava o efeito de tirar esses meses. Desde a revisão de 2026-11, todo o período é medido pelo km real republicado; a comparação mostra o efeito de tirar 2023-10 a 2026-06.

| Fator | MR, período todo | MR, até 2023-09 | EF, período todo | EF, até 2023-09 |
|---|---|---|---|---|
| faixa=pico_manha | 1.35 | 1.22 | 1.26 | 1.17 |
| temp=abaixo_-15 | 0.94 | 1.07 | 1.07 | 0.91 |
| precip=acima_1mm | 0.95 | 1.01 | 1.15 | 1.16 |
| linha=verde | 2.08 | 2.35 | 0.78 | 0.81 |

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

