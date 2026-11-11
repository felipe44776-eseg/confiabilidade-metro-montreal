# 020 — Revalidação e revisão: tarefas

- [x] v1.1.0 congelada (etiqueta no `e793bba`, Release com o zip do site; 2026-11-10).
- [x] Pré-registro v1 commitado (`fontes/verificacao/preregistro/modelo_v1.json`; commit `4fe203d`, 2026-11-10).
- [x] Pré-registro v2 commitado, depois da spec 018 e antes de baixar incidentes novos (`fontes/verificacao/preregistro/modelo_v2.json`, código do commit a43784b, 2026-11-11; avaliação conferida em modo interno num mês do treino).
- [ ] Avaliação fora da amostra (pendente até a STM publicar 3 meses depois de 2026-06).
- [ ] Backtest A a D refeito sobre os dados revistos, marcado como posterior. Código pronto em 2026-11-10 (alvos por família, 5 min ou mais e minutos por família; nota no topo de `backtest.md` com o resultado oficial da v1.1.0); falta rodar com B = 100.
- [ ] Monte Carlo contra o histórico e indicador da STM. Em 2026-11-10: o indicador por ano compara os dados abertos (todas as causas e só técnicas, faixa oficial; `normaliza.py` grava a contagem) com o publicado.
- [x] Exposição dos dias de greve com o km medido (D63, 2026-11-10, depois de ver): o multiplicador de greve de 1,73 vinha de contagem dupla; o ajuste completo foi parado e refeito.
- [ ] `fontes/verificacao/revisao_2026-11.md` (antes e depois).
- [ ] Seções "Revisão de 2026-11" nas specs atingidas; avisos no relatório, apresentação, painel, guia, arquitetura e README.
- [ ] Referências de 2026-11 (D62): teste exato do método de estados; massa em zero por fonte e ano em `distribuicoes.py`; escopo, área de perda, verificação × validação e duração de serviço no relatório e no guia; DOIs no Crossref.
- [ ] Agente crítico.
- [ ] E-mail à STM enviado pela equipe (Service aux trains, TCPE, terminais de 2024, Saint-Michel em out/2024, diferença do indicador de 5 min).
