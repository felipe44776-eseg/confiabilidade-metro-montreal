# 015 — Confiabilidade de uma viagem: de uma estação a outra

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 007, 008, 009, 011
**Origem:** pedido da equipe em 2026-10-21 ("confiabilidades cruzadas, do tipo pessoa precisa ir de um ponto a outro")

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** Com as durações pela faixa oficial e as taxas por fonte, a viagem padrão Angrignon → Saint-Michel sobe de 98,46% para 99,28%, o atraso médio cai de 3,27 para 0,13 min, e a viagem continua se comportando como série. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

## Pergunta de engenharia

Para uma pessoa que precisa ir da estação A à estação B, com que frequência a falha de alguma linha do caminho impede a viagem ou a atrasa, e como a confiabilidade da viagem se compõe das linhas que ela usa (em série) e dos caminhos alternativos (em paralelo)?

## Contexto

- O simulador já mede a disponibilidade de cada linha e a de todos os pares de estações juntos, ponderados pela oferta (spec 009). Não há medida para um par escolhido.
- Uma viagem com baldeação depende de todas as linhas que usa: é um sistema em série. Se as falhas fossem independentes, a disponibilidade da viagem seria o produto das disponibilidades dos trechos. A causa comum (spec 006) para várias linhas juntas e quebra essa independência.
- Com a política "rota alternativa" (spec 008), a viagem vale por qualquer caminho livre: os caminhos ficam em paralelo.
- Não há passageiros diários nem pesquisa origem-destino (dicionário de dados). A viagem é de uma pessoa: não é ponderada por demanda.

## Critérios de aceite

- **Caminho:** dadas duas estações, quando escolhidas, então a página mostra o caminho de sempre (o mais rápido sem falhas no horário do tipo de dia): os trechos por linha e sentido, as baldeações e o tempo programado.
- **Disponibilidade da viagem:** dadas as rodadas do cenário, quando a viagem é avaliada, então a página mostra, com intervalo de 95%: a fração do horário de serviço em que o caminho existe; a mesma fração para cada trecho; o produto dos trechos (o valor em série, supondo independência) ao lado da medida simulada; os minutos por dia sem caminho e a chance de o dia ter ao menos uma interrupção no caminho.
- **Atraso de quem viaja:** dadas saídas de A a cada 10 minutos do horário de serviço, quando cada uma é simulada com os trens do dia (atrasos, bloqueios, cortes e cancelamentos), então a página mostra, com intervalo de 95%, a chance de chegar a B mais de 5, de 15 e de 60 minutos depois do programado, a chance de não chegar até o fim do serviço, o atraso médio e a chance de atraso de mais de 5 minutos por hora de saída.
- **Política de rota alternativa:** dada a política desligada, quando a viagem é simulada, então a pessoa só usa o caminho de sempre e espera a linha voltar; ligada, então pode usar qualquer caminho livre.
- **Coerência com a rede:** dado um dia simulado, quando a disponibilidade de cada par é calculada por este método e ponderada pela oferta, então reproduz a disponibilidade origem-destino da rede (spec 009) do mesmo dia.
- **Sem falhas:** dado um dia sem falhas, quando a viagem é simulada, então o atraso é zero em toda saída e a disponibilidade é 1.
- **Reprodutível:** dado o mesmo link (cenário, semente, rodadas, origem e destino), quando aberto, então dá os mesmos números; a rodada i usa o mesmo dia sorteado da aba "Muitos dias".

## Resultado (2026-10-21)

Código em `app/src/motor/viagem.ts`; aba "Viagem de A a B" no `/simulador/`; relatório [`viagem.md`](../../fontes/verificacao/viagem.md) gerado por `app/relatorios/viagem.relatorio.ts` (cenário padrão, dia útil, 1.000 dias por viagem, semente 20261021); testes em `app/tests/motor/viagem.test.ts`.

| Critério | Resultado |
|---|---|
| Caminho de sempre com trechos, sentido, baldeações e tempo | **Atende**. Ex.: Angrignon → Saint-Michel vai pela Verde até Berri-UQAM, pela Laranja até Jean-Talon e pela Azul até Saint-Michel |
| Disponibilidade total, por trecho, produto em série, minutos sem caminho e dias com interrupção | **Atende**. Angrignon → Saint-Michel: trechos 99,54%, 99,46% e 99,43%; produto 98,43%; simulado 98,46% (98,06% a 98,86%), ou seja, a viagem se comporta como série; 18,4 minutos por dia sem caminho; 75,2% dos dias com ao menos uma interrupção no caminho |
| Atraso por limiar, não chegar, atraso médio e por hora de saída | **Atende**. Na mesma viagem, 1,29% das saídas chegam mais de 5 min atrasadas, 0,85% mais de 15 e 0,62% mais de 60; o atraso médio de 3,27 min é puxado por paradas de horas na amostra de durações da STM |
| Rota alternativa desligada: só o caminho de sempre; ligada: qualquer caminho | **Atende**. Lionel-Groulx → Berri-UQAM sobe de 99,54% para 99,98% (Verde e Laranja em paralelo); Côte-Vertu → Montmorency, de 98,90% para 99,46% |
| Ponderada pela oferta, reproduz a disponibilidade origem-destino da rede no mesmo dia | **Atende** (teste, com e sem rota alternativa, até a 10ª casa) |
| Sem falhas: atraso zero e disponibilidade 1 | **Atende** (teste) |
| Mesmo link, mesmos números; rodada i = dia i do Monte Carlo | **Atende** (testes do link e das rodadas) |
| Conferência no site publicado (commit c2ff117) | Em tamanho de celular e de notebook, a viagem padrão rodou 1.000 dias em 3,1 e 3,2 s com 12 workers (navegador sem placa de vídeo), com as tabelas, as 20 barras por hora de saída e o caminho no mapa; sem rolagem lateral e sem erro no console (`fontes/verificacao/viagem_navegador_2026-10-21.json`) |

Achado: quando a mesma linha aparece em dois trechos (Côte-Vertu → Montmorency usa a Laranja duas vezes), os trechos não são independentes, e o produto (98,35%) fica abaixo do simulado (98,90%). A página explica esse caso na leitura do resultado.

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D56, D57 e D59; specs 019 e 020).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **O que mudou na entrada:**
  - nas 100 falhas em que a duração calculada contradiz a faixa oficial da STM, vale a faixa (D55). Os minutos das falhas técnicas vão de 43.971 para 33.404, e saem da amostra de durações as interrupções de quase 20 h da Azul em Saint-Michel (outubro de 2024);
  - a taxa de cada linha vem de 9 fontes, por frota e setor, com o ano-base 2025 e a exposição medida (specs 017 e 018).
- **O que mudou no método:** nada nesta spec. O motor sorteia a lista de fontes (spec 019); com os parâmetros da v1.1.0, ele reproduz byte a byte os 198 casos da referência anterior. As diferenças abaixo vêm dos parâmetros.
- **Relatório:** [`viagem.md`](../../fontes/verificacao/viagem.md) refeito em 2026-11-11 (código `sha256-scripts:489914bafbbe991e`), com o mesmo cenário, os mesmos 1.000 dias e a mesma semente.

Números de Angrignon → Saint-Michel, salvo quando a linha nomeia outra viagem.

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| Trechos Verde, Laranja e Azul | 99,54%, 99,46% e 99,43% | 99,74%, 99,71% e 99,81% |
| Produto dos trechos (série) | 98,43% | 99,25% |
| Viagem inteira, simulada | 98,46% (98,06% a 98,86%) | 99,28% (99,20% a 99,37%) |
| Minutos por dia sem caminho | 18,4 (13,6 a 23,2) | 8,6 (7,6 a 9,6) |
| Dias com ao menos uma interrupção no caminho | 75,2% | 72,7% |
| Saídas com mais de 5, 15 e 60 min de atraso | 1,29%, 0,85% e 0,62% | 0,40%, 0,16% e 0,05% |
| Chance de não chegar até o fim do serviço | 0,0053% | 0,0009% |
| Atraso médio | 3,27 min (0,87 a 5,67) | 0,13 min (0,03 a 0,24) |
| Lionel-Groulx → Berri-UQAM, sem e com rota alternativa | 99,54% e 99,98% | 99,74% e 99,98% |
| Côte-Vertu → Montmorency, sem e com rota alternativa | 98,90% e 99,46% | 99,53% e 99,71% |
| Côte-Vertu → Montmorency: produto contra simulado | 98,35% contra 98,90% (98,51% a 99,29%) | 99,22% contra 99,53% (99,45% a 99,60%) |
| Disponibilidade origem-destino da rede, dia útil (spec 009, 4.000 dias) | 99,246% | 99,484% |

Não mudam: o caminho de sempre de cada viagem (linhas, baldeações e tempo programado) e Lionel-Groulx → Berri-UQAM com rota alternativa (99,98%). As interrupções ficam mais curtas, não muito mais raras: os dias com interrupção caem pouco, e os minutos sem caminho, para menos da metade.

| Critério | Após a revisão |
|---|---|
| Caminho de sempre com trechos, sentido, baldeações e tempo | **Continua atendendo**: o mesmo caminho pela Verde, Laranja e Azul |
| Disponibilidade total, por trecho, produto em série, minutos sem caminho e dias com interrupção | **Continua atendendo**. A viagem continua se comportando como série: o produto (99,25%) fica dentro do intervalo do simulado (99,20% a 99,37%) |
| Atraso por limiar, não chegar, atraso médio e por hora de saída | **Continua atendendo**. A leitura muda: sem as paradas de quase 20 h da Azul, o atraso médio cai de 3,27 para 0,13 min, e as saídas com mais de 60 min de atraso, de 0,62% para 0,05% |
| Rota alternativa desligada: só o caminho de sempre; ligada: qualquer caminho | **Continua atendendo**. O ganho da rota alternativa fica menor porque o caminho de sempre ficou mais disponível: Lionel-Groulx → Berri-UQAM vai de 99,74% para 99,98%; Côte-Vertu → Montmorency, de 99,53% para 99,71% |
| Ponderada pela oferta, reproduz a disponibilidade origem-destino da rede no mesmo dia | **Continua atendendo** (teste com a fixture, com e sem rota alternativa; `viagem.test.ts` passa na versão revista em 2026-11-11) |
| Sem falhas: atraso zero e disponibilidade 1 | **Continua atendendo** (teste) |
| Mesmo link, mesmos números; rodada i = dia i do Monte Carlo | **Continua atendendo** (testes) |
| Conferência no site publicado | Não refeita aqui: a conferência da versão revista está na spec 020 |

O achado da mesma linha em dois trechos continua valendo: em Côte-Vertu → Montmorency, o produto (99,22%) fica abaixo do intervalo do simulado (99,45% a 99,60%), porque uma falha na Laranja para os dois trechos ao mesmo tempo.

## Fora de escopo

- Demanda: quantas pessoas fazem a viagem (não há dado diário).
- Ônibus de substituição durante a interrupção (não há dado de quando e onde a STM os põe).
- Tempo de caminhada até a plataforma de origem e da plataforma de destino até a saída.

## Riscos e dependências

- A escolha de caminho com a rota alternativa supõe que a pessoa sabe, ao sair, quanto vai durar cada interrupção: é o limite otimista da política.
- O tempo de baldeação é a hipótese `tempo_transferencia_min`, a mesma do grafo da spec 009.

## Perguntas em aberto

- Limiares de atraso: 5, 15 e 60 minutos são escolha de apresentação, não norma da STM.
