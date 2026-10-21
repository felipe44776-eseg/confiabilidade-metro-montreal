# 006 — Distribuições do tempo entre falhas, do tempo até retomar e da causa comum

**Status:** implementada
**Fase:** F2 (semanas 3 a 5)
**Depende de:** 001, 005

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

## Fora de escopo
- Tempo de reparo na oficina: não existe na base. Entra como hipótese na spec 008.
- Análise de falha por componente (porta, freio): o sintoma da base é genérico demais.

## Riscos e dependências
- Os zeros e a resolução de 1 minuto distorcem o ajuste de tempos curtos. Mitigação: tratar intervalos menores que 1 minuto como censurados à esquerda.
- O resultado do teste de reescala depende da qualidade da spec 005.

## Perguntas em aberto
- Vale um modelo de mistura de duas Weibull por linha, se a reescala falhar?
- A causa comum deve incluir eventos não técnicos (326 eventos de todas as causas na Verde e Laranja) num cenário à parte?
