# 008 — Políticas de tolerância a falhas

**Status:** especificada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 006, 007, 009

## Pergunta de engenharia
Que política de tolerância a falhas reduz mais os trens-hora perdidos e os minutos de interrupção, separando falha de trem e falha de equipamento fixo? O número que responde é a diferença de cada política contra "nenhuma política", com intervalo de 95%.

## Contexto
- O painel atual já tem um modelo de reserva k-de-n por Markov: na Laranja, com reparo de 1 dia, a chance de ter todos os trens necessários é de 67% sem reserva e de 99,2% com 2 trens de reserva.
- Os trens necessários por dia útil foram estimados pelo km real: Verde cerca de 50, Laranja 47, Azul 15, Amarela 6.
- O tempo de reparo na oficina não está em nenhuma fonte. É hipótese, entre 0,5 e 4 dias.
- Causa comum: 31 eventos técnicos param a Verde e a Laranja juntas; isso limita a redundância do corredor entre Lionel-Groulx e Berri-UQAM (FONTES.md).

## Critérios de aceite
- Dadas as políticas reserva fria k-de-n, retirada do trem falho, operação degradada (velocidade reduzida), retorno parcial antes do trecho bloqueado, rota alternativa de passageiros e tratamento de causa comum, quando o simulador roda, então cada uma pode ser ligada e desligada sozinha.
- Dada cada política, quando comparada a "nenhuma política", então a diferença usa números aleatórios comuns (mesmas falhas nas duas rodadas) e tem intervalo de 95%.
- Dada a reserva k-de-n sem outras políticas, quando simulada com os mesmos parâmetros do painel, então a chance de frota completa bate com o modelo de Markov a até 5 pontos percentuais.
- Dado o retorno parcial, quando a posição dos aparelhos de mudança de via não estiver verificada, então a política só usa terminais, e o resultado aparece marcado como hipótese.
- Dado cada resultado, quando publicado, então o relatório separa o efeito em falhas de trem e em falhas de equipamento fixo.
- Dado o tempo de reparo, quando varia de 0,5 a 4 dias, então o relatório traz a sensibilidade de cada política a ele.

## Fora de escopo
- Custo financeiro de cada política (pode entrar depois, com fonte).
- Ônibus de substituição: não há dados de oferta.

## Riscos e dependências
- Sem a posição real dos aparelhos de mudança de via, o retorno parcial pode ser otimista ou pessimista.
- A rota alternativa depende da spec 009 (pares origem e destino ponderados pela oferta).

## Perguntas em aberto
- Vale buscar os aparelhos de mudança de via (`railway=switch`) no OpenStreetMap, marcados como não verificados?
- Quantos trens de reserva a STM mantém de fato por linha?
