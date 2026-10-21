# 009 — Monte Carlo e métricas: plano

## Fluxo

```mermaid
flowchart LR
  P[Página] -->|PedidoMC| POOL[mc/pool.ts: PoolMC]
  POOL -->|lote de índices| W1[Worker 1]
  POOL -->|lote de índices| WN[Worker k]
  W1 --> RR[mc/rodadas.ts: rodaRodadas]
  WN --> RR
  RR -->|rodada i: semente = f(base, i)| D[motor/dia.ts: simulaDia]
  RR -->|métricas por rodada| POOL
  POOL --> AG[agrega: ordena pelo índice, média, IC95, n, semente]
```

## Desenho

| Peça | Como funciona |
|---|---|
| Rodada | Um dia de operação. A rodada i usa `sementeDaRodada(semente-base, i)`, que só depende dos dois números |
| Função pura | `rodaRodadas(indices, contexto, políticas, semente-base, políticasB?)` devolve as métricas de cada rodada. Com `políticasB`, roda a variante com a mesma semente (números aleatórios comuns) |
| Agregação | `agrega` ordena pelo índice antes de somar. Por isso 1 ou 8 lotes, em qualquer ordem, dão o mesmo resultado bit a bit (teste) |
| Intervalo | IC95 normal: média ± 1,96 × dp / √n. Toda estimativa leva n e semente |
| Pool | `PoolMC` com `navigator.hardwareConcurrency` workers (teto 16), um lote contíguo por worker, progresso a cada 50 rodadas e cancelamento (`terminate`). O worker remonta a rede só quando a `chaveRede` muda |
| Modo adaptativo | `rodaAtePrecisao`: lotes de 1.000 rodadas até a meia-largura do IC95 ficar em 5% da média das métricas pedidas, com teto de 50.000 |
| Ano | `anualiza` soma os tipos de dia pelo calendário típico: 251 úteis, 52 sábados, 62 domingos e feriados (aproximação declarada) |

## Métricas por rodada

Por linha: minutos de interrupção (total e por causa: MR, EF, causa comum), disponibilidade (1 − interrupção / janela de serviço da linha), trens-hora perdidos (atraso no terminal + viagens canceladas × duração programada + trecho não feito pelas viagens retiradas), viagens afetadas (atraso acima de 3 min, canceladas ou retiradas), viagens canceladas, frota completa, falhas por causa.

Na rede: minutos de interrupção, trens-hora perdidos, disponibilidade origem-destino ponderada pela oferta, tempo extra de viagem (média ponderada) e minutos de par interrompido.

### Origem-destino

- **Pares:** as 68 estações distintas, 4.556 pares ordenados.
- **Peso:** viagens programadas que servem o par no tipo de dia. Com baldeação, o menor valor entre as pernas do caminho mínimo.
- **Disponibilidade:** varredura no tempo dos conjuntos de arestas bloqueadas. Sem rota alternativa, o par cai quando o caminho de sempre tem aresta bloqueada; com ela, quando não sobra caminho. O resultado de cada conjunto fica em cache, porque os conjuntos se repetem muito entre rodadas.

## Respostas às perguntas em aberto

- **Número de rodadas:** adaptativo, até 5% da média dos minutos parados de cada linha, com teto de 50.000. No dia útil, com a fixture, cada linha precisa de: Verde 5.924, Laranja 6.558, Amarela 19.658 e Azul 9.777 rodadas. A Amarela tem poucas falhas por dia, e a média fica pequena perto da variância.
- **Pares origem-destino:** todos (68 estações), ponderados pela oferta.

## Resultados medidos

### Tempo

5.000 rodadas de dia útil em 9,9 s numa thread (Node 22.21, Windows 11, 2026-10-20), ou 2 ms por dia. Fica dentro da estimativa de 10 a 30 s da spec já sem paralelismo; com 8 workers, a expectativa é de 1 a 2 s. Com a máquina carregada por outros processos, a mesma medida chegou a 3,6 ms por dia.

### Laranja sem redundância contra o painel

1.500 rodadas por tipo de dia, semente 20261021, fixture tirada do painel:

| Medida | Minutos por ano | IC95 |
|---|---|---|
| Total da Laranja (MR + EF + causa comum) | 1.789 | 1.640 a 1.938 |
| Só MR + EF | 1.597 | 1.462 a 1.733 |
| Painel, Monte Carlo do corredor | 1.852 | — |
| Painel, cálculo analítico | 1.797 | — |

O IC95 do total contém os dois números do painel. As duas contas não são idênticas: o cenário `so_laranja` do painel soma às falhas da Laranja só a causa comum Verde–Laranja (`pipeline/analise_confiabilidade.py`), enquanto o total do motor inclui também os pares Laranja–Azul e Laranja–Amarela. Os parâmetros são os da fixture, tirados do painel; o critério deve ser repetido com o `parametros.json` real.

## Desvios do desenho pedido

| Desvio | Por quê |
|---|---|
| Teste de "1 vs 8 workers" feito com a função pura em 8 lotes, em ordem invertida e com contextos separados | O vitest roda em Node, sem Web Worker. O pool só divide índices e chama a mesma função |
| O pool não foi testado num navegador | Conferido que o Vite empacota o worker como arquivo próprio (`trabalhador-*.js`) |

## Testes

| Critério | Teste |
|---|---|
| 1 ou 8 processos dão o mesmo resultado | `montecarlo.test.ts` |
| Meia-largura até 5% com o número padrão | `montecarlo.test.ts` (rodadas necessárias cabem no teto; modo adaptativo para quando atinge) |
| Laranja contra 1.852 ou 1.797 | `montecarlo.test.ts` |
| Métricas publicadas com IC95, n e semente | `montecarlo.test.ts` |
| Tempo de 5.000 rodadas medido | `montecarlo.test.ts` |
