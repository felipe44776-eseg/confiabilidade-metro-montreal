# Confiabilidade e tolerância a falhas do metrô de Montreal: dados públicos, modelos e simulação

Trabalho da disciplina Sistemas Tolerantes a Falhas — Engenharia de Produção, ESEG, 2026.

Equipe: Ana Paula Duanetti, Felipe Marins, Lorena Feitosa de Freitas e Sophia Braz.

> **Revisão de 2026-11 (após a ressegmentação).** As falhas passaram a ser separadas por frota (MR-73, MPM-10) e por setor do equipamento fixo, a duração segue a faixa oficial da STM quando a calculada pelos horários a contradiz, e a exposição é medida em todo o período (km real republicado pela STM em 2026-10-23). Specs 017 a 020; decisões D55 a D63. A versão anterior continua em [`/versoes/v1.1.0/`](https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/versoes/v1.1.0/), e cada número que mudou está em [`revisao_2026-11.md`](../../fontes/verificacao/revisao_2026-11.md). Os números do texto são os revistos; onde mudaram, aparecem marcados "após a revisão", com o valor da v1.1.0 ao lado quando a mudança pesa na conclusão. A seção 8 resume o que a revisão encontrou e o que mudou nas conclusões.

Site: https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/ · Repositório: https://github.com/felipe44776-eseg/confiabilidade-metro-montreal

Versão de 2026-10-21, revista em 2026-11-11 (após a ressegmentação). Os números vêm dos relatórios em `fontes/verificacao/`, gerados pelos scripts do repositório.

## Resumo

Medimos a confiabilidade das quatro linhas do metrô de Montreal com 45.785 incidentes registrados pela Société de transport de Montréal (STM) de 2019-01-01 a 2026-06-30, dos quais 8.530 são falhas técnicas de uma linha só (material rodante ou equipamentos fixos). Ligamos cada falha à oferta de trens da hora (horário GTFS calibrado pela quilometragem real), ao clima horário e a eventos externos, ajustamos um modelo de taxa de falha e as distribuições do tempo entre falhas e do tempo até o serviço voltar, e construímos um simulador por eventos discretos da rede, que roda no navegador, para comparar políticas de tolerância a falhas e linhas candidatas de expansão. Todo número é rastreável a uma fonte pública com hash registrado e pode ser refeito por qualquer pessoa. As falhas não são independentes: agrupam-se no tempo (Weibull com forma de 0,43 a 0,80) e 45 eventos param duas a quatro linhas juntas. Neve acumulada (mais de 10 cm no solo, +37%), calor (+84% nos equipamentos fixos) e a abertura do serviço (2,6 a 3,6 vezes) elevam a taxa. Entre as políticas simuladas, a operação degradada em marcha lenta é a que mais reduz os minutos parados. Para a rede ficar mais confiável, a ligação nova que mais ajuda é a que dá à Linha Azul um caminho que não passe pela Laranja. A validação contra 2025 e 2026 não passou na versão pré-registrada (66,7% de cobertura contra 80% exigidos), porque 2024 foi um ano atípico; a regra corrigida, testada de novo em outro período, cobriu 90%. Numa revisão em 2026-11, separamos cada falha pela frota do trem e pelo setor do equipamento fixo e corrigimos as durações que contradiziam a faixa oficial da STM. A frota pesa mais que a linha: na Verde, o MR-73 falha cerca de 9 vezes mais que o MPM-10. A Azul parava metade do que parecia, e o "2024 atípico" vem de um tipo de registro nos terminais. As conclusões se mantêm.

## 1. Introdução

Um sistema tolerante a falhas continua entregando o serviço, talvez degradado, quando um componente falha. No metrô, os componentes são os trens (material rodante) e a infraestrutura (via, sinalização, energia, portas de plataforma: os "equipamentos fixos" da STM). A rede tem redundância de dois tipos: reserva de trens na garagem (redundância fria k-de-n) e caminhos alternativos entre estações (redundância de rota), que só existem onde duas linhas se cruzam duas vezes.

O trabalho responde a quatro perguntas de engenharia:

1. Quanto cada linha falha e por quanto tempo fica parada, com que distribuição e sob quais condições (hora, clima, eventos)?
2. As falhas são independentes ou se agrupam? Quanto pesa a causa comum, que para duas linhas ao mesmo tempo?
3. Que políticas de tolerância a falhas mais reduzem a indisponibilidade (reserva de trens, retirada do trem falho, operação degradada, retorno parcial, rota alternativa, redução da causa comum)?
4. Que nova ligação tornaria a rede mais confiável como sistema?

**Escopo (revisão de 2026-11, D62).** O trabalho mede confiabilidade e disponibilidade do serviço diante das falhas de rotina que a STM registra. Não mede resiliência a desastres, em que o sistema sai do equilíbrio e precisa ser recuperado (Zhou et al., 2019; Chen et al., 2023), nem segurança, a probabilidade de não chegar a um estado inseguro (Almeida Jr. et al., 2008). Os incidentes do CSV são falhas detectadas, que viraram parada ou atraso; falha perigosa não detectada não aparece neles. As classes de gravidade (D58) são operacionais, pela duração, e não classes de perigo.

A equipe adotou uma regra desde o início: nenhum número sem fonte. O projeto foi conduzido por especificações (Spec-Driven Development), com critérios de aceite mensuráveis escritos antes do código, e toda exceção a um critério ficou registrada em vez de o critério ser afrouxado.

## 2. Referencial

| Conceito | Definição usada |
|---|---|
| MTBF | Tempo médio entre falhas, em horas de operação (janela de 20 h por dia, 05:00 a 01:00) |
| MTTR | Aqui, tempo médio até o serviço voltar; a STM não publica o tempo de reparo na oficina. Não é o tempo de reparo do equipamento, que estudos com ordens de serviço usam (Marinho et al., 2023) |
| Disponibilidade | Fração do tempo de operação sem interrupção do serviço (não de um equipamento); A = MTBF / (MTBF + MTTR) no modelo de dois estados. Os noves são −log₁₀(1 − A) |
| Perda de resiliência | Área ∫[1 − Q(t)] dt entre a ruptura e a volta do desempenho Q(t) (Zhou et al., 2019, Eq. 3). Os minutos de pares sem caminho do simulador são essa área, com Q(t) = fração da oferta origem-destino que tem caminho. Como o CSV só tem início e fim, Q(t) cai e volta de uma vez |
| Segurança | Probabilidade de não chegar a um estado inseguro (Almeida Jr. et al., 2008). Não é o que medimos. Uma sinalização de falha segura troca disponibilidade por segurança: na dúvida, para o trem |
| Verificação e validação | Verificação: o motor bate com contas feitas das mesmas hipóteses. Validação: o modelo prevê o observado que não viu (seção 5). Comparar a simulação só com fórmulas das mesmas entradas, como em Marinho et al. (2023) e dos Santos Neto e Callou (2026), é verificação |
| Confiabilidade R(t) | Probabilidade de passar t horas de operação sem falha |
| Processo de Poisson com taxa variável | Falhas independentes com taxa λ(t) que muda com hora, clima e oferta |
| Processo de renovação | Intervalos independentes e identicamente distribuídos; Weibull com forma < 1 indica agrupamento |
| Reescala do tempo | Se as falhas são Poisson com taxa λ(t), os intervalos medidos em Λ(t) = ∫λ seguem uma exponencial de média 1 (Brown et al., 2002) |
| Redundância k-de-n | O serviço exige n trens; com s reservas, falha quando mais de s trens estão na oficina |
| Fator β | Fração das falhas de um componente que ocorre junto com a de outro por causa comum (NUREG/CR-4780) |
| Binomial negativa | Modelo de contagem com variância μ + αμ², para dados mais dispersos que a Poisson |

## 3. Dados e proveniência

### 3.1 Fontes

| Fonte | Editor e licença | Uso |
|---|---|---|
| Incidentes do metrô, 2019-01 a 2026-06 | STM, CC BY 4.0 | Falhas, causas, linhas, horários, duração, local |
| Quilometragem real das voitures, 2019-01 a 2026-09 (republicada em 2026-10-23; até a v1.1.0, 2019-01 a 2023-09) | STM, CC BY 4.0 | Exposição (km-carro e trens por dia), parcela de cada frota por dia |
| GTFS da STM (versão 20261007130000_26N) | STM, CC BY 4.0 | Horários, estações, oferta por hora |
| Traçado das linhas | Colaboradores do OpenStreetMap, ODbL 1.0 | Mapa e km ao longo da linha |
| Coordenadas de referência | Wikidata, CC0 | Segunda referência das estações |
| Clima diário e horário (estações 51157, 10761 e 30165) | Environment and Climate Change Canada, Licença de Governo Aberto | Temperatura, precipitação, condição, neve no solo |
| Jogos do Canadiens; GP do Canadá; feriados | API da NHL; Jolpica; Nager.Date | Eventos externos (não redistribuídos) |
| Greves da STM em 2025 | Imprensa de Montreal (URLs por dia) | Faixas com serviço |
| Linhas candidatas de expansão | OSM, Wikidata e documentos públicos (STM, ARTM, Ville de Montréal, imprensa) | Spec 014 |

Lista completa, com links, hashes e APIs acessadas: `fontes/FONTES.md`. Colunas e fatores sem fonte: `docs/dicionario_dados.md`.

### 3.2 Como garantimos que os números não foram inventados

- **Cópia exata:** os dados brutos redistribuíveis estão em três Releases do GitHub (`dados-2026-10-20`, `dados-2026-10-21` e `dados-2026-11`, com o km real republicado), com o SHA-256 de cada arquivo no manifesto.
- **Segunda implementação:** `pipeline/verifica_fontes.py`, em Python puro e sem usar o pipeline, recalcula 38 números publicados direto dos dados brutos (25 até a v1.1.0; após a revisão, também os minutos parados pela faixa oficial e as falhas de cada fonte, com uma reimplementação própria da regra de duração). Diferença atual: zero.
- **Previsões congeladas:** antes de a STM publicar os meses depois de 2026-06, os modelos da v1.1.0 e o revisto ficaram congelados num commit (`fontes/verificacao/preregistro/`), com o critério de avaliação fixado em código (spec 020).
- **Publicação bloqueada por erro:** cada publicação do site baixa a Release, confere os hashes, recalcula, roda os testes do pipeline e do simulador e só então publica.
- **Auditoria independente:** um agente sem acesso aos scripts tentou refutar os números com código próprio e não achou divergência (seção 5 do FONTES.md).
- **Verificação semanal na origem:** toda segunda-feira, cada fonte é baixada de novo e comparada; mudança na origem vira aviso, porque vale a cópia da Release.

### 3.3 Preparação (fase F1)

| Etapa | Resultado | Exceção registrada |
|---|---|---|
| Normalização (spec 001) | 8.530 falhas técnicas com início e fim absolutos; horas 24:xx e 25:xx resolvidas; 45 eventos de causa comum (31 Verde e Laranja); 44 sem linha | 98,83% das durações na faixa oficial ou na vizinha, contra 99% pedidos; os 100 restantes estão listados |
| Fontes e durações (spec 017, após a revisão) | 9 fontes de falha: frota do trem (MR-73 2.740, MPM-10 1.191, outros 51) e setor do equipamento fixo, dividido pelo sintoma quando cada parte tem 400 falhas ou mais (via e "Service aux trains" divididos; estações e TCPE inteiros). Nas 100 exceções, vale a faixa oficial: os minutos parados das falhas técnicas vão de 43.971 para 33.404 | As 100 exceções eram 1,2% das falhas e 25% dos minutos (11.129); com a faixa, somam 562 |
| Base geoespacial (spec 002) | Traçado com comprimento a até 3% do oficial; 73 de 73 estações casadas; 94,0% das falhas com posição | 5 estações de 104 a 142 m do nó do OSM; 6% das falhas sem posição (sobretudo subestações) |
| Clima e eventos (spec 003) | 65.717 horas; precipitação em 99,99% das horas de operação; trocas de horário de verão testadas; chuva congelante de 2023-04-05 reproduzida; 348 eventos com URL e status | Condição do tempo só em 45,8% das horas de operação |
| Exposição (spec 004) | Trens em viagem às 08:00: 26, 31, 2 e 9; após a revisão, exposição e parcela de cada frota medidas pelo km real até 2026-06 (na v1.1.0, até 2023-09); erro mensal mediano de 0,50% (0,44% na v1.1.0); nos 25 dias de greve, fator típico nas horas com serviço (D63) | 6 de 356 meses acima de 10% (abril e maio de 2020 nas três linhas grandes). Na v1.1.0, 4 de 220 |

## 4. Métodos

### 4.1 Modelo da taxa de falha (spec 005)

Uma linha por hora de serviço e por linha do metrô (226.658 horas-linha). A resposta é o número de falhas que começaram na hora; o deslocamento é o logaritmo dos trens em viagem na hora. As covariáveis são linha, faixa do dia, tipo de dia, estação do ano, temperatura, precipitação, condição do tempo, neve no solo, ano e indicadores de jogo, GP, feriado e greve. Comparamos Poisson e binomial negativa por AIC e razão de verossimilhança, e os intervalos de 95% vêm de bootstrap em blocos semanais (Künsch, 1989), pareado entre as duas causas para comparar material rodante e equipamentos fixos. Os resíduos são quantílicos aleatorizados (Dunn e Smyth, 1996), com rootograma (Kleiber e Zeileis, 2016).

**Resultado.** A binomial negativa vence a Poisson nas duas causas (material rodante: α = 1,83; equipamentos fixos: α = 5,55, após a revisão; 5,47 na v1.1.0; p < 10⁻³⁰), sinal de falhas mais agrupadas do que o acaso explica. Os resíduos quantílicos têm média 0,000 e desvio 1,00, e o modelo reproduz o total de cada faixa do dia com erro de até 2% (exceto equipamentos fixos na abertura, com observado ÷ esperado de 0,91: 733 falhas contra 804,4 esperadas).

Após a revisão, com a exposição medida em todo o período e as durações pela faixa oficial, os multiplicadores da tabela abaixo mudam só na segunda casa decimal (IC por bootstrap com B = 200; a v1.1.0 está em `fontes/verificacao/revisao_2026-11.md`). Fora da tabela, o efeito da Amarela muda mais: de 5,05 para 5,44 no material rodante e de 2,14 para 2,37 nos equipamentos fixos.

| Fator (multiplicador da taxa por trem-hora; IC 95%) | Material rodante | Equipamentos fixos |
|---|---|---|
| Abertura do serviço (5 a 6 h) | 2,64 (2,36–2,92) | 3,59 (3,14–4,03) |
| Pico da manhã | 1,35 (1,23–1,48) | 1,26 (1,14–1,37) |
| Pico da tarde | 0,85 (0,77–0,93) | 0,61 (0,55–0,68) |
| Mais de 10 cm de neve no solo | 1,37 (1,09–1,67) | 1,37 (1,09–1,69) |
| 25 °C ou mais | 1,07 (0,83–1,34) | 1,84 (1,29–2,33) |
| Abaixo de −15 °C | 0,94 (0,72–1,26) | 1,07 (0,73–1,59) |
| Precipitação acima de 1 mm/h | 0,95 (0,74–1,18) | 1,15 (0,92–1,42) |
| Jogo do Canadiens | 1,26 (1,01–1,59) | 0,91 (0,65–1,15) |
| Dia de greve (além da oferta reduzida) | 1,16 (0,55–2,23) | 1,10 (0,52–1,72) |

Referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação. Com o km real medido em 2025, o multiplicador da greve chegou a sair 1,73 por contagem dupla da redução do serviço; corrigido antes do ajuste final (D63, depois de ver), ele volta ao da v1.1.0. Na comparação pareada entre as causas, o pico da tarde eleva mais o material rodante (razão 1,39; IC 1,22–1,66) e a abertura eleva mais os equipamentos fixos (0,73; 0,63–0,88, após a revisão; 0,74 na v1.1.0); para o frio, não há diferença detectável. A greve atua só pela oferta: a taxa por trem-hora não muda de forma detectável. Uma falha na hora anterior dobra a taxa de material rodante e quase triplica a de equipamentos fixos na hora seguinte, o que motiva o processo de renovação da seção 4.2.

**Por fonte (revisão de 2026-11, spec 018).** O material rodante é um modelo só para as duas frotas, com a parcela diária de cada uma no deslocamento. Na Verde, a única linha com as duas, o MR-73 falha 8,9 vezes mais que o MPM-10 por trem-hora da frota em 2025 (IC 6,6–11,2; de 6,1 a 15,5 entre os anos), e a linha ainda pesa dentro de cada frota (razão de verossimilhança 131,5 com 3 graus de liberdade). A hipótese de a parcela da frota valer igual em todas as horas é rejeitada: o MR-73 pesa mais nos picos, e a razão fica com essa ressalva. Nos equipamentos fixos, quatro fontes têm modelo próprio (via e "Service aux trains", cada uma com sintoma de trem ou fixo) e duas, modelo reduzido (estações e TCPE). A abertura eleva todas as fontes em que a faixa do dia entra (todas menos `mr_outros`, que só tem a linha); na TCPE, 8,5 vezes, o que lemos como falha ao energizar a rede. O calor vem sobretudo da via (2,2 e 2,7; no "Service aux trains" com sintoma fixo, 1,4) e não do material rodante. Medido com um ano de fora de cada vez, o modelo por fonte prevê melhor que o da v1.1.0 nas duas famílias (erro de 0,31 para 0,25 no material rodante e de 0,65 para 0,59 nos equipamentos fixos), sobretudo na Verde, onde a frota mudou.

### 4.2 Distribuições (spec 006)

Para cada linha, causa, frota e estação do ano, comparamos exponencial, Weibull, gama, lognormal e log-logística por AIC, com testes de Kolmogorov-Smirnov e Anderson-Darling e p-valor por bootstrap paramétrico (correção de Lilliefors, 1967). O teste de reescala do tempo decide o processo do simulador. O tempo até o serviço voltar é uma massa em zero mais uma lognormal, com regressão de tempo acelerado. O fator β tem intervalo exato de Clopper e Pearson (1934), e a taxa de causa comum, intervalo de Garwood (1936).

**Resultado.** A Weibull é a melhor família em 23 dos 29 estratos, sempre com forma abaixo de 1: o risco de nova falha é maior logo depois de uma falha. O teste de reescala rejeita o processo de Poisson em todas as linhas e causas, mesmo com a taxa variável da seção 4.1 (as médias reescaladas ficam entre 0,97 e 1,03, então a taxa está calibrada). Há agrupamento além do que hora, clima e oferta explicam, e por isso o simulador usa renovação Weibull no tempo reescalado, com forma de 0,43 (Amarela, equipamentos fixos; 0,44 na v1.1.0) a 0,80 (Verde, material rodante). Após a revisão, cada fonte tem a sua forma, sempre abaixo de 1: de 0,37 (Azul, via com sintoma de trem, a fonte mais em rajadas) a 0,83 (Verde, MR-73).

O serviço volta sem interrupção em 20% a 42% das falhas de material rodante e em 58% a 67% das de equipamentos fixos. Quando há interrupção, a duração segue uma lognormal; a evacuação multiplica a duração por 2,92 (IC 2,74–3,11) e falhas da via ("Service de la voie") por 2,19 (2,30 na v1.1.0, antes da regra da faixa oficial). Os 45 eventos de causa comum formam 7 grupos de linhas; o mais frequente é Verde e Laranja juntas (12 eventos só das duas, 31 contando os de três ou quatro linhas), com fator β de 0,011 para a Verde (IC 0,007–0,015) quando o denominador são todas as falhas. Após a revisão, o β usa o denominador da família, porque 40 dos 45 eventos são de equipamento fixo: nas falhas fixas, o β da Verde com a Laranja é 0,022 (0,015–0,031), o dobro.

**Falhas de zero minuto (revisão de 2026-11, D62).** A proporção de falhas que não interrompem o serviço difere muito entre as fontes (qui-quadrado de homogeneidade, p < 0,0001): 90% nas estações, 89% na via com sintoma de trem, 57% a 82% no "Service aux trains", 39% no MPM-10, 33% na TCPE, 27% na via com sintoma fixo e 25% no MR-73. A leitura, fixada antes de calcular, saiu **inconclusiva**: o padrão não é o de parada segura com rearme rápido (controle de trens e frotas acima das demais fontes e estáveis entre os anos), nem o de mudança de registro (um ano em que metade das fontes salta junto). Duas fontes sobem por conta própria: a via com sintoma de trem, de 17% em 2019 para 98% em 2025, e o MPM-10, de 21% para 66%. As duas estão no pedido da equipe à STM.

### 4.3 Simulador (specs 007 a 011)

O simulador é um motor de eventos discretos em TypeScript que roda no navegador. Cada trem segue o horário do GTFS do tipo de dia; cada trecho entre duas estações, por sentido, admite um trem por vez, com separação mínima de 90 s (hipótese). As falhas são sorteadas pela taxa da seção 4.1, que muda hora a hora com a oferta e o cenário (clima, eventos, greve), e pela renovação Weibull da seção 4.2:

- **Material rodante:** para o trem no ponto onde está e bloqueia aquele sentido.
- **Equipamento fixo:** bloqueia o trecho sorteado entre os locais históricos, nos dois sentidos.
- **Causa comum:** para de uma vez o grupo de linhas sorteado.

Após a revisão (spec 019), cada linha sorteia as 9 fontes à parte, cada uma com a sua taxa, renovação, duração, locais e sequência de números aleatórios: a frota decide a taxa do material rodante (já multiplicada pela parcela dos km da linha que a frota rodou no ano-base), e o setor e o sintoma decidem a do equipamento fixo. A família da fonte decide o efeito e as políticas, como antes. Com os parâmetros da v1.1.0, o motor revisto reproduz byte a byte os 198 casos gravados antes da mudança.

A duração vem da massa em zero e da amostra observada das durações positivas. Os atrasos se propagam aos trens de trás. Uma camada de frota (nascimento e morte com reparo na oficina) decide quantos trens faltam no início de cada dia.

Verificação (o motor contra contas das mesmas hipóteses): sem falhas, o motor reproduz o horário exatamente (26, 31, 2 e 9 trens às 08:00). A reserva k-de-n simulada bate com o modelo de Markov (Laranja: 0,674, 0,939 e 0,992 contra 0,671, 0,938 e 0,992). Na v1.1.0, os minutos parados por ano da Laranja, 1.704 (IC 1.528–1.881), continham os 1.797 do cálculo analítico e os 1.852 do Monte Carlo do painel. Após a revisão, o simulador dá 1.319 (1.215–1.422), abaixo dos 1.601 e 1.639 do painel revisto: o simulador usa a taxa de 2025, e o painel, a média de 2019 a 2026, e 2025 ficou abaixo da média. A comparação certa passou a ser contra o próprio 2025 (seção 5). Com os parâmetros da v1.1.0, o motor revisto reproduz byte a byte os 198 casos gravados antes da revisão. O Monte Carlo usa Web Workers e dá o mesmo resultado com 1 ou 8 processos; 1.000 dias levam cerca de 3 s no navegador.

Esse teste também mudou o modelo. Na v1.1.0, a média observada das durações era maior que a da lognormal ajustada (23% a 29% na Laranja (material rodante e equipamentos fixos) e 26% nos equipamentos fixos da Verde; 3,4 vezes nos equipamentos fixos da Azul, por poucas interrupções de quase 20 horas), e o simulador passou a sortear da amostra observada. Após a revisão, as razões são 1,23 e 1,24 na Laranja, 1,17 nos equipamentos fixos da Verde e 2,04 nos da Azul (tabela em `fontes/verificacao/duracoes.md`). A causa comum era sorteada por par de linhas e contava duas ou três vezes os eventos de 3 ou 4 linhas; passou a ser sorteada por grupo. As duas mudanças estão registradas com data nas specs 006 e 009.

**Políticas (dia útil, reparo de 1 dia; diferença contra nenhuma política, IC 95%; após a revisão, com a v1.1.0 ao lado quando mudou):**

| Política | Minutos parados por dia útil (4 linhas) | Trens-hora perdidos | Outro efeito |
|---|---|---|---|
| Operação degradada (marcha lenta após falha de equipamento fixo) | −3,4 (−4,0 a −2,8); v1.1.0: −7,8 | −2,3 (−3,2 a −1,4); v1.1.0: −16,4 | disponibilidade origem-destino +0,17 p.p. (v1.1.0: +0,35) |
| Retirada do trem falho | −1,0 (−1,3 a −0,7); v1.1.0: −1,1 | −0,28 (−0,55 a −0,02); v1.1.0: −0,18 (−0,40 a 0,03) | só material rodante |
| Tratamento de causa comum (redução de 50%, hipótese) | −0,8 (−1,3 a −0,3) | −0,52 (−0,89 a −0,15) | só causa comum |
| Reserva fria (2 trens por linha) | 0 | −0,63 (−0,67 a −0,58) | frota completa na Laranja +32,5 p.p. (+58 p.p. com reparo de 4 dias) |
| Retorno parcial nas pontas de viagem (hipótese) | 0 | 0 | disponibilidade origem-destino +0,15 p.p. (v1.1.0: +0,21) |
| Rota alternativa de passageiros | 0 | 0 | disponibilidade origem-destino +0,006 p.p. (v1.1.0: +0,01) |

A política com maior efeito continua a operação degradada, que ataca a causa mais frequente (equipamentos fixos). Após a revisão, o ganho dela cai à metade: boa parte das interrupções longas de equipamento fixo, em que a marcha lenta mais rendia, eram registros com a duração calculada contradizendo a faixa oficial (D55). A reserva fria protege a oferta, não a continuidade do serviço, e o efeito dela cresce com o tempo de reparo, que é hipótese (0,5 a 4 dias). O retorno parcial vale mais que a rota alternativa porque a rede tem poucos caminhos alternativos.

### 4.4 Expansão da rede (spec 014)

Cinco candidatas, todas com coordenadas de consultas salvas ao OSM ou ao Wikidata: prolongamento da Azul até Anjou (em obras, inauguração prevista para 2031), Linha Rosa (proposta de 2017, 29 estações), prolongamento da Amarela em Longueuil, prolongamento da Laranja até Bois-Franc e o anel da Laranja proposto pela ARTM em 2019. O método de estados sorteia 200 mil vezes o estado de cada trecho (aberto ou bloqueado, pela taxa e pela duração das falhas) e mede a disponibilidade dos pares de estações atuais, ponderada pela oferta de hoje. A rede atual tem disponibilidade origem-destino de 99,425% em dia útil após a revisão (99,236% na v1.1.0). O ganho de cada candidata é pareado com a rede atual. Verificação (revisão de 2026-11, D62): num grafo de três estações com uma ligação nova que fecha um ciclo, o método de estados fica a menos de 4 erros-padrão da enumeração exata dos 8 estados, sem e com a ligação (`app/tests/motor/expansao.test.ts`).

| Candidata (sem retorno parcial) | km (aprox.) | Ganho, p.p. (IC 95%), após a revisão | v1.1.0 |
|---|---|---|---|
| Rosa com a Azul até Anjou | 42,3 | +0,036 (0,030 a 0,043) | +0,003 (−0,006 a 0,012) |
| Linha Rosa | 35,4 | +0,017 (0,016 a 0,018) | +0,021 |
| Anel da Laranja (ARTM, 2019) | 9,9 | +0,0002 | +0,0002 |
| Amarela em Longueuil | 7,2 | −0,005 | −0,005 |
| Laranja até Bois-Franc | 3,0 | −0,029 | −0,035 |
| Azul até Anjou (em obras) | 6,9 | −0,032 | −0,075 |

Após a revisão, a Rosa com a Azul até Anjou passa à frente da Rosa sozinha, com intervalo que não cruza zero. A explicação provável: o trecho novo herda as durações da Azul, que perderam as interrupções de quase 20 horas (D55); o prolongamento sozinho passa a custar menos (−0,032 contra −0,075), e o ciclo que ele fecha com a Rosa passa a render. Com retorno parcial nas pontas de viagem (hipótese): Rosa com a Azul +0,038 (v1.1.0: +0,053), anel da Laranja +0,021 (+0,019), Rosa +0,008 (+0,011), ramais 0. Na busca exaustiva de ligações diretas entre estações atuais (até 3 km em linha reta), a melhor continua Atwater (Verde) – Université-de-Montréal (Azul), com +0,063 p.p. (v1.1.0: +0,085). Hoje a Azul só alcança o resto da rede pela Laranja, em Snowdon e Jean-Talon: quando a Laranja para, a Azul fica isolada. Essa dependência é o maior ponto único de falha da rede no modelo.

Leitura para a decisão: uma linha nova aumenta a confiabilidade da rede pelos caminhos alternativos que cria, não pela extensão. Ramais, como o prolongamento da Azul já em obras, ampliam a cobertura, que esta métrica não mede por falta de dados de passageiros, mas não criam redundância.

## 5. Validação contra o histórico (spec 012)

Validação, aqui, é prever o que o modelo não viu; a comparação do motor com contas (seção 4.3) é verificação. Ajustamos o modelo só com os dados até 2024-12-31 e previmos o número de falhas de cada linha em cada mês de 2025-01 a 2026-06 (72 casos), com o mesmo processo do simulador. O critério, escrito antes de ver o teste, era que o intervalo de predição de 90% contivesse o observado em 80% a 98% dos casos.

| Versão | Definida | Cobertura do IP 90% (IC 95%) | PIT (KS) |
|---|---|---|---|
| A: treino até 2024-12, efeito do ano de 2024 | antes do teste (oficial) | **66,7%** (54,6%–77,3%) | p = 2,4e-11 |
| B: treino até 2023-09, só exposição medida | antes do teste | 81,9% (71,1%–90,0%) | p = 0,06 |
| C: treino até 2024-12, efeito do ano sorteado | depois de ver A | 84,7% (74,3%–92,1%) | p = 0,01 |
| D: regra C em outro período (teste 2023-01 a 2024-06) | depois de ver A | 90,3% (81,0%–96,0%) | p = 0,16 |

A versão oficial não passou: 22 dos 24 meses fora do intervalo ficaram abaixo dele. O modelo superestimou 2025 porque herdou o efeito de 2024, um ano atípico (o segundo semestre de 2024 teve cerca de 1.000 falhas técnicas, contra cerca de 500 nos semestres vizinhos). Registramos a mudança com data e testamos a regra nova num período diferente, como a especificação manda. Ela cobriu 90% dos casos, com PIT compatível com a uniforme. A lição de engenharia é que o efeito de um ano não se transfere para o seguinte: a incerteza entre anos precisa entrar na previsão.

No primeiro ano de teste (2025 nas versões A, B e C; 2023 na versão D), os minutos parados observados ficaram dentro do intervalo de 95% nas quatro linhas nas versões B, C e D; na versão A, Verde e Amarela ficaram abaixo.

**Após a revisão (pós-hoc, spec 020).** Refeito sobre os dados revistos, com as mesmas versões e regras, o backtest dá A 65,3%, B 84,7%, C 87,5% e D 90,3%. O resultado oficial continua o de cima, e a conclusão não muda. Separado por família, ele mostra onde a versão A falha: nos equipamentos fixos (65,3% de cobertura), não no material rodante (87,5%). É o "2024 atípico", que a revisão explicou como 516 registros de via com sintoma de trem, quase todos de zero minuto e nos terminais (seção 8).

**Simulador contra 2025 (spec 020).** Cada dia de 2025 foi simulado 6 vezes com o clima, os eventos e o tipo de dia daquele dia. As médias anuais por linha × família (falhas, minutos e falhas de 5 min ou mais) ficaram dentro do IC 95% do observado em 25 de 28 comparações, contra 21 de 28 da v1.1.0; o critério pedia 90% (exceção por uma comparação). Ficaram fora os equipamentos fixos da Amarela, que em 2025 teve o menor número de falhas fixas registradas da série (19; 2020 teve 20), e os minutos de causa comum da Azul. A dispersão diária simulada fica dentro do IC da observada em 9 de 12 combinações: abaixo nos equipamentos fixos da Verde (somar fontes independentes agrupa menos) e acima nas duas famílias da Amarela.

**Indicador da STM.** Os dados abertos dão de 85% a 89% do indicador publicado de incidentes de 5 min ou mais por milhão de km-carro, em todos os anos de 2019 a 2025 (2025: 9,89 contra 11,66). A STM não publica a regra de contagem; a diferença fica declarada e está no pedido da equipe à STM.

**O teste que nenhum modelo viu.** Os modelos da v1.1.0 e o revisto ficaram congelados num commit antes de a STM publicar os meses depois de 2026-06 (`fontes/verificacao/preregistro/`), com o critério fixado em código. A avaliação roda quando houver 3 meses novos.

## 6. Limitações

- Não há passageiros diários: todas as métricas são ponderadas pela oferta.
- O tempo de reparo na oficina e a posição dos aparelhos de mudança de via não são públicos e entram como hipóteses ajustáveis.
- Na v1.1.0, a exposição de outubro de 2023 em diante era estimada pelo horário; após a revisão, o km real republicado pela STM cobre todo o período, e a limitação deixou de existir no modelo e no simulador. O painel do site continua com o km real até 2023-09, como na v1.1.0.
- O que são o "Service aux trains" e o "Service TCPE" não está publicado: "controle de trens" e "energia" são dedução nossa, e a pergunta está no pedido da equipe à STM, com a dos registros de terminal de 2024 e a do indicador de 5 min.
- As durações vêm de dois campos que às vezes se contradizem (horários e faixa oficial). Após a revisão vale a faixa nas 100 exceções; a versão com o ponto médio da faixa fica como sensibilidade (33.476 minutos, contra 33.404).
- Os traçados das candidatas, exceto a Azul, são aproximações em linha reta entre estações.

## 7. Conclusão

O metrô de Montreal tem disponibilidade alta em cada linha (99,7% a 99,9% do tempo de serviço num dia útil, pelo simulador com as taxas de 2025, após a revisão; 99,5% a 99,9% na v1.1.0; o painel, com todos os dias de 2019 a 2026, dá valores um pouco diferentes), mas a confiabilidade da rede como sistema depende de poucos pontos. Três conclusões valem para a decisão:

1. **As falhas se agrupam e têm causa comum.** Tratar as falhas como independentes subestima o risco. O agrupamento aparece no tempo (uma falha dobra ou quase triplica a chance de outra na hora seguinte) e no espaço (eventos que param a Verde e a Laranja juntas tiram a única redundância de rota do centro).
2. **A política que mais rende ataca os equipamentos fixos.** Eles são mais da metade das falhas, e a operação degradada (liberar o trecho em marcha lenta) reduz mais os minutos parados do que reservar trens. A reserva de trens protege a oferta, e o efeito dela depende do tempo de reparo na oficina, que não é público.
3. **Uma linha nova vale pelos caminhos alternativos que cria.** Ramais, como o prolongamento da Azul já em obras, ampliam a cobertura, mas não criam redundância. O maior ponto único de falha do modelo é a dependência da Azul em relação à Laranja.

A validação mostrou o limite do modelo: o efeito de um ano não se transfere para o seguinte, e a previsão precisa carregar a incerteza entre anos. As decisões tomadas depois de ver os dados estão registradas com data, e a versão que falhou continua publicada.

Próximos passos: conferir o simulador num navegador comum e no celular, pedir à STM os dados que faltam (passageiros diários, posição das subestações, tempo de reparo na oficina) e repetir o backtest com o motor TypeScript, como segunda implementação. Depois da revisão de 2026-11: um fator diário comum por família nos equipamentos fixos, para o simulador agrupar as falhas como o observado; avaliar os pré-registros quando a STM publicar os meses novos; e as specs 021 (importância de cada componente) e 022 (cenário de 2031).

## 8. Revisão de 2026-11 (após a ressegmentação)

Na reunião de 2026-10-27, a turma perguntou por fabricantes, por via ou trem e por sistemas separados. Os dados da STM separam mais do que o modelo usava: a frota no material rodante e o setor nos equipamentos fixos. Revisamos tudo no lugar, com a versão anterior congelada (`/versoes/v1.1.0/`), as regras escritas antes de ajustar e cada decisão tomada depois de ver os dados marcada assim (D55 a D63). A tabela de cada número que mudou está em `fontes/verificacao/revisao_2026-11.md`.

**O que a revisão encontrou:**

1. **Durações que contradiziam a faixa oficial.** 100 falhas (1,2%) tinham 25% dos minutos parados. Seis delas, de quase 20 horas em Saint-Michel (Azul, outubro de 2024), estavam registradas pela STM como "2 min ou menos". Nelas passou a valer a faixa oficial: os minutos das falhas técnicas vão de 43.971 para 33.404, e a Azul, que parecia a linha que mais ficava parada, para metade do que parecia (MTTR de 9,69 para 4,72 min).
2. **A frota pesa mais que a linha.** Na Verde, no mesmo trilho, o MR-73 falha 8,9 vezes mais que o MPM-10 por trem-hora em 2025. Como a parcela do MPM-10 na Verde foi de 39% (2019) a 85% (2025), parte do que o modelo atribuía à linha e ao ano era a troca de frota. Fora da amostra, o modelo por fonte erra menos que o da v1.1.0.
3. **O "2024 atípico" é de registro.** De maio a dezembro de 2024, 516 falhas de via com sintoma de trem, 472 de zero minuto, quase todas nos terminais; em 2025, 52. É o que a versão A do backtest carregou para 2025: separada por família, ela falha só nos equipamentos fixos.
4. **A causa comum é de equipamento fixo.** 40 dos 45 eventos são de equipamento fixo; com o denominador da família, o β da Verde com a Laranja dobra (0,011 para 0,022).
5. **Um defeito da própria revisão.** Com o km real medido em 2025, a exposição dos dias de greve contava a redução do serviço duas vezes, e o multiplicador da greve saiu 1,73. O ajuste foi parado e refeito com o fator típico nesses dias (D63); o multiplicador voltou a 1,16, com intervalo que contém 1.

**O que muda nas conclusões:** nada nas três conclusões da seção 7. Os números mudam: a operação degradada continua a política que mais reduz os minutos parados, mas o ganho cai de −7,8 para −3,4 por dia útil; a melhor ligação continua Atwater–Université-de-Montréal; entre as candidatas oficiais, a Rosa com a Azul até Anjou passa à frente da Rosa sozinha.

**O que continua valendo sem mudança:** binomial negativa contra Poisson, agrupamento além das condições (Weibull com forma abaixo de 1 em todas as fontes), reserva k-de-n contra Markov, o motor e o grafo, a greve só pela oferta (D42).

**Exceções novas, registradas sem afrouxar o critério:** o simulador fica dentro do IC do observado de 2025 em 25 de 28 comparações (o critério pedia 90%); a dispersão diária simulada fica fora do IC da observada em 3 de 12 combinações (abaixo nos equipamentos fixos da Verde, acima nas duas famílias da Amarela); a parcela da frota não vale igual em todas as horas; os dados abertos dão de 85% a 89% do indicador de 5 min publicado pela STM. As perguntas sobre os setores, os registros de 2024, Saint-Michel e o indicador estão no pedido da equipe à STM.

## Referências

DOIs conferidos na API do Crossref em 2026-10-21 e, para as cinco referências da revisão de 2026-11 (D62), em 2026-11-10 (`fontes/verificacao/referencias_crossref.json`).

- Almeida Jr., J. R.; Camargo Jr., J. B.; Cugnasca, P. S. Software safety in subway and air traffic control applications. *IEEE Latin America Transactions*, 6(1), 106–113, 2008. doi:10.1109/TLA.2008.4461639
- Brown, E. N.; Barbieri, R.; Ventura, V.; Kass, R. E.; Frank, L. M. The time-rescaling theorem and its application to neural spike train data analysis. *Neural Computation*, 14(2), 325–346, 2002. doi:10.1162/08997660252741149
- Chen, Z.; Song, K.; Shen, Z.; Xiao, D.; Xu, X. A review of resilient transportation systems in the last five years. In: *7th International Conference on Transportation Information and Safety (ICTIS)*, IEEE, 521–529, 2023. doi:10.1109/ICTIS60134.2023.10243879
- Clopper, C. J.; Pearson, E. S. The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26(4), 404–413, 1934. doi:10.1093/biomet/26.4.404
- Dunn, P. K.; Smyth, G. K. Randomized quantile residuals. *Journal of Computational and Graphical Statistics*, 5(3), 236–244, 1996. doi:10.1080/10618600.1996.10474708
- Garwood, F. Fiducial limits for the Poisson distribution. *Biometrika*, 28(3/4), p. 437, 1936. doi:10.2307/2333958
- Gneiting, T.; Balabdaoui, F.; Raftery, A. E. Probabilistic forecasts, calibration and sharpness. *Journal of the Royal Statistical Society: Series B*, 69(2), 243–268, 2007. doi:10.1111/j.1467-9868.2007.00587.x
- Kleiber, C.; Zeileis, A. Visualizing count data regressions using rootograms. *The American Statistician*, 70(3), 296–303, 2016. doi:10.1080/00031305.2016.1173590
- Künsch, H. R. The jackknife and the bootstrap for general stationary observations. *The Annals of Statistics*, 17(3), 1217–1241, 1989. doi:10.1214/aos/1176347265
- Lilliefors, H. W. On the Kolmogorov-Smirnov test for normality with mean and variance unknown. *Journal of the American Statistical Association*, 62(318), 399–402, 1967. doi:10.1080/01621459.1967.10482916
- Marinho, O.; Callou, G.; Melo, R.; Andrade, E. Performability evaluation of railway systems: a study on the impact of adding alternative routes. *IEEE Latin America Transactions*, 21(2), 270–276, 2023. doi:10.1109/TLA.2023.10015219
- Mosleh, A. et al. *Procedures for Treating Common Cause Failures in Safety and Reliability Studies*. NUREG/CR-4780, U.S. Nuclear Regulatory Commission, 1988. **Não conferido:** o site da NRC recusou o acesso desta máquina e o OSTI não devolveu o documento.
- Santos Neto, O. M. dos; Callou, G. R. de A. Infrastructure availability and urban railway performability: a stochastic Petri net approach to resilience, congestion, and service reliability. *Reliability Engineering & System Safety*, 278, 113439, 2027 (online em 2026). doi:10.1016/j.ress.2026.113439
- Zhou, Y.; Wang, J.; Yang, H. Resilience of transportation systems: concepts and comprehensive review. *IEEE Transactions on Intelligent Transportation Systems*, 20(12), 4262–4276, 2019. doi:10.1109/TITS.2018.2883766

## Apêndice: como reproduzir

```bash
python -I pipeline/verifica_fontes.py --baixa-release --recalcula
python -m pip install -r pipeline/requirements.txt
python -m pytest pipeline/tests -q
cd app && npm ci && npm test && npm run build
```
