# Políticas de tolerância a falhas e Monte Carlo (specs 008 e 009)

Gerado por `app/relatorios/politicas.relatorio.ts` com o motor do simulador e o `parametros.json` real (4e5a3d4+alteracoes-locais), semente 20261021. Intervalos de 95% pela aproximação normal; diferenças pareadas com números aleatórios comuns (as mesmas falhas nas duas variantes).

## Minutos de interrupção por ano, sem políticas (spec 009)

4000 dias simulados por tipo de dia (útil, sábado, domingo), somados pelo calendário de 251, 52 e 62 dias. Tempo: 11,7 s para 12000 dias numa thread.

| Linha | Minutos por ano (IC 95%) | Disponibilidade no dia útil | Rodadas para 5% de precisão no dia útil |
|---|---|---|---|
| verde | 1.802 (1.639 a 1.966) | 99,504% | 18.435 |
| laranja | 1.704 (1.528 a 1.881) | 99,545% | 25.097 |
| amarela | 410 (357 a 462) | 99,892% | 40.288 |
| azul | 1.323 (967 a 1.678) | 99,635% | 168.183 |
| rede (soma) | 5.239 (4.800 a 5.679) | disponibilidade origem-destino 99,246% | |

Laranja contra o painel: o painel tem 1.852 min/ano (Monte Carlo) e 1.797 (analítico). O intervalo do motor é 1.528 a 1.881 (contém 1.852; contém 1.797). Diferenças de definição: o motor soma a causa comum de todos os grupos de linhas que incluem a Laranja (140 min/ano; 44 dos 45 eventos multilinha), o painel só a Verde–Laranja (31 eventos); o motor usa a taxa de 2025 do modelo da spec 005 e o horário do GTFS, o painel a média de 2019 a 2026; o motor conta a união dos intervalos bloqueados (falhas sobrepostas não somam duas vezes), o painel soma as durações. A duração positiva é sorteada da amostra observada (a lognormal subestimava a média em 23% a 29% na Laranja; decisão de 2026-10-21).

## Cada política contra nenhuma política (spec 008)

3000 dias úteis por política. Valores negativos = a política reduz. "Minutos" é a soma das quatro linhas por dia útil; MR, EF e CC separam o efeito pela causa da interrupção.

### Reparo na oficina de 0,5 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,30 (-0,33 a -0,27) | 0,000 (0,000 a 0,000) | 18,2 (16,9 a 19,6) |
| Retirada do trem falho | -1,1 (-1,4 a -0,8) | -1,1 (-1,4 a -0,8) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,18 (-0,40 a 0,03) | 0,050 (0,036 a 0,064) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -16,37 (-24,75 a -7,99) | 0,353 (0,283 a 0,423) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,205 (0,180 a 0,230) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,012 (0,007 a 0,016) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,89 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

### Reparo na oficina de 1,0 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,63 (-0,67 a -0,58) | 0,000 (0,000 a 0,000) | 32,5 (30,9 a 34,2) |
| Retirada do trem falho | -1,1 (-1,4 a -0,8) | -1,1 (-1,4 a -0,8) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,18 (-0,40 a 0,03) | 0,050 (0,036 a 0,064) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -16,37 (-24,75 a -7,99) | 0,353 (0,283 a 0,423) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,205 (0,180 a 0,230) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,012 (0,007 a 0,016) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,89 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

### Reparo na oficina de 2,0 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (-0,0 a 0,0) | 0,0 (-0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -1,36 (-1,43 a -1,29) | -0,000 (-0,000 a 0,000) | 50,0 (48,2 a 51,8) |
| Retirada do trem falho | -1,1 (-1,4 a -0,8) | -1,1 (-1,4 a -0,8) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,18 (-0,40 a 0,03) | 0,050 (0,036 a 0,064) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -16,37 (-24,75 a -7,99) | 0,353 (0,283 a 0,423) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,205 (0,180 a 0,230) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,012 (0,007 a 0,016) | 0,0 (0,0 a 0,0) |
| Tratamento de causa comum | -0,8 (-1,3 a -0,3) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,8 (-1,3 a -0,3) | -0,52 (-0,89 a -0,15) | 0,024 (0,010 a 0,037) | 0,0 (0,0 a 0,0) |

### Reparo na oficina de 4,0 dia(s) (hipótese)

| Política | Minutos de interrupção | Material rodante | Equip. fixos | Causa comum | Trens-hora perdidos | Disp. origem-destino (p.p.) | Frota completa na Laranja (p.p.) |
|---|---|---|---|---|---|---|---|
| Reserva fria k-de-n | 0,0 (-0,0 a 0,1) | 0,0 (-0,0 a 0,1) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -3,08 (-3,17 a -2,98) | -0,000 (-0,000 a 0,000) | 58,2 (56,4 a 59,9) |
| Retirada do trem falho | -1,1 (-1,3 a -0,8) | -1,1 (-1,4 a -0,8) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | -0,17 (-0,39 a 0,04) | 0,050 (0,036 a 0,064) | 0,0 (0,0 a 0,0) |
| Operação degradada (marcha lenta) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -7,8 (-9,7 a -5,9) | 0,0 (0,0 a 0,0) | -16,33 (-24,69 a -7,96) | 0,353 (0,283 a 0,423) | 0,0 (0,0 a 0,0) |
| Retorno parcial antes do trecho bloqueado | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,205 (0,180 a 0,230) | 0,0 (0,0 a 0,0) |
| Rota alternativa de passageiros | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,0 (0,0 a 0,0) | 0,00 (0,00 a 0,00) | 0,012 (0,007 a 0,016) | 0,0 (0,0 a 0,0) |
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

