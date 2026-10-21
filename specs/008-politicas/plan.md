# 008 — Políticas de tolerância a falhas: plano

## Políticas e o que cada uma muda no motor

| Política | Efeito no motor | Hipóteses |
|---|---|---|
| Reserva fria k-de-n | No início do dia sorteia os trens na oficina pela distribuição estacionária do nascimento-morte da frota. Com a política, `reservas_por_linha` trens parados cobrem os da oficina (evento `INJETA_RESERVA`). Se faltar trem, cancela viagens no pico: capacidade = pico do horário × (n − falta) / n, e as viagens que partem quando o horário passa da capacidade são canceladas na proporção do excesso, espaçadas por um acumulador | `reservas_por_linha` (2), `reparo_oficina_dias` (1), `p_retirada` (1) |
| Retirada do trem falho | Com probabilidade `p_retirada`, o trem com falha sai da via em até `tempo_retirada_min` e encerra a viagem na estação seguinte (evento `RETIRADA`). A interrupção fica em min(duração sorteada, tempo de retirada) | `tempo_retirada_min` (10 min, nova) |
| Operação degradada | Falha de equipamento fixo com duração D > `tempo_ativacao_degradada_min`: o trecho fica parado só até a ativação e depois reabre em marcha lenta (tempo de percurso × `fator_velocidade_degradada`) até o fim do reparo D | `tempo_ativacao_degradada_min` (5 min, nova), `fator_velocidade_degradada` (1,25) |
| Retorno parcial | Para as métricas origem-destino: sem a política, um trecho bloqueado para a linha inteira, nos dois sentidos. Com ela, para só o pedaço entre os pontos de retorno que cercam o trecho, no sentido bloqueado | Pontos de retorno = pontas de viagem do horário (verificadas pelo GTFS) + `cenario.pontosRetorno` (hipótese) |
| Rota alternativa | Para as métricas origem-destino: sem a política, o par só vale pelo caminho de sempre; com ela, por qualquer caminho livre, com o tempo extra medido | `tempo_transferencia_min` (4) |
| Tratamento de causa comum | Cada evento de causa comum é evitado com probabilidade igual à redução (alimentação ou controle redundante) | `reducao_causa_comum`; se for 0, usa `reducao_causa_comum_politica` (0,5, nova) |

## Números aleatórios comuns

Cada fonte de sorteio tem seu fluxo (`prng.ts`). Os instantes de falha não dependem da política, e cada evento gasta sempre os mesmos sorteios: duração (uniforme + normal), escolha do trem, decisão de retirada, local e sentido da falha de equipamento fixo, decisão de evitar a causa comum. Assim a rodada i tem as mesmas falhas com e sem cada política, e a diferença é pareada (`rodaRodadas(..., politicasB)` e `agrega(...).diferenca`). O teste confere que as falhas sorteadas são idênticas, rodada a rodada, para cinco políticas.

## Camada de frota (k-de-n)

- **Modelo:** estado i = trens na oficina. Saída para a oficina a min(n, n + s − i) × λ × p_retirada por dia (a reserva parada não falha). Volta a i / reparo por dia, sem fila de oficina.
- **Distribuição estacionária:** fórmula do nascimento-morte (`estacionariaFrota`). Simulação por eventos para conferência (`simulaFrota`).

### Resultado contra o painel

Laranja, n = 48, λ = 0,00835 por trem-dia, reparo de 1 dia, p_retirada = 1:

| Reservas | Painel (kdn.json) | Markov do motor | Simulação, 200 mil dias |
|---|---|---|---|
| 0 | 0,6710 | 0,6709 | 0,6740 |
| 1 | 0,9385 | 0,9384 | 0,9393 |
| 2 | 0,9921 | 0,9920 | 0,9920 |

O Markov do motor bate com as 144 linhas de `kdn.json` a menos de 0,001; a diferença vem do λ arredondado em 5 casas no arquivo. A simulação fica a menos de 1 ponto percentual do Markov, bem dentro dos 5 pedidos.

## Desvios do desenho pedido

| Desvio | Por quê |
|---|---|
| Operação degradada: a marcha lenta dura o restante do reparo (D − ativação), não `duracao_degradada_min` | Uma política que só acrescenta marcha lenta depois do reparo nunca melhora nada. A política troca parada total por marcha lenta. `duracao_degradada_min` fica sem uso no motor; sugestão: trocar por `tempo_ativacao_degradada_min` no `pipeline/parametros.py` |
| Retirada: a política é "retirada rápida" com tempo-alvo | As durações observadas já refletem a prática atual da STM; a política mede quanto se ganha com um tempo de retirada menor |
| Retorno parcial e rota alternativa só mudam as métricas origem-destino | O movimento dos trens não muda: os trens da linha continuam no horário nos trechos livres. O efeito aparece na disponibilidade origem-destino |
| Retorno parcial com as pontas de viagem do horário | Os aparelhos de mudança de via não estão verificados. O GTFS mostra onde as viagens começam e terminam: Laranja em Côte-Vertu, Henri-Bourassa e Montmorency; as outras linhas só nos terminais. Pontos extras entram como hipótese do cenário, e `avisosDoCenario` marca o resultado |
| Uma falha de trem com retirada não tira o trem das viagens seguintes no mesmo dia | O rede.json não encadeia viagens num trem (sem `block_id`). O efeito sobre a frota fica na camada k-de-n |

## Separação MR e EF

As métricas saem por causa: `minutosMR`, `minutosEF` e `minutosCC` por linha. Os testes conferem que a retirada muda só os minutos de material rodante (os de equipamento fixo ficam idênticos, rodada a rodada) e que a operação degradada muda só os de equipamento fixo.

## Sensibilidade ao tempo de reparo

`politicas.test.ts` roda a reserva fria contra "nenhuma política" com reparo de 0,5, 1, 2 e 4 dias. O efeito em viagens canceladas cresce com o reparo. Para as outras políticas, a interface (spec 011) varia `reparo_oficina_dias` no cenário e repete a comparação.

## Testes

| Critério | Teste |
|---|---|
| Cada política liga e desliga sozinha | `politicas.test.ts` (seis testes, um por política) |
| Comparação com números aleatórios comuns e IC95 | `politicas.test.ts` (falhas idênticas; diferença pareada com IC95, n e semente; erro-padrão pareado menor que o de amostras independentes) |
| k-de-n contra o Markov a até 5 pontos | `frota.test.ts` |
| Retorno parcial só com pontas de viagem e marcado como hipótese | `politicas.test.ts` |
| Relatório separa MR e EF | `politicas.test.ts` |
| Sensibilidade ao reparo de 0,5 a 4 dias | `frota.test.ts` e `politicas.test.ts` |
