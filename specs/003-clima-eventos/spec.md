# 003 — Clima horário e eventos externos

**Status:** implementada
**Fase:** F1 (semanas 2 e 3)
**Depende de:** 000, 001

## Pergunta de engenharia
Chuva, neve, chuva congelante, frio intenso, greves e grandes eventos mudam a taxa de falha ou a oferta de serviço do metrô? Para responder, cada hora de operação de 2019 a junho de 2026 precisa ter clima e eventos ligados a ela.

## Contexto
- Hoje o painel usa clima diário da estação 51157 (MONTREAL INTL A). A taxa de falha de material rodante sobe de cerca de 5,3 por milhão de km-carro (10 a 20 °C) para 7,4 a 7,7 abaixo de 10 °C. A correlação diária com a temperatura é fraca (r = −0,10).
- A pesquisa de 2026-10-20 (research.md) mostrou que a estação 51157 não tem precipitação horária. Têm precipitação horária completa a 10761 (McTavish, centro) e a 30165 (aeroporto). A 51157 tem o campo de condição, que inclui "Freezing Rain".
- O clima horário do ECCC está em hora padrão local (LST, UTC−5 fixo o ano todo).
- Eventos: greves da STM em 2025 com faixas de serviço (fonte: imprensa); jogos do Canadiens; GP de F1. Não existem dados públicos de passageiros diários, de fechamentos planejados nem de quedas de energia.

## Critérios de aceite
- Dada cada hora de operação de 2019-01-01 a 2026-06-30, quando o painel horário é montado, então pelo menos 95% das horas têm precipitação (estação 10761, com a 30165 como reserva) e o painel diz qual estação foi usada em cada hora.
- Dadas as horas de troca de horário de verão, quando o clima em LST é convertido para a hora local, então um teste confere pelo menos 4 trocas (março e novembro de dois anos) sem hora duplicada nem faltando.
- Dado um episódio conhecido de chuva congelante (2023-04-05, das 09h às 20h, confirmado pela pesquisa), quando o painel é montado, então essas horas aparecem marcadas como chuva congelante.
- Dado cada evento externo (greve, jogo, GP), quando entra no painel, então tem data, faixa horária, URL da fonte e status (verificado ou não verificado).
- Dadas as greves de 2025, quando cruzadas com o serviço previsto, então as horas sem serviço viram exposição zero, e não "hora sem falha".
- Dado um fator sem fonte pública (passageiros diários, fechamentos planejados, quedas de energia), quando a spec é encerrada, então ele aparece como ausente no dicionário de dados, nunca como zero.

## Resultado (2026-10-21)

Scripts `pipeline/baixa_clima_eventos.py` e `pipeline/clima_eventos.py`; testes em `pipeline/tests/test_clima.py`; saídas em `dados/derivados/clima/`.

| Critério | Resultado |
|---|---|
| ≥ 95% das horas de operação com precipitação e estação indicada | **Atende**: 99,99% (99,3% da 10761, o resto da 30165) |
| 4 trocas de horário sem hora repetida nem faltando | **Atende** (teste em março e novembro de 2023 e 2024) |
| Chuva congelante em 2023-04-05, 09h a 20h | **Atende**: as 12 horas (09h a 20h LST, 10h a 21h locais); recálculo independente direto do ECCC |
| Evento com data, faixa, URL e status | **Atende**: 348 eventos; jogos "verificado", greves e GP "não verificado" |
| Greve vira exposição zero | **Atende** (teste): 2025-11-01 sem serviço; faixas parciais nos demais dias |
| Fatores sem fonte como ausentes no dicionário | **Atende**: `docs/dicionario_dados.md` |

Limitação declarada: a condição do tempo (campo "Weather" da 51157) só existe em 45,8% das horas de operação; o resto fica "sem_dado".

## Fora de escopo
- Previsão do tempo. O projeto usa só o histórico.
- Alertas meteorológicos históricos: o ECCC guarda cerca de 50 dias, e a pesquisa não achou arquivo público.
- Festivais sem fonte estruturada, que ficam como tabela manual opcional.

## Riscos e dependências
- A API de jogos da NHL não é documentada e pode mudar. Mitigação: guardar a resposta com hash, como as demais fontes.
- O horário das greves vem da imprensa. Fica com status "imprensa" e pode ser trocado por fonte oficial se aparecer.
- Os limiares oficiais de evento extremo do ECCC não foram verificados. Usaremos limiares próprios, declarados.

## Perguntas em aberto
- A estação McTavish representa bem as linhas da periferia (Montmorency, Angrignon)?
- Vale usar o Open-Meteo (reanálise) para preencher horas sem medição, sabendo que ele erra o tipo de precipitação em chuva congelante?
