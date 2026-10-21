# 012 — Validação contra o histórico: tarefas

- [x] `pipeline/backtest.py`: ajuste só no treino, bootstrap em blocos semanais (B = 100), renovação Weibull no tempo reescalado com início estacionário, 20 caminhos por vetor.
- [x] Durações sorteadas da amostra observada no treino, como no simulador (desde 2026-10-21).
- [x] Cobertura do IP 90% com IC de Clopper-Pearson; PIT aleatorizado com histograma e KS; meses de greve separados; minutos parados no primeiro ano do teste.
- [x] Versões A e B pré-registradas; C e D registradas em 2026-10-21 depois de ver A (efeito do ano sorteado; reteste em 2023-01 a 2024-06).
- [x] Relatório `fontes/verificacao/backtest.md` com onde o modelo falhou, linha a linha, e o gráfico do PIT.
- [x] Testes em `pipeline/tests/test_backtest.py`.
- [ ] Repetir o backtest com o motor TypeScript (mesmo processo, segunda implementação) e comparar com este.
- [ ] Validação cruzada deixando um ano de fora (pergunta em aberto).
