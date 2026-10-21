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
| ≥ 30 quadros por segundo no pico | **Atende no teste disponível, com pouca folga**: 0,10 ms de cálculo por quadro (orçamento de 33 ms) e, com a animação tocando a 300× no pico da manhã, 34 fps em tamanho de notebook e 60 em tamanho de celular no Edge sem janela com WebGL por software (`publicacao/testa_navegador.py`, revisão crítica de 2026-10-21, rodada 3). Os 60 fps registrados antes foram medidos com a animação parada e a página oculta (correção de 2026-10-21, D46). **Pendente**: conferir num notebook comum no endereço publicado |
| Falha no local certo e trecho bloqueado com outra aparência até a retomada | **Atende** |
| Incidente histórico clicável com código, falhas, tipo, status e método | **Atende** |
| Atribuição ao OpenStreetMap, à STM e ao fornecedor do fundo | **Atende** |
| Pausar, acelerar e voltar com mapa e indicadores sincronizados | **Atende** |
| Celular sem rolagem lateral | **Pendente**: layout com gutter de 16 px, não conferido num aparelho. No navegador sem janela em 390×844, a rolagem lateral é zero e nenhum elemento passa da largura (`publicacao/testa_navegador.py`, revisão crítica de 2026-10-21, rodada 3) |

## Fora de escopo
- Mapa 3D, túneis em profundidade e plantas de estação.
- Posição em tempo real dos trens da STM (exigiria chave de API e servidor).

## Riscos e dependências
- O mapa de fundo gratuito não tem garantia de serviço. Mitigação: testar mapa de fundo hospedado no próprio site e manter um fundo simples de reserva.
- Locais "sem posição" (6% das falhas, sobretudo subestações) não aparecem no mapa; a legenda precisa dizer isso.

## Perguntas em aberto
- Mostrar só uma rodada por vez ou um resumo de muitas rodadas (mapa de calor de interrupções)?
- Desenhar os dois sentidos de cada linha separados?
