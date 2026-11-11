# Revisão de 2026-11: números antes e depois

Gerado por `pipeline/compara_versoes.py`, comparando os arquivos derivados da etiqueta `v1.1.0` (versão anterior, publicada em `/versoes/v1.1.0/`) com os atuais. Os números revistos vêm da ressegmentação por frota e setor (specs 017 e 018), da duração pela faixa oficial (D55), do km real republicado pela STM em 2026-10-23 (exposição medida em todo o período) e do simulador com várias fontes (spec 019). Só aparecem os números que mudaram.

## Normalização (specs 001 e 017)

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| Minutos parados das falhas técnicas | 43.971 | 33.404 | -24,0% |
| Minutos das 100 exceções (calculados → regra) | 11.129 | 562 | -95,0% |

## Exposição (spec 004)

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| meses_comparados | 220,0000 | 356,0000 | +61,8% |
| meses_com_erro_acima_de_10pct | 4,0000 | 6,0000 | +50,0% |
| pct_meses_dentro | 0,9818 | 0,9831 | +0,1% |
| dias_medidos | 6.936,0000 | 10.852,0000 | +56,5% |
| dias_estimados | 4.016,0000 | 100,0000 | -97,5% |

## Painel do site, por linha

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| verde · mttr_min | 4,7200 | 4,1400 | -12,3% |
| verde · min_fora_ano | 1.779,8000 | 1.560,2000 | -12,3% |
| verde · disponibilidade | 0,9959 | 0,9964 | +0,1% |
| verde · a_markov | 0,9960 | 0,9965 | +0,0% |
| verde · pct_sem_interrupcao | 0,4006 | 0,4023 | +0,4% |
| laranja · mttr_min | 4,1200 | 3,6400 | -11,7% |
| laranja · min_fora_ano | 1.696,7000 | 1.500,8000 | -11,5% |
| laranja · disponibilidade | 0,9961 | 0,9966 | +0,0% |
| laranja · a_markov | 0,9961 | 0,9966 | +0,0% |
| laranja · pct_sem_interrupcao | 0,5735 | 0,5758 | +0,4% |
| amarela · mttr_min | 3,2000 | 3,0700 | -4,1% |
| amarela · p90_ttr_min | 8,0000 | 7,0000 | -12,5% |
| amarela · min_fora_ano | 488,9000 | 470,0000 | -3,9% |
| amarela · pct_sem_interrupcao | 0,5393 | 0,5401 | +0,1% |
| azul · mttr_min | 9,6900 | 4,7200 | -51,3% |
| azul · p90_ttr_min | 9,0000 | 8,0000 | -11,1% |
| azul · min_fora_ano | 1.900,3000 | 925,1000 | -51,3% |
| azul · disponibilidade | 0,9957 | 0,9979 | +0,2% |
| azul · a_markov | 0,9957 | 0,9979 | +0,2% |
| azul · pct_sem_interrupcao | 0,3156 | 0,3218 | +2,0% |
| rede · mttr_min | 5,1500 | 3,9200 | -23,9% |
| rede · min_fora_ano | 5.865,7000 | 4.456,1000 | -24,0% |
| rede · disponibilidade | 0,9967 | 0,9975 | +0,1% |
| rede · pct_sem_interrupcao | 0,4672 | 0,4698 | +0,6% |

## Painel do site: corredor Verde e Laranja (minutos por ano)

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| so_laranja · min_ano_analitico | 1.797,04 | 1.601,07 | -10,9% |
| so_laranja · sim_min_ano | 1.852,34 | 1.639,36 | -11,5% |
| so_verde · min_ano_analitico | 1.880,14 | 1.660,57 | -11,7% |
| so_verde · sim_min_ano | 1.897,08 | 1.704,05 | -10,2% |
| paralelo_indep · min_ano_analitico | 6,89 | 5,34 | -22,5% |
| paralelo_indep · sim_min_ano | 8,08 | 6,94 | -14,1% |
| paralelo_cc · min_ano_analitico | 107,21 | 105,66 | -1,4% |
| paralelo_cc · sim_min_ano | 107,31 | 106,17 | -1,1% |
| serie_laranja_azul · min_ano_analitico | 3.661,30 | 2.490,18 | -32,0% |

## Modelo da taxa, família MR (spec 005)

Mesma especificação da v1.1.0; muda a exposição (medida em todo o período) e, nos multiplicadores, só o que isso move.

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| α | 1,833 | 1,830 | -0,2% |
| multiplicador linha=amarela | 5,049 | 5,439 | +7,7% |
| multiplicador linha=azul | 3,742 | 3,759 | +0,5% |
| multiplicador linha=verde | 2,111 | 2,085 | -1,2% |
| multiplicador faixa=abertura | 2,642 | 2,639 | -0,1% |
| multiplicador faixa=pico_manha | 1,355 | 1,353 | -0,1% |
| multiplicador tipo_dia=domingo | 0,742 | 0,744 | +0,3% |
| multiplicador tipo_dia=sabado | 0,725 | 0,727 | +0,3% |
| multiplicador estacao=inverno | 1,054 | 1,056 | +0,2% |
| multiplicador estacao=primavera | 1,116 | 1,114 | -0,2% |
| multiplicador estacao=verao | 1,134 | 1,142 | +0,7% |
| multiplicador temp=-15a-5 | 1,091 | 1,094 | +0,3% |
| multiplicador temp=-5a5 | 1,071 | 1,074 | +0,3% |
| multiplicador temp=15a25 | 1,078 | 1,076 | -0,2% |
| multiplicador temp=25_ou_mais | 1,070 | 1,068 | -0,2% |
| multiplicador temp=abaixo_-15 | 0,926 | 0,937 | +1,2% |
| multiplicador precip=acima_1mm | 0,950 | 0,951 | +0,1% |
| multiplicador precip=ate_1mm | 0,953 | 0,952 | -0,0% |
| multiplicador cond=chuva | 0,898 | 0,897 | -0,1% |
| multiplicador cond=chuva_congelante | 0,890 | 0,889 | -0,1% |
| multiplicador neve_solo=1a10 | 1,390 | 1,387 | -0,2% |
| multiplicador neve_solo=acima_10 | 1,374 | 1,368 | -0,4% |
| multiplicador ano=2023 | 0,625 | 0,624 | -0,2% |
| multiplicador ano=2024 | 0,548 | 0,540 | -1,4% |
| multiplicador ano=2025 | 0,572 | 0,563 | -1,6% |
| multiplicador ano=2026 | 0,672 | 0,664 | -1,2% |
| multiplicador jogo | 1,258 | 1,257 | -0,1% |
| multiplicador gp_fds | 1,164 | 1,100 | -5,5% |
| multiplicador feriado | 0,891 | 0,886 | -0,5% |
| multiplicador greve | 1,168 | 1,161 | -0,6% |

## Modelo da taxa, família EF (spec 005)

Mesma especificação da v1.1.0; muda a exposição (medida em todo o período) e, nos multiplicadores, só o que isso move.

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| α | 5,472 | 5,546 | +1,4% |
| multiplicador linha=amarela | 2,143 | 2,367 | +10,5% |
| multiplicador linha=azul | 0,656 | 0,661 | +0,7% |
| multiplicador linha=verde | 0,793 | 0,781 | -1,5% |
| multiplicador faixa=abertura | 3,585 | 3,591 | +0,2% |
| multiplicador tipo_dia=sabado | 0,858 | 0,861 | +0,3% |
| multiplicador estacao=inverno | 0,652 | 0,654 | +0,4% |
| multiplicador estacao=primavera | 0,673 | 0,672 | -0,1% |
| multiplicador estacao=verao | 0,651 | 0,652 | +0,1% |
| multiplicador temp=-15a-5 | 0,974 | 0,976 | +0,3% |
| multiplicador temp=-5a5 | 0,911 | 0,912 | +0,1% |
| multiplicador temp=15a25 | 1,386 | 1,385 | -0,1% |
| multiplicador temp=25_ou_mais | 1,832 | 1,836 | +0,2% |
| multiplicador temp=abaixo_-15 | 1,053 | 1,065 | +1,1% |
| multiplicador precip=acima_1mm | 1,150 | 1,152 | +0,2% |
| multiplicador precip=ate_1mm | 1,197 | 1,198 | +0,1% |
| multiplicador cond=chuva_congelante | 0,689 | 0,685 | -0,5% |
| multiplicador neve_solo=1a10 | 1,181 | 1,178 | -0,3% |
| multiplicador neve_solo=acima_10 | 1,377 | 1,367 | -0,7% |
| multiplicador ano=2023 | 1,118 | 1,116 | -0,2% |
| multiplicador ano=2024 | 2,028 | 2,007 | -1,0% |
| multiplicador ano=2025 | 0,903 | 0,888 | -1,7% |
| multiplicador ano=2026 | 1,030 | 1,021 | -0,9% |
| multiplicador jogo | 0,910 | 0,908 | -0,2% |
| multiplicador gp_fds | 0,756 | 0,704 | -6,9% |
| multiplicador feriado | 1,108 | 1,094 | -1,3% |
| multiplicador greve | 1,114 | 1,105 | -0,8% |

## Tempo entre falhas, duração e causa comum (spec 006)

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| forma da renovação verde|MR | 0,8017 | 0,8009 | -0,1% |
| forma da renovação laranja|MR | 0,7335 | 0,7339 | +0,1% |
| forma da renovação amarela|MR | 0,6982 | 0,6990 | +0,1% |
| forma da renovação azul|MR | 0,7472 | 0,7477 | +0,1% |
| forma da renovação verde|EF | 0,7625 | 0,7610 | -0,2% |
| forma da renovação laranja|EF | 0,6691 | 0,6689 | -0,0% |
| forma da renovação amarela|EF | 0,4387 | 0,4350 | -0,8% |
| forma da renovação azul|EF | 0,6560 | 0,6552 | -0,1% |
| sem interrupção verde|MR | 0,2417 | 0,2423 | +0,2% |
| sem interrupção verde|EF | 0,5808 | 0,5838 | +0,5% |
| sem interrupção laranja|EF | 0,6380 | 0,6412 | +0,5% |
| sem interrupção amarela|MR | 0,3971 | 0,3989 | +0,5% |
| sem interrupção azul|EF | 0,5787 | 0,5987 | +3,5% |
| duração média verde|MR (min) | 4,4240 | 4,2330 | -4,3% |
| duração média verde|EF (min) | 5,0580 | 4,0320 | -20,3% |
| duração média laranja|MR (min) | 4,0280 | 3,9210 | -2,7% |
| duração média laranja|EF (min) | 4,1570 | 3,5260 | -15,2% |
| duração média amarela|MR (min) | 2,8900 | 2,8440 | -1,6% |
| duração média amarela|EF (min) | 3,4770 | 3,2820 | -5,6% |
| duração média azul|MR (min) | 4,2890 | 4,1790 | -2,6% |
| duração média azul|EF (min) | 21,8940 | 5,9360 | -72,9% |

### β com o denominador da família (novo, spec 018)

| Par e família | Eventos | β da 1ª linha (IC 95%) | β da 2ª linha (IC 95%) |
|---|---|---|---|
| verde-laranja|MR | 1 | 0,0007 (0,0000–0,0037) | 0,0011 (0,0000–0,0060) |
| verde-laranja|EF | 30 | 0,0222 (0,0150–0,0315) | 0,0136 (0,0092–0,0194) |
| verde-amarela|MR | 1 | 0,0007 (0,0000–0,0037) | 0,0018 (0,0001–0,0102) |
| verde-amarela|EF | 17 | 0,0127 (0,0074–0,0202) | 0,0275 (0,0161–0,0436) |
| verde-azul|MR | 1 | 0,0007 (0,0000–0,0037) | 0,0010 (0,0000–0,0054) |
| verde-azul|EF | 11 | 0,0082 (0,0041–0,0147) | 0,0238 (0,0119–0,0422) |
| laranja-amarela|MR | 2 | 0,0022 (0,0003–0,0078) | 0,0037 (0,0004–0,0132) |
| laranja-amarela|EF | 19 | 0,0087 (0,0052–0,0135) | 0,0306 (0,0185–0,0474) |
| laranja-azul|MR | 2 | 0,0022 (0,0003–0,0078) | 0,0020 (0,0002–0,0071) |
| laranja-azul|EF | 19 | 0,0087 (0,0052–0,0135) | 0,0404 (0,0245–0,0624) |
| amarela-azul|EF | 10 | 0,0163 (0,0079–0,0298) | 0,0217 (0,0104–0,0395) |

## Validação contra o histórico (spec 012), refeita após a revisão (pós-hoc)

Mesmas versões e regras da spec 012; mudam os dados de entrada (durações pela faixa oficial e exposição medida). O resultado oficial da spec 012 continua sendo o da v1.1.0.

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| versão A · cobertura do IP 90% | 0,667 | 0,653 | -2,1% |
| versão B · cobertura do IP 90% | 0,819 | 0,847 | +3,4% |
| versão C · cobertura do IP 90% | 0,847 | 0,875 | +3,3% |
| versão A · minutos previstos no 1º ano, verde (mediana) | 2.207,000 | 2.043,000 | -7,4% |
| versão A · minutos previstos no 1º ano, laranja (mediana) | 2.355,500 | 2.206,500 | -6,3% |
| versão A · minutos previstos no 1º ano, amarela (mediana) | 767,500 | 645,000 | -16,0% |
| versão A · minutos previstos no 1º ano, azul (mediana) | 2.961,500 | 849,500 | -71,3% |
| versão B · minutos previstos no 1º ano, verde (mediana) | 1.736,000 | 1.721,500 | -0,8% |
| versão B · minutos previstos no 1º ano, laranja (mediana) | 1.492,000 | 1.482,500 | -0,6% |
| versão B · minutos previstos no 1º ano, amarela (mediana) | 468,000 | 368,000 | -21,4% |
| versão B · minutos previstos no 1º ano, azul (mediana) | 610,000 | 603,000 | -1,1% |
| versão C · minutos previstos no 1º ano, verde (mediana) | 1.658,500 | 1.585,500 | -4,4% |
| versão C · minutos previstos no 1º ano, laranja (mediana) | 1.598,500 | 1.481,000 | -7,4% |
| versão C · minutos previstos no 1º ano, amarela (mediana) | 561,000 | 474,000 | -15,5% |
| versão C · minutos previstos no 1º ano, azul (mediana) | 1.817,500 | 772,000 | -57,5% |
| versão D · minutos previstos no 1º ano, verde (mediana) | 1.913,000 | 1.717,000 | -10,2% |
| versão D · minutos previstos no 1º ano, laranja (mediana) | 1.619,000 | 1.524,000 | -5,9% |
| versão D · minutos previstos no 1º ano, amarela (mediana) | 559,000 | 519,000 | -7,2% |
| versão D · minutos previstos no 1º ano, azul (mediana) | 701,000 | 687,000 | -2,0% |
| versão A · minutos observados no 1º ano, verde | 1.450,000 | 1.363,000 | -6,0% |
| versão A · minutos observados no 1º ano, laranja | 1.698,000 | 1.160,000 | -31,7% |
| versão A · minutos observados no 1º ano, azul | 708,000 | 660,000 | -6,8% |
| versão B · minutos observados no 1º ano, verde | 1.450,000 | 1.363,000 | -6,0% |
| versão B · minutos observados no 1º ano, laranja | 1.698,000 | 1.160,000 | -31,7% |
| versão B · minutos observados no 1º ano, azul | 708,000 | 660,000 | -6,8% |
| versão C · minutos observados no 1º ano, verde | 1.450,000 | 1.363,000 | -6,0% |
| versão C · minutos observados no 1º ano, laranja | 1.698,000 | 1.160,000 | -31,7% |
| versão C · minutos observados no 1º ano, azul | 708,000 | 660,000 | -6,8% |
| versão D · minutos observados no 1º ano, verde | 1.390,000 | 1.349,000 | -2,9% |
| versão D · minutos observados no 1º ano, laranja | 1.492,000 | 1.322,000 | -11,4% |
| versão D · minutos observados no 1º ano, amarela | 448,000 | 440,000 | -1,8% |
| versão D · minutos observados no 1º ano, azul | 688,000 | 643,000 | -6,5% |

## Simulador: políticas e Monte Carlo (specs 008 e 009)

| Número | v1.1.0 | Após a revisão | Variação |
|---|---|---|---|
| minutos_por_ano.verde.media | 1.802,399 | 1.219,303 | -32,4% |
| minutos_por_ano.verde.ep | 83,349 | 58,956 | -29,3% |
| minutos_por_ano.verde.meiaLargura | 163,361 | 115,553 | -29,3% |
| minutos_por_ano.laranja.media | 1.704,493 | 1.318,515 | -22,6% |
| minutos_por_ano.laranja.ep | 90,111 | 52,972 | -41,2% |
| minutos_por_ano.laranja.meiaLargura | 176,614 | 103,823 | -41,2% |
| minutos_por_ano.amarela.media | 409,710 | 365,723 | -10,7% |
| minutos_por_ano.amarela.ep | 26,732 | 22,727 | -15,0% |
| minutos_por_ano.amarela.meiaLargura | 52,393 | 44,543 | -15,0% |
| minutos_por_ano.azul.media | 1.322,649 | 674,824 | -49,0% |
| minutos_por_ano.azul.ep | 181,425 | 35,950 | -80,2% |
| minutos_por_ano.azul.meiaLargura | 355,587 | 70,461 | -80,2% |
| minutos_por_ano.rede.media | 5.239,251 | 3.578,365 | -31,7% |
| minutos_por_ano.rede.ep | 224,251 | 101,113 | -54,9% |
| minutos_por_ano.rede.meiaLargura | 439,524 | 198,177 | -54,9% |
| minutos_cc_laranja_por_ano.media | 140,251 | 139,430 | -0,6% |
| minutos_cc_laranja_por_ano.ep | 20,754 | 20,740 | -0,1% |
| minutos_cc_laranja_por_ano.meiaLargura | 40,678 | 40,650 | -0,1% |
| rodadas_para_5pct_dia_util.verde | 18.435,000 | 21.291,000 | +15,5% |
| rodadas_para_5pct_dia_util.laranja | 25.097,000 | 14.778,000 | -41,1% |
| rodadas_para_5pct_dia_util.amarela | 40.288,000 | 37.633,000 | -6,6% |
| rodadas_para_5pct_dia_util.azul | 168.183,000 | 26.056,000 | -84,5% |
| meia_largura_pct_com_50000_dias.verde | 3,036 | 3,263 | +7,5% |
| meia_largura_pct_com_50000_dias.laranja | 3,542 | 2,718 | -23,3% |
| meia_largura_pct_com_50000_dias.amarela | 4,488 | 4,338 | -3,4% |
| meia_largura_pct_com_50000_dias.azul | 9,170 | 3,609 | -60,6% |
| disponibilidade_dia_util.verde.media | 0,995 | 0,997 | +0,2% |
| disponibilidade_dia_util.verde.dp | 0,017 | 0,012 | -29,2% |
| disponibilidade_dia_util.verde.meiaLargura | 0,001 | 0,000 | -29,2% |
| disponibilidade_dia_util.laranja.media | 0,995 | 0,997 | +0,1% |
| disponibilidade_dia_util.laranja.dp | 0,018 | 0,011 | -41,2% |
| disponibilidade_dia_util.laranja.meiaLargura | 0,001 | 0,000 | -41,2% |
| disponibilidade_dia_util.amarela.dp | 0,006 | 0,005 | -15,1% |
| disponibilidade_dia_util.azul.media | 0,996 | 0,998 | +0,2% |
| disponibilidade_dia_util.azul.dp | 0,038 | 0,007 | -80,3% |
| disponibilidade_dia_util.azul.ep | 0,001 | 0,000 | -80,3% |
| disponibilidade_dia_util.azul.meiaLargura | 0,001 | 0,000 | -80,3% |
| disp_od_dia_util.media | 0,992 | 0,995 | +0,2% |
| disp_od_dia_util.dp | 0,021 | 0,011 | -44,1% |
| disp_od_dia_util.meiaLargura | 0,001 | 0,000 | -44,1% |
| politicas.1.reservaFria.trens_hora.dp | 1,275 | 1,288 | +1,0% |
| politicas.1.reservaFria.trens_hora.ep | 0,023 | 0,024 | +1,0% |
| politicas.1.retiradaTrem.minutos_rede.media | -1,110 | -0,968 | -12,8% |
| politicas.1.retiradaTrem.minutos_rede.dp | 7,531 | 8,818 | +17,1% |
| politicas.1.retiradaTrem.minutos_rede.ep | 0,138 | 0,161 | +17,1% |
| politicas.1.retiradaTrem.minutos_rede.meiaLargura | 0,270 | 0,316 | +17,1% |
| politicas.1.retiradaTrem.trens_hora.media | -0,184 | -0,281 | +52,7% |
| politicas.1.retiradaTrem.trens_hora.dp | 6,056 | 7,414 | +22,4% |
| politicas.1.retiradaTrem.trens_hora.ep | 0,111 | 0,135 | +22,4% |
| politicas.1.retiradaTrem.trens_hora.meiaLargura | 0,217 | 0,265 | +22,4% |
| politicas.1.retiradaTrem.disp_od_pp.media | 0,050 | 0,049 | -1,8% |
| politicas.1.retiradaTrem.disp_od_pp.dp | 0,398 | 0,524 | +31,7% |
| politicas.1.retiradaTrem.disp_od_pp.ep | 0,007 | 0,010 | +31,7% |
| politicas.1.retiradaTrem.disp_od_pp.meiaLargura | 0,014 | 0,019 | +31,7% |
| politicas.1.retiradaTrem.par_interrompido_min.media | -0,599 | -0,588 | -1,8% |
| politicas.1.retiradaTrem.par_interrompido_min.dp | 4,767 | 6,276 | +31,7% |
| politicas.1.retiradaTrem.par_interrompido_min.ep | 0,087 | 0,115 | +31,7% |
| politicas.1.retiradaTrem.par_interrompido_min.meiaLargura | 0,171 | 0,225 | +31,7% |
| politicas.1.retiradaTrem.minutos_MR.media | -1,115 | -0,968 | -13,2% |
| politicas.1.retiradaTrem.minutos_MR.dp | 7,628 | 8,818 | +15,6% |
| politicas.1.retiradaTrem.minutos_MR.ep | 0,139 | 0,161 | +15,6% |
| politicas.1.retiradaTrem.minutos_MR.meiaLargura | 0,273 | 0,316 | +15,6% |
| politicas.1.operacaoDegradada.minutos_rede.media | -7,775 | -3,372 | -56,6% |
| politicas.1.operacaoDegradada.minutos_rede.dp | 52,826 | 16,649 | -68,5% |
| politicas.1.operacaoDegradada.minutos_rede.ep | 0,964 | 0,304 | -68,5% |
| politicas.1.operacaoDegradada.minutos_rede.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.1.operacaoDegradada.trens_hora.media | -16,372 | -2,316 | -85,9% |
| politicas.1.operacaoDegradada.trens_hora.dp | 234,171 | 24,537 | -89,5% |
| politicas.1.operacaoDegradada.trens_hora.ep | 4,275 | 0,448 | -89,5% |
| politicas.1.operacaoDegradada.trens_hora.meiaLargura | 8,380 | 0,878 | -89,5% |
| politicas.1.operacaoDegradada.disp_od_pp.media | 0,353 | 0,169 | -52,0% |
| politicas.1.operacaoDegradada.disp_od_pp.dp | 1,962 | 0,842 | -57,1% |
| politicas.1.operacaoDegradada.disp_od_pp.ep | 0,036 | 0,015 | -57,1% |
| politicas.1.operacaoDegradada.disp_od_pp.meiaLargura | 0,070 | 0,030 | -57,1% |
| politicas.1.operacaoDegradada.par_interrompido_min.media | -4,228 | -2,029 | -52,0% |
| politicas.1.operacaoDegradada.par_interrompido_min.dp | 23,500 | 10,088 | -57,1% |
| politicas.1.operacaoDegradada.par_interrompido_min.ep | 0,429 | 0,184 | -57,1% |
| politicas.1.operacaoDegradada.par_interrompido_min.meiaLargura | 0,841 | 0,361 | -57,1% |
| politicas.1.operacaoDegradada.minutos_EF.media | -7,780 | -3,372 | -56,7% |
| politicas.1.operacaoDegradada.minutos_EF.dp | 52,828 | 16,649 | -68,5% |
| politicas.1.operacaoDegradada.minutos_EF.ep | 0,964 | 0,304 | -68,5% |
| politicas.1.operacaoDegradada.minutos_EF.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.1.retornoParcial.disp_od_pp.media | 0,205 | 0,152 | -25,8% |
| politicas.1.retornoParcial.disp_od_pp.dp | 0,706 | 0,540 | -23,4% |
| politicas.1.retornoParcial.disp_od_pp.ep | 0,013 | 0,010 | -23,4% |
| politicas.1.retornoParcial.disp_od_pp.meiaLargura | 0,025 | 0,019 | -23,4% |
| politicas.1.retornoParcial.par_interrompido_min.media | -2,454 | -1,822 | -25,8% |
| politicas.1.retornoParcial.par_interrompido_min.dp | 8,454 | 6,475 | -23,4% |
| politicas.1.retornoParcial.par_interrompido_min.ep | 0,154 | 0,118 | -23,4% |
| politicas.1.retornoParcial.par_interrompido_min.meiaLargura | 0,303 | 0,232 | -23,4% |
| politicas.1.rotaAlternativa.disp_od_pp.media | 0,012 | 0,006 | -52,3% |
| politicas.1.rotaAlternativa.disp_od_pp.dp | 0,122 | 0,024 | -80,3% |
| politicas.1.rotaAlternativa.disp_od_pp.ep | 0,002 | 0,000 | -80,3% |
| politicas.1.rotaAlternativa.disp_od_pp.meiaLargura | 0,004 | 0,001 | -80,3% |
| politicas.1.rotaAlternativa.par_interrompido_min.media | -0,142 | -0,068 | -52,3% |
| politicas.1.rotaAlternativa.par_interrompido_min.dp | 1,459 | 0,287 | -80,3% |
| politicas.1.rotaAlternativa.par_interrompido_min.ep | 0,027 | 0,005 | -80,3% |
| politicas.1.rotaAlternativa.par_interrompido_min.meiaLargura | 0,052 | 0,010 | -80,3% |
| politicas.1.tratamentoCausaComum.minutos_rede.media | -0,790 | -0,784 | -0,8% |
| politicas.1.tratamentoCausaComum.minutos_rede.dp | 13,167 | 13,132 | -0,3% |
| politicas.1.tratamentoCausaComum.minutos_rede.meiaLargura | 0,471 | 0,470 | -0,3% |
| politicas.1.tratamentoCausaComum.trens_hora.dp | 10,360 | 10,367 | +0,1% |
| politicas.1.tratamentoCausaComum.disp_od_pp.dp | 0,376 | 0,374 | -0,4% |
| politicas.1.tratamentoCausaComum.par_interrompido_min.media | -0,285 | -0,283 | -0,7% |
| politicas.1.tratamentoCausaComum.par_interrompido_min.dp | 4,501 | 4,482 | -0,4% |
| politicas.1.tratamentoCausaComum.par_interrompido_min.meiaLargura | 0,161 | 0,160 | -0,4% |
| politicas.1.tratamentoCausaComum.minutos_CC.media | -0,790 | -0,784 | -0,7% |
| politicas.1.tratamentoCausaComum.minutos_CC.dp | 13,167 | 13,155 | -0,1% |
| politicas.2.reservaFria.minutos_rede.media | 0,001 | 0,002 | +200,0% |
| politicas.2.reservaFria.minutos_rede.dp | 0,037 | 0,082 | +123,6% |
| politicas.2.reservaFria.minutos_rede.meiaLargura | 0,001 | 0,003 | +123,6% |
| politicas.2.reservaFria.trens_hora.media | -1,360 | -1,364 | +0,3% |
| politicas.2.reservaFria.trens_hora.dp | 1,823 | 1,839 | +0,9% |
| politicas.2.reservaFria.trens_hora.ep | 0,033 | 0,034 | +0,9% |
| politicas.2.reservaFria.trens_hora.meiaLargura | 0,065 | 0,066 | +0,9% |
| politicas.2.reservaFria.par_interrompido_min.dp | 0,002 | 0,003 | +123,6% |
| politicas.2.reservaFria.minutos_MR.media | 0,001 | 0,002 | +200,0% |
| politicas.2.reservaFria.minutos_MR.dp | 0,037 | 0,082 | +123,6% |
| politicas.2.reservaFria.minutos_MR.meiaLargura | 0,001 | 0,003 | +123,6% |
| politicas.2.retiradaTrem.minutos_rede.media | -1,110 | -0,968 | -12,8% |
| politicas.2.retiradaTrem.minutos_rede.dp | 7,531 | 8,818 | +17,1% |
| politicas.2.retiradaTrem.minutos_rede.ep | 0,138 | 0,161 | +17,1% |
| politicas.2.retiradaTrem.minutos_rede.meiaLargura | 0,270 | 0,316 | +17,1% |
| politicas.2.retiradaTrem.trens_hora.media | -0,183 | -0,281 | +53,1% |
| politicas.2.retiradaTrem.trens_hora.dp | 6,056 | 7,414 | +22,4% |
| politicas.2.retiradaTrem.trens_hora.ep | 0,111 | 0,135 | +22,4% |
| politicas.2.retiradaTrem.trens_hora.meiaLargura | 0,217 | 0,265 | +22,4% |
| politicas.2.retiradaTrem.disp_od_pp.media | 0,050 | 0,049 | -1,8% |
| politicas.2.retiradaTrem.disp_od_pp.dp | 0,398 | 0,524 | +31,7% |
| politicas.2.retiradaTrem.disp_od_pp.ep | 0,007 | 0,010 | +31,7% |
| politicas.2.retiradaTrem.disp_od_pp.meiaLargura | 0,014 | 0,019 | +31,7% |
| politicas.2.retiradaTrem.par_interrompido_min.media | -0,599 | -0,588 | -1,8% |
| politicas.2.retiradaTrem.par_interrompido_min.dp | 4,767 | 6,276 | +31,7% |
| politicas.2.retiradaTrem.par_interrompido_min.ep | 0,087 | 0,115 | +31,7% |
| politicas.2.retiradaTrem.par_interrompido_min.meiaLargura | 0,171 | 0,225 | +31,7% |
| politicas.2.retiradaTrem.minutos_MR.media | -1,115 | -0,968 | -13,2% |
| politicas.2.retiradaTrem.minutos_MR.dp | 7,628 | 8,818 | +15,6% |
| politicas.2.retiradaTrem.minutos_MR.ep | 0,139 | 0,161 | +15,6% |
| politicas.2.retiradaTrem.minutos_MR.meiaLargura | 0,273 | 0,316 | +15,6% |
| politicas.2.operacaoDegradada.minutos_rede.media | -7,775 | -3,372 | -56,6% |
| politicas.2.operacaoDegradada.minutos_rede.dp | 52,826 | 16,649 | -68,5% |
| politicas.2.operacaoDegradada.minutos_rede.ep | 0,964 | 0,304 | -68,5% |
| politicas.2.operacaoDegradada.minutos_rede.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.2.operacaoDegradada.trens_hora.media | -16,366 | -2,312 | -85,9% |
| politicas.2.operacaoDegradada.trens_hora.dp | 234,169 | 24,524 | -89,5% |
| politicas.2.operacaoDegradada.trens_hora.ep | 4,275 | 0,448 | -89,5% |
| politicas.2.operacaoDegradada.trens_hora.meiaLargura | 8,379 | 0,878 | -89,5% |
| politicas.2.operacaoDegradada.disp_od_pp.media | 0,353 | 0,169 | -52,0% |
| politicas.2.operacaoDegradada.disp_od_pp.dp | 1,962 | 0,842 | -57,1% |
| politicas.2.operacaoDegradada.disp_od_pp.ep | 0,036 | 0,015 | -57,1% |
| politicas.2.operacaoDegradada.disp_od_pp.meiaLargura | 0,070 | 0,030 | -57,1% |
| politicas.2.operacaoDegradada.par_interrompido_min.media | -4,228 | -2,029 | -52,0% |
| politicas.2.operacaoDegradada.par_interrompido_min.dp | 23,500 | 10,088 | -57,1% |
| politicas.2.operacaoDegradada.par_interrompido_min.ep | 0,429 | 0,184 | -57,1% |
| politicas.2.operacaoDegradada.par_interrompido_min.meiaLargura | 0,841 | 0,361 | -57,1% |
| politicas.2.operacaoDegradada.minutos_EF.media | -7,780 | -3,372 | -56,7% |
| politicas.2.operacaoDegradada.minutos_EF.dp | 52,828 | 16,649 | -68,5% |
| politicas.2.operacaoDegradada.minutos_EF.ep | 0,964 | 0,304 | -68,5% |
| politicas.2.operacaoDegradada.minutos_EF.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.2.retornoParcial.disp_od_pp.media | 0,205 | 0,152 | -25,8% |
| politicas.2.retornoParcial.disp_od_pp.dp | 0,706 | 0,540 | -23,4% |
| politicas.2.retornoParcial.disp_od_pp.ep | 0,013 | 0,010 | -23,4% |
| politicas.2.retornoParcial.disp_od_pp.meiaLargura | 0,025 | 0,019 | -23,4% |
| politicas.2.retornoParcial.par_interrompido_min.media | -2,454 | -1,821 | -25,8% |
| politicas.2.retornoParcial.par_interrompido_min.dp | 8,454 | 6,475 | -23,4% |
| politicas.2.retornoParcial.par_interrompido_min.ep | 0,154 | 0,118 | -23,4% |
| politicas.2.retornoParcial.par_interrompido_min.meiaLargura | 0,303 | 0,232 | -23,4% |
| politicas.2.rotaAlternativa.disp_od_pp.media | 0,012 | 0,006 | -52,3% |
| politicas.2.rotaAlternativa.disp_od_pp.dp | 0,122 | 0,024 | -80,3% |
| politicas.2.rotaAlternativa.disp_od_pp.ep | 0,002 | 0,000 | -80,3% |
| politicas.2.rotaAlternativa.disp_od_pp.meiaLargura | 0,004 | 0,001 | -80,3% |
| politicas.2.rotaAlternativa.par_interrompido_min.media | -0,142 | -0,068 | -52,3% |
| politicas.2.rotaAlternativa.par_interrompido_min.dp | 1,459 | 0,287 | -80,3% |
| politicas.2.rotaAlternativa.par_interrompido_min.ep | 0,027 | 0,005 | -80,3% |
| politicas.2.rotaAlternativa.par_interrompido_min.meiaLargura | 0,052 | 0,010 | -80,3% |
| politicas.2.tratamentoCausaComum.minutos_rede.media | -0,790 | -0,784 | -0,8% |
| politicas.2.tratamentoCausaComum.minutos_rede.dp | 13,167 | 13,132 | -0,3% |
| politicas.2.tratamentoCausaComum.minutos_rede.meiaLargura | 0,471 | 0,470 | -0,3% |
| politicas.2.tratamentoCausaComum.trens_hora.dp | 10,360 | 10,367 | +0,1% |
| politicas.2.tratamentoCausaComum.disp_od_pp.dp | 0,376 | 0,374 | -0,4% |
| politicas.2.tratamentoCausaComum.par_interrompido_min.media | -0,285 | -0,283 | -0,7% |
| politicas.2.tratamentoCausaComum.par_interrompido_min.dp | 4,501 | 4,482 | -0,4% |
| politicas.2.tratamentoCausaComum.par_interrompido_min.meiaLargura | 0,161 | 0,160 | -0,4% |
| politicas.2.tratamentoCausaComum.minutos_CC.media | -0,790 | -0,784 | -0,7% |
| politicas.2.tratamentoCausaComum.minutos_CC.dp | 13,167 | 13,155 | -0,1% |
| politicas.4.reservaFria.minutos_rede.media | 0,041 | 0,009 | -78,0% |
| politicas.4.reservaFria.minutos_rede.dp | 1,841 | 0,196 | -89,4% |
| politicas.4.reservaFria.minutos_rede.ep | 0,034 | 0,004 | -89,4% |
| politicas.4.reservaFria.minutos_rede.meiaLargura | 0,066 | 0,007 | -89,4% |
| politicas.4.reservaFria.trens_hora.media | -3,075 | -3,110 | +1,1% |
| politicas.4.reservaFria.trens_hora.dp | 2,731 | 2,631 | -3,7% |
| politicas.4.reservaFria.trens_hora.ep | 0,050 | 0,048 | -3,7% |
| politicas.4.reservaFria.trens_hora.meiaLargura | 0,098 | 0,094 | -3,7% |
| politicas.4.reservaFria.disp_od_pp.dp | 0,006 | 0,001 | -89,4% |
| politicas.4.reservaFria.par_interrompido_min.media | 0,002 | 0,000 | -78,0% |
| politicas.4.reservaFria.par_interrompido_min.dp | 0,077 | 0,008 | -89,4% |
| politicas.4.reservaFria.par_interrompido_min.ep | 0,001 | 0,000 | -89,4% |
| politicas.4.reservaFria.par_interrompido_min.meiaLargura | 0,003 | 0,000 | -89,4% |
| politicas.4.reservaFria.minutos_MR.media | 0,041 | 0,009 | -78,0% |
| politicas.4.reservaFria.minutos_MR.dp | 1,841 | 0,196 | -89,4% |
| politicas.4.reservaFria.minutos_MR.ep | 0,034 | 0,004 | -89,4% |
| politicas.4.reservaFria.minutos_MR.meiaLargura | 0,066 | 0,007 | -89,4% |
| politicas.4.retiradaTrem.minutos_rede.media | -1,079 | -0,968 | -10,3% |
| politicas.4.retiradaTrem.minutos_rede.dp | 7,338 | 8,818 | +20,2% |
| politicas.4.retiradaTrem.minutos_rede.ep | 0,134 | 0,161 | +20,2% |
| politicas.4.retiradaTrem.minutos_rede.meiaLargura | 0,263 | 0,316 | +20,2% |
| politicas.4.retiradaTrem.trens_hora.media | -0,173 | -0,279 | +61,1% |
| politicas.4.retiradaTrem.trens_hora.dp | 6,033 | 7,406 | +22,8% |
| politicas.4.retiradaTrem.trens_hora.ep | 0,110 | 0,135 | +22,8% |
| politicas.4.retiradaTrem.trens_hora.meiaLargura | 0,216 | 0,265 | +22,8% |
| politicas.4.retiradaTrem.disp_od_pp.media | 0,050 | 0,049 | -1,6% |
| politicas.4.retiradaTrem.disp_od_pp.dp | 0,398 | 0,524 | +31,7% |
| politicas.4.retiradaTrem.disp_od_pp.ep | 0,007 | 0,010 | +31,7% |
| politicas.4.retiradaTrem.disp_od_pp.meiaLargura | 0,014 | 0,019 | +31,7% |
| politicas.4.retiradaTrem.par_interrompido_min.media | -0,598 | -0,588 | -1,6% |
| politicas.4.retiradaTrem.par_interrompido_min.dp | 4,766 | 6,276 | +31,7% |
| politicas.4.retiradaTrem.par_interrompido_min.ep | 0,087 | 0,115 | +31,7% |
| politicas.4.retiradaTrem.par_interrompido_min.meiaLargura | 0,171 | 0,225 | +31,7% |
| politicas.4.retiradaTrem.minutos_MR.media | -1,084 | -0,968 | -10,7% |
| politicas.4.retiradaTrem.minutos_MR.dp | 7,437 | 8,818 | +18,6% |
| politicas.4.retiradaTrem.minutos_MR.ep | 0,136 | 0,161 | +18,6% |
| politicas.4.retiradaTrem.minutos_MR.meiaLargura | 0,266 | 0,316 | +18,6% |
| politicas.4.operacaoDegradada.minutos_rede.media | -7,775 | -3,372 | -56,6% |
| politicas.4.operacaoDegradada.minutos_rede.dp | 52,826 | 16,649 | -68,5% |
| politicas.4.operacaoDegradada.minutos_rede.ep | 0,964 | 0,304 | -68,5% |
| politicas.4.operacaoDegradada.minutos_rede.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.4.operacaoDegradada.trens_hora.media | -16,326 | -2,294 | -86,0% |
| politicas.4.operacaoDegradada.trens_hora.dp | 233,804 | 24,464 | -89,5% |
| politicas.4.operacaoDegradada.trens_hora.ep | 4,269 | 0,447 | -89,5% |
| politicas.4.operacaoDegradada.trens_hora.meiaLargura | 8,366 | 0,875 | -89,5% |
| politicas.4.operacaoDegradada.disp_od_pp.media | 0,353 | 0,169 | -52,0% |
| politicas.4.operacaoDegradada.disp_od_pp.dp | 1,962 | 0,842 | -57,1% |
| politicas.4.operacaoDegradada.disp_od_pp.ep | 0,036 | 0,015 | -57,1% |
| politicas.4.operacaoDegradada.disp_od_pp.meiaLargura | 0,070 | 0,030 | -57,1% |
| politicas.4.operacaoDegradada.par_interrompido_min.media | -4,228 | -2,029 | -52,0% |
| politicas.4.operacaoDegradada.par_interrompido_min.dp | 23,500 | 10,088 | -57,1% |
| politicas.4.operacaoDegradada.par_interrompido_min.ep | 0,429 | 0,184 | -57,1% |
| politicas.4.operacaoDegradada.par_interrompido_min.meiaLargura | 0,841 | 0,361 | -57,1% |
| politicas.4.operacaoDegradada.minutos_EF.media | -7,780 | -3,372 | -56,7% |
| politicas.4.operacaoDegradada.minutos_EF.dp | 52,828 | 16,649 | -68,5% |
| politicas.4.operacaoDegradada.minutos_EF.ep | 0,964 | 0,304 | -68,5% |
| politicas.4.operacaoDegradada.minutos_EF.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.4.retornoParcial.disp_od_pp.media | 0,205 | 0,152 | -25,7% |
| politicas.4.retornoParcial.disp_od_pp.dp | 0,706 | 0,540 | -23,4% |
| politicas.4.retornoParcial.disp_od_pp.ep | 0,013 | 0,010 | -23,4% |
| politicas.4.retornoParcial.disp_od_pp.meiaLargura | 0,025 | 0,019 | -23,4% |
| politicas.4.retornoParcial.par_interrompido_min.media | -2,453 | -1,821 | -25,7% |
| politicas.4.retornoParcial.par_interrompido_min.dp | 8,453 | 6,475 | -23,4% |
| politicas.4.retornoParcial.par_interrompido_min.ep | 0,154 | 0,118 | -23,4% |
| politicas.4.retornoParcial.par_interrompido_min.meiaLargura | 0,302 | 0,232 | -23,4% |
| politicas.4.rotaAlternativa.disp_od_pp.media | 0,012 | 0,006 | -52,3% |
| politicas.4.rotaAlternativa.disp_od_pp.dp | 0,122 | 0,024 | -80,3% |
| politicas.4.rotaAlternativa.disp_od_pp.ep | 0,002 | 0,000 | -80,3% |
| politicas.4.rotaAlternativa.disp_od_pp.meiaLargura | 0,004 | 0,001 | -80,3% |
| politicas.4.rotaAlternativa.par_interrompido_min.media | -0,142 | -0,068 | -52,3% |
| politicas.4.rotaAlternativa.par_interrompido_min.dp | 1,459 | 0,287 | -80,3% |
| politicas.4.rotaAlternativa.par_interrompido_min.ep | 0,027 | 0,005 | -80,3% |
| politicas.4.rotaAlternativa.par_interrompido_min.meiaLargura | 0,052 | 0,010 | -80,3% |
| politicas.4.tratamentoCausaComum.minutos_rede.media | -0,790 | -0,784 | -0,8% |
| politicas.4.tratamentoCausaComum.minutos_rede.dp | 13,167 | 13,132 | -0,3% |
| politicas.4.tratamentoCausaComum.minutos_rede.meiaLargura | 0,471 | 0,470 | -0,3% |
| politicas.4.tratamentoCausaComum.trens_hora.dp | 10,154 | 10,161 | +0,1% |
| politicas.4.tratamentoCausaComum.trens_hora.ep | 0,185 | 0,186 | +0,1% |
| politicas.4.tratamentoCausaComum.trens_hora.meiaLargura | 0,363 | 0,364 | +0,1% |
| politicas.4.tratamentoCausaComum.disp_od_pp.dp | 0,376 | 0,374 | -0,4% |
| politicas.4.tratamentoCausaComum.par_interrompido_min.media | -0,285 | -0,283 | -0,7% |
| politicas.4.tratamentoCausaComum.par_interrompido_min.dp | 4,501 | 4,482 | -0,4% |
| politicas.4.tratamentoCausaComum.par_interrompido_min.meiaLargura | 0,161 | 0,160 | -0,4% |
| politicas.4.tratamentoCausaComum.minutos_CC.media | -0,790 | -0,784 | -0,7% |
| politicas.4.tratamentoCausaComum.minutos_CC.dp | 13,167 | 13,155 | -0,1% |
| politicas.0.5.reservaFria.trens_hora.media | -0,299 | -0,306 | +2,1% |
| politicas.0.5.reservaFria.trens_hora.dp | 0,926 | 0,913 | -1,3% |
| politicas.0.5.retiradaTrem.minutos_rede.media | -1,110 | -0,968 | -12,8% |
| politicas.0.5.retiradaTrem.minutos_rede.dp | 7,531 | 8,818 | +17,1% |
| politicas.0.5.retiradaTrem.minutos_rede.ep | 0,138 | 0,161 | +17,1% |
| politicas.0.5.retiradaTrem.minutos_rede.meiaLargura | 0,270 | 0,316 | +17,1% |
| politicas.0.5.retiradaTrem.trens_hora.media | -0,184 | -0,281 | +52,8% |
| politicas.0.5.retiradaTrem.trens_hora.dp | 6,056 | 7,414 | +22,4% |
| politicas.0.5.retiradaTrem.trens_hora.ep | 0,111 | 0,135 | +22,4% |
| politicas.0.5.retiradaTrem.trens_hora.meiaLargura | 0,217 | 0,265 | +22,4% |
| politicas.0.5.retiradaTrem.disp_od_pp.media | 0,050 | 0,049 | -1,8% |
| politicas.0.5.retiradaTrem.disp_od_pp.dp | 0,398 | 0,524 | +31,7% |
| politicas.0.5.retiradaTrem.disp_od_pp.ep | 0,007 | 0,010 | +31,7% |
| politicas.0.5.retiradaTrem.disp_od_pp.meiaLargura | 0,014 | 0,019 | +31,7% |
| politicas.0.5.retiradaTrem.par_interrompido_min.media | -0,599 | -0,588 | -1,8% |
| politicas.0.5.retiradaTrem.par_interrompido_min.dp | 4,767 | 6,276 | +31,7% |
| politicas.0.5.retiradaTrem.par_interrompido_min.ep | 0,087 | 0,115 | +31,7% |
| politicas.0.5.retiradaTrem.par_interrompido_min.meiaLargura | 0,171 | 0,225 | +31,7% |
| politicas.0.5.retiradaTrem.minutos_MR.media | -1,115 | -0,968 | -13,2% |
| politicas.0.5.retiradaTrem.minutos_MR.dp | 7,628 | 8,818 | +15,6% |
| politicas.0.5.retiradaTrem.minutos_MR.ep | 0,139 | 0,161 | +15,6% |
| politicas.0.5.retiradaTrem.minutos_MR.meiaLargura | 0,273 | 0,316 | +15,6% |
| politicas.0.5.operacaoDegradada.minutos_rede.media | -7,775 | -3,372 | -56,6% |
| politicas.0.5.operacaoDegradada.minutos_rede.dp | 52,826 | 16,649 | -68,5% |
| politicas.0.5.operacaoDegradada.minutos_rede.ep | 0,964 | 0,304 | -68,5% |
| politicas.0.5.operacaoDegradada.minutos_rede.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.0.5.operacaoDegradada.trens_hora.media | -16,374 | -2,323 | -85,8% |
| politicas.0.5.operacaoDegradada.trens_hora.dp | 234,171 | 24,546 | -89,5% |
| politicas.0.5.operacaoDegradada.trens_hora.ep | 4,275 | 0,448 | -89,5% |
| politicas.0.5.operacaoDegradada.trens_hora.meiaLargura | 8,380 | 0,878 | -89,5% |
| politicas.0.5.operacaoDegradada.disp_od_pp.media | 0,353 | 0,169 | -52,0% |
| politicas.0.5.operacaoDegradada.disp_od_pp.dp | 1,962 | 0,842 | -57,1% |
| politicas.0.5.operacaoDegradada.disp_od_pp.ep | 0,036 | 0,015 | -57,1% |
| politicas.0.5.operacaoDegradada.disp_od_pp.meiaLargura | 0,070 | 0,030 | -57,1% |
| politicas.0.5.operacaoDegradada.par_interrompido_min.media | -4,228 | -2,029 | -52,0% |
| politicas.0.5.operacaoDegradada.par_interrompido_min.dp | 23,500 | 10,088 | -57,1% |
| politicas.0.5.operacaoDegradada.par_interrompido_min.ep | 0,429 | 0,184 | -57,1% |
| politicas.0.5.operacaoDegradada.par_interrompido_min.meiaLargura | 0,841 | 0,361 | -57,1% |
| politicas.0.5.operacaoDegradada.minutos_EF.media | -7,780 | -3,372 | -56,7% |
| politicas.0.5.operacaoDegradada.minutos_EF.dp | 52,828 | 16,649 | -68,5% |
| politicas.0.5.operacaoDegradada.minutos_EF.ep | 0,964 | 0,304 | -68,5% |
| politicas.0.5.operacaoDegradada.minutos_EF.meiaLargura | 1,890 | 0,596 | -68,5% |
| politicas.0.5.retornoParcial.disp_od_pp.media | 0,205 | 0,152 | -25,8% |
| politicas.0.5.retornoParcial.disp_od_pp.dp | 0,706 | 0,540 | -23,4% |
| politicas.0.5.retornoParcial.disp_od_pp.ep | 0,013 | 0,010 | -23,4% |
| politicas.0.5.retornoParcial.disp_od_pp.meiaLargura | 0,025 | 0,019 | -23,4% |
| politicas.0.5.retornoParcial.par_interrompido_min.media | -2,454 | -1,822 | -25,8% |
| politicas.0.5.retornoParcial.par_interrompido_min.dp | 8,454 | 6,475 | -23,4% |
| politicas.0.5.retornoParcial.par_interrompido_min.ep | 0,154 | 0,118 | -23,4% |
| politicas.0.5.retornoParcial.par_interrompido_min.meiaLargura | 0,303 | 0,232 | -23,4% |
| politicas.0.5.rotaAlternativa.disp_od_pp.media | 0,012 | 0,006 | -52,3% |
| politicas.0.5.rotaAlternativa.disp_od_pp.dp | 0,122 | 0,024 | -80,3% |
| politicas.0.5.rotaAlternativa.disp_od_pp.ep | 0,002 | 0,000 | -80,3% |
| politicas.0.5.rotaAlternativa.disp_od_pp.meiaLargura | 0,004 | 0,001 | -80,3% |
| politicas.0.5.rotaAlternativa.par_interrompido_min.media | -0,142 | -0,068 | -52,3% |
| politicas.0.5.rotaAlternativa.par_interrompido_min.dp | 1,459 | 0,287 | -80,3% |
| politicas.0.5.rotaAlternativa.par_interrompido_min.ep | 0,027 | 0,005 | -80,3% |
| politicas.0.5.rotaAlternativa.par_interrompido_min.meiaLargura | 0,052 | 0,010 | -80,3% |
| politicas.0.5.tratamentoCausaComum.minutos_rede.media | -0,790 | -0,784 | -0,8% |
| politicas.0.5.tratamentoCausaComum.minutos_rede.dp | 13,167 | 13,132 | -0,3% |
| politicas.0.5.tratamentoCausaComum.minutos_rede.meiaLargura | 0,471 | 0,470 | -0,3% |
| politicas.0.5.tratamentoCausaComum.trens_hora.dp | 10,360 | 10,367 | +0,1% |
| politicas.0.5.tratamentoCausaComum.disp_od_pp.dp | 0,376 | 0,374 | -0,4% |
| politicas.0.5.tratamentoCausaComum.par_interrompido_min.media | -0,285 | -0,283 | -0,7% |
| politicas.0.5.tratamentoCausaComum.par_interrompido_min.dp | 4,501 | 4,482 | -0,4% |
| politicas.0.5.tratamentoCausaComum.par_interrompido_min.meiaLargura | 0,161 | 0,160 | -0,4% |
| politicas.0.5.tratamentoCausaComum.minutos_CC.media | -0,790 | -0,784 | -0,7% |
| politicas.0.5.tratamentoCausaComum.minutos_CC.dp | 13,167 | 13,155 | -0,1% |

