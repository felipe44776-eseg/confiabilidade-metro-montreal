# 005 — Modelo da taxa de falha: tarefas

- [x] Painel hora × linha com exposição, faixa do dia, tipo de dia, estação, clima, eventos e falhas (`monta_painel` em `pipeline/modelo_taxa.py`).
- [x] Poisson e binomial negativa com deslocamento log(trens-hora); α por verossimilhança perfilada (o ajuste direto não convergiu).
- [x] Bootstrap em blocos semanais, B = 200, pareado entre MR e EF; nível ausente numa reamostra vira lacuna.
- [x] Proteção contra falta de memória: a mesma reamostra é repetida (o resultado não depende da memória livre).
- [x] Resíduos quantílicos, rootograma e observado contra esperado por faixa (`pipeline/diagnostico_taxa.py`).
- [x] Comparação MR contra EF com IC pareado; greves pela exposição; defasagem de 1 hora; ajuste só no período com km real.
- [x] Taxa-base por trem-hora de cada linha em 2025 e multiplicadores no `parametros.json`, sem os níveis "sem dado".
- [x] Testes em `pipeline/tests/test_modelos.py`.
- [ ] Sensibilidade com a estação McTavish contra a do aeroporto para a periferia (pergunta em aberto da spec 003).
