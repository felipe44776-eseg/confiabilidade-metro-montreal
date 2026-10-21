# 001 — Normalização dos incidentes: tarefas

- [x] `pipeline/normaliza.py` com funções puras (`minutos`, `instante_local`, `para_utc`, `duracao`, `faixa_de`, `linhas_do_campo`).
- [x] Teste da virada de dia, mês e ano para 24:xx e 25:xx (`pipeline/tests/test_normaliza.py`).
- [x] Teste da retomada menor que o início (duração entre 0 e 1.440).
- [x] Teste do horário de verão (UTC−5 no inverno, UTC−4 no verão).
- [x] 8.530 eventos técnicos com início e fim; 45 de causa comum (31 Verde e Laranja); 44 sem linha.
- [x] Conferência com a faixa oficial: 8.430 de 8.530 (98,83%) na faixa ou na vizinha; 100 exceções em `excecoes.csv`.
- [x] Reprodutibilidade: duas execuções seguidas dão arquivos idênticos (teste automatizado).
- [x] Recálculo independente em `verifica_fontes.py`: 8.530 eventos e 224 iniciados depois da meia-noite.
- [ ] Responder às perguntas em aberto (durações zero; códigos de linha compostos) com a STM, se ela responder ao pedido de acesso.
