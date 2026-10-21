# 004 — Exposição: trens-hora e km-carro

**Status:** especificada
**Fase:** F1 (semanas 2 e 3)
**Depende de:** 000, 001, 002

## Pergunta de engenharia
Quanto serviço cada linha ofereceu em cada hora, para que a taxa de falha seja medida por exposição e não por tempo de calendário? O número que responde é o erro mensal da exposição estimada contra o km real.

## Contexto
- A quilometragem real por composição, linha e dia vai de 2019-01-01 a 2023-09-30 e soma 411,63 milhões de km-carro (FONTES.md). Os incidentes vão até 2026-06-30: de outubro de 2023 em diante a exposição precisa ser estimada.
- O horário do GTFS (feed 20261007130000_26N) dá o intervalo mediano em dia útil: Verde 3 min no pico, 6 no entrepico e 8 à noite; Laranja 3, 6 e 8; Amarela 5, 10 e 10; Azul 4, 7 e 8. A viagem de ponta a ponta leva 36 a 38, 46 a 49, 6 a 7 e 15 a 17 minutos.
- Às 08:00 circulam 26, 32, 2 e 9 trens (sem contar os parados nos terminais).
- Frota: MPM-10 com 71 trens de 9 vagões; MR-73 em blocos de 3 vagões; a Azul roda com 6 vagões e a Amarela com 9.
- O km real traz o modo de condução (`Code dégradation`: PA, condução automática, em 88% do km; CMC, manual; CD com significado não verificado) e o período de exploração (J, M, U, S, N).
- Composições distintas por dia útil: Verde cerca de 50, Laranja 47, Azul 15, Amarela 6.

## Critérios de aceite
- Dado o horário do GTFS, quando a exposição é calculada, então às 08:00 de um dia útil o número de trens em viagem é 26, 32, 2 e 9, com tolerância de 1 trem por linha.
- Dado o período de 2019-01 a 2023-09, quando a exposição estimada pelo horário é comparada ao km real, então o erro mensal fica em até 10% por linha, depois de um fator de calibração por linha e período de exploração.
- Dado um mês depois de 2023-09, quando a exposição é usada, então ela aparece com status "estimado", nunca como medida.
- Dadas as horas de greve da spec 003, quando a exposição é montada, então essas horas têm a oferta reduzida, e não a oferta normal.
- Dado o km real, quando dividido por frota, então MR-73 e MPM-10 somam o total menos os 22 registros do material tipo 63, e a diferença aparece no relatório.
- Dada cada linha, hora e frota, quando a tabela de exposição é gravada, então cada valor tem fonte (km real ou horário) e status.

## Fora de escopo
- Exposição por passageiro: não existe dado diário de passageiros.
- Reconstituir horários de anos passados a partir de feeds antigos, salvo se aparecerem no Mobility Database (não verificado).

## Riscos e dependências
- O horário é do feed atual. Pode não representar 2019 a 2023 (pandemia, obras). Mitigação: calibrar por período contra o km real e mostrar o resíduo.
- O significado de `Code dégradation` CD não é conhecido. Fica fora do modelo até confirmação.

## Perguntas em aberto
- O que significam os sufixos B e V nos códigos de período usados desde 2021?
- Vale pedir à STM, por acesso à informação, o km real depois de 2023-09?
