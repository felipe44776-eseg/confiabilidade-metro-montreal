# 017 — Fontes de falha e durações pela faixa oficial: tarefas

- [x] `pipeline/duracao.py`: regra da faixa oficial (sorteio entre coerentes da mesma faixa e família; semente pelo número do incidente), ponto médio para a sensibilidade, classes de gravidade.
- [x] `pipeline/normaliza.py`: fonte (frota, setor × sintoma, `mr_outros`), colunas novas, virada de dia, duração final em `duracao_min` e calculada em `duracao_calculada_min`; causa comum com fonte.
- [x] Painel do site (`analise_confiabilidade.py`, `monta_painel.py`) com a mesma duração.
- [x] `verifica_fontes.py --recalcula`: minutos por linha pela regra e contagens por fonte, com código próprio (13 checagens novas, 0 diferenças).
- [x] Testes (`pipeline/tests/test_normaliza.py`): fontes e divisão, regra da faixa, ordem dos registros, minutos e viradas de dia.
- [x] Relatório `fontes/verificacao/fontes_e_duracoes.md`.
- [x] Leitor do km real nos dois formatos (`pipeline/km_real.py`); Release `dados-2026-11`; manifesto regenerado.
