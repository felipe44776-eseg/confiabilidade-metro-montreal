# 012 — Validação contra o histórico (backtest)

**Status:** especificada
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

## Fora de escopo
- Recalibrar até o modelo passar no teste. Qualquer mudança feita depois de ver o período de teste fica registrada com data, e o teste é repetido num período diferente.

## Riscos e dependências
- 18 meses × 4 linhas dão 72 comparações; a cobertura tem incerteza grande. O relatório deve mostrar o intervalo dessa cobertura.
- Mudança de frota ao longo do período (Azur indo para a Azul, segundo a imprensa) pode mudar a taxa; precisa entrar como fator se confirmada.

## Perguntas em aberto
- Vale fazer validação cruzada por ano (deixar um ano de fora de cada vez) além do corte em 2025?
