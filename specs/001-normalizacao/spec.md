# 001 — Normalização dos incidentes

**Status:** implementada com exceções
**Fase:** F1 (semanas 2 e 3)
**Depende de:** 000

## Pergunta de engenharia
Conseguimos transformar cada incidente técnico num evento com início e fim absolutos, classe de causa e linha, sem perder nenhum? O número que responde é a parcela dos 8.530 eventos técnicos resolvidos sem ambiguidade.

## Contexto
- A base de incidentes da STM tem 45.785 registros de 2019-01-01 a 2026-06-30 (FONTES.md).
- Há 8.530 falhas técnicas de uma linha só: 3.982 de material rodante e 4.548 de equipamentos fixos. Outras 45 foram registradas em mais de uma linha e 44 não têm linha ("Non affecté").
- A hora depois da meia-noite continua como 24:xx e 25:xx, contada no dia de operação anterior.
- A hora de retomada não tem data. A duração calculada cai na faixa oficial `Incident en minutes` em 97,5% dos eventos técnicos (8.319 de 8.530).
- A janela de operação adotada é de 20 h por dia (05:00 a 01:00), inferida do horário dos incidentes. É hipótese declarada.

## Critérios de aceite
- Dado o arquivo de incidentes, quando a normalização roda, então 100% dos 8.530 eventos técnicos de uma linha recebem início e fim absolutos (data e hora) ou aparecem numa lista de exceções com o motivo.
- Dado um incidente às 24:xx ou 25:xx, quando é normalizado, então o início cai no dia civil seguinte ao `Jour calendaire`, e um teste cobre a virada de mês e de ano.
- Dado um evento cuja retomada tem hora menor que a do incidente, quando é normalizado, então a retomada passa para o dia seguinte e a duração fica entre 0 e 1.440 minutos.
- Dada a duração calculada, quando comparada à faixa oficial, então pelo menos 99% dos eventos ficam dentro da faixa ou da faixa vizinha, e os demais vão para a lista de exceções.
- Dados os 45 eventos multilinha, quando normalizados, então cada um gera um evento de causa comum com a lista de linhas atingidas, e a soma bate com o painel (31 eventos técnicos Verde e Laranja).
- Dados os 44 eventos sem linha, quando normalizados, então ficam registrados como "sem linha" e fora das métricas por linha, sem serem descartados em silêncio.
- Dado o mesmo arquivo de entrada, quando a normalização roda duas vezes, então a saída é idêntica byte a byte.

## Resultado (2026-10-21)

Script `pipeline/normaliza.py`; testes em `pipeline/tests/test_normaliza.py`; saídas em `dados/derivados/eventos/`.

| Critério | Resultado |
|---|---|
| 100% dos 8.530 com início e fim ou na lista de exceções | **Atende**: 8.530 com início e fim; 100 também listados em `excecoes.csv` |
| 24:xx e 25:xx no dia seguinte, com virada de mês e ano | **Atende** (teste) |
| Retomada menor que o início vai para o dia seguinte, duração entre 0 e 1.440 | **Atende** (teste); máxima de 1.170 min |
| ≥ 99% na faixa oficial ou na vizinha | **Exceção**: 98,83% (8.430 de 8.530). Os 100 restantes estão em `excecoes.csv` com o motivo; o critério não foi afrouxado |
| 45 multilinha como causa comum, 31 Verde e Laranja | **Atende** |
| 44 sem linha registrados, fora das métricas por linha | **Atende** |
| Saída idêntica ao repetir | **Atende** (teste) |

## Fora de escopo
- Corrigir ou reinterpretar a causa atribuída pela STM.
- Localização geográfica dos eventos (spec 002).
- Incidentes de causa não técnica (passageiros, operação, "outras"), que ficam registrados mas não entram nos modelos de falha.

## Riscos e dependências
- A retomada sem data pode esconder interrupções de mais de 24 h. Mitigação: comparar com a faixa oficial e listar todo evento acima de 30 minutos que não bata.
- O fuso horário da base não é documentado. Supomos hora local de Montreal, a confirmar na spec 003 ao cruzar com o clima.

## Perguntas em aberto
- Os eventos com duração zero (40% das falhas da Verde) são falhas sem interrupção ou registro incompleto?
- Existe significado para os códigos de linha "4-2" e combinações parecidas além de multilinha?
