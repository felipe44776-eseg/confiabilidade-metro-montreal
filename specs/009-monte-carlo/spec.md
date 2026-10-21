# 009 — Monte Carlo e métricas

**Status:** especificada
**Fase:** F3 (semanas 4 a 7)
**Depende de:** 006, 007

## Pergunta de engenharia
Com quantas rodadas a estimativa de disponibilidade fica precisa, e a simulação reproduz os números já validados no painel? O número que responde é a meia-largura do intervalo de 95% em relação à média.

## Contexto
- O painel atual tem um Monte Carlo do corredor: na Laranja sozinha, 1.852 minutos parados por ano simulados contra 1.797 pelo cálculo analítico (FONTES.md, tabela corredor).
- Não há passageiros diários. As métricas por par origem-destino são ponderadas pela oferta do horário, não por pessoas.
- A janela de operação é de 20 h por dia.

## Critérios de aceite
- Dado o mesmo conjunto de rodadas, quando executado em paralelo com 1 ou com 8 processos, então os resultados são idênticos.
- Dado o número de rodadas padrão, quando a disponibilidade de cada linha é estimada, então a meia-largura do intervalo de 95% fica em até 5% da média dos minutos parados.
- Dada a Laranja sem redundância e os parâmetros do painel, quando simulada, então o intervalo de 95% dos minutos parados por ano contém 1.852 (simulado no painel) ou 1.797 (analítico); se não contiver, o relatório explica a diferença.
- Dadas as métricas, quando publicadas, então incluem: disponibilidade por linha; disponibilidade por par origem-destino (fração do tempo com caminho, mais o tempo extra de viagem), ponderada pela oferta; trens-hora perdidos contra o horário; minutos de interrupção.
- Dada cada métrica, quando mostrada, então vem com intervalo de 95%, número de rodadas e semente.
- Dado um cenário, quando executado, então o tempo total para o número padrão de rodadas é medido e registrado, para confirmar a estimativa de 10 a 30 segundos para 5.000 rodadas.

## Fora de escopo
- Otimização automática de parâmetros.
- Métricas de passageiros (lotação, tempo de espera por pessoa).

## Riscos e dependências
- Rodadas longas podem ficar lentas em computador fraco. Mitigação: mostrar o progresso e permitir menos rodadas, com o intervalo maior avisado.

## Perguntas em aberto
- Qual o número padrão de rodadas: fixo ou até atingir a precisão pedida?
- Os pares origem-destino devem ser todos (73 estações) ou só os de estações de correspondência?
