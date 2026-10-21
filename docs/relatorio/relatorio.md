# Confiabilidade e tolerância a falhas do metrô de Montreal: dados públicos, modelos e simulação

Trabalho da disciplina Sistemas Tolerantes a Falhas — Engenharia de Produção, ESEG, 2026.

Equipe: Ana Paula Duanetti, Felipe Marins, Lorena Feitosa de Freitas e Sophia Braz.

Site: https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/ · Repositório: https://github.com/felipe44776-eseg/confiabilidade-metro-montreal

Versão de 2026-10-21. Os números vêm dos relatórios em `fontes/verificacao/`, gerados pelos scripts do repositório.

## Resumo

Medimos a confiabilidade das quatro linhas do metrô de Montreal com 45.785 incidentes registrados pela Société de transport de Montréal (STM) de 2019-01-01 a 2026-06-30, dos quais 8.530 são falhas técnicas de uma linha só (material rodante ou equipamentos fixos). Ligamos cada falha à oferta de trens da hora (horário GTFS calibrado pela quilometragem real), ao clima horário e a eventos externos, ajustamos um modelo de taxa de falha e as distribuições do tempo entre falhas e do tempo até o serviço voltar, e construímos um simulador por eventos discretos da rede, que roda no navegador, para comparar políticas de tolerância a falhas e linhas candidatas de expansão. Todo número é rastreável a uma fonte pública com hash registrado e pode ser refeito por qualquer pessoa. As falhas não são independentes: agrupam-se no tempo (Weibull com forma de 0,44 a 0,80) e 45 eventos param duas a quatro linhas juntas. Nevascas (mais de 10 cm de neve no solo, +37%), calor (+83% nos equipamentos fixos) e a abertura do serviço (2,6 a 3,6 vezes) elevam a taxa. Entre as políticas simuladas, a operação degradada em marcha lenta é a que mais reduz os minutos parados. Para a rede ficar mais confiável, a ligação nova que mais ajuda é a que dá à Linha Azul um caminho que não passe pela Laranja. A validação contra 2025 e 2026 não passou na versão pré-registrada (66,7% de cobertura contra 80% exigidos), porque 2024 foi um ano atípico; a regra corrigida, testada de novo em outro período, cobriu 90%.

## 1. Introdução

Um sistema tolerante a falhas continua entregando o serviço, talvez degradado, quando um componente falha. No metrô, os componentes são os trens (material rodante) e a infraestrutura (via, sinalização, energia, portas de plataforma: os "equipamentos fixos" da STM). A rede tem redundância de dois tipos: reserva de trens na garagem (redundância fria k-de-n) e caminhos alternativos entre estações (redundância de rota), que só existem onde duas linhas se cruzam duas vezes.

O trabalho responde a quatro perguntas de engenharia:

1. Quanto cada linha falha e por quanto tempo fica parada, com que distribuição e sob quais condições (hora, clima, eventos)?
2. As falhas são independentes ou se agrupam? Quanto pesa a causa comum, que para duas linhas ao mesmo tempo?
3. Que políticas de tolerância a falhas mais reduzem a indisponibilidade (reserva de trens, retirada do trem falho, operação degradada, retorno parcial, rota alternativa, redução da causa comum)?
4. Que nova ligação tornaria a rede mais confiável como sistema?

A equipe adotou uma regra desde o início: nenhum número sem fonte. O projeto foi conduzido por especificações (Spec-Driven Development), com critérios de aceite mensuráveis escritos antes do código, e toda exceção a um critério ficou registrada em vez de o critério ser afrouxado.

## 2. Referencial

| Conceito | Definição usada |
|---|---|
| MTBF | Tempo médio entre falhas, em horas de operação (janela de 20 h por dia, 05:00 a 01:00) |
| MTTR | Aqui, tempo médio até o serviço voltar; a STM não publica o tempo de reparo na oficina |
| Disponibilidade | Fração do tempo de operação sem interrupção; A = MTBF / (MTBF + MTTR) no modelo de dois estados |
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
| Quilometragem real das voitures, 2019-01 a 2023-09 | STM, CC BY 4.0 | Exposição (km-carro e trens por dia), frota |
| GTFS da STM (versão 20261007130000_26N) | STM, CC BY 4.0 | Horários, estações, oferta por hora |
| Traçado das linhas | Colaboradores do OpenStreetMap, ODbL 1.0 | Mapa e km ao longo da linha |
| Coordenadas de referência | Wikidata, CC0 | Segunda referência das estações |
| Clima diário e horário (estações 51157, 10761 e 30165) | Environment and Climate Change Canada, Licença de Governo Aberto | Temperatura, precipitação, condição, neve no solo |
| Jogos do Canadiens; GP do Canadá; feriados | API da NHL; Jolpica; Nager.Date | Eventos externos (não redistribuídos) |
| Greves da STM em 2025 | Imprensa de Montreal (URLs por dia) | Faixas com serviço |
| Linhas candidatas de expansão | OSM, Wikidata e documentos públicos (STM, ARTM, Ville de Montréal, imprensa) | Spec 014 |

Lista completa, com links, hashes e APIs acessadas: `fontes/FONTES.md`. Colunas e fatores sem fonte: `docs/dicionario_dados.md`.

### 3.2 Como garantimos que os números não foram inventados

- **Cópia exata:** os dados brutos redistribuíveis estão em duas Releases do GitHub (`dados-2026-10-20` e `dados-2026-10-21`), com o SHA-256 de cada arquivo no manifesto.
- **Segunda implementação:** `pipeline/verifica_fontes.py`, em Python puro e sem usar o pipeline, recalcula 25 números publicados direto dos dados brutos. Diferença atual: zero.
- **Publicação bloqueada por erro:** cada publicação do site baixa a Release, confere os hashes, recalcula, roda os testes do pipeline e do simulador e só então publica.
- **Auditoria independente:** um agente sem acesso aos scripts tentou refutar os números com código próprio e não achou divergência (seção 5 do FONTES.md).
- **Verificação semanal na origem:** toda segunda-feira, cada fonte é baixada de novo e comparada; mudança na origem vira aviso, porque vale a cópia da Release.

### 3.3 Preparação (fase F1)

| Etapa | Resultado | Exceção registrada |
|---|---|---|
| Normalização (spec 001) | 8.530 falhas técnicas com início e fim absolutos; horas 24:xx e 25:xx resolvidas; 45 eventos de causa comum (31 Verde e Laranja); 44 sem linha | 98,83% das durações na faixa oficial ou na vizinha, contra 99% pedidos; os 100 restantes estão listados |
| Base geoespacial (spec 002) | Traçado com comprimento a até 3% do oficial; 73 de 73 estações casadas; 94,0% das falhas com posição | 5 estações de 104 a 142 m do nó do OSM; 6% das falhas sem posição (sobretudo subestações) |
| Clima e eventos (spec 003) | 65.717 horas; precipitação em 99,99% das horas de operação; trocas de horário de verão testadas; chuva congelante de 2023-04-05 reproduzida; 348 eventos com URL e status | Condição do tempo só em 45,8% das horas |
| Exposição (spec 004) | Trens em viagem às 08:00: 26, 31, 2 e 9; erro mensal mediano de 0,44% contra o km real | 4 de 220 meses acima de 10% (abril de 2020 e junho de 2019 na Amarela) |

## 4. Métodos

### 4.1 Modelo da taxa de falha (spec 005)

Uma linha por hora de serviço e por linha do metrô (226.658 horas-linha). A resposta é o número de falhas que começaram na hora; o deslocamento é o logaritmo dos trens em viagem na hora. As covariáveis são linha, faixa do dia, tipo de dia, estação do ano, temperatura, precipitação, condição do tempo, neve no solo, ano e indicadores de jogo, GP, feriado e greve. Comparamos Poisson e binomial negativa por AIC e razão de verossimilhança, e os intervalos de 95% vêm de bootstrap em blocos semanais (Künsch, 1989), pareado entre as duas causas para comparar material rodante e equipamentos fixos. Os resíduos são quantílicos aleatorizados (Dunn e Smyth, 1996), com rootograma (Kleiber e Zeileis, 2016).

**Resultado.** A binomial negativa vence a Poisson nas duas causas (material rodante: α = 1,83; equipamentos fixos: α = 5,47; p < 10⁻³⁰), sinal de falhas mais agrupadas do que o acaso explica. Os resíduos quantílicos têm média 0,000 e desvio 1,00, e o modelo reproduz o total de cada faixa do dia com erro de até 2% (exceto equipamentos fixos na abertura, 9% acima do observado).

| Fator (multiplicador da taxa por trem-hora; IC 95%) | Material rodante | Equipamentos fixos |
|---|---|---|
| Abertura do serviço (5 a 6 h) | 2,64 (2,36–2,92) | 3,59 (3,13–4,03) |
| Pico da manhã | 1,35 (1,23–1,48) | 1,26 (1,14–1,37) |
| Pico da tarde | 0,85 (0,77–0,93) | 0,61 (0,55–0,67) |
| Mais de 10 cm de neve no solo | 1,37 (1,10–1,67) | 1,38 (1,10–1,70) |
| 25 °C ou mais | 1,07 (0,83–1,35) | 1,83 (1,29–2,32) |
| Abaixo de −15 °C | 0,93 (0,71–1,24) | 1,05 (0,72–1,56) |
| Precipitação acima de 1 mm/h | 0,95 (0,73–1,18) | 1,15 (0,92–1,41) |
| Jogo do Canadiens | 1,26 (1,00–1,59) | 0,91 (0,65–1,16) |
| Dia de greve (além da oferta reduzida) | 1,17 (0,56–2,24) | 1,11 (0,52–1,73) |

Referência: Laranja, entrepico, dia útil, outono, 5 a 15 °C, sem precipitação. Na comparação pareada entre as causas, o pico da tarde eleva mais o material rodante (razão 1,39; IC 1,22–1,66) e a abertura eleva mais os equipamentos fixos (0,74; 0,63–0,89); para o frio, não há diferença detectável. A greve atua só pela oferta: a taxa por trem-hora não muda de forma detectável. Uma falha na hora anterior dobra a taxa de material rodante e quase triplica a de equipamentos fixos na hora seguinte, o que motiva o processo de renovação da seção 4.2.

### 4.2 Distribuições (spec 006)

Para cada linha, causa, frota e estação do ano, comparamos exponencial, Weibull, gama, lognormal e log-logística por AIC, com testes de Kolmogorov-Smirnov e Anderson-Darling e p-valor por bootstrap paramétrico (correção de Lilliefors, 1967). O teste de reescala do tempo decide o processo do simulador. O tempo até o serviço voltar é uma massa em zero mais uma lognormal, com regressão de tempo acelerado. O fator β tem intervalo exato de Clopper e Pearson (1934), e a taxa de causa comum, intervalo de Garwood (1936).

**Resultado.** A Weibull é a melhor família em 23 dos 29 estratos, sempre com forma abaixo de 1: o risco de nova falha é maior logo depois de uma falha. O teste de reescala rejeita o processo de Poisson em todas as linhas e causas, mesmo com a taxa variável da seção 4.1 (as médias reescaladas ficam entre 0,97 e 1,03, então a taxa está calibrada). Há agrupamento além do que hora, clima e oferta explicam, e por isso o simulador usa renovação Weibull no tempo reescalado, com forma de 0,44 (Amarela, equipamentos fixos) a 0,80 (Verde, material rodante).

O serviço volta sem interrupção em 20% a 42% das falhas de material rodante e em 58% a 67% das de equipamentos fixos. Quando há interrupção, a duração segue uma lognormal; a evacuação multiplica a duração por 2,92 (IC 2,73–3,13) e falhas da via ("Service de la voie") por 2,30. Os 45 eventos de causa comum formam 7 grupos de linhas; o mais frequente é Verde e Laranja juntas (12 eventos só das duas, 31 contando os de três ou quatro linhas), com fator β de 0,011 para a Verde (IC 0,007–0,015).

### 4.3 Simulador (specs 007 a 011)

O simulador é um motor de eventos discretos em TypeScript que roda no navegador. Cada trem segue o horário do GTFS do tipo de dia; cada trecho entre duas estações, por sentido, admite um trem por vez, com separação mínima de 90 s (hipótese). As falhas são sorteadas pela taxa da seção 4.1, que muda hora a hora com a oferta e o cenário (clima, eventos, greve), e pela renovação Weibull da seção 4.2:

- **Material rodante:** para o trem no ponto onde está e bloqueia aquele sentido.
- **Equipamento fixo:** bloqueia o trecho sorteado entre os locais históricos, nos dois sentidos.
- **Causa comum:** para de uma vez o grupo de linhas sorteado.

A duração vem da massa em zero e da amostra observada das durações positivas. Os atrasos se propagam aos trens de trás. Uma camada de frota (nascimento e morte com reparo na oficina) decide quantos trens faltam no início de cada dia.

Validação: sem falhas, o motor reproduz o horário exatamente (26, 31, 2 e 9 trens às 08:00). A reserva k-de-n simulada bate com o modelo de Markov (Laranja: 0,674, 0,939 e 0,992 contra 0,671, 0,938 e 0,992). Os minutos parados por ano da Laranja, 1.704 (IC 1.528–1.881), contêm os 1.797 do cálculo analítico e os 1.852 do Monte Carlo do painel. O Monte Carlo usa Web Workers e dá o mesmo resultado com 1 ou 8 processos; 1.000 dias levam cerca de 3 s no navegador.

Esse teste também mudou o modelo. A lognormal das durações subestimava a média (23% a 29% na Laranja e na Verde; 3,4 vezes na Azul, por poucas interrupções de quase 20 horas), e o simulador passou a sortear da amostra observada. A causa comum era sorteada por par de linhas e contava duas ou três vezes os eventos de 3 ou 4 linhas; passou a ser sorteada por grupo. As duas mudanças estão registradas com data nas specs 006 e 009.

**Políticas (dia útil, reparo de 1 dia; diferença contra nenhuma política, IC 95%):**

| Política | Minutos parados por dia útil (4 linhas) | Trens-hora perdidos | Outro efeito |
|---|---|---|---|
| Operação degradada (marcha lenta após falha de equipamento fixo) | −7,8 (−9,7 a −5,9) | −16,4 (−24,8 a −8,0) | disponibilidade origem-destino +0,35 p.p. |
| Retirada do trem falho | −1,1 (−1,4 a −0,8) | −0,18 (−0,40 a 0,03) | só material rodante |
| Tratamento de causa comum (redução de 50%, hipótese) | −0,8 (−1,3 a −0,3) | −0,52 (−0,89 a −0,15) | só causa comum |
| Reserva fria (2 trens por linha) | 0 | −0,63 (−0,67 a −0,58) | frota completa na Laranja +32,5 p.p. (+58 p.p. com reparo de 4 dias) |
| Retorno parcial nas pontas de viagem (hipótese) | 0 | 0 | disponibilidade origem-destino +0,21 p.p. |
| Rota alternativa de passageiros | 0 | 0 | disponibilidade origem-destino +0,01 p.p. |

A política com maior efeito é a operação degradada, que ataca a causa mais frequente (equipamentos fixos). A reserva fria protege a oferta, não a continuidade do serviço, e o efeito dela cresce com o tempo de reparo, que é hipótese (0,5 a 4 dias). O retorno parcial vale mais que a rota alternativa porque a rede tem poucos caminhos alternativos.

### 4.4 Expansão da rede (spec 014)

Cinco candidatas, todas com coordenadas de consultas salvas ao OSM ou ao Wikidata: prolongamento da Azul até Anjou (em obras, inauguração prevista para 2031), Linha Rosa (proposta de 2017, 29 estações), prolongamento da Amarela em Longueuil, prolongamento da Laranja até Bois-Franc e o anel da Laranja proposto pela ARTM em 2019. O método de estados sorteia 200 mil vezes o estado de cada trecho (aberto ou bloqueado, pela taxa e pela duração das falhas) e mede a disponibilidade dos pares de estações atuais, ponderada pela oferta de hoje. A rede atual tem disponibilidade origem-destino de 99,236% em dia útil. O ganho de cada candidata é pareado com a rede atual.

| Candidata (sem retorno parcial) | km (aprox.) | Ganho, p.p. (IC 95%) |
|---|---|---|
| Linha Rosa | 35,4 | +0,021 (0,020 a 0,022) |
| Rosa com a Azul até Anjou | 42,3 | +0,003 (−0,006 a 0,012) |
| Anel da Laranja (ARTM, 2019) | 9,9 | +0,0002 |
| Amarela em Longueuil | 7,2 | −0,005 |
| Laranja até Bois-Franc | 3,0 | −0,035 |
| Azul até Anjou (em obras) | 6,9 | −0,075 |

Com retorno parcial nas pontas de viagem (hipótese), a ordem muda: Rosa com a Azul +0,053, anel da Laranja +0,019, Rosa +0,011, ramais 0. Na busca exaustiva de ligações diretas entre estações atuais (até 3 km em linha reta), a melhor é Atwater (Verde) – Université-de-Montréal (Azul), com +0,085 p.p. Hoje a Azul só alcança o resto da rede pela Laranja, em Snowdon e Jean-Talon: quando a Laranja para, a Azul fica isolada. Essa dependência é o maior ponto único de falha da rede no modelo.

Leitura para a decisão: uma linha nova aumenta a confiabilidade da rede pelos caminhos alternativos que cria, não pela extensão. Ramais, como o prolongamento da Azul já em obras, ampliam a cobertura, que esta métrica não mede por falta de dados de passageiros, mas não criam redundância.

## 5. Validação contra o histórico (spec 012)

Ajustamos o modelo só com os dados até 2024-12-31 e previmos o número de falhas de cada linha em cada mês de 2025-01 a 2026-06 (72 casos), com o mesmo processo do simulador. O critério, escrito antes de ver o teste, era que o intervalo de predição de 90% contivesse o observado em 80% a 98% dos casos.

| Versão | Definida | Cobertura do IP 90% (IC 95%) | PIT (KS) |
|---|---|---|---|
| A: treino até 2024-12, efeito do ano de 2024 | antes do teste (oficial) | **66,7%** (54,6%–77,3%) | p = 2,4e-11 |
| B: treino até 2023-09, só exposição medida | antes do teste | 81,9% (71,1%–90,0%) | p = 0,06 |
| C: treino até 2024-12, efeito do ano sorteado | depois de ver A | 84,7% (74,3%–92,1%) | p = 0,01 |
| D: regra C em outro período (teste 2023-01 a 2024-06) | depois de ver A | 90,3% (81,0%–96,0%) | p = 0,16 |

A versão oficial não passou: 22 dos 24 meses fora do intervalo ficaram abaixo dele. O modelo superestimou 2025 porque herdou o efeito de 2024, um ano atípico (o segundo semestre de 2024 teve cerca de 1.000 falhas técnicas, contra cerca de 500 nos semestres vizinhos). Registramos a mudança com data e testamos a regra nova num período diferente, como a especificação manda. Ela cobriu 90% dos casos, com PIT compatível com a uniforme. A lição de engenharia é que o efeito de um ano não se transfere para o seguinte: a incerteza entre anos precisa entrar na previsão.

Em 2025, os minutos parados observados ficaram dentro do intervalo de 95% nas quatro linhas nas versões B, C e D; na versão A, Verde e Amarela ficaram abaixo.

## 6. Limitações

- Não há passageiros diários: todas as métricas são ponderadas pela oferta.
- O tempo de reparo na oficina e a posição dos aparelhos de mudança de via não são públicos e entram como hipóteses ajustáveis.
- A exposição de outubro de 2023 em diante é estimada pelo horário.
- Os traçados das candidatas, exceto a Azul, são aproximações em linha reta entre estações.

## 7. Conclusão

O metrô de Montreal tem disponibilidade alta em cada linha (99,5% a 99,9% do tempo de operação em dia útil), mas a confiabilidade da rede como sistema depende de poucos pontos. Três conclusões valem para a decisão:

1. **As falhas se agrupam e têm causa comum.** Tratar as falhas como independentes subestima o risco. O agrupamento aparece no tempo (uma falha dobra ou triplica a chance de outra na hora seguinte) e no espaço (eventos que param a Verde e a Laranja juntas tiram a única redundância de rota do centro).
2. **A política que mais rende ataca os equipamentos fixos.** Eles são mais da metade das falhas, e a operação degradada (liberar o trecho em marcha lenta) reduz mais os minutos parados do que reservar trens. A reserva de trens protege a oferta, e o efeito dela depende do tempo de reparo na oficina, que não é público.
3. **Uma linha nova vale pelos caminhos alternativos que cria.** Ramais, como o prolongamento da Azul já em obras, ampliam a cobertura, mas não criam redundância. O maior ponto único de falha do modelo é a dependência da Azul em relação à Laranja.

A validação mostrou o limite do modelo: o efeito de um ano não se transfere para o seguinte, e a previsão precisa carregar a incerteza entre anos. As decisões tomadas depois de ver os dados estão registradas com data, e a versão que falhou continua publicada.

Próximos passos: conferir o simulador num navegador comum e no celular, pedir à STM os dados que faltam (passageiros diários, posição das subestações, tempo de reparo na oficina) e repetir o backtest com o motor TypeScript, como segunda implementação.

## Referências

DOIs conferidos na API do Crossref em 2026-10-21 (`fontes/verificacao/referencias_crossref.json`).

- Brown, E. N.; Barbieri, R.; Ventura, V.; Kass, R. E.; Frank, L. M. The time-rescaling theorem and its application to neural spike train data analysis. *Neural Computation*, 14(2), 325–346, 2002. doi:10.1162/08997660252741149
- Clopper, C. J.; Pearson, E. S. The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26(4), 404–413, 1934. doi:10.1093/biomet/26.4.404
- Dunn, P. K.; Smyth, G. K. Randomized quantile residuals. *Journal of Computational and Graphical Statistics*, 5(3), 236–244, 1996. doi:10.1080/10618600.1996.10474708
- Garwood, F. Fiducial limits for the Poisson distribution. *Biometrika*, 28(3/4), p. 437, 1936. doi:10.2307/2333958
- Gneiting, T.; Balabdaoui, F.; Raftery, A. E. Probabilistic forecasts, calibration and sharpness. *Journal of the Royal Statistical Society: Series B*, 69(2), 243–268, 2007. doi:10.1111/j.1467-9868.2007.00587.x
- Kleiber, C.; Zeileis, A. Visualizing count data regressions using rootograms. *The American Statistician*, 70(3), 296–303, 2016. doi:10.1080/00031305.2016.1173590
- Künsch, H. R. The jackknife and the bootstrap for general stationary observations. *The Annals of Statistics*, 17(3), 1217–1241, 1989. doi:10.1214/aos/1176347265
- Lilliefors, H. W. On the Kolmogorov-Smirnov test for normality with mean and variance unknown. *Journal of the American Statistical Association*, 62(318), 399–402, 1967. doi:10.1080/01621459.1967.10482916
- Mosleh, A. et al. *Procedures for Treating Common Cause Failures in Safety and Reliability Studies*. NUREG/CR-4780, U.S. Nuclear Regulatory Commission, 1988. **Não conferido:** o site da NRC recusou o acesso desta máquina e o OSTI não devolveu o documento.

## Apêndice: como reproduzir

```bash
python -I pipeline/verifica_fontes.py --baixa-release --recalcula
python -m pip install -r pipeline/requirements.txt
python -m pytest pipeline/tests -q
cd app && npm ci && npm test && npm run build
```
