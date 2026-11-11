# 012 — Validação contra o histórico (backtest)

**Status:** implementada com exceções
**Fase:** F5 (semanas 8 e 9)
**Depende de:** 005, 006, 007, 009

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** O backtest foi refeito sobre os dados revistos, marcado como posterior (pós-hoc); o resultado oficial continua o da v1.1.0. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

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
| Minutos parados de 2025 dentro do IC 95% | **Exceção na versão A** (Verde e Amarela acima do observado); nas versões B e C (2025) e D (2023, primeiro ano do seu teste), as 4 linhas ficam dentro |
| Greve separada | **Atende**: meses de greve com cobertura própria (A: 56,2%; C: 93,8%) |
| Onde o modelo falhou, linha a linha | **Atende** |
| Comparação com o treino só até 2023-09 | **Atende**: versão B, pré-registrada, 81,9% (59 de 72) |

Registro de mudança (2026-10-21, depois de ver a versão A): versão C, com o efeito do ano sorteado entre os anos do treino, 84,7% no mesmo teste. Como a spec pede, a regra foi testada de novo num período diferente (versão D: treino até 2022-12, teste de 2023-01 a 2024-06): 90,3% (65 de 72; IC 81,0%–96,0%), PIT com KS p = 0,16 e minutos parados dentro do intervalo nas 4 linhas. O resultado oficial do critério continua sendo o da versão A.

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D57, D60, D61 e D63; spec 020).* Os critérios acima não mudam. **O resultado oficial desta spec continua sendo o da v1.1.0:** a versão A, pré-registrada, cobriu 66,7% dos casos e não passou. O que segue foi refeito depois de ver os dados (pós-hoc) e não substitui o oficial.

- **O que mudou na entrada:** duração pela faixa oficial nas 100 exceções (D55), exposição medida pelo km real até 2026-06 (D57), dias de greve com o fator típico (D63).
- **O que mudou no método:** nada nas versões A a D: mesmo modelo por família da spec 005, mesmas regras do ano, B = 100. Foram acrescentados alvos (spec 020): cobertura por família, falhas de 5 min ou mais e minutos por família no primeiro ano do teste, só como intervalo, sem PIT.

| Número | v1.1.0 (oficial) | Após a revisão (pós-hoc) |
|---|---|---|
| A: cobertura do IP 90% | 66,7% (48/72; 54,6%–77,3%) | 65,3% (47/72; 53,1%–76,1%) |
| A: fora acima / abaixo | 2 / 22 | 1 / 24 |
| A: PIT (KS) | p = 2,4e-11 | p = 5,3e-12 |
| B: cobertura | 81,9% (59/72) | 84,7% (61/72; 74,3%–92,1%) |
| C: cobertura | 84,7% (61/72) | 87,5% (63/72; 77,6%–94,1%) |
| D: cobertura | 90,3% (65/72) | 90,3% (65/72; 81,0%–96,0%) |
| D: PIT (KS) | p = 0,16 | p = 0,05 |
| Minutos parados no 1º ano, linhas fora do IC 95% na versão A | Verde e Amarela | Verde, Laranja e Amarela |
| Minutos da Azul no 1º ano, versão A (previsto, mediana, contra observado) | 2.962 contra 708 | 850 contra 660, dentro do IC |

- **Leitura:** a conclusão não muda. A versão pré-registrada continua fora do critério (65,3%), e a regra corrigida continua passando no período diferente (D, 90,3%).
- **Por família (novo):** a falha da versão A está nos equipamentos fixos: cobertura de 65,3% neles e de 87,5% no material rodante. Com o efeito do ano sorteado (C), 98,6% e 86,1%. É o que a revisão achou na causa do "2024 atípico": 516 registros de via com sintoma de trem, quase todos de zero minuto e nos terminais (spec 017), que a versão A carrega para 2025.
- **Falhas de 5 min ou mais no primeiro ano (novo):** na versão C, as quatro linhas ficam dentro do IC 95%; na A, o observado fica abaixo do IC na Verde e na Laranja (o modelo previu mais).
- **D, PIT:** o p do KS cai de 0,16 para 0,05, no limite do critério de compatibilidade com a uniforme usado na leitura de 2026-10-21. Fica registrado.
- **Teste fora da amostra de verdade:** os modelos da v1.1.0 e o revisto ficaram congelados antes de a STM publicar os meses depois de 2026-06 (`fontes/verificacao/preregistro/`, spec 020). Esse é o teste que nenhuma das versões viu.

## Fora de escopo
- Recalibrar até o modelo passar no teste. Qualquer mudança feita depois de ver o período de teste fica registrada com data, e o teste é repetido num período diferente.

## Riscos e dependências
- 18 meses × 4 linhas dão 72 comparações; a cobertura tem incerteza grande. O relatório deve mostrar o intervalo dessa cobertura.
- Mudança de frota ao longo do período (Azur indo para a Azul, segundo a imprensa) pode mudar a taxa; precisa entrar como fator se confirmada.

## Perguntas em aberto
- Vale fazer validação cruzada por ano (deixar um ano de fora de cada vez) além do corte em 2025?
