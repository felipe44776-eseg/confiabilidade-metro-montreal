# 017 — Fontes de falha e durações pela faixa oficial: tarefas

- [ ] `pipeline/duracao.py`: regra da faixa oficial (sorteio entre coerentes da mesma faixa e família; semente pelo número do incidente), ponto médio para a sensibilidade, classes de gravidade.
- [ ] `pipeline/normaliza.py`: fonte (frota, setor × sintoma, `mr_outros`), colunas novas, virada de dia, duração final em `duracao_min` e calculada em `duracao_calculada_min`; causa comum com fonte.
- [ ] Painel do site (`analise_confiabilidade.py`, `monta_painel.py`) com a mesma duração.
- [ ] `verifica_fontes.py --recalcula`: minutos por linha pela regra e contagens por fonte, com código próprio.
- [ ] Testes (`pipeline/tests/test_normaliza.py`): totais 8.530/45/31/44; soma das fontes; regra da faixa (uma exceção de cada tipo); sorteio reprodutível; gravidade.
- [ ] Relatório `fontes/verificacao/fontes_e_duracoes.md`.
- [ ] Manifesto, `FONTES.md` e lista de scripts do contrato atualizados.
