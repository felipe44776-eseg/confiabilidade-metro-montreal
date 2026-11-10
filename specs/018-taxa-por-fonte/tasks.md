# 018 — Taxa, renovação e duração por fonte: tarefas

- [ ] Baixar o km real de 2026-10-23 para a Release `dados-2026-11` (manifesto, `FONTES.md`, D18); conferir a cobertura e os meses sobrepostos.
- [ ] `exposicao.py`: parcela diária por frota; dedução da parcela da Verde onde faltar medida.
- [ ] `modelo_taxa.py`: painel por fonte, MR empilhado, EF por fonte, modelos reduzidos, bootstrap com as mesmas semanas.
- [ ] `diagnostico_taxa.py`: um ano de fora, v1.1.0 contra o novo.
- [ ] `distribuicoes.py`: renovação e duração por linha × fonte; β pela família.
- [ ] `parametros.py` e schema: contrato v2.
- [ ] Testes (`pipeline/tests/test_modelos.py`, `test_exposicao.py`).
- [ ] Relatório `fontes/verificacao/taxa_por_fonte.md`.
- [ ] Pré-registro v2 (`preregistro.py congela v2`), commitado antes de baixar incidentes novos.
