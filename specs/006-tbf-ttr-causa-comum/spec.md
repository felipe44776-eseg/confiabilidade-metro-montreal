# 006 — Distribuições do tempo entre falhas, do tempo até retomar e da causa comum

**Status:** especificada
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

## Fora de escopo
- Tempo de reparo na oficina: não existe na base. Entra como hipótese na spec 008.
- Análise de falha por componente (porta, freio): o sintoma da base é genérico demais.

## Riscos e dependências
- Os zeros e a resolução de 1 minuto distorcem o ajuste de tempos curtos. Mitigação: tratar intervalos menores que 1 minuto como censurados à esquerda.
- O resultado do teste de reescala depende da qualidade da spec 005.

## Perguntas em aberto
- Vale um modelo de mistura de duas Weibull por linha, se a reescala falhar?
- A causa comum deve incluir eventos não técnicos (326 eventos de todas as causas na Verde e Laranja) num cenário à parte?
