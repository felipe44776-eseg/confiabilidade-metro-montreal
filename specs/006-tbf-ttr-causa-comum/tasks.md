# 006 — Tempo entre falhas, tempo até restabelecer e causa comum: tarefas

- [x] Estratos linha × causa, × frota e × condição (inverno ou resto do ano); herança abaixo de 30 intervalos.
- [x] Cinco famílias por máxima verossimilhança; AIC; KS e Anderson-Darling com bootstrap paramétrico (B = 200).
- [x] Teste de reescala com a taxa da spec 005; Weibull no tempo reescalado com IC por bootstrap.
- [x] Tempo até restabelecer: massa em zero (Wilson), lognormal dos positivos (IC por bootstrap) e regressão de tempo acelerado.
- [x] Causa comum: β por par (Clopper-Pearson) para o relatório e 7 grupos de linhas sem dupla contagem para o simulador (corrigido em 2026-10-21: antes o simulador sorteava por par e contava duas ou três vezes os eventos de 3 ou 4 linhas).
- [x] Contrato `parametros.json` (`pipeline/parametros.py`) com as hipóteses do motor e faixas para a interface.
- [x] Testes em `pipeline/tests/test_modelos.py`.
- [ ] Estratos por frota com mais dados quando a STM publicar km depois de 2023-09.
