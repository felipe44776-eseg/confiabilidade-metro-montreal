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
| verde · MR | 1493 | 0.9887 | 0.0833 | 1.9e-09 | 0.8009 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| laranja · MR | 912 | 1.0032 | 0.1238 | 1.2e-12 | 0.7339 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| amarela · MR | 542 | 0.995 | 0.1572 | 3.7e-12 | 0.699 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| azul · MR | 1015 | 1.0037 | 0.1121 | 1.4e-11 | 0.7477 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| verde · EF | 1272 | 1.0326 | 0.0945 | 2.5e-10 | 0.761 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| laranja · EF | 2116 | 1.0291 | 0.1466 | 3.8e-40 | 0.6689 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| amarela · EF | 598 | 0.9744 | 0.4146 | 1.5e-93 | 0.435 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |
| azul · EF | 433 | 0.9964 | 0.1482 | 9e-09 | 0.6552 | renovação Weibull no tempo reescalado (taxa variável + agrupamento) |

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

## Causa comum: fator β pelo denominador da família (spec 018)

O evento conta na família da sua fonte (trem ou fixo), e o β divide pelas falhas daquela família na linha. 40 dos 45 eventos são de equipamento fixo.

| Par e família | Eventos | β da 1ª (IC 95%) | β da 2ª (IC 95%) |
|---|---|---|---|
| verde-laranja · MR | 1 | 0,0007 (0,0000–0,0037) | 0,0011 (0,0000–0,0060) |
| verde-laranja · EF | 30 | 0,0222 (0,0150–0,0315) | 0,0136 (0,0092–0,0194) |
| verde-amarela · MR | 1 | 0,0007 (0,0000–0,0037) | 0,0018 (0,0001–0,0102) |
| verde-amarela · EF | 17 | 0,0127 (0,0074–0,0202) | 0,0275 (0,0161–0,0436) |
| verde-azul · MR | 1 | 0,0007 (0,0000–0,0037) | 0,0010 (0,0000–0,0054) |
| verde-azul · EF | 11 | 0,0082 (0,0041–0,0147) | 0,0238 (0,0119–0,0422) |
| laranja-amarela · MR | 2 | 0,0022 (0,0003–0,0078) | 0,0037 (0,0004–0,0132) |
| laranja-amarela · EF | 19 | 0,0087 (0,0052–0,0135) | 0,0306 (0,0185–0,0474) |
| laranja-azul · MR | 2 | 0,0022 (0,0003–0,0078) | 0,0020 (0,0002–0,0071) |
| laranja-azul · EF | 19 | 0,0087 (0,0052–0,0135) | 0,0404 (0,0245–0,0624) |
| amarela-azul · EF | 10 | 0,0163 (0,0079–0,0298) | 0,0217 (0,0104–0,0395) |

## Renovação e duração por linha × fonte (spec 018)

Forma da Weibull no tempo reescalado pela taxa da fonte (spec 018) e duração (sem interrupção e média quando para). Herda da mesma fonte na rede (colunas de origem): a renovação, o estrato com menos de 30 intervalos; a duração, o estrato com menos de 30 durações positivas.

| Linha · fonte | Falhas | Forma (IC 95%) | Origem da renovação | Sem interrupção (IC 95%) | Média quando para (min) | Origem da duração |
|---|---|---|---|---|---|---|
| verde · aux_stations | 212 | 0,7500 (0,6934–0,8309) | linha | 0,900 (0,868–0,925) | 23,3 | rede (estrato pequeno) |
| laranja · aux_stations | 145 | 0,6984 (0,6347–0,7763) | linha | 0,900 (0,868–0,925) | 23,3 | rede (estrato pequeno) |
| amarela · aux_stations | 9 | 0,7293 (0,6778–0,7855) | rede (estrato pequeno) | 0,900 (0,868–0,925) | 23,3 | rede (estrato pequeno) |
| azul · aux_stations | 18 | 0,7293 (0,6778–0,7855) | rede (estrato pequeno) | 0,900 (0,868–0,925) | 23,3 | rede (estrato pequeno) |
| verde · aux_trains_sintoma_fixo | 468 | 0,8155 (0,7621–0,8710) | linha | 0,590 (0,545–0,633) | 8,5 | linha |
| laranja · aux_trains_sintoma_fixo | 782 | 0,7167 (0,6775–0,7765) | linha | 0,597 (0,563–0,630) | 7,8 | linha |
| amarela · aux_trains_sintoma_fixo | 95 | 0,5751 (0,4937–0,6877) | linha | 0,448 (0,352–0,547) | 10,0 | linha |
| azul · aux_trains_sintoma_fixo | 151 | 0,6912 (0,6159–0,8230) | linha | 0,480 (0,403–0,559) | 5,0 | linha |
| verde · aux_trains_sintoma_trem | 145 | 0,6473 (0,5526–0,7368) | linha | 0,616 (0,535–0,691) | 7,6 | linha |
| laranja · aux_trains_sintoma_trem | 368 | 0,4492 (0,4203–0,4837) | linha | 0,903 (0,868–0,929) | 9,0 | linha |
| amarela · aux_trains_sintoma_trem | 96 | 0,4371 (0,3889–0,5207) | linha | 0,817 (0,787–0,844) | 8,5 | rede (estrato pequeno) |
| azul · aux_trains_sintoma_trem | 81 | 0,5580 (0,4755–0,6772) | linha | 0,817 (0,787–0,844) | 8,5 | rede (estrato pequeno) |
| verde · mpm10 | 304 | 0,7206 (0,6466–0,7793) | linha | 0,278 (0,231–0,331) | 5,9 | linha |
| laranja · mpm10 | 884 | 0,7407 (0,7077–0,7727) | linha | 0,421 (0,389–0,454) | 6,4 | linha |
| verde · mr73 | 1184 | 0,8257 (0,7936–0,8761) | linha | 0,231 (0,208–0,255) | 5,5 | linha |
| amarela · mr73 | 542 | 0,6919 (0,6544–0,7233) | linha | 0,398 (0,357–0,440) | 4,7 | linha |
| azul · mr73 | 1007 | 0,7547 (0,7149–0,7923) | linha | 0,196 (0,173–0,222) | 5,2 | linha |
| verde · mr_outros | 3 | 0,7046 (0,5411–1,1127) | rede (estrato pequeno) | 0,471 (0,341–0,605) | 14,0 | rede (estrato pequeno) |
| laranja · mr_outros | 27 | 0,7046 (0,5411–1,1127) | rede (estrato pequeno) | 0,471 (0,341–0,605) | 14,0 | rede (estrato pequeno) |
| azul · mr_outros | 7 | 0,7046 (0,5411–1,1127) | rede (estrato pequeno) | 0,471 (0,341–0,605) | 14,0 | rede (estrato pequeno) |
| verde · tcpe | 50 | 0,7170 (0,5931–0,9204) | linha | 0,331 (0,259–0,412) | 7,8 | rede (estrato pequeno) |
| laranja · tcpe | 50 | 0,7540 (0,6060–1,0244) | linha | 0,241 (0,146–0,369) | 10,0 | linha |
| amarela · tcpe | 12 | 0,7642 (0,6552–0,9075) | rede (estrato pequeno) | 0,331 (0,259–0,412) | 7,8 | rede (estrato pequeno) |
| azul · tcpe | 16 | 0,7642 (0,6552–0,9075) | rede (estrato pequeno) | 0,331 (0,259–0,412) | 7,8 | rede (estrato pequeno) |
| verde · voie_sintoma_fixo | 309 | 0,7748 (0,7179–0,8553) | linha | 0,279 (0,233–0,330) | 10,6 | linha |
| laranja · voie_sintoma_fixo | 415 | 0,7982 (0,7634–0,8641) | linha | 0,214 (0,178–0,255) | 11,4 | linha |
| amarela · voie_sintoma_fixo | 88 | 0,4329 (0,3935–0,4811) | linha | 0,130 (0,076–0,214) | 8,3 | linha |
| azul · voie_sintoma_fixo | 108 | 0,6213 (0,5422–0,7188) | linha | 0,556 (0,465–0,642) | 36,1 | linha |
| verde · voie_sintoma_trem | 83 | 0,4405 (0,3857–0,5177) | linha | 0,892 (0,869–0,912) | 9,6 | rede (estrato pequeno) |
| laranja · voie_sintoma_trem | 351 | 0,4714 (0,4278–0,5199) | linha | 0,892 (0,869–0,912) | 9,6 | rede (estrato pequeno) |
| amarela · voie_sintoma_trem | 293 | 0,4117 (0,3796–0,4612) | linha | 0,857 (0,812–0,892) | 9,2 | linha |
| azul · voie_sintoma_trem | 54 | 0,3701 (0,3291–0,4575) | linha | 0,892 (0,869–0,912) | 9,6 | rede (estrato pequeno) |

## Falhas de zero minuto por fonte e ano (spec 020, D62)

A massa em zero vem de parada segura com rearme rápido (Almeida Jr. et al., 2008) ou de artefato de registro? Proporções em %, com IC 95% de Clopper–Pearson; p do qui-quadrado de homogeneidade. A leitura foi fixada na spec 020 antes de calcular:
- **parada segura com rearme rápido:** fontes heterogêneas (p < 0,01), a menor proporção entre controle de trens e frotas acima da maior entre via, estações e TCPE, e essas quatro fontes estáveis entre os anos;
- **artefato de registro:** fontes homogêneas, ou um ano em que pelo menos metade das fontes tem o IC inteiro acima ou abaixo da própria proporção.

**Leitura: inconclusiva.** Homogeneidade entre as fontes comparadas: p < 0,0001. Controle de trens e frotas estáveis entre os anos: não. Anos com salto comum: nenhum. "Controle de trens" (Service aux trains) é dedução até a resposta da STM.

| Fonte | n | Duração zero (IC 95%) | Até 1 min (IC 95%) | p entre anos |
|---|---|---|---|---|
| aux_stations | 420 | 90,0 (86,7–92,7) | 90,7 (87,5–93,3) | 0,00036 |
| aux_trains_sintoma_fixo | 1534 | 57,4 (54,8–59,9) | 64,3 (61,9–66,7) | 0,18 |
| aux_trains_sintoma_trem | 695 | 81,7 (78,6–84,5) | 83,0 (80,0–85,7) | 0,091 |
| mpm10 | 1191 | 38,5 (35,7–41,3) | 43,8 (41,0–46,7) | < 0,0001 |
| mr73 | 2740 | 25,1 (23,5–26,8) | 29,1 (27,4–30,8) | < 0,0001 |
| mr_outros | 51 | 47,1 (32,9–61,5) | 49,0 (34,8–63,4) | 0,054 |
| tcpe | 142 | 33,1 (25,4–41,5) | 36,6 (28,7–45,1) | 0,77 |
| voie_sintoma_fixo | 969 | 26,9 (24,2–29,8) | 27,9 (25,1–30,8) | 0,096 |
| voie_sintoma_trem | 788 | 89,2 (86,8–91,3) | 89,5 (87,1–91,5) | < 0,0001 |

Duração zero por ano (%):

| Fonte | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| aux_stations | 78,6 (28) | 76,2 (21) | 93,1 (29) | 77,4 (31) | 80,4 (46) | 94,7 (95) | 94,6 (111) | 96,6 (59) |
| aux_trains_sintoma_fixo | 57,5 (266) | 52,1 (167) | 59,7 (201) | 53,1 (194) | 60,4 (225) | 53,1 (194) | 59,5 (190) | 67,0 (97) |
| aux_trains_sintoma_trem | 78,6 (131) | 85,0 (93) | 77,0 (100) | 89,4 (161) | 80,9 (68) | 73,9 (69) | 81,0 (58) | 80,0 (15) |
| mpm10 | 20,7 (208) | 28,0 (189) | 28,0 (175) | 44,5 (110) | 43,9 (139) | 37,6 (109) | 65,8 (158) | 56,3 (103) |
| mr73 | 29,9 (623) | 22,1 (425) | 33,5 (251) | 25,5 (376) | 18,3 (334) | 28,1 (292) | 22,1 (271) | 14,9 (168) |
| mr_outros | 100,0 (2) |  | 33,3 (6) | 50,0 (6) | 25,0 (8) | 23,1 (13) | 77,8 (9) | 71,4 (7) |
| tcpe | 20,8 (24) | 28,6 (14) | 38,5 (13) | 43,8 (16) | 42,1 (19) | 38,1 (21) | 31,2 (16) | 26,3 (19) |
| voie_sintoma_fixo | 25,8 (128) | 25,6 (86) | 20,4 (157) | 28,0 (143) | 22,1 (136) | 32,1 (196) | 29,3 (75) | 39,6 (48) |
| voie_sintoma_trem | 16,7 (6) | 58,3 (12) | 54,5 (11) | 67,7 (34) | 92,1 (139) | 91,5 (516) | 98,1 (52) | 83,3 (18) |

Entre parênteses, o número de falhas da fonte no ano. `mr_outros` fica fora das comparações; o salto de 2024 da via com sintoma de trem já era conhecido (D56).
