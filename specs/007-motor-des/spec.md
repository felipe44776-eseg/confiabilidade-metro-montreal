# 007 — Motor de simulação por eventos discretos

**Status:** implementada
**Fase:** F3 (semanas 4 a 7)
**Depende de:** 002, 004

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** O motor passou a sortear 9 fontes por linha (spec 019); com os parâmetros da v1.1.0, os 198 casos da referência saem idênticos, e nenhum número desta spec muda. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

## Pergunta de engenharia
Um modelo da rede, trem a trem, reproduz a operação real sem falhas e permite injetar falhas que se propagam como na prática? O número que responde é o desvio entre a operação simulada sem falhas e o horário publicado.

## Contexto
- Horário do GTFS: intervalo mediano em dia útil de 3, 6 e 8 min (Verde e Laranja), 5, 10 e 10 min (Amarela) e 4, 7 e 8 min (Azul), no pico, no entrepico e à noite. Viagem de ponta a ponta de 36 a 38, 46 a 49, 6 a 7 e 15 a 17 minutos (research.md da spec 004).
- Às 08:00 circulam 26, 32, 2 e 9 trens.
- Traçado real e posição de cada estação ao longo da linha vêm da spec 002.
- Falha de trem para a linha naquele sentido; falha de equipamento fixo para um trecho ou uma estação.

## Critérios de aceite
- Dada a simulação com falhas desligadas, quando um dia útil é simulado, então o intervalo entre trens por linha e período fica a até 30 segundos do horário, e a viagem de ponta a ponta a até 1 minuto.
- Dada a simulação com falhas desligadas, quando se conta os trens em viagem às 08:00, então o resultado é 26, 32, 2 e 9, com tolerância de 1 trem.
- Dada a mesma semente e os mesmos parâmetros, quando a simulação roda duas vezes, então o registro de eventos é idêntico (mesmo hash).
- Dada uma falha de trem num trecho, quando injetada, então o trecho fica bloqueado no sentido do trem até o fim da interrupção, e os trens atrás esperam, com o atraso visível no registro.
- Dada uma falha de equipamento fixo, quando injetada, então bloqueia o trecho ou a estação num ou nos dois sentidos, conforme o parâmetro.
- Dado um evento de causa comum, quando injetado, então para a Verde e a Laranja ao mesmo tempo.
- Dado o registro de uma rodada, quando lido, então tem para cada evento: hora, linha, trem, trecho, tipo e origem do sorteio.

## Resultado (2026-10-21)

Código em `app/src/motor/`; testes em `app/tests/motor/` (`horario`, `falhas`, `prng`, `reais`).

| Critério | Resultado |
|---|---|
| Sem falhas: intervalos a até 30 s e ponta a ponta a até 1 min do horário | **Atende**: o motor reproduz o horário do GTFS exatamente nos três tipos de dia |
| Trens em viagem às 08:00: 26, 32, 2 e 9 (±1) | **Atende**: 26, 31, 2 e 9 |
| Mesma semente, mesmo registro (hash) | **Atende** (teste) |
| Falha de trem bloqueia o sentido e os trens de trás esperam | **Atende** (teste com falha injetada) |
| Falha de equipamento fixo em 1 ou 2 sentidos, conforme o parâmetro | **Atende** (teste) |
| Causa comum para Verde e Laranja juntas | **Atende**; com os dados reais, a causa comum é sorteada por grupo de linhas (2 a 4), sem contar um evento duas vezes |
| Registro com hora, linha, trem, trecho, tipo e origem do sorteio | **Atende** |

Desvios registrados no `plan.md`: o bloco inclui a plataforma de chegada; a escala da renovação Weibull é normalizada para média 1; desde 2026-10-21 a duração positiva é sorteada da amostra observada.

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-10 (decisão D59; spec 019).* Os critérios e os resultados acima não mudam: nenhum depende das taxas.

- **O que mudou no motor:** cada linha deixou de ter duas fontes fixas (MR e EF) e passou a ter a lista do contrato v2, com 9 fontes por frota e setor. Cada fonte tem taxa, renovação, duração, locais e sub-fluxo de números aleatórios próprios. A família da fonte decide o efeito: a de trem para o trem no sentido, a fixa bloqueia o trecho, como antes.
- **Como se provou que nada mais mudou:** antes da troca, a equipe gravou a referência do motor (198 casos: registro de dias fixos, vetor de métricas, bloqueios origem-destino, viagens com linhas novas e expansão). Com o contrato v1 (v1.1.0), os 198 saem idênticos depois dos passos 1 e 2 da spec 019 (`app/tests/motor/referencia_v1.test.ts`).
- **Registro:** a falha passa a levar o id da fonte e a classe de gravidade (D58); os rótulos `falhas_mr` e `falhas_ef` continuam, como soma das fontes de cada família.

## Fora de escopo
- Física da tração, frenagem e consumo de energia.
- Sinalização fina: cada trecho entre estações é tratado como um bloco que admite um trem por sentido (simplificação declarada).
- Passageiros embarcando e desembarcando.

## Riscos e dependências
- A simplificação em blocos pode errar a propagação de atrasos no pico. Mitigação: comparar com o histórico na spec 012.
- O horário é do feed atual; anos passados podem ter outra oferta (spec 004).

## Perguntas em aberto
- Onde ficam os aparelhos de mudança de via, que permitem retorno parcial? A posição não está verificada (spec 008).
- Quanto tempo leva para retirar um trem falho de serviço? Não está na base; entra como parâmetro.
