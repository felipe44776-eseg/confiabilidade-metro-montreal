# 008 — Políticas de tolerância a falhas: tarefas

- [x] `app/src/motor/politicas.ts`: as seis políticas, "nenhuma política" e `soPolitica`.
- [x] `app/src/motor/frota.ts`: nascimento-morte da frota, distribuição estacionária, simulação por eventos e sorteio diário.
- [x] Reserva fria, retirada, operação degradada e tratamento de causa comum no laço de eventos (`app/src/motor/dia.ts`).
- [x] Retorno parcial e rota alternativa nas métricas origem-destino (`app/src/motor/grafo.ts`, `efeitoBloqueio` e `avaliaOD`).
- [x] Números aleatórios comuns e diferença pareada com IC95 (`app/src/mc/rodadas.ts`).
- [x] `avisosDoCenario`: hipóteses ativas que acompanham cada resultado.
- [x] Testes (`frota.test.ts`, `politicas.test.ts`).
- [ ] Interface das políticas e relatório com a sensibilidade ao reparo para todas elas (spec 011).
- [ ] Pipeline: incluir `tempo_retirada_min`, `tempo_ativacao_degradada_min` e `reducao_causa_comum_politica` em `parametros.json` (hoje vêm do padrão do motor).
- [ ] Buscar aparelhos de mudança de via (`railway=switch`) no OpenStreetMap, como não verificados (pergunta em aberto).
