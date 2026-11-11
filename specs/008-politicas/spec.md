# 008 — Políticas de tolerância a falhas

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 006, 007, 009

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** A operação degradada continua a política que mais reduz os minutos parados, mas o efeito cai de −7,8 para −3,4 min por dia útil, porque parte das interrupções longas de equipamento fixo eram registros com duração contraditória (D55). Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

## Pergunta de engenharia
Que política de tolerância a falhas reduz mais os trens-hora perdidos e os minutos de interrupção, separando falha de trem e falha de equipamento fixo? O número que responde é a diferença de cada política contra "nenhuma política", com intervalo de 95%.

## Contexto
- O painel atual já tem um modelo de reserva k-de-n por Markov: na Laranja, com reparo de 1 dia, a chance de ter todos os trens necessários é de 67% sem reserva e de 99,2% com 2 trens de reserva.
- Os trens necessários por dia útil foram estimados pelo km real: Verde cerca de 50, Laranja 47, Azul 15, Amarela 6.
- O tempo de reparo na oficina não está em nenhuma fonte. É hipótese, entre 0,5 e 4 dias.
- Causa comum: 31 eventos técnicos param a Verde e a Laranja juntas; isso limita a redundância do corredor entre Lionel-Groulx e Berri-UQAM (FONTES.md).

## Critérios de aceite
- Dadas as políticas reserva fria k-de-n, retirada do trem falho, operação degradada (velocidade reduzida), retorno parcial antes do trecho bloqueado, rota alternativa de passageiros e tratamento de causa comum, quando o simulador roda, então cada uma pode ser ligada e desligada sozinha.
- Dada cada política, quando comparada a "nenhuma política", então a diferença usa números aleatórios comuns (mesmas falhas nas duas rodadas) e tem intervalo de 95%.
- Dada a reserva k-de-n sem outras políticas, quando simulada com os mesmos parâmetros do painel, então a chance de frota completa bate com o modelo de Markov a até 5 pontos percentuais.
- Dado o retorno parcial, quando a posição dos aparelhos de mudança de via não estiver verificada, então a política só usa terminais, e o resultado aparece marcado como hipótese.
- Dado cada resultado, quando publicado, então o relatório separa o efeito em falhas de trem e em falhas de equipamento fixo.
- Dado o tempo de reparo, quando varia de 0,5 a 4 dias, então o relatório traz a sensibilidade de cada política a ele.

## Resultado (2026-10-21)

Código em `app/src/motor/politicas.ts`, `frota.ts` e `dia.ts`; relatório [`politicas.md`](../../fontes/verificacao/politicas.md) gerado por `app/relatorios/politicas.relatorio.ts` com o `parametros.json` real.

| Critério | Resultado |
|---|---|
| Cada política liga e desliga sozinha | **Atende** (teste) |
| Diferença contra "nenhuma política" com números aleatórios comuns e IC 95% | **Atende**: 3.000 dias úteis pareados por política e por tempo de reparo |
| Reserva k-de-n contra Markov a até 5 p.p. | **Atende**: na Laranja, simulação 0,674, 0,939 e 0,992 contra Markov 0,671, 0,938 e 0,992 (0, 1 e 2 reservas) |
| Retorno parcial só nos terminais, marcado como hipótese | **Atende**: só nas pontas de viagem do horário; aviso no relatório e na página |
| Efeito separado em falha de trem e de equipamento fixo | **Atende**: colunas MR, EF e causa comum |
| Sensibilidade ao reparo de 0,5 a 4 dias | **Atende**: tabelas para 0,5, 1, 2 e 4 dias |

Achados (reparo de 1 dia): a operação degradada é a política que mais reduz minutos parados (−7,8 min por dia útil na soma das linhas; IC −9,7 a −5,9) e trens-hora perdidos; a reserva fria não muda os minutos parados, mas eleva a chance de frota completa na Laranja em 32,5 p.p. (58 p.p. com reparo de 4 dias); a retirada do trem falho reduz os minutos de material rodante em 1,1 por dia útil; retorno parcial e rota alternativa só mudam a disponibilidade origem-destino.

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D56, D57 e D59; specs 019 e 020).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **O que mudou na entrada:** o `parametros.json` passa ao contrato v2 (`sha256-scripts:489914bafbbe991e`; v1.1.0: `70cf9c002aa2ba0a`):
  - 9 fontes por linha, 3 de trem e 6 de equipamento fixo (D56, D59);
  - taxa-base do ano 2025 por fonte, com a exposição medida até 2026-06 (D57, spec 018);
  - nas 100 falhas em que a duração calculada contradiz a faixa oficial, vale a faixa (D55). Os minutos das falhas técnicas caem de 43.971 para 33.404.
- **O que mudou no método:** nada no experimento: 3.000 dias úteis pareados por política e por tempo de reparo, semente 20261021. O motor lê a lista de fontes e, com os parâmetros da v1.1.0, reproduz a referência anterior sem diferença (spec 019). As diferenças abaixo vêm, portanto, dos parâmetros. A retirada do trem vale para as fontes de trem e a operação degradada para as fixas, como antes por família.
- **O que não mudou na entrada:** a camada de frota (k-de-n) usa a taxa por trem-dia de 2019-01 a 2023-09 (Laranja: 48 trens, 0,00835), igual nas duas versões.

Reparo de 1 dia, soma das quatro linhas por dia útil (`politicas.md`):

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| Operação degradada: minutos parados | −7,8 (−9,7 a −5,9) | −3,4 (−4,0 a −2,8) |
| Operação degradada: trens-hora perdidos | −16,37 (−24,75 a −7,99) | −2,32 (−3,19 a −1,44) |
| Operação degradada: disponibilidade origem-destino | +0,353 p.p. (0,283 a 0,423) | +0,169 p.p. (0,139 a 0,199) |
| Retirada do trem falho: minutos de material rodante | −1,1 (−1,4 a −0,8) | −1,0 (−1,3 a −0,7) |
| Retirada do trem falho: trens-hora perdidos | −0,18 (−0,40 a 0,03) | −0,28 (−0,55 a −0,02) |
| Retorno parcial: disponibilidade origem-destino | +0,205 p.p. (0,180 a 0,230) | +0,152 p.p. (0,133 a 0,171) |
| Rota alternativa: disponibilidade origem-destino | +0,012 p.p. (0,007 a 0,016) | +0,006 p.p. (0,005 a 0,007) |

Não mudaram: a chance de frota completa na Laranja com a reserva fria (+18,2, +32,5, +50,0 e +58,2 p.p. com reparo de 0,5, 1, 2 e 4 dias), a simulação da reserva contra o Markov (0,674, 0,939 e 0,992 contra 0,671, 0,938 e 0,992) e o tratamento de causa comum (−0,8 min, IC −1,3 a −0,3; −0,52 trens-hora).

| Critério | Após a revisão |
|---|---|
| Cada política liga e desliga sozinha | **Continua atendendo** (teste) |
| Diferença contra "nenhuma política" com números aleatórios comuns e IC 95% | **Continua atendendo**: 3.000 dias úteis pareados por política e por tempo de reparo |
| Reserva k-de-n contra Markov a até 5 p.p. | **Continua atendendo**, com os mesmos números: a camada de frota não usa as taxas revistas |
| Retorno parcial só nos terminais, marcado como hipótese | **Continua atendendo**: aviso em `politicas.md` |
| Efeito separado em falha de trem e de equipamento fixo | **Continua atendendo**: colunas MR, EF e causa comum, agora como soma das fontes de cada família |
| Sensibilidade ao reparo de 0,5 a 4 dias | **Continua atendendo**: tabelas para 0,5, 1, 2 e 4 dias |

Achados após a revisão (reparo de 1 dia, salvo quando dito):

- A operação degradada continua a política que mais reduz minutos parados e trens-hora perdidos, mas o efeito nos minutos cai para menos da metade (−3,4 contra −7,8 min por dia útil).
- Por quê (D55): a política reabre o trecho em marcha lenta depois de 5 min (`tempo_ativacao_degradada_min`, hipótese). O ganho é a parte de cada interrupção de equipamento fixo que passa disso. Parte das interrupções longas de equipamento fixo eram registros com duração contraditória. Nessas exceções, a Azul tinha 7.207 minutos calculados, que ficam 10 pela faixa; a Verde, 1.479 → 120; a Laranja, 1.472 → 101 (`fontes_e_duracoes.md`). Sobra menos tempo bloqueado para a marcha lenta recuperar.
- A retirada do trem falho reduz os minutos de material rodante em 1,0 por dia útil. O ganho em trens-hora passa a ter IC que não contém zero.
- A reserva fria continua sem efeito nos minutos parados. Com reparo de 4 dias, ela passa à frente da operação degradada em trens-hora pela estimativa pontual (−3,11 contra −2,29), com intervalos que se sobrepõem (−3,20 a −3,02 e −3,17 a −1,42).
- Retorno parcial e rota alternativa continuam mudando só a disponibilidade origem-destino, com ganho menor, porque há menos tempo de trecho bloqueado.

## Fora de escopo
- Custo financeiro de cada política (pode entrar depois, com fonte).
- Ônibus de substituição: não há dados de oferta.

## Riscos e dependências
- Sem a posição real dos aparelhos de mudança de via, o retorno parcial pode ser otimista ou pessimista.
- A rota alternativa depende da spec 009 (pares origem e destino ponderados pela oferta).

## Perguntas em aberto
- Vale buscar os aparelhos de mudança de via (`railway=switch`) no OpenStreetMap, marcados como não verificados?
- Quantos trens de reserva a STM mantém de fato por linha?
