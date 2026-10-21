# 009 — Monte Carlo e métricas: tarefas

- [x] `app/src/mc/rodadas.ts`: `rodaRodadas` (função pura), métricas por rodada, `agrega` com IC95, `anualiza`, `rodadasParaPrecisao`, `rodaAtePrecisao`, `divideEmLotes`.
- [x] `app/src/mc/pool.ts`, `trabalhador.ts` e `protocolo.ts`: pool de Web Workers com progresso e cancelamento.
- [x] Métricas origem-destino ponderadas pela oferta, com tempo extra de viagem (`app/src/motor/grafo.ts`).
- [x] Testes (`montecarlo.test.ts`): 1 vs 8 lotes, IC95, Laranja contra o painel, precisão e tempo de 5.000 rodadas.
- [ ] Conferir o pool num navegador quando a interface da spec 011 chamar o `PoolMC`.
- [ ] Repetir a comparação com o painel usando o `parametros.json` real e registrar aqui.
