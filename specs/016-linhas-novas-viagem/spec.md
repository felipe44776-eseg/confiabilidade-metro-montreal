# 016 — Linhas novas numa viagem e escala para confiabilidade alta

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 007, 009, 014, 015
**Origem:** pedido da equipe em 2026-10-21 ("testar construções de linha: alocar novas linhas para ver como alguns caminhos aumentam de confiabilidade; e uma escala que pegue pequenas variações, porque a confiabilidade é alta e fica tudo muito próximo")

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** Com as durações pela faixa oficial e as taxas por fonte, as viagens dos exemplos ficam mais disponíveis na rede atual e as linhas novas falham menos por dia; os quatro achados se mantêm. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

## Pergunta de engenharia

Para uma viagem de A a B, quanto a construção de uma linha (proposta oficial ou desenhada pela equipe) muda a confiabilidade dessa viagem, e como mostrar a diferença entre valores que passam todos de 99%?

## Contexto

- A spec 014 avalia linhas candidatas pela rede inteira (disponibilidade origem-destino ponderada pela oferta), pelo método de estados, sem horário nem atraso. Não responde por um caminho escolhido.
- A spec 015 mede uma viagem no dia simulado (disponibilidade do caminho e atraso de quem viaja), só na rede atual.
- Perto de 100%, a disponibilidade esconde as diferenças: 99,54% e 99,98% parecem iguais, mas o tempo sem caminho cai 23 vezes. Em sistemas tolerantes a falhas, a escala usual é a indisponibilidade (tempo parado) e o número de noves.
- Comparar duas simulações independentes pede muitos dias para separar diferenças pequenas. Com números aleatórios comuns (o mesmo dia sorteado nas duas versões da rede), a diferença dia a dia tem variância bem menor.

## Critérios de aceite

- **Linhas novas na viagem:** dada a aba "Viagem de A a B", quando a pessoa marca candidatas da spec 014 ou desenha uma linha (estações da rede escolhidas na lista ou tocadas no mapa; toque fora das estações vira estação nova), então cada linha aparece no mapa e na lista, vai no link e pode ser removida.
- **Mesmo dia, com e sem:** dadas as rodadas do cenário, quando a viagem é avaliada com linhas novas, então cada dia é simulado uma vez e medido na rede atual, com cada linha sozinha e, com duas ou mais, com todas juntas; a diferença de cada medida (com − atual) tem intervalo de 95% pareado.
- **Falhas da linha nova:** dada uma linha nova, quando simulada, então seus trechos falham com as taxas por km e as durações observadas da linha de que herdam (prolongamento: a própria; linha nova: `herdaTaxasDe` ou a média da rede), com status "hipótese"; as políticas de retirada do trem e operação degradada valem também para elas; a causa comum compartilhada com as linhas em que encosta pode ser ligada.
- **Trens da linha nova:** dado o prolongamento, quando simulado, então as viagens do horário que chegam ao terminal antigo seguem pelo trecho novo; dada uma linha nova, então ela tem as partidas por hora da linha de referência; numa interrupção, as conexões do trecho parado não acontecem.
- **Caminho de sempre:** dada uma linha nova que encurta a viagem, quando avaliada, então o caminho de sempre passa por ela e a página mostra o tempo programado novo; sem rota alternativa, a pessoa usa só esse caminho.
- **Rede atual intacta:** dado o mesmo dia, quando a viagem é medida junto com as variantes, então os números da rede atual são idênticos aos da spec 015.
- **Sem falhas:** dado um dia sem falhas, quando a viagem é medida com linhas novas, então o atraso é zero e a disponibilidade é 1.
- **Paralelo nunca piora:** dada uma linha nova independente (não prolongamento, sem causa comum compartilhada) e a rota alternativa ligada, quando medida, então a disponibilidade da viagem não cai em nenhum dia.
- **Escala:** dados os resultados da viagem, quando mostrados, então ao lado da disponibilidade aparecem os minutos por dia sem caminho, o número de noves (−log₁₀ da indisponibilidade) e, para cada linha nova, a razão do tempo sem caminho contra a rede atual com intervalo de 95%; o tempo sem caminho vai num gráfico em escala logarítmica.
- **Reprodutível:** dado o mesmo link (cenário, semente, rodadas, viagem e linhas novas), quando aberto, então dá os mesmos números.

## Resultado (2026-10-21)

Código em `app/src/motor/linhas_novas.ts` (com mudanças em `viagem.ts`, `dia.ts`, `grafo.ts` e `expansao.ts`) e `app/src/ui/escala.ts`; seção "Linhas novas" na aba "Viagem de A a B"; relatório [`linhas_novas.md`](../../fontes/verificacao/linhas_novas.md) gerado por `app/relatorios/linhas_novas.relatorio.ts` (dia útil, 1.000 dias por caso, semente 20261021, `parametros.json` real); testes em `app/tests/motor/linhas_novas.test.ts` e `app/tests/simulador/escala.test.ts`.

| Critério | Resultado |
|---|---|
| Linhas propostas e desenhadas (lista e toque no mapa), no mapa, na lista e no link | **Atende**. Conferido no navegador local, em celular e notebook: a Rosa marcada, uma linha desenhada com estação da lista e com toque no mapa (perto de uma estação entra a estação; fora, uma estação nova), remoção e link (`ln`, `ld`, `lc`) |
| Mesmo dia com e sem; cada linha sozinha e todas juntas; diferença com IC pareado | **Atende**. Ex.: Snowdon → Saint-Michel com o prolongamento da Azul: −0,214 pp (−0,380 a −0,049), contra intervalos de ±0,35 pp em cada valor |
| Falhas próprias herdadas por km, políticas, causa comum compartilhada | **Atende** (testes). A Rosa (29 km, média da rede) falha 1,83 vez por dia; o anel da Laranja, 0,42; a ligação Atwater–Université-de-Montréal, 0,20 |
| Trens do prolongamento seguem o horário; linha nova com as partidas da linha de referência; interrupção corta as conexões | **Atende** (testes: as partidas do trecho novo da Azul são as chegadas a Saint-Michel do horário; falha injetada de 30 min) |
| Caminho de sempre passa pela linha nova quando ela encurta a viagem | **Atende**. Côte-Vertu → Montmorency: 40 → 16,5 min pelo anel; Atwater → Université-de-Montréal: 20 → 5,9 min pela ligação |
| Rede atual idêntica sozinha e com variantes | **Atende** (teste, igualdade exata). No relatório, Angrignon → Saint-Michel na rede atual dá 98,463% e 18,42 min por dia, os números da spec 015 |
| Sem falhas: atraso zero e disponibilidade 1 | **Atende** (teste) |
| Paralelo nunca piora | **Atende** (teste, 40 dias, com a linha falhando) |
| Escala: minutos sem caminho, noves, razão com IC, gráfico logarítmico | **Atende**. Ex.: Côte-Vertu → Montmorency com rota alternativa vai de 2,27 para 5,38 noves (6,50 para 0,01 min por dia; razão 0,001) |
| Mesmo link, mesmos números | **Atende** (teste de rodadas determinísticas e do link) |
| Conferência no site publicado (commit 9f167d8) | Em tamanho de celular, a viagem padrão com a Rosa e a linha desenhada Angrignon–Snowdon rodou 1.000 dias, 4 versões da rede, em 3,7 s com 12 workers (navegador sem placa de vídeo), sem rolagem lateral e sem erro no console (`fontes/verificacao/linhas_novas_navegador_2026-10-21.json`). O mesmo teste em tamanho de notebook perdeu a conexão com o navegador no meio, com a memória da máquina quase no limite, e não foi repetido; o notebook ficou conferido no build local |

Achados (relatório, dia útil):

- **Uma linha nova no caminho de sempre ajuda mesmo sem rota alternativa quando troca várias linhas em série por uma curta.** O anel da Laranja leva Côte-Vertu → Montmorency de 98,90% para 99,90% (de 1,96 para 3,02 noves; 13,2 para 1,1 min por dia sem caminho) e encurta a viagem em 30 min.
- **Uma linha longa sem retorno parcial pode não ajudar a viagem curta que a usa.** Sem rota alternativa, a Rosa leva Vendôme → Place-des-Arts de 99,02% para 99,20%, diferença que não se separa do zero (−0,16 a +0,52 pp): ela tira a Laranja e a Verde do caminho, mas para inteira a cada uma das 1,83 falhas por dia nos seus 29 km. Com rota alternativa, a mesma Rosa leva a viagem a 99,991% (de 2,01 para 4,06 noves).
- **Um prolongamento que a viagem não usa piora a viagem sem retorno parcial** (Snowdon → Saint-Michel, −0,21 pp) e não muda nada com retorno parcial (diferença exatamente zero).
- **Causa comum compartilhada pesa quando há rota alternativa:** Atwater → Université-de-Montréal com a ligação vai a 4,84 noves com a linha independente e a 3,58 noves quando ela para junto com a Verde e a Azul.

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D56, D57 e D59; specs 019 e 020).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **O que mudou na entrada:** o mesmo da spec 015. A duração segue a faixa oficial da STM quando a calculada a contradiz (D55; minutos das falhas técnicas de 43.971 para 33.404, sem as interrupções de quase 20 h da Azul em Saint-Michel), e a taxa de cada linha vem de 9 fontes, por frota e setor, com o ano-base 2025 e a exposição medida (specs 017 e 018).
- **O que mudou no método:** a linha nova herda a taxa por km pela soma das fontes de cada família (trem e fixo) da linha de que herda (spec 019). As hipóteses do relatório (traçado, km, 36 km/h, partidas, causa comum, retorno parcial) não mudam. Com os parâmetros da v1.1.0, as viagens com linhas novas da referência saem idênticas (198 casos, spec 019): as diferenças abaixo vêm dos parâmetros.
- **Relatório:** [`linhas_novas.md`](../../fontes/verificacao/linhas_novas.md) refeito em 2026-11-11 (código `sha256-scripts:489914bafbbe991e`), com os mesmos casos, os mesmos 1.000 dias e a mesma semente.

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| Snowdon → Saint-Michel com o prolongamento da Azul, sem retorno parcial: diferença pareada | −0,214 pp (−0,380 a −0,049) | −0,111 pp (−0,134 a −0,088) |
| Mesmo caso: intervalo de cada valor | cerca de ±0,35 pp | cerca de ±0,07 pp |
| Falhas por dia: Rosa, anel da Laranja, ligação Atwater–Université-de-Montréal | 1,834, 0,416 e 0,197 | 1,575, 0,361 e 0,175 |
| Angrignon → Saint-Michel na rede atual | 98,463%; 18,42 min por dia | 99,282%; 8,60 min por dia |
| Côte-Vertu → Montmorency sem rota alternativa, sem e com o anel | 98,90% → 99,90%; 1,96 → 3,02 noves; 13,2 → 1,1 min por dia | 99,53% → 99,91%; 2,33 → 3,04 noves; 5,66 → 1,10 min por dia |
| Mesma viagem: tempo médio da saída à chegada, com − atual | −30,06 min | −29,53 min |
| Côte-Vertu → Montmorency com rota alternativa, sem e com o anel | 2,27 → 5,38 noves; 6,50 → 0,01 min por dia; razão 0,001 | 2,53 → ∞ noves; 3,51 → 0,00 min por dia; razão 0,000 |
| Vendôme → Place-des-Arts com a Rosa, sem rota alternativa | 99,02% → 99,20%; +0,179 pp (−0,160 a +0,518) | 99,46% → 99,49%; +0,026 pp (−0,101 a +0,153) |
| Mesmo caso: atraso médio, com − atual | −0,43 min (−1,14 a +0,28) | +0,10 min (+0,07 a +0,14) |
| Vendôme → Place-des-Arts com a Rosa e rota alternativa | 99,991%; 2,01 → 4,06 noves | 99,997%; 2,27 → 4,57 noves |
| Atwater → Université-de-Montréal com a ligação e rota alternativa: independente e com causa comum | 4,84 e 3,58 noves (0,02 e 0,31 min por dia) | ∞ e 3,61 noves (0,00 e 0,30 min por dia) |

∞ quer dizer nenhum minuto sem caminho nos 1.000 dias simulados, não risco zero. Não mudam: os caminhos de sempre e os tempos programados (Côte-Vertu → Montmorency, 40 → 16,5 min; Atwater → Université-de-Montréal, 20 → 5,9 min), as hipóteses das linhas novas e a diferença exatamente zero do prolongamento com retorno parcial. O exemplo do Contexto (99,54% e 99,98%) é da v1.1.0; após a revisão, Lionel-Groulx → Berri-UQAM vai de 99,74% para 99,98% (spec 015).

| Critério | Após a revisão |
|---|---|
| Linhas propostas e desenhadas, no mapa, na lista e no link | Não depende das taxas. A conferência no navegador da versão revista está na spec 020 |
| Mesmo dia com e sem; cada linha sozinha e todas juntas; diferença com IC pareado | **Continua atendendo**. Snowdon → Saint-Michel com o prolongamento: −0,111 pp (−0,134 a −0,088), contra cerca de ±0,07 pp em cada valor |
| Falhas próprias herdadas por km, políticas, causa comum compartilhada | **Continua atendendo** (testes). A Rosa falha 1,575 vez por dia; o anel, 0,361; a ligação Atwater–Université-de-Montréal, 0,175 |
| Trens do prolongamento seguem o horário; linha nova com as partidas da linha de referência; interrupção corta as conexões | **Continua atendendo** (testes) |
| Caminho de sempre passa pela linha nova quando ela encurta a viagem | **Continua atendendo**: os mesmos caminhos e tempos programados |
| Rede atual idêntica sozinha e com variantes | **Continua atendendo** (teste). No relatório, Angrignon → Saint-Michel na rede atual dá 99,282% e 8,60 min por dia, os números revistos da spec 015 (99,28% e 8,6 min) |
| Sem falhas: atraso zero e disponibilidade 1 | **Continua atendendo** (teste) |
| Paralelo nunca piora | **Continua atendendo** (teste) |
| Escala: minutos sem caminho, noves, razão com IC, gráfico logarítmico | **Continua atendendo**. Côte-Vertu → Montmorency com rota alternativa vai de 2,53 noves a ∞ (3,51 para 0,00 min por dia; razão 0,000) |
| Mesmo link, mesmos números | **Continua atendendo** (testes) |
| Conferência no site publicado | Não refeita aqui: a conferência da versão revista está na spec 020 |

Os testes com a fixture (`linhas_novas.test.ts`, `escala.test.ts` e `referencia_v1.test.ts`) passam na versão revista em 2026-11-11.

Achados, após a revisão (relatório, dia útil):

- **Linha nova que troca várias linhas em série por uma curta: se mantém, com ganho menor.** O anel leva Côte-Vertu → Montmorency de 99,53% para 99,91% (+0,381 pp, de +0,299 a +0,464), de 2,33 para 3,04 noves e de 5,66 para 1,10 min por dia sem caminho, e encurta a viagem em cerca de 30 min (−29,53). O ganho cai porque a rede atual melhorou; o tempo sem caminho com o anel quase não muda (1,1 min por dia).
- **Linha longa sem retorno parcial pode não ajudar a viagem curta: se mantém.** Sem rota alternativa, a Rosa leva Vendôme → Place-des-Arts de 99,46% para 99,49%, diferença que não se separa do zero (−0,101 a +0,153 pp), com 1,575 falha por dia. Agora ela também piora o atraso médio (+0,10 min, de +0,07 a +0,14), que na v1.1.0 não se separava do zero. Com rota alternativa, a Rosa leva a viagem a 99,997% (de 2,27 para 4,57 noves).
- **Prolongamento que a viagem não usa piora sem retorno parcial e não muda nada com ele: se mantém.** Snowdon → Saint-Michel: −0,111 pp (−0,134 a −0,088) sem retorno parcial; diferença exatamente zero com ele.
- **Causa comum compartilhada pesa quando há rota alternativa: se mantém, com distância maior.** Atwater → Université-de-Montréal com a ligação não fica nenhum minuto sem caminho nos 1.000 dias com a linha independente (∞ noves), e vai a 3,61 noves (0,30 min por dia) quando ela para junto com a Verde e a Azul.

## Fora de escopo

- Custo de construção e demanda induzida (como na spec 014).
- Engenharia de traçado: o traçado da linha desenhada é a linha reta entre as estações, com o fator de traçado da spec 014.
- Estações novas como origem ou destino da viagem (não há oferta nem demanda para elas).
- Fila de trens da linha nova depois de uma interrupção (os trens dela voltam ao horário).

## Riscos e dependências

- A linha nova herda as falhas das linhas atuais por km: uma linha longa sem retorno parcial para inteira a cada falha em qualquer trecho. É a hipótese da spec 014, e a página explica quando ela pesa no resultado.
- As partidas por hora da linha nova são hipótese (a linha de referência mais servida entre as que ela encosta).
- Com a rota alternativa, a escolha de caminho continua otimista (spec 015).

## Perguntas em aberto

- Pontos de retorno nas linhas novas além das pontas: hoje só as pontas e os terminais antigos dos prolongamentos.
