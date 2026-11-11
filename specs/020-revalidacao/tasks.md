# 020 — Revalidação e revisão: tarefas

- [x] v1.1.0 congelada (etiqueta no `e793bba`, Release com o zip do site; 2026-11-10).
- [x] Pré-registro v1 commitado (`fontes/verificacao/preregistro/modelo_v1.json`; commit `4fe203d`, 2026-11-10).
- [x] Pré-registro v2 commitado, depois da spec 018 e antes de baixar incidentes novos (`fontes/verificacao/preregistro/modelo_v2.json`, código do commit a43784b, 2026-11-11; avaliação conferida em modo interno num mês do treino).
- [ ] Avaliação fora da amostra (pendente até a STM publicar 3 meses depois de 2026-06).
- [x] Backtest A a D refeito sobre os dados revistos, marcado como posterior (2026-11-11, B = 100): A 65,3%, B 84,7%, C 87,5%, D 90,3%; por família, a A falha nos equipamentos fixos (`backtest.md`; spec 012).
- [x] Monte Carlo contra o histórico e indicador da STM (2026-11-11): 25 de 28 dentro do IC de 2025 (exceção), dispersão 9 de 12 (exceção), dados abertos de 85% a 89% do indicador publicado (`revalidacao.md`).
- [x] Exposição dos dias de greve com o km medido (D63, 2026-11-10, depois de ver): o multiplicador de greve de 1,73 vinha de contagem dupla; o ajuste completo foi parado e refeito.
- [x] `fontes/verificacao/revisao_2026-11.md` (antes e depois), com a expansão acrescentada depois da crítica.
- [x] Seções "Revisão de 2026-11" nas specs 001, 004 a 009, 011, 012 e 014 a 016; avisos no relatório, apresentação, painel, guia, arquitetura e README (2026-11-11).
- [x] Referências de 2026-11 (D62): teste exato do método de estados; massa em zero por fonte e ano em `distribuicoes.py`; escopo, área de perda, verificação × validação e duração de serviço no relatório e no guia; DOIs no Crossref.
- [x] Agente crítico (`critica_2026-11-11.md`, D64): 28 achados, 0 altos; propostas abertas nas tarefas da spec 019.
- [x] E-mail à STM (Service aux trains, TCPE, terminais de 2024, Saint-Michel em out/2024, diferença do indicador de 5 min): cancelado em 2026-11-11 pela equipe, sem prazo para a resposta antes da entrega (D65). As perguntas ficam como limitação declarada.
- [x] Publicado em 2026-11-11 (merge na `main`, deploy de 5a665a4): páginas, `/versoes/v1.1.0/` e navegador conferidos (`navegador_2026-11-11.json`).
- [x] Reprodução do zero (`reproduz.yml`): a execução de 2026-11-01 (41312932829) falhou na integridade dos JSON da NHL baixados da origem (a API mudou a resposta). Em 2026-11-11, a equipe decidiu não refazer a reprodução depois da revisão: agenda mensal desligada, workflow só à mão (D65; spec 013).
