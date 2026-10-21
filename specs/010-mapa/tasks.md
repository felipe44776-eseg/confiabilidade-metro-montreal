# 010 — Mapa e animação: tarefas

- [x] `app/src/simulador/tracado.ts`: km → ponto no traçado do OSM, pedaço entre dois km (testes: sintético e as 73 estações a menos de 150 m da coordenada do GTFS; maior distância 129 m).
- [x] `app/src/simulador/animacao.ts`: posição de cada trem pela trajetória simulada, bloqueios do registro, minutos parados até t (testes: 26, 31, 2 e 9 trens às 08:00 iguais ao motor; falha injetada bloqueia de 08:00 a 08:15 e soma 15 min, igual ao motor).
- [x] `app/src/simulador/mapa_sim.ts`: traçado, estações, trens com a cor da linha, trecho bloqueado em vermelho tracejado, marcador de falha, locais históricos clicáveis (código, falhas, tipo, status e método), candidatas tracejadas.
- [x] Atribuição visível: OpenStreetMap (ODbL), STM (CC BY 4.0) e OpenFreeMap.
- [x] Controle de tempo (tocar, pausar, 1× a 300×, barra) sincronizado com o relógio e os indicadores.
- [x] Velocidades de 1 h/s, 10 h/s e 1 dia/s, com os dias emendados e o placar de dias e falhas (D49).
- [x] Evento vermelho por falha: pulso de 2,6 s de relógio no local, lista de eventos sobre o mapa e marcas na barra de tempo (D49).
- [x] Custo por quadro medido: 0,10 ms no pico; contador de fps na página.
- [x] Correção do worker do MapLibre 6 nas duas páginas (o mapa não desenhava as fontes sem ele).
- [x] Teste de ponta a ponta no Chrome sem janela: mapa abre, 58 trens às 07:30 no cenário padrão, falhas listadas, sem erro no console.
- [ ] Equipe: conferir os fps num notebook comum e o layout no celular, no endereço publicado.
