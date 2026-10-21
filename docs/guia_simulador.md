# Guia do simulador

Como usar a página https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/simulador/ e como ler o que ela mostra. Tudo roda no seu navegador: nada é enviado para servidor.

## O que o simulador faz

Ele recria um dia de operação do metrô de Montreal, trem a trem, com o horário real (GTFS da STM), e sorteia falhas com as taxas e as durações estimadas dos dados de 2019 a 2026. Repetindo o dia milhares de vezes (Monte Carlo), estima quanto cada linha fica parada, quantos trens-hora se perdem e com que frequência um par de estações fica sem caminho, sempre com intervalo de 95%.

## O painel da esquerda: o cenário

| Grupo | O que muda |
|---|---|
| **Dia** | Tipo de dia (útil, sábado, domingo) e mês. O tipo de dia muda o horário; o mês muda a estação do ano no modelo de falhas |
| **Clima** | Temperatura, precipitação, condição (seco, chuva, neve, chuva congelante) e neve no solo. Cada escolha multiplica a taxa de falha pelo fator estimado no modelo (spec 005), nunca por um número escolhido à mão |
| **Eventos** | Jogo do Canadiens, fim de semana do GP, feriado e greve. A greve deixa só as viagens que partem nas faixas com serviço e não muda a taxa de falha por trem: o modelo estimou 1,17 (material rodante) e 1,11 (equipamentos fixos) para dia de greve, mas o intervalo de 95% contém 1 (`fontes/verificacao/modelo_taxa.md`), e desde 2026-10-21 o simulador não aplica esse multiplicador (decisão D42) |
| **Políticas de tolerância a falhas** | Liga ou desliga cada uma das seis políticas da spec 008 |
| **Hipóteses (sem dado)** | Parâmetros que não existem nas fontes públicas (tempo de reparo na oficina, separação mínima entre trens, tempo de retirada do trem falho...). Cada uma tem uma faixa razoável no `parametros.json`; o controle vai meia faixa além de cada ponta, para testar extrapolações, e fora da faixa a página avisa. O valor aparece com o rótulo "hipótese" |
| **Rodadas e semente** | Quantos dias simular e a semente do sorteio. A mesma semente dá os mesmos números |

**Copiar o link do cenário** guarda tudo (cenário, semente e rodadas) no endereço. Quem abrir o link vê exatamente os mesmos números. **Voltar ao padrão** limpa o cenário.

**Avisos** aparecem quando o cenário sai do que foi observado nos dados (por exemplo, neve no solo em julho) ou quando uma hipótese sai da faixa. O simulador continua rodando, mas o número passa a ser extrapolação.

## As abas

### Dia no mapa

Um dia simulado, com os trens andando sobre o traçado real. Use ▶ para tocar ou pausar, **Velocidade** para acelerar (1× a 300×) e a barra para avançar ou voltar no dia. Trecho bloqueado fica em vermelho tracejado até a retomada; o marcador mostra onde a falha ocorreu. **Dia mostrado** troca o dia sorteado e **Falhas do dia** lista as falhas com hora, linha, tipo e duração. Com **Locais históricos de falha** ligado, os pontos podem ser clicados: mostram o código da STM, o número de falhas, o tipo e se a posição é verificada, deduzida ou aproximada. No canto do mapa há um contador de quadros por segundo.

### Muitos dias

**Rodar** simula os dias pedidos em paralelo (um processo por núcleo do computador, até 16) e mostra, por linha: minutos parados, disponibilidade, trens-hora perdidos, viagens afetadas e chance de frota completa, cada um com o intervalo de 95%; falhas por dia (soma das três causas, só a média); e, para a rede, a disponibilidade por par origem-destino. O resultado traz o número de dias e a semente. **Estimar o ano** roda dia útil, sábado e domingo e soma pelo calendário (251, 52 e 62 dias). Ao abrir a página, o cenário do link (ou o padrão) já roda com o número de dias escolhido: 1.000 no padrão.

### Comparar cenários

**Fixar o cenário atual como A**, mude o que quiser e **Comparar A com o cenário atual (B)**. Os dois lados usam as mesmas falhas sorteadas (números aleatórios comuns), então a diferença mostra só o efeito da mudança, com intervalo de 95%. É assim que se mede o efeito de uma política.

### Que linha construir

Avalia as cinco candidatas de expansão com fonte pública e qualquer ligação entre duas estações escolhidas em **De** e **Para**. **Busca em todas as ligações curtas** testa todas as ligações diretas até a distância escolhida. O ganho é a mudança na disponibilidade dos pares de estações atuais, com e sem causa comum compartilhada. Uma linha nova só ganha quando cria um caminho alternativo; ramais não ganham (veja `fontes/verificacao/expansao.md`).

### Parâmetros

Todos os números do modelo: valor, intervalo de 95%, status (ajustado, deduzido, hipótese, não verificado) e link para o relatório que os produziu. O método aparece ao passar o mouse sobre o link; o número de observações aparece nas durações e na causa comum.

## Como ler os resultados

- **Disponibilidade** é a fração do tempo de serviço sem bloqueio na linha. 99,5% num dia útil de 20 horas são cerca de 6 minutos parados.
- **Disponibilidade origem-destino** é a fração dos pares de estações que têm caminho, ponderada pela oferta de trens (não há dado de passageiros).
- **Intervalo de 95%** é a incerteza do Monte Carlo. Se o intervalo de uma diferença contém zero, o efeito não é detectável com aquele número de dias.
- **Hipótese** é escolha nossa, sem dado. O resultado que depende dela deve ser lido como "se o reparo levar X dias, então...".

## Limites que valem para toda simulação

- Um trem por trecho e por sentido; os trens seguem viagens individuais do horário (o GTFS não tem blocos de trem).
- O retorno parcial só acontece nas pontas de viagem do horário: a posição dos aparelhos de mudança de via não é pública.
- O tempo de reparo na oficina não é publicado pela STM.
- Fechamentos planejados e quedas de energia não têm série própria.

## Para conferir no seu computador

O desempenho foi medido sem placa de vídeo, com WebGL por software e a animação tocando a 300× no pico da manhã: 34 quadros por segundo em tela de notebook e 60 em tela de celular (spec 010). Com a animação parada, o contador mostra o ritmo da página (60), não o da animação. Falta a equipe conferir num notebook comum, no celular e no Firefox e no Safari. Se algo não abrir, anote o navegador e o que apareceu no console (F12).
