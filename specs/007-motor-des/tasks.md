# 007 — Motor de simulação por eventos discretos: tarefas

- [x] `app/src/motor/tipos.ts`: tipos de rede.json e do contrato `contratos/parametros.schema.json`.
- [x] `app/src/motor/prng.ts`: xoshiro128**, fluxos por fonte de sorteio, normal, Weibull, Gama e função gama.
- [x] `app/src/motor/heap.ts`: fila de prioridade com desempate pela ordem de inserção.
- [x] `app/src/motor/rede.ts`: linhas, trechos, viagens em ordem de circulação (ordenação topológica), trens em circulação minuto a minuto, pontas de viagem.
- [x] `app/src/motor/taxas.ts`: multiplicadores por hora, taxa acumulada, renovação Weibull com início em equilíbrio.
- [x] `app/src/motor/contexto.ts`: preparação do cenário (o que não muda entre rodadas).
- [x] `app/src/motor/dia.ts`: laço de eventos, recursão max-plus com bloqueios, registro e hash.
- [x] Fixture `app/tests/fixtures/parametros_teste.json` (gerada por `app/tests/fixtures/gera_parametros_teste.mjs` a partir do painel; status "hipótese").
- [x] Testes dos critérios de aceite (`horario.test.ts`, `falhas.test.ts`, `prng.test.ts`).
- [x] Conferido com o `parametros.json` real do pipeline, sem mudança de código (`reais.test.ts`).
- [ ] Comparar a propagação de atrasos com o histórico (spec 012).
