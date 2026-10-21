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

### Peso de cada variável

No topo do painel, o bloco **Peso de cada variável** diz como ler os pesos, e **Como o peso foi calculado** abre o método. Embaixo de cada campo aparece o peso do valor escolhido: o multiplicador da taxa de falha por trem em circulação, para material rodante (MR) e equipamentos fixos (EF), com o intervalo de 95%. 1 é a condição de referência do modelo, que é o cenário padrão; ×1,30 quer dizer 30% mais falhas por trem-hora, com o resto igual. Nas caixas desmarcadas aparece o peso de marcar.

Os pesos vêm de uma regressão binomial negativa ajustada às horas de serviço de cada linha de 2019 a junho de 2026 (`pipeline/modelo_taxa.py`, spec 005), com o log dos trens-hora como deslocamento e todas as variáveis no mesmo modelo. Por isso cada peso vale com as outras variáveis fixas, e variáveis que andam juntas nos dados (inverno, frio e neve no solo) repartem o efeito entre si. Quando o intervalo contém 1, os dados não distinguem o efeito de nenhum efeito; o simulador usa o valor estimado mesmo assim, e os **Avisos** apontam os intervalos largos. A faixa do dia (abertura, picos, noite) também tem peso, que muda hora a hora; a tabela dela está no fim da nota. O efeito do cenário inteiro nas falhas por dia aparece em **Cenário aplicado**, acima do mapa.

## Como saber que o cenário está valendo

A faixa **Cenário aplicado**, acima do mapa, mostra:

- cada item do cenário, com o que difere do padrão em destaque;
- as **falhas esperadas por dia** nesse cenário e no cenário padrão, a razão entre elas e o valor por linha. É a taxa do modelo somada ao longo do dia, a mesma que o sorteio usa;
- a hora em que o cenário foi aplicado. A faixa pisca a cada mudança, e o dia no mapa é sorteado de novo com o cenário novo;
- com a animação emendando os dias, quantos dias completos já passaram e a média de falhas sorteadas neles, para comparar com o esperado. Com poucos dias a média varia bastante, porque as falhas vêm agrupadas; com dezenas de dias ela se aproxima do esperado.

Alguns fatores aumentam a taxa e outros a diminuem (veja a aba **Parâmetros**), e combinados podem quase se cancelar: a faixa mostra o efeito líquido. As políticas, exceto o tratamento da causa comum, não mudam quantas falhas ocorrem; mudam quanto elas param a linha, o que aparece em **Muitos dias** e **Comparar cenários**.

## As abas

### Dia no mapa

Um dia simulado, com os trens andando sobre o traçado real. Use ▶ para tocar ou pausar, **Velocidade** para acelerar e a barra para avançar ou voltar no dia. As velocidades vão de 1× (tempo real) a **1 h/s**, **10 h/s** e **1 dia/s**. Como a rede tem poucas falhas por dia, use 1 h/s ou mais rápido para vê-las. Com **Ao fim do dia, seguir para o próximo dia sorteado** ligado (o padrão), a animação não para: emenda os dias do mesmo cenário (a noite sem serviço é pulada), e o **Dia mostrado** avança sozinho.

**Evento vermelho:** quando a animação passa por uma falha, o local pisca em vermelho por 2,6 segundos de relógio, em qualquer velocidade, e a falha entra na lista no canto do mapa (dia, hora, linha, tipo e quanto parou). O círculo vermelho grande fica enquanto a linha está parada; depois, um ponto vermelho menor marca a falha até o fim do dia. Na barra de tempo, cada risco vermelho é uma falha do dia (o risco mais alto parou a linha), e na tabela **Falhas do dia** as que ainda não aconteceram ficam em cinza. Clicar numa falha da tabela leva a 1 minuto antes dela e pisca o local. Trecho bloqueado fica em vermelho tracejado até a retomada; o marcador mostra onde a falha ocorreu. **Dia mostrado** troca o dia sorteado e **Falhas do dia** lista as falhas com hora, linha, tipo e duração. Com **Locais históricos de falha** ligado, os pontos podem ser clicados: mostram o código da STM, o número de falhas, o tipo e se a posição é verificada, deduzida ou aproximada. No canto do mapa há um contador de quadros por segundo.

### Muitos dias

**Rodar** simula os dias pedidos em paralelo (um processo por núcleo do computador, até 16) e mostra o cenário da rodada e, por linha: minutos parados, disponibilidade, trens-hora perdidos, viagens afetadas e chance de frota completa, cada um com o intervalo de 95%; falhas por dia (soma das três causas, só a média), ao lado do **esperado pelo modelo**; e, para a rede, a disponibilidade por par origem-destino. O resultado traz o número de dias e a semente. **Estimar o ano** roda dia útil, sábado e domingo e soma pelo calendário (251, 52 e 62 dias). Ao abrir a página, o cenário do link (ou o padrão) já roda com o número de dias escolhido: 1.000 no padrão.

### Viagem de A a B

Para quem precisa ir de uma estação a outra. Escolha **De** e **Para** (⇄ inverte). A página mostra o caminho de sempre, o mais rápido sem falhas no horário do tipo de dia: os trechos por linha e sentido e as baldeações, também destacados no mapa. **Avaliar a viagem** simula os dias pedidos no painel (os mesmos dias da aba **Muitos dias**) e mostra:

- **Disponibilidade do caminho:** a fração do horário de serviço em que dá para fazer a viagem, para cada trecho e para a viagem inteira, com os minutos por dia sem caminho e a chance de o dia ter ao menos uma interrupção no caminho;
- **Produto dos trechos:** a conta em série, como se as linhas falhassem de forma independente, ao lado do valor simulado. Se o produto cai dentro do intervalo do simulado, a viagem se comporta como série. Se a mesma linha aparece em dois trechos, eles não são independentes, e a página avisa;
- **Atraso de quem viaja:** para saídas a cada 10 minutos, a chance de chegar mais de 5, 15 e 60 minutos depois do programado, de não chegar até o fim do serviço, o atraso médio e a chance de atraso por hora de saída. O atraso usa os trens simulados do dia, inclusive a espera até a linha voltar e a fila de trens depois.

Com a política **Rota alternativa de passageiros** ligada no painel, a pessoa pode usar qualquer caminho livre: os caminhos ficam em paralelo. Ela escolhe sabendo quanto vai durar cada interrupção, o que é o limite otimista. Não entram ônibus de substituição, caminhada até a plataforma nem lotação. O atraso médio é puxado pelas poucas saídas que pegam paradas longas: a amostra de durações da STM tem paradas de horas. Origem e destino vão no link.

**Linhas novas: construir e comparar** (spec 016). Marque linhas propostas (as cinco da aba **Que linha construir** e o projeto Rosa com a Azul) ou desenhe uma: **Desenhar uma linha**, depois escolha as estações na lista ou toque no mapa (perto de uma estação, ela entra; fora das estações, vira uma estação nova) e **Concluir a linha**. **Avaliar a viagem** passa a medir, nos mesmos dias simulados, a rede atual, cada linha nova sozinha e, com duas ou mais, todas juntas. A página mostra o caminho de sempre com cada linha (se ela encurta a viagem, ele passa por ela), uma tabela com disponibilidade, minutos sem caminho, noves, razão contra a rede atual, atraso e tempo médio da viagem, e o ganho medido dia a dia, com intervalo de 95%. A linha nova falha como as linhas atuais (taxa por km e durações herdadas): uma linha longa sem retorno parcial para inteira com uma falha em qualquer trecho, e pode deixar a viagem menos confiável. Sem a rota alternativa, a linha nova só conta se entrar no caminho de sempre; com ela, vale como caminho em paralelo. A opção da causa comum faz a linha nova parar junto com as linhas em que encosta. As linhas vão no link.

### Comparar cenários

**Fixar o cenário atual como A**, mude o que quiser e **Comparar A com o cenário atual (B)**. Os dois lados usam as mesmas falhas sorteadas (números aleatórios comuns), então a diferença mostra só o efeito da mudança, com intervalo de 95%. É assim que se mede o efeito de uma política.

### Que linha construir

Avalia as cinco candidatas de expansão com fonte pública e qualquer ligação entre duas estações escolhidas em **De** e **Para**. **Busca em todas as ligações curtas** testa todas as ligações diretas até a distância escolhida. O ganho é a mudança na disponibilidade dos pares de estações atuais, com e sem causa comum compartilhada. Uma linha nova só ganha quando cria um caminho alternativo; ramais não ganham (veja `fontes/verificacao/expansao.md`).

### Parâmetros

Todos os números do modelo: valor, intervalo de 95%, status (ajustado, deduzido, hipótese, não verificado) e link para o relatório que os produziu. O método aparece ao passar o mouse sobre o link; o número de observações aparece nas durações e na causa comum.

## Como ler os resultados

- **Disponibilidade** é a fração do tempo de serviço sem bloqueio na linha. 99,5% num dia útil de 20 horas são cerca de 6 minutos parados.
- **Disponibilidade origem-destino** é a fração dos pares de estações que têm caminho, ponderada pela oferta de trens (não há dado de passageiros).
- **Noves** são −log₁₀ da indisponibilidade: 99% são 2 noves, 99,9% são 3, 99,99% são 4. Perto de 100%, a disponibilidade esconde as diferenças (99,5% e 99,9% parecem iguais, mas o tempo parado cai 5 vezes); os noves, os minutos parados e o gráfico em escala logarítmica, em que cada marca é 10 vezes a anterior, mostram a diferença.
- **Intervalo de 95%** é a incerteza do Monte Carlo. Se o intervalo de uma diferença contém zero, o efeito não é detectável com aquele número de dias.
- **Hipótese** é escolha nossa, sem dado. O resultado que depende dela deve ser lido como "se o reparo levar X dias, então...".

## Limites que valem para toda simulação

- Um trem por trecho e por sentido; os trens seguem viagens individuais do horário (o GTFS não tem blocos de trem).
- O retorno parcial só acontece nas pontas de viagem do horário: a posição dos aparelhos de mudança de via não é pública.
- O tempo de reparo na oficina não é publicado pela STM.
- Fechamentos planejados e quedas de energia não têm série própria.

## Para conferir no seu computador

O desempenho foi medido sem placa de vídeo, com WebGL por software, e os números de cada medição estão na spec 010. A 1 dia/s a página faz mais trabalho (dias novos, eventos vermelhos), e os quadros por segundo caem um pouco em relação a 300×. Com a animação parada, o contador mostra o ritmo da página (60), não o da animação. Falta a equipe conferir num notebook comum, no celular e no Firefox e no Safari. Se algo não abrir, anote o navegador e o que apareceu no console (F12).
