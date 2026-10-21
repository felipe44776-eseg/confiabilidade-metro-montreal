# 014 — Expansão da rede: tarefas

- [x] `app/src/motor/grafo.ts`: grafo de plataformas, pesos pela oferta, caminhos mínimos, disponibilidade origem-destino com cache, efeito de um bloqueio com e sem retorno parcial.
- [x] `app/src/motor/expansao.ts`: componentes de falha, probabilidade estacionária, amostragem por afinamento, ganho pareado com IC95, prolongamento pelo fim ou pelo começo da linha, linha nova, candidata livre, busca exaustiva.
- [x] Validação da rede atual contra a camada diária a até 0,1 pp (fixture e parametros.json real).
- [x] Testes (`expansao.test.ts`).
- [x] Candidatas oficiais com traçado aproximado, fonte e status (spec 011): `app/src/simulador/candidatas.ts`, função pura `candidatasDoJson(json, rede)` sobre `dados/derivados/simulador/candidatas.json`, com testes (`tests/simulador/candidatas.test.ts`). Regras:
  - prolongamentos (Azul até Anjou, Amarela em Longueuil, Laranja até Bois-Franc) começam no terminal certo de cada linha no `rede.json`: Saint-Michel é o último da Azul; Longueuil e Côte-Vertu são os primeiros da Amarela e da Laranja;
  - o anel da Laranja (ARTM, 2019), que sai de Côte-Vertu e volta em Montmorency, vira a linha nova `laranja_anel` com as taxas por km da Laranja (`herdaTaxasDe`, campo novo no motor), porque o motor não fecha anel numa linha existente;
  - a Rosa vira a linha nova `rosa` com Mont-Royal, Place-des-Arts e Vendôme fundidas no id da estação atual; as taxas por km são a média da rede;
  - a Vertières da Rosa é estação simples; no projeto conjunto "Rosa com a Azul" (`extras`, campo novo no motor), ela vira a Vertières da Azul e passa a ser correspondência;
  - km = linha reta × `fator_tracado_candidata`; `fonte` = primeira URL; status "em obras (OSM)" na Azul e "hipótese de traçado" nas demais (tipo do motor ampliado).
- [x] Sanidade: os ramais não têm ganho de redundância (limite superior do IC 95% abaixo de 1e-4; o ganho é negativo, porque somam trechos que podem falhar); anel e Rosa têm ganho positivo.
- [x] Interface: lista das candidatas com tipo, status, fontes e traçado tracejado no mapa; ranking por ganho de disponibilidade e por ganho por km, com e sem causa comum, IC 95%, amostras, semente e hipóteses; ligação livre entre duas estações; busca exaustiva com distância máxima. Tudo num Web Worker.
- [ ] Rodar a busca exaustiva com o parametros.json real e publicar o ranking com as hipóteses.
