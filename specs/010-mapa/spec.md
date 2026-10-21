# 010 — Mapa com trens animados

**Status:** implementada com exceções
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 002, 007

## Pergunta de engenharia
A pessoa consegue ver a simulação acontecendo no espaço real: trens andando no traçado, falhas aparecendo onde ocorrem e o atraso se espalhando? O número que responde é a fluidez da animação com todos os trens em movimento.

## Contexto
- A spec 002 entrega o traçado real das 4 linhas (OpenStreetMap), as 73 estações com posição ao longo da linha e os locais dos incidentes com status (verificado, deduzido, aproximado, sem posição).
- Na hora de pico circulam cerca de 70 trens (26, 32, 2 e 9 às 08:00, sem contar os parados nos terminais).
- A página mínima de mapa da Fase 0 já mostra linhas, estações e locais de falha.

## Critérios de aceite
- Dada uma rodada da simulação, quando reproduzida no mapa, então cada trem anda sobre o traçado real, com a posição interpolada entre as estações pelo horário simulado.
- Dado o pico com todos os trens em movimento, quando a animação roda num notebook comum, então mantém pelo menos 30 quadros por segundo.
- Dada uma falha, quando acontece na rodada, então aparece no local certo do mapa e o trecho bloqueado muda de aparência até a retomada.
- Dado um incidente histórico no mapa, quando clicado, então mostra código, número de falhas, tipo, status da posição e método usado para localizá-lo.
- Dado o mapa, quando aberto, então a atribuição ao OpenStreetMap (ODbL), à STM (CC BY 4.0) e ao fornecedor do mapa de fundo fica visível.
- Dado o controle de tempo, quando a pessoa pausa, acelera ou volta, então o mapa e os indicadores ficam sincronizados.
- Dada uma tela de celular, quando a página abre, então o mapa e os controles cabem sem rolagem lateral.
- *Acrescentado em 2026-10-21, a pedido da equipe (decisão D49):* dado o controle de velocidade, quando a pessoa escolhe 1 h/s, 10 h/s ou 1 dia/s, então a animação emenda os dias sorteados sem parar e conta os dias completos e as falhas sorteadas neles.
- *Acrescentado em 2026-10-21 (D49):* dada uma falha, quando a animação passa pelo instante dela, em qualquer velocidade, então aparece um evento vermelho no local por pelo menos 2 segundos de relógio e um item na lista de eventos sobre o mapa; a barra de tempo marca em vermelho as falhas do dia.

## Resultado (2026-10-21)

Página `/simulador/` (código em `app/src/simulador/`); testes em `app/tests/simulador/`; plano com as medições em `plan.md`.

| Critério | Resultado |
|---|---|
| Trens andam sobre o traçado real, interpolados pelo horário simulado | **Atende**: as 73 estações caem a menos de 150 m da coordenada do GTFS no traçado (maior 129 m) |
| ≥ 30 quadros por segundo no pico | **Atende a 300× no teste disponível; abaixo de 30 em alta velocidade no mesmo teste, com a página folgada. Pendente**: conferir num notebook comum. Sem placa de vídeo (Edge sem janela, WebGL por software), no site publicado (commit abbe2ec), em tamanho de notebook: 33 quadros por segundo a 300×, 30 a 1 h/s e 28 a 10 h/s e a 1 dia/s, com a thread da página ocupada de 22% a 35% do tempo; em tamanho de celular, de 33 a 60 (`fontes/verificacao/navegador_2026-10-21.json`). Com a thread folgada, o limite é o desenho por software, não o cálculo: sortear um dia com trajetórias custa cerca de 3 ms e as posições de todos os trens, 0,12 ms. As medidas variam entre execuções na mesma máquina. Registros anteriores: 34 fps (notebook) e 60 (celular) a 300× na rodada 3 da revisão crítica; os 60 fps de antes disso foram medidos com a animação parada e a página oculta (D46) |
| Falha no local certo e trecho bloqueado com outra aparência até a retomada | **Atende** |
| Incidente histórico clicável com código, falhas, tipo, status e método | **Atende** |
| Atribuição ao OpenStreetMap, à STM e ao fornecedor do fundo | **Atende** |
| Pausar, acelerar e voltar com mapa e indicadores sincronizados | **Atende** |
| Celular sem rolagem lateral | **Pendente**: layout com gutter de 16 px, não conferido num aparelho. No navegador sem janela em 390×844, a rolagem lateral é zero e nenhum elemento passa da largura (`publicacao/testa_navegador.py`, revisão crítica de 2026-10-21, rodada 3) |
| Velocidades de 1 h/s, 10 h/s e 1 dia/s com os dias emendados e o placar (acrescentado em 2026-10-21, D49) | **Atende**: a 1 dia/s, 7 dias emendados em 6 segundos nos dois tamanhos; depois de 15 dias completos, o placar mostrou 48 falhas sorteadas, 3,20 por dia, contra 3,35 esperadas (`fontes/verificacao/navegador_2026-10-21.json`) |
| Evento vermelho por falha em qualquer velocidade, lista de eventos e marcas na barra (acrescentado em 2026-10-21, D49) | **Atende**: a 1 dia/s, 19 (celular) e 21 (notebook) pulsos vermelhos em 6 segundos, cada um com 2,6 segundos de relógio, e a lista com as 4 últimas falhas (`navegador_2026-10-21.json`); teste de que um quadro em alta velocidade não perde nem repete falha (`app/tests/simulador/animacao.test.ts`) |

## Fora de escopo
- Mapa 3D, túneis em profundidade e plantas de estação.
- Posição em tempo real dos trens da STM (exigiria chave de API e servidor).

## Riscos e dependências
- O mapa de fundo gratuito não tem garantia de serviço. Mitigação: testar mapa de fundo hospedado no próprio site e manter um fundo simples de reserva.
- Locais "sem posição" (6% das falhas, sobretudo subestações) não aparecem no mapa; a legenda precisa dizer isso.

## Perguntas em aberto
- Mostrar só uma rodada por vez ou um resumo de muitas rodadas (mapa de calor de interrupções)?
- Desenhar os dois sentidos de cada linha separados?
