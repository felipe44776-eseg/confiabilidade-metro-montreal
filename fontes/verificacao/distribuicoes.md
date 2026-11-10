# Distribuições do tempo entre falhas, do tempo até restabelecer e da causa comum (spec 006)

Gerado por `pipeline/distribuicoes.py`, semente 20261021, bootstrap paramétrico com 200 reamostras. Tempo em horas de operação (20 h por dia).

## Tempo entre falhas por estrato

| Estrato (linha, causa, frota, condição) | n | Média (h) | CV | Melhor por AIC | ΔAIC Weibull | ΔAIC exponencial | KS | p KS | AD | p AD |
|---|---|---|---|---|---|---|---|---|---|---|
| amarela · EF · todas | 601 | 90.654 | 2.536 | lognormal | 53.77 | 1536.15 | 0.0688 | 0.0 | 5.227 | 0.0 |
| amarela · EF · todas · inverno | 67 | 201.264 | 1.406 | gama | 2.96 | 41.63 | 0.0789 | 0.375 | 0.419 | 0.385 |
| amarela · EF · todas · resto_do_ano | 534 | 76.776 | 2.845 | lognormal | 68.23 | 1483.9 | 0.0602 | 0.0 | 4.248 | 0.0 |
| amarela · MR · todas | 543 | 100.336 | 1.423 | weibull | 0.0 | 175.27 | 0.03 | 0.24 | 0.606 | 0.09 |
| amarela · MR · todas · inverno | 152 | 93.825 | 1.428 | weibull | 0.0 | 41.31 | 0.0412 | 0.785 | 0.26 | 0.73 |
| amarela · MR · todas · resto_do_ano | 391 | 102.867 | 1.419 | weibull | 0.0 | 131.63 | 0.0392 | 0.115 | 0.722 | 0.045 |
| amarela · MR · MR-73 | 542 | 100.521 | 1.421 | weibull | 0.0 | 173.54 | 0.0296 | 0.265 | 0.607 | 0.115 |
| azul · EF · todas | 450 | 120.488 | 1.484 | gama | 8.19 | 228.15 | 0.0435 | 0.12 | 0.841 | 0.06 |
| azul · EF · todas · inverno | 102 | 123.504 | 1.113 | gama | 6.91 | 28.96 | 0.0847 | 0.105 | 1.248 | 0.0 |
| azul · EF · todas · resto_do_ano | 348 | 119.604 | 1.582 | weibull | 0.0 | 199.18 | 0.0555 | 0.01 | 0.974 | 0.035 |
| azul · MR · todas | 1018 | 53.647 | 1.364 | weibull | 0.0 | 208.11 | 0.0191 | 0.51 | 0.496 | 0.22 |
| azul · MR · todas · inverno | 307 | 48.04 | 1.339 | weibull | 0.0 | 48.7 | 0.0397 | 0.295 | 0.418 | 0.345 |
| azul · MR · todas · resto_do_ano | 711 | 56.068 | 1.365 | weibull | 0.0 | 155.31 | 0.0236 | 0.505 | 0.38 | 0.46 |
| azul · MR · MPM-10 | 4 | | | herda de azul · MR · todas | | | | | | |
| azul · MR · MR-73 | 1008 | 54.179 | 1.36 | weibull | 0.0 | 205.23 | 0.0189 | 0.52 | 0.484 | 0.235 |
| laranja · EF · todas | 2170 | 25.138 | 1.513 | weibull | 0.0 | 825.15 | 0.0213 | 0.01 | 1.824 | 0.0 |
| laranja · EF · todas · inverno | 541 | 25.655 | 1.592 | weibull | 0.0 | 221.35 | 0.032 | 0.21 | 0.892 | 0.04 |
| laranja · EF · todas · resto_do_ano | 1629 | 24.967 | 1.484 | weibull | 0.0 | 601.84 | 0.0239 | 0.025 | 1.329 | 0.005 |
| laranja · MR · todas | 916 | 59.61 | 1.387 | weibull | 0.0 | 208.79 | 0.0311 | 0.03 | 0.935 | 0.005 |
| laranja · MR · todas · inverno | 271 | 51.649 | 1.591 | weibull | 0.0 | 83.6 | 0.0396 | 0.37 | 0.399 | 0.37 |
| laranja · MR · todas · resto_do_ano | 645 | 62.955 | 1.313 | weibull | 0.0 | 122.74 | 0.0386 | 0.02 | 0.923 | 0.015 |
| laranja · MR · MPM-10 | 884 | 61.768 | 1.417 | weibull | 0.0 | 218.76 | 0.0302 | 0.065 | 0.929 | 0.01 |
| laranja · MR · MR-73 | 20 | | | herda de laranja · MR · todas | | | | | | |
| verde · EF · todas | 1323 | 41.291 | 1.323 | weibull | 0.0 | 213.46 | 0.0172 | 0.45 | 0.59 | 0.125 |
| verde · EF · todas · inverno | 301 | 47.052 | 1.223 | weibull | 0.0 | 32.44 | 0.0398 | 0.295 | 0.253 | 0.77 |
| verde · EF · todas · resto_do_ano | 1022 | 39.595 | 1.355 | weibull | 0.0 | 177.62 | 0.0239 | 0.2 | 0.649 | 0.08 |
| verde · MR · todas | 1501 | 36.343 | 1.413 | weibull | 0.0 | 367.36 | 0.0333 | 0.0 | 1.333 | 0.0 |
| verde · MR · todas · inverno | 455 | 31.541 | 1.553 | weibull | 0.0 | 147.36 | 0.0379 | 0.105 | 0.635 | 0.1 |
| verde · MR · todas · resto_do_ano | 1046 | 38.431 | 1.359 | weibull | 0.0 | 216.65 | 0.0366 | 0.0 | 0.974 | 0.005 |
| verde · MR · MPM-10 | 305 | 177.578 | 1.215 | gama | 8.74 | 72.55 | 0.0541 | 0.045 | 0.634 | 0.165 |
| verde · MR · MR-73 | 1187 | 45.956 | 1.426 | weibull | 0.0 | 339.97 | 0.0389 | 0.0 | 1.527 | 0.0 |

## Teste de reescala do tempo (o agrupamento é só heterogeneidade?)

Com a taxa horária da spec 005, os intervalos reescalados deveriam seguir uma exponencial de média 1 se as falhas fossem um processo de Poisson com taxa variável.

| Linha e causa | n | Média reescalada | KS contra Exp(1) | p | Forma da Weibull reescalada | Processo usado no simulador |
|---|---|---|---|---|---|---|
| verde · MR | 1493 | 0.9888 | 0.0821 | 3.4e-09 | 0.8017 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| laranja · MR | 912 | 1.0033 | 0.1238 | 1.2e-12 | 0.7335 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| amarela · MR | 542 | 0.9952 | 0.1565 | 4.7e-12 | 0.6982 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| azul · MR | 1015 | 1.0038 | 0.112 | 1.5e-11 | 0.7472 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| verde · EF | 1272 | 1.0298 | 0.0963 | 1e-10 | 0.7625 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| laranja · EF | 2116 | 1.0276 | 0.1479 | 7.7e-41 | 0.6691 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| amarela · EF | 598 | 0.9719 | 0.4079 | 2e-90 | 0.4387 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| azul · EF | 433 | 0.9961 | 0.147 | 1.2e-08 | 0.656 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |

## Tempo até o serviço voltar

| Linha e causa | n | Sem interrupção (IC 95%) | μ log (IC 95%) | σ log | Média (min) | p90 (min) |
|---|---|---|---|---|---|---|
| verde · MR | 1502 | 0.2423 (0.2213–0.2647) | 1.411 (1.3777–1.4508) | 0.7063 | 4.233 | 9.0 |
| verde · EF | 1324 | 0.5838 (0.5571–0.6101) | 1.6246 (1.5495–1.7047) | 0.9864 | 4.032 | 9.0 |
| laranja · MR | 917 | 0.4209 (0.3894–0.4532) | 1.3366 (1.2728–1.3961) | 0.8554 | 3.921 | 7.0 |
| laranja · EF | 2171 | 0.6412 (0.6208–0.6611) | 1.6257 (1.5674–1.6987) | 0.9389 | 3.526 | 7.0 |
| amarela · MR | 544 | 0.3989 (0.3586–0.4406) | 1.2678 (1.2012–1.3282) | 0.6849 | 2.844 | 6.0 |
| amarela · EF | 602 | 0.6678 (0.6292–0.7042) | 1.8188 (1.6978–1.9215) | 0.918 | 3.282 | 8.0 |
| azul · MR | 1019 | 0.1992 (0.1758–0.2248) | 1.3769 (1.3346–1.4191) | 0.6833 | 4.179 | 9.0 |
| azul · EF | 451 | 0.5987 (0.5528–0.6429) | 1.4703 (1.3347–1.6325) | 1.0112 | 5.936 | 6.0 |

Regressão de tempo acelerado (lognormal) nas 4523 interrupções com duração positiva: R² 0.2519, σ 0.7232. Multiplicadores da duração:

| Termo | Multiplicador | IC 95% |
|---|---|---|
| const | 2.8781 | 2.5952–3.1918 |
| linha_azul | 0.9233 | 0.8544–0.9977 |
| linha_laranja | 0.972 | 0.8951–1.0555 |
| linha_verde | 0.9521 | 0.886–1.0232 |
| sec_MR-73 | 1.2429 | 1.1521–1.3409 |
| sec_Service TCPE | 1.5643 | 1.3369–1.8305 |
| sec_Service aux trains | 1.2729 | 1.1804–1.3727 |
| sec_Service de la voie | 2.1942 | 2.034–2.3669 |
| sec_outra | 2.4991 | 2.0365–3.0668 |
| faixa_entrepico | 1.0182 | 0.9506–1.0906 |
| faixa_fim | 1.0018 | 0.8888–1.1293 |
| faixa_noite | 1.0512 | 0.9667–1.143 |
| faixa_pico_manha | 0.9641 | 0.8977–1.0354 |
| faixa_pico_tarde | 1.06 | 0.98–1.1467 |
| evacuacao | 2.92 | 2.7413–3.1103 |

## Causa comum: fator β por par

Um evento que para três ou quatro linhas conta em todos os pares que ele contém. Por isso a soma dos pares passa do total de 45 eventos.

| Par | Eventos | β da 1ª (IC 95%) | β da 2ª (IC 95%) | Taxa por hora de operação (IC 95%) | Duração média (min) |
|---|---|---|---|---|---|
| verde-laranja | 31 | 0.01085 (0.00738–0.01537) | 0.00994 (0.00676–0.01408) | 5.66e-04 (3.85e-04–8.04e-04) | 24.26 |
| verde-amarela | 18 | 0.00633 (0.00376–0.00998) | 0.01546 (0.00919–0.02433) | 3.29e-04 (1.95e-04–5.19e-04) | 25.44 |
| verde-azul | 12 | 0.00423 (0.00219–0.00737) | 0.0081 (0.00419–0.0141) | 2.19e-04 (1.13e-04–3.83e-04) | 20.67 |
| laranja-amarela | 21 | 0.00675 (0.00419–0.01031) | 0.01799 (0.01117–0.02738) | 3.83e-04 (2.37e-04–5.86e-04) | 22.19 |
| laranja-azul | 21 | 0.00675 (0.00419–0.01031) | 0.01408 (0.00874–0.02145) | 3.83e-04 (2.37e-04–5.86e-04) | 22.95 |
| amarela-azul | 10 | 0.00865 (0.00416–0.01585) | 0.00676 (0.00324–0.01239) | 1.83e-04 (8.76e-05–3.36e-04) | 17.4 |

## Causa comum: grupos usados pelo simulador

Cada evento entra uma vez só, no grupo exato de linhas que parou. A duração vem dos 45 eventos juntos: sem interrupção 0.2444 (IC 0.1424–0.3867), lognormal com μ log 2.5922 e σ log 1.4069, média 22.27 min.

| Grupo de linhas | Eventos | Taxa por hora de operação (IC 95%) | Duração média no grupo (min) |
|---|---|---|---|
| amarela-azul-laranja-verde | 10 | 1.83e-04 (8.76e-05–3.36e-04) | 17.4 |
| amarela-laranja | 3 | 5.48e-05 (1.13e-05–1.60e-04) | 2.67 |
| amarela-laranja-verde | 8 | 1.46e-04 (6.31e-05–2.88e-04) | 35.5 |
| azul-laranja | 10 | 1.83e-04 (8.76e-05–3.36e-04) | 23.8 |
| azul-laranja-verde | 1 | 1.83e-05 (4.60e-07–1.02e-04) | 70.0 |
| azul-verde | 1 | 1.83e-05 (4.60e-07–1.02e-04) | 4.0 |
| laranja-verde | 12 | 2.19e-04 (1.13e-04–3.83e-04) | 18.67 |
