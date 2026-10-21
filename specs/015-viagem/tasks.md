# 015 — Confiabilidade de uma viagem: tarefas

- [x] `app/src/motor/viagem.ts`: caminho de sempre, disponibilidade total e por trecho, conexões do dia, chegada mais cedo, referência sem falhas, métricas por dia e rodadas.
- [x] `app/src/motor/dia.ts` e `grafo.ts`: bloqueios do grafo no resultado do dia (`bloqueiosOD`), varredura no tempo compartilhada com a métrica da rede, opção para pular a métrica da rede.
- [x] Testes (`app/tests/motor/viagem.test.ts`): caminho com baldeações; sem falhas, atraso zero e disponibilidade 1; interrupção injetada de 30 min (caminho falta 30 min, quem sai antes não atrasa, quem sai durante atrasa); rota alternativa contorna a interrupção; disponibilidade de cada par ponderada pela oferta reproduz a da rede no mesmo dia, com e sem rota alternativa; rodada i igual à do Monte Carlo e resultado determinístico.
- [x] Link: origem e destino no endereço, sem mudar a chave do cenário (`app/tests/simulador/cenario.test.ts`).
- [x] Aba "Viagem de A a B" no `/simulador/`: escolha das estações, caminho no mapa, disponibilidade por trecho, produto em série ao lado do simulado com a leitura, atraso por limiar e por hora de saída (`simulador/pool_viagem.ts`, `trabalhador_viagem.ts`, `main.ts`, `mapa_sim.ts`).
- [x] Relatório com cinco viagens, com e sem rota alternativa (`app/relatorios/viagem.relatorio.ts` → `fontes/verificacao/viagem.md`).
- [x] Conferência no navegador (`publicacao/testa_navegador.py`).
- [ ] Ônibus de substituição durante a interrupção (sem dado).
