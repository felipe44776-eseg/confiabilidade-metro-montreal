# Políticas de tolerância a falhas e Monte Carlo (specs 008 e 009)

Gerado por `app/relatorios/politicas.relatorio.ts` com o motor do simulador e o `parametros.json` real (sha256-scripts:a0ff551bd3d56c35), semente 20261021. Intervalos de 95% pela aproximação normal; diferenças pareadas com números aleatórios comuns (as mesmas falhas nas duas variantes).

## Minutos de interrupção por ano, sem políticas (spec 009)

4000 dias simulados por tipo de dia (útil, sábado, domingo), somados pelo calendário de 251, 52 e 62 dias. Tempo: 9,0 s para 12000 dias numa thread.

| Linha | Minutos por ano (IC 95%) | Disponibilidade no dia útil | Rodadas para 5% de precisão no dia útil | Meia-largura com 50.000 dias (% da média) |
|---|---|---|---|---|
| verde | 1.219 (1.104 a 1.335) | 99,673% | 21.291 | 3,3 |
| laranja | 1.319 (1.215 a 1.422) | 99,652% | 14.778 | 2,7 |
| amarela | 366 (321 a 410) | 99,905% | 37.633 | 4,3 |
| azul | 675 (604 a 745) | 99,818% | 26.056 | 3,6 |
| rede (soma) | 3.578 (3.380 a 3.777) | disponibilidade origem-destino 99,484% | |

Laranja contra o painel: o painel tem 1.639 min/ano (Monte Carlo) e 1.601 (analítico), lidos de `dados/derivados/painel/corredor.json` (na v1.1.0, 1.852 e 1.797). O intervalo do motor é 1.215 a 1.422 (não contém 1.639; não contém 1.601). Diferenças de definição: o motor soma a causa comum de todos os grupos de linhas que incluem a Laranja (139 min/ano; 44 dos 45 eventos multilinha), o painel só a Verde–Laranja (31 eventos); o motor usa a taxa de 2025 (por fonte desde a revisão de 2026-11, specs 018 e 019) e o horário do GTFS, o painel a média de 2019 a 2026; o motor conta a união dos intervalos bloqueados (falhas sobrepostas não somam duas vezes), o painel soma as durações. A duração positiva é sorteada da amostra observada (a média observada era 23% a 29% maior que a da lognormal na Laranja; decisão de 2026-10-21).

## Cada política contra nenhuma política (spec 008)

3000 dias úteis por política. Valores negativos = a política reduz. "Minutos" é a soma das quatro linhas por dia útil; MR, EF e CC separam o efeito pela causa da interrupção.

### Reparo na oficina de 0,5 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,31 (-0,34 a -0,27) | 0,000 (0,000 a 0,000) | 18,2 (16,9 a 19,6) |
| Retirada do trem falho | -1,0 (-1,3 a -0,7) | -1,0 (-1,3 a -0,7) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,28 (-0,55 a -0,02) | 0,049 (0,030 a 0,068) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -2,32 (-3,20 a -1,44) | 0,169 (0,139 a 0,199) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,152 (0,133 a 0,171) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,006 (0,005 a 0,007) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,89 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

### Reparo na oficina de 1,0 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,63 (-0,67 a -0,58) | 0,000 (0,000 a 0,000) | 32,5 (30,9 a 34,2) |
| Retirada do trem falho | -1,0 (-1,3 a -0,7) | -1,0 (-1,3 a -0,7) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,28 (-0,55 a -0,02) | 0,049 (0,030 a 0,068) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -2,32 (-3,19 a -1,44) | 0,169 (0,139 a 0,199) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,152 (0,133 a 0,171) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,006 (0,005 a 0,007) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,89 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

### Reparo na oficina de 2,0 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (-0,0 a 0,0) | 0,0 (-0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -1,36 (-1,43 a -1,30) | -0,000 (-0,000 a 0,000) | 50,0 (48,2 a 51,8) |
| Retirada do trem falho | -1,0 (-1,3 a -0,7) | -1,0 (-1,3 a -0,7) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,28 (-0,55 a -0,02) | 0,049 (0,030 a 0,068) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -2,31 (-3,19 a -1,43) | 0,169 (0,139 a 0,199) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,152 (0,133 a 0,171) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,006 (0,005 a 0,007) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,89 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

### Reparo na oficina de 4,0 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -3,11 (-3,20 a -3,02) | -0,000 (-0,000 a -0,000) | 58,2 (56,4 a 59,9) |
| Retirada do trem falho | -1,0 (-1,3 a -0,7) | -1,0 (-1,3 a -0,7) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,28 (-0,54 a -0,01) | 0,049 (0,030 a 0,068) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -3,4 (-4,0 a -2,8) | 0,0 (0,0 a 0,0) | -2,29 (-3,17 a -1,42) | 0,169 (0,139 a 0,199) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,152 (0,133 a 0,171) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,006 (0,005 a 0,007) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,88 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

## Hipóteses e avisos

- intervalo_minimo_s = 90 s
- sentidos_bloqueio_ef = 2
- tempo_transferencia_min = 4 min
- um trem por trecho e sentido (simplificação da spec 007)
- reservas_por_linha = 2
- reparo_oficina_dias = 1 dias
- p_retirada = 1
- retorno parcial: só nas pontas de viagem do horário (aparelhos de mudança de via não verificados)
- O retorno parcial usa só as pontas de viagem do horário: a posição dos aparelhos de mudança de via não está verificada. O resultado dessa política é hipótese.
- O tempo de reparo na oficina não está em nenhuma fonte (0,5 a 4 dias); a sensibilidade está nas tabelas acima.

