# 006 — Distribuições do tempo entre falhas, do tempo até retomar e da causa comum

**Status:** implementada
**Fase:** F2 (semanas 3 a 5)
**Depende de:** 001, 005

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** A duração pela faixa oficial e as 9 fontes de falha mudam a duração, trazem a renovação por fonte e o β pelo denominador da família; o tempo entre falhas e as conclusões não mudam. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

## Pergunta de engenharia
Que distribuição descreve o tempo entre falhas e o tempo até o serviço voltar, por linha, causa, frota e condição? E o agrupamento das falhas (Weibull com β < 1) vem de heterogeneidade das condições ou de um mecanismo próprio? O número que responde é o resultado do teste de reescala do tempo.

## Contexto
- No painel atual, a Weibull vence a exponencial e a lognormal nas 4 linhas, sempre com forma β entre 0,52 e 0,73 (FONTES.md, tabela de ajustes).
- β < 1 quer dizer que, logo depois de uma falha, a chance de outra é maior. Pode ser falha em cascata ou só mistura de condições (frio, pico) com taxas diferentes.
- O tempo registrado é até o serviço voltar, não o reparo do equipamento. A mediana é de 2 a 3 minutos; 40% das falhas da Verde não têm interrupção registrada.
- Causa comum: 31 eventos técnicos param a Verde e a Laranja juntas. O fator β de causa comum é cerca de 1% de cada linha, mas responde por 100,3 minutos por ano.

## Critérios de aceite
- Dado cada estrato (linha × causa × frota × condição), quando as distribuições são ajustadas, então são comparadas exponencial, Weibull, gama, lognormal e log-logística por AIC.
- Dado o melhor modelo de cada estrato, quando a aderência é testada, então o relatório traz KS e Anderson-Darling com p-valor por bootstrap paramétrico (correção de Lilliefors).
- Dado um estrato com menos de 30 observações, quando é ajustado, então herda o modelo do estrato pai, e isso fica registrado.
- Dada a taxa variável no tempo da spec 005, quando o tempo é reescalado pela taxa acumulada, então se os intervalos reescalados forem compatíveis com exponencial de média 1 (KS com p > 0,05 por linha), o simulador usa um processo de Poisson com taxa variável; se não, usa renovação Weibull. O relatório diz qual caso valeu para cada linha.
- Dado o tempo até retomar, quando modelado, então usa um modelo de tempo acelerado lognormal com causa secundária, hora e evacuação como fatores, e trata os zeros como massa separada.
- Dado o fator β de causa comum, quando estimado, então tem intervalo de Clopper-Pearson para cada par de linhas.
- Dado cada parâmetro publicado, quando vai para o simulador, então leva valor, intervalo, número de observações, método, fontes e status.

## Resultado (2026-10-21)

Script `pipeline/distribuicoes.py`; contrato montado por `pipeline/parametros.py`; testes em `pipeline/tests/test_modelos.py`; relatório [`distribuicoes.md`](../../fontes/verificacao/distribuicoes.md).

| Critério | Resultado |
|---|---|
| Cinco famílias comparadas por AIC em cada estrato | **Atende**: 29 estratos ajustados (linha × causa, × frota e × inverno ou resto do ano); a Weibull vence em 23, a gama em 4 e a lognormal em 2 |
| KS e Anderson-Darling com p-valor por bootstrap paramétrico | **Atende** (B = 200). 14 dos 29 estratos passam nos dois testes a 5%; nos grandes (até 2.170 intervalos) o teste rejeita até desvios pequenos, e o relatório mostra cada p |
| Estrato com menos de 30 intervalos herda do pai | **Atende**: Azul MPM-10 (4) e Laranja MR-73 (20) herdam de linha × causa |
| Teste de reescala decide o processo | **Atende**: nas 8 combinações linha × causa, o KS rejeita a exponencial de média 1 (p de 1e-8 a 1e-90), com média reescalada entre 0,97 e 1,03. O simulador usa renovação Weibull no tempo reescalado, forma de 0,44 (Amarela, EF) a 0,80 (Verde, MR): há agrupamento além do que hora, clima e oferta explicam |
| Tempo até restabelecer: massa em zero + tempo acelerado lognormal com causa secundária, hora e evacuação | **Atende**: sem interrupção de 20% (Azul, MR) a 67% (Amarela, EF); evacuação multiplica a duração por 2,92 (2,73–3,13); "Service de la voie" por 2,30; R² 0,23 |
| Mudança registrada em 2026-10-21 | Ao validar o simulador (spec 009), a média observada das durações positivas era maior que a da lognormal: 23% a 29% na Laranja (material rodante e equipamentos fixos) e 26% nos equipamentos fixos da Verde, e 3,4 vezes na Azul (EF), por causa de poucos eventos de quase 20 horas. A lognormal continua no modelo de fatores (tempo acelerado); o simulador passou a sortear a duração positiva da amostra observada (`amostra_positivos` no contrato) |
| β com Clopper-Pearson por par | **Atende**: Verde–Laranja 31 eventos, β 0,011 (0,007–0,015) para a Verde. Os 45 eventos multilinha formam 7 grupos; o simulador sorteia por grupo, para não contar duas vezes um evento que para 3 ou 4 linhas |
| Parâmetro com valor, intervalo, n, método, fontes e status | **Atende**: `dados/derivados/simulador/parametros.json` |

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D56, D57 e D62; spec 018).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **O que mudou na entrada:**
  - *depois de ver (D55):* nas 100 falhas em que a duração calculada pelos horários contradiz a faixa oficial da STM, vale a faixa. Os minutos parados das falhas técnicas vão de 43.971 para 33.404. Os 6 registros de cerca de 19 h em Saint-Michel (Azul, outubro de 2024) com faixa "02 min et moins" passam a ter duração dessa faixa;
  - a taxa da spec 005, que reescala o tempo, usa a exposição medida até 2026-06 (spec 004);
  - o início das falhas não muda, então o tempo entre falhas é o mesmo.
- **O que mudou no método:**
  - *depois de ver (D56):* cada falha ganha uma de 9 fontes (frota no material rodante; setor × sintoma no equipamento fixo). A renovação, no tempo reescalado pela taxa da fonte (spec 018), e a duração passam a ser ajustadas por linha × fonte, em 32 estratos. Estrato com menos de 30 intervalos (na renovação) ou com menos de 30 durações positivas (na duração, `distribuicoes.py`) herda da mesma fonte na rede: 7 na renovação e 15 na duração. O simulador usa esses estratos (contrato v2);
  - os ajustes por linha × família (MR e EF) continuam, com o mesmo método;
  - o β da causa comum ganha o denominador da família (trem ou fixo) de cada evento, porque 40 dos 45 eventos são de equipamento fixo;
  - entra a massa em zero por fonte e ano (D62, spec 020), com a leitura fixada antes de calcular.

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| p do KS na reescala (8 combinações linha × família) | 1e-8 a 1e-90 | 9e-9 a 1,5e-93 |
| Forma da renovação por linha × família | 0,439 (Amarela, EF) a 0,802 (Verde, MR) | 0,435 (Amarela, EF) a 0,801 (Verde, MR) |
| Evacuação na duração | 2,92 (2,73–3,13) | 2,92 (2,74–3,11) |
| "Service de la voie" na duração | 2,30 | 2,19 |
| R² do tempo acelerado | 0,23 | 0,25 |
| Média observada ÷ média da lognormal, durações positivas | Laranja 1,23 (MR) e 1,29 (EF); Verde EF 1,26; Azul EF 3,38 | Laranja 1,23 (MR) e 1,24 (EF); Verde EF 1,17; Azul EF 2,04 |
| Média observada das durações positivas, Azul EF | 51,97 min | 14,79 min |
| Forma da renovação por linha × fonte (novo) | — | 0,37 (Azul, via com sintoma de trem) a 0,83 (Verde, MR-73), sempre < 1 |
| β Verde–Laranja pelo denominador da família (novo) | — | EF: 30 eventos, Verde 0,022 (0,015–0,031), Laranja 0,014 (0,009–0,019). MR: 1 evento, Verde 0,0007 (0,00002–0,0037) |

Não mudam: os 29 estratos do tempo entre falhas, com a Weibull vencendo em 23, a gama em 4 e a lognormal em 2; os 14 de 29 que passam no KS e no Anderson-Darling; as heranças da Azul MPM-10 (4) e da Laranja MR-73 (20); a média reescalada entre 0,97 e 1,03; a falha sem interrupção de 20% (Azul, MR) a 67% (Amarela, EF); o β da Verde com o denominador de todas as falhas, 0,011 (0,007–0,015), com 31 eventos; os 7 grupos dos 45 eventos multilinha. Relatórios: [`distribuicoes.md`](../../fontes/verificacao/distribuicoes.md) e [`duracoes.md`](../../fontes/verificacao/duracoes.md); renovação e duração por fonte e β pela família em `dados/derivados/modelos/distribuicoes.json` (`reescala_fonte`, `ttr_fonte`, `causa_comum_beta_familia`).

Critérios:
- Cinco famílias por AIC, KS e Anderson-Darling: continuam atendendo, com o mesmo resultado.
- Estrato com menos de 30 observações: continua atendendo. A regra vale também nos 32 estratos linha × fonte, herdando da mesma fonte na rede.
- Teste de reescala: continua atendendo. O KS rejeita a exponencial de média 1 nas 8 combinações linha × família, e o simulador usa renovação Weibull. O KS é feito só por linha × família; por fonte, a forma fica abaixo de 1 nos 32 estratos.
- Tempo até restabelecer: continua atendendo. A lognormal ainda subestima a média das durações positivas nas 8 combinações (razão de 1,04 a 2,04), e o simulador continua sorteando da amostra observada, agora por linha × fonte. A diferença da Azul (EF) cai de 3,38 para 2,04 vezes com a regra da D55.
- β com Clopper-Pearson por par: continua atendendo, nas duas versões do denominador. Pela família, o β da Verde com a Laranja dobra nas falhas fixas (0,011 para 0,022).
- Parâmetro com valor, intervalo, n, método, fontes e status: continua atendendo no contrato v2, com renovação e duração por linha × fonte.

Nenhum critério passou a exceção.

**Massa em zero por fonte e ano (D62; leitura fixada antes na spec 020): inconclusiva.** As fontes diferem (p < 0,0001): a duração zero vai de 25,1% no MR-73 a 89,2% na via com sintoma de trem e 90,0% nas estações. O padrão de parada segura com rearme rápido não aparece: a menor proporção entre controle de trens e frotas (25,1%, MR-73) fica abaixo da maior entre via, estações e TCPE (90,0%, estações), e as frotas variam entre os anos (p < 0,0001 no MR-73 e no MPM-10). O de artefato de registro também não: as fontes não são homogêneas e nenhum ano tem salto comum. "Controle de trens" (Service aux trains) é dedução até a resposta da STM.

## Fora de escopo
- Tempo de reparo na oficina: não existe na base. Entra como hipótese na spec 008.
- Análise de falha por componente (porta, freio): o sintoma da base é genérico demais.

## Riscos e dependências
- Os zeros e a resolução de 1 minuto distorcem o ajuste de tempos curtos. Mitigação: tratar intervalos menores que 1 minuto como censurados à esquerda.
- O resultado do teste de reescala depende da qualidade da spec 005.

## Perguntas em aberto
- Vale um modelo de mistura de duas Weibull por linha, se a reescala falhar?
- A causa comum deve incluir eventos não técnicos (326 eventos de todas as causas na Verde e Laranja) num cenário à parte?
