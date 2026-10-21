# 015 — Confiabilidade de uma viagem: de uma estação a outra

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 007, 008, 009, 011
**Origem:** pedido da equipe em 2026-10-21 ("confiabilidades cruzadas, do tipo pessoa precisa ir de um ponto a outro")

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

Achado: quando a mesma linha aparece em dois trechos (Côte-Vertu → Montmorency usa a Laranja duas vezes), os trechos não são independentes, e o produto (98,35%) fica abaixo do simulado (98,90%). A página explica esse caso na leitura do resultado.

## Fora de escopo

- Demanda: quantas pessoas fazem a viagem (não há dado diário).
- Ônibus de substituição durante a interrupção (não há dado de quando e onde a STM os põe).
- Tempo de caminhada até a plataforma de origem e da plataforma de destino até a saída.

## Riscos e dependências

- A escolha de caminho com a rota alternativa supõe que a pessoa sabe, ao sair, quanto vai durar cada interrupção: é o limite otimista da política.
- O tempo de baldeação é a hipótese `tempo_transferencia_min`, a mesma do grafo da spec 009.

## Perguntas em aberto

- Limiares de atraso: 5, 15 e 60 minutos são escolha de apresentação, não norma da STM.
