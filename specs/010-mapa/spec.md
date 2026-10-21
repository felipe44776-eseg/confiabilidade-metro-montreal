# 010 — Mapa com trens animados

**Status:** especificada
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

## Fora de escopo
- Mapa 3D, túneis em profundidade e plantas de estação.
- Posição em tempo real dos trens da STM (exigiria chave de API e servidor).

## Riscos e dependências
- O mapa de fundo gratuito não tem garantia de serviço. Mitigação: testar mapa de fundo hospedado no próprio site e manter um fundo simples de reserva.
- Locais "sem posição" (6% das falhas, sobretudo subestações) não aparecem no mapa; a legenda precisa dizer isso.

## Perguntas em aberto
- Mostrar só uma rodada por vez ou um resumo de muitas rodadas (mapa de calor de interrupções)?
- Desenhar os dois sentidos de cada linha separados?
