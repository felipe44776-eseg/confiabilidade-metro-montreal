# 014 — Expansão da rede: plano (núcleo de cálculo)

## Método

```mermaid
flowchart LR
  CX[Contexto do cenário] --> COMP[Componentes de falha]
  COMP -->|p = νd / (1 + νd)| AM[Amostra: quais componentes estão fora]
  CAND[Candidata: estações e trechos] --> G[Grafo com a candidata]
  AM --> BL[Arestas bloqueadas]
  G --> OD[avaliaOD: disponibilidade origem-destino]
  BL --> OD
  OD --> GAN[Ganho contra a rede atual, pareado, IC95]
```

| Peça | Como funciona | Arquivo |
|---|---|---|
| Componentes | Material rodante por trecho e sentido (taxa da linha dividida pelo tempo de trem em cada trecho e sentido); equipamento fixo por trecho (pesos dos locais com posição + falhas sem posição uniformes por km); causa comum por grupo de linhas (desde 2026-10-21) | `app/src/motor/expansao.ts` |
| Probabilidade | Estacionária de um processo liga-desliga: p = νd / (1 + νd), com ν a taxa média do cenário na janela de serviço da linha e d a duração média (com a massa em zero) | `expansao.ts` |
| Amostragem | Bernoulli independentes por afinamento geométrico (salta para o próximo candidato a cair com a maior probabilidade e aceita com p / p_max): uma ou duas extrações por amostra | `expansao.ts` |
| Efeito | Sem retorno parcial, um componente fora para a linha inteira; com ele, o pedaço entre pontos de retorno. Causa comum para as duas linhas | `grafo.ts` (`efeitoBloqueio`) |
| Disponibilidade | A mesma função da camada diária (`avaliaOD`), com cache por conjunto de arestas | `grafo.ts` |
| Pares | Os da rede atual, com a oferta de hoje como peso. Estações novas não entram nos pares: o ganho mede a confiabilidade dos deslocamentos que já existem | `grafo.ts` (`pesosDe`) |
| Intervalo | 50 lotes de amostras; IC95 normal sobre as médias dos lotes | `expansao.ts` |
| Ganho | Números aleatórios comuns: os componentes da rede atual usam o mesmo fluxo com e sem a candidata; os da candidata, um fluxo próprio. Ganho = diferença lote a lote | `expansao.ts` |

## Candidatas

- **Prolongamento:** `linha` = linha existente e `sequencia` começando num terminal. Os trechos novos entram na própria linha; o terminal antigo continua ponto de retorno (é ponta de viagem no horário).
- **Linha nova:** `linha` = id novo. Pontas de retorno nos dois extremos.
- **Livre:** `candidataLivre(rede, A, B)`, ligação direta entre duas estações da rede atual.
- **Busca exaustiva:** `buscaExaustiva(rede, parâmetros, cenário, distância máxima)`. Lista todos os pares de estações até a distância em linha reta, menos os vizinhos que já existem e os mais curtos que `km_minimo_candidata`. Ranking por ganho e por ganho por km.

## Parâmetros das candidatas (hipóteses)

| Nome | Padrão | Uso |
|---|---|---|
| `velocidade_comercial_candidata_kmh` | 36 km/h | tempo de percurso dos trechos novos |
| `fator_tracado_candidata` | 1,2 (nova) | km de via = linha reta × fator, quando o km não é informado |
| `km_minimo_candidata` | 0,3 km (nova) | menor ligação aceita na busca exaustiva |
| Taxas por km | — | Prolongamento: as da própria linha. Linha nova ou livre: média da rede ponderada pelo km. MR e EF, com as durações médias correspondentes |
| Causa comum | — | Ganho reportado nas duas versões: candidata independente e candidata que divide a causa comum das linhas em que encosta (ou de `compartilhaCausaComumCom`) |

## Validação contra a camada diária

Rede atual, dia útil, sem políticas, sem rota alternativa. Camada diária com 3.000 rodadas; método de estados com 200.000 amostras.

| Linha | Fixture: diária | Fixture: estados | Diferença | parametros.json real: diferença |
|---|---|---|---|---|
| Verde | 99,487% | 99,513% | +0,026 pp | −0,014 pp |
| Laranja | 99,516% | 99,499% | −0,017 pp | −0,002 pp |
| Amarela | 99,851% | 99,853% | +0,003 pp | −0,024 pp |
| Azul | 99,454% | 99,485% | +0,032 pp | +0,020 pp |

Todas ficam abaixo do limite de 0,1 ponto percentual. A origem-destino também bate: 99,163% contra 99,171% com a fixture. A diferença residual cabe no ruído da camada diária (meia-largura de cerca de 0,03 pp com 3.000 rodadas) e é compatível com dois efeitos que o método de estados ignora: falhas agrupadas (forma da Weibull abaixo de 1) que se sobrepõem no mesmo dia e o corte das interrupções no fim do serviço.

## Primeiros resultados (fixture, não publicar)

- **Ligações livres:** Angrignon–Snowdon e Jean-Talon–Berri-UQAM têm ganho positivo com IC95 acima de zero (cerca de +0,07 e +0,06 pp de disponibilidade origem-destino).
- **Busca exaustiva até 1,5 km:** 66 candidatas em 4 s.
  - Melhor por ganho: Atwater–Georges-Vanier.
  - Melhor por ganho por km: Guy-Concordia–Lucien-L'Allier.
- **Prolongamentos para estações novas:** não criam caminho alternativo para os pares de hoje. Sem retorno parcial, ainda acrescentam exposição à linha, e o ganho fica zero ou negativo.

## Desvios do desenho pedido

| Desvio | Por quê |
|---|---|
| As durações do método de estados são as da operação atual, sem as políticas de retirada e operação degradada | A pergunta da spec é estrutural (que ligação construir); as políticas operacionais ficam na camada diária |
| Estações novas não entram nos pares | Sem dado de demanda, a oferta futura delas seria inventada. O ganho mede só os pares de hoje |
| Candidatas oficiais (Azul até Anjou, linha Rosa, Laranja além de Côte-Vertu) não vêm prontas no motor | Coordenadas de estações projetadas precisam de fonte citada; entram pela interface (spec 011) com status "hipótese de traçado" e a fonte de cada uma |

## Testes

| Critério | Teste |
|---|---|
| Validação contra o simulador a até 0,1 pp | `expansao.test.ts` |
| Candidatas livres avaliadas do mesmo jeito | `expansao.test.ts` |
| Busca com ranking por ganho e por km | `expansao.test.ts` |
| Trechos herdam taxas e durações, com status hipótese | `expansao.test.ts` (lista de hipóteses de cada item) |
| Ganho com e sem causa comum | `expansao.test.ts` |
| Ranking com IC95, rodadas, semente e hipóteses | `expansao.test.ts` |
