# 003 — Clima horário e eventos externos: tarefas

- [x] Download de 270 meses do ECCC (3 estações × 90 meses), 8 temporadas da NHL e o calendário do GP (`pipeline/baixa_clima_eventos.py`).
- [x] Zips determinísticos por estação para a Release `dados-2026-10-21`; o painel lido do zip é idêntico ao lido dos CSV.
- [x] Painel horário de 65.717 horas (`pipeline/clima_eventos.py`): precipitação em 99,99% das horas de operação (99,3% da 10761).
- [x] Teste de 4 trocas de horário (março e novembro de 2023 e 2024): 23 e 25 horas locais, sem repetição; 01:00 duplicada com −0400 e −0500.
- [x] Teste LST = UTC−5 contra o arquivo bruto.
- [x] Chuva congelante em 2023-04-05, das 09h às 20h LST (10h às 21h locais): 12 horas marcadas; recálculo independente direto do CSV do ECCC.
- [x] `eventos_externos.csv`: 348 eventos com data, faixa, URL e status (317 jogos verificados; 25 greves e 6 GPs não verificados).
- [x] Greves como exposição zero: 2025-11-01 sem serviço; faixas parciais nos demais dias (teste).
- [x] Fatores ausentes no dicionário de dados (`docs/dicionario_dados.md`).
- [x] Correção: vento de 0 km/h e sensação térmica de 0 °C não viram dado ausente.
- [ ] Conferir as datas do GP em uma segunda fonte para passar de "não verificado" a "verificado".
- [ ] Perguntas em aberto (McTavish representa a periferia? Open-Meteo para lacunas?) ficam para a análise de sensibilidade da spec 005.
