# 012 — Validação contra o histórico (backtest)

**Status:** implementada com exceções
**Fase:** F5 (semanas 8 e 9)
**Depende de:** 005, 006, 007, 009

## Pergunta de engenharia
O modelo ajustado só com 2019 a 2024 consegue prever o que aconteceu de janeiro de 2025 a junho de 2026? O número que responde é a cobertura do intervalo de predição de 90% por linha e mês.

## Contexto
- A base vai de 2019-01-01 a 2026-06-30 (FONTES.md). O período de teste tem 18 meses.
- O período de teste inclui greves da STM em 2025, que reduzem a oferta (spec 003).
- A exposição medida (km real) só vai até 2023-09-30; depois disso é estimada pelo horário (spec 004).

## Critérios de aceite
- Dados os parâmetros ajustados só com dados até 2024-12-31, quando a simulação prevê cada linha e mês de 2025-01 a 2026-06, então o intervalo de predição de 90% contém o número observado de falhas em 80% a 98% dos casos linha × mês.
- Dadas as previsões, quando avaliadas, então o histograma do PIT (posição do valor observado na distribuição prevista) é aproximadamente uniforme, e o relatório traz o gráfico.
- Dados os minutos parados por ano em 2025, quando comparados, então o valor observado de cada linha cai dentro do intervalo de 95% previsto, ou o relatório explica a diferença.
- Dado o período de greve, quando avaliado, então aparece separado no relatório, para não mascarar o resto do ano.
- Dado o relatório final, quando publicado, então lista também onde o modelo falhou, linha a linha.
- Dado o ajuste, quando refeito com dados até 2023-09-30 (só exposição medida), então o relatório compara as duas versões.

## Resultado (2026-10-21)

Script `pipeline/backtest.py`; testes em `pipeline/tests/test_backtest.py`; relatório [`backtest.md`](../../fontes/verificacao/backtest.md) com os 72 casos.

| Critério | Resultado |
|---|---|
| IP 90% contém o observado em 80% a 98% dos casos linha × mês (treino até 2024-12) | **Exceção**: 66,7% (48 de 72; IC 54,6%–77,3%) na versão A, pré-registrada. 22 dos 24 casos fora ficam abaixo do intervalo: o efeito do ano de 2024, que foi atípico (cerca de 1.000 falhas no 2º semestre, contra cerca de 500 nos vizinhos), superestima 2025 |
| PIT aproximadamente uniforme, com gráfico | **Exceção na versão A** (KS p = 2,4e-11, concentrado perto de zero); gráficos em `backtest_pit.svg` e `backtest_pit_C.svg` |
| Minutos parados de 2025 dentro do IC 95% | **Exceção na versão A** (Verde e Amarela acima do observado); nas versões B, C e D, as 4 linhas ficam dentro |
| Greve separada | **Atende**: meses de greve com cobertura própria (A: 56,2%; C: 93,8%) |
| Onde o modelo falhou, linha a linha | **Atende** |
| Comparação com o treino só até 2023-09 | **Atende**: versão B, pré-registrada, 81,9% (59 de 72) |

Registro de mudança (2026-10-21, depois de ver a versão A): versão C, com o efeito do ano sorteado entre os anos do treino, 84,7% no mesmo teste. Como a spec pede, a regra foi testada de novo num período diferente (versão D: treino até 2022-12, teste de 2023-01 a 2024-06): 90,3% (65 de 72; IC 81,0%–96,0%), PIT com KS p = 0,16 e minutos parados dentro do intervalo nas 4 linhas. O resultado oficial do critério continua sendo o da versão A.

## Fora de escopo
- Recalibrar até o modelo passar no teste. Qualquer mudança feita depois de ver o período de teste fica registrada com data, e o teste é repetido num período diferente.

## Riscos e dependências
- 18 meses × 4 linhas dão 72 comparações; a cobertura tem incerteza grande. O relatório deve mostrar o intervalo dessa cobertura.
- Mudança de frota ao longo do período (Azur indo para a Azul, segundo a imprensa) pode mudar a taxa; precisa entrar como fator se confirmada.

## Perguntas em aberto
- Vale fazer validação cruzada por ano (deixar um ano de fora de cada vez) além do corte em 2025?
