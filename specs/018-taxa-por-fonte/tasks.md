# 018 — Taxa, renovação e duração por fonte: tarefas

- [x] Baixar o km real de 2026-10-23 para a Release `dados-2026-11` (manifesto, `FONTES.md`, D18); conferir a cobertura e os meses sobrepostos (2019-01 a 2026-09; nos meses em comum, igual ao retrato anterior).
- [x] `exposicao.py`: parcela diária por frota (`frota_diaria.csv`). A dedução da parcela da Verde não foi necessária: nenhum mês ficou sem medida. Dias de greve com o fator típico (D63).
- [x] `modelo_taxa.py`: painel por fonte, MR empilhado, EF por fonte, modelos reduzidos, bootstrap com as mesmas semanas (B = 200, 2026-11-11).
- [x] `diagnostico_taxa.py` e `fora_da_amostra.py`: parcela da frota por faixa (rejeitada) e um ano de fora, v1.1.0 contra o novo.
- [x] `distribuicoes.py`: renovação e duração por linha × fonte; β pela família; massa em zero por fonte e ano (D62).
- [x] `parametros.py` e schema: contrato v2.
- [x] Testes (`pipeline/tests/test_modelos.py`, `test_exposicao.py`, `test_massa_em_zero.py`).
- [x] Relatório `fontes/verificacao/taxa_por_fonte.md`.
- [x] Pré-registro v2 (`preregistro.py congela v2`), commitado antes de baixar incidentes novos (aabbef5; spec 020).
- [ ] Horas de serviço como sensibilidade da exposição dos equipamentos fixos (critério da spec; não feita nesta rodada, a exposição continua trens-hora, D17).
