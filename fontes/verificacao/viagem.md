# Confiabilidade de uma viagem (spec 015)

Gerado por `app/relatorios/viagem.relatorio.ts` com o `parametros.json` real (código sha256-scripts:a0ff551bd3d56c35). Cenário padrão (dia útil, condições de referência do modelo), 1.000 dias por viagem, semente 20261021: os mesmos dias da aba "Muitos dias" com essa semente. Média e intervalo de 95%.

Disponibilidade: fração da janela de serviço da rede em que o caminho existe, a partir dos bloqueios do dia no grafo das estações (o mesmo método da disponibilidade origem-destino da spec 009). "Produto" é o valor em série, multiplicando as disponibilidades dos trechos como se as linhas falhassem de forma independente. Atraso: saídas a cada 10 minutos; para cada uma, a chegada mais cedo com os trens simulados do dia contra a mesma saída num dia sem falhas.

## Angrignon → Saint-Michel

Caminho de sempre: Verde de Angrignon a Berri-Uqam, baldeação, Laranja de Berri-Uqam a Jean-Talon, baldeação, Azul de Jean-Talon a Saint-Michel.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Verde 99,74% (99,70% a 99,78%); Laranja 99,71% (99,66% a 99,75%); Azul 99,81% (99,74% a 99,87%) |
| Produto dos trechos (série) | 99,25% |
| Viagem inteira, simulada | 99,28% (99,20% a 99,37%) |
| Minutos por dia sem caminho | 8,6 (7,6 a 9,6) |
| Dias com ao menos uma interrupção no caminho | 72,7% (69,9% a 75,5%) |
| Chance de chegar mais de 5 min atrasado | 0,40% (0,30% a 0,50%) |
| Chance de chegar mais de 15 min atrasado | 0,16% (0,09% a 0,24%) |
| Chance de chegar mais de 60 min atrasado | 0,05% (0,00% a 0,10%) |
| Chance de não chegar até o fim do serviço | 0,0009% (0,0000% a 0,0026%) |
| Atraso médio por viagem (min) | 0,13 (0,03 a 0,24) |
| Com rota alternativa: viagem inteira | 99,28% (99,20% a 99,37%) |
| Com rota alternativa: chance de mais de 5 min | 0,29% (0,20% a 0,38%) |
| Com rota alternativa: atraso médio (min) | 0,11 (0,00 a 0,21) |

## Côte-Vertu → Montmorency

Caminho de sempre: Laranja de Côte-Vertu a Snowdon, baldeação, Azul de Snowdon a Jean-Talon, baldeação, Laranja de Jean-Talon a Montmorency.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Laranja 99,71% (99,66% a 99,75%); Azul 99,81% (99,74% a 99,87%); Laranja 99,71% (99,66% a 99,75%) |
| Produto dos trechos (série) | 99,22% |
| Viagem inteira, simulada | 99,53% (99,45% a 99,60%) |
| Minutos por dia sem caminho | 5,7 (4,7 a 6,6) |
| Dias com ao menos uma interrupção no caminho | 53,4% (50,3% a 56,5%) |
| Chance de chegar mais de 5 min atrasado | 0,28% (0,20% a 0,36%) |
| Chance de chegar mais de 15 min atrasado | 0,11% (0,06% a 0,15%) |
| Chance de chegar mais de 60 min atrasado | 0,01% (0,00% a 0,02%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,07 (0,04 a 0,09) |
| Com rota alternativa: viagem inteira | 99,71% (99,66% a 99,75%) |
| Com rota alternativa: chance de mais de 5 min | 0,28% (0,20% a 0,36%) |
| Com rota alternativa: atraso médio (min) | 0,07 (0,04 a 0,09) |

## Longueuil- U. De Sherbrooke → Snowdon

Caminho de sempre: Amarela de Longueuil- U. De Sherbrooke a Berri-Uqam, baldeação, Laranja de Berri-Uqam a Snowdon.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Amarela 99,90% (99,87% a 99,93%); Laranja 99,71% (99,66% a 99,75%) |
| Produto dos trechos (série) | 99,61% |
| Viagem inteira, simulada | 99,61% (99,56% a 99,67%) |
| Minutos por dia sem caminho | 4,6 (4,0 a 5,3) |
| Dias com ao menos uma interrupção no caminho | 44,4% (41,3% a 47,5%) |
| Chance de chegar mais de 5 min atrasado | 0,53% (0,45% a 0,61%) |
| Chance de chegar mais de 15 min atrasado | 0,10% (0,06% a 0,15%) |
| Chance de chegar mais de 60 min atrasado | 0,01% (0,00% a 0,03%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,11 (0,09 a 0,14) |
| Com rota alternativa: viagem inteira | 99,61% (99,56% a 99,67%) |
| Com rota alternativa: chance de mais de 5 min | 0,52% (0,44% a 0,59%) |
| Com rota alternativa: atraso médio (min) | 0,10 (0,09 a 0,12) |

## Lionel-Groulx → Berri-Uqam

Caminho de sempre: Verde de Lionel-Groulx a Berri-Uqam.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Verde 99,74% (99,70% a 99,78%) |
| Produto dos trechos (série) | 99,74% |
| Viagem inteira, simulada | 99,74% (99,70% a 99,78%) |
| Minutos por dia sem caminho | 3,2 (2,7 a 3,6) |
| Dias com ao menos uma interrupção no caminho | 36,8% (33,8% a 39,8%) |
| Chance de chegar mais de 5 min atrasado | 0,10% (0,06% a 0,14%) |
| Chance de chegar mais de 15 min atrasado | 0,04% (0,02% a 0,07%) |
| Chance de chegar mais de 60 min atrasado | 0,01% (0,00% a 0,02%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,02 (0,01 a 0,04) |
| Com rota alternativa: viagem inteira | 99,98% (99,97% a 100,00%) |
| Com rota alternativa: chance de mais de 5 min | 0,02% (0,00% a 0,04%) |
| Com rota alternativa: atraso médio (min) | 0,01 (0,00 a 0,02) |

## Atwater → Berri-Uqam

Caminho de sempre: Verde de Atwater a Berri-Uqam.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Verde 99,74% (99,70% a 99,78%) |
| Produto dos trechos (série) | 99,74% |
| Viagem inteira, simulada | 99,74% (99,70% a 99,78%) |
| Minutos por dia sem caminho | 3,2 (2,7 a 3,6) |
| Dias com ao menos uma interrupção no caminho | 36,8% (33,8% a 39,8%) |
| Chance de chegar mais de 5 min atrasado | 0,09% (0,06% a 0,12%) |
| Chance de chegar mais de 15 min atrasado | 0,04% (0,01% a 0,06%) |
| Chance de chegar mais de 60 min atrasado | 0,01% (0,00% a 0,02%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,02 (0,01 a 0,04) |
| Com rota alternativa: viagem inteira | 99,74% (99,70% a 99,78%) |
| Com rota alternativa: chance de mais de 5 min | 0,09% (0,06% a 0,12%) |
| Com rota alternativa: atraso médio (min) | 0,02 (0,01 a 0,02) |

## Como ler

- Se o produto dos trechos cai dentro do intervalo do simulado, as linhas do caminho falham quase de forma independente: a viagem é um sistema em série.
- Quando a mesma linha aparece em dois trechos (Côte-Vertu → Montmorency usa a Laranja duas vezes), uma falha nela para os dois ao mesmo tempo: os trechos não são independentes e o produto fica abaixo do simulado. Sem a política de retorno parcial, qualquer falha numa linha tira a linha inteira do caminho.
- Com a rota alternativa, a viagem só fica sem caminho quando nenhum caminho está livre (paralelo). A escolha supõe que a pessoa sabe quanto vai durar cada interrupção: é o limite otimista da política.
- O atraso médio é puxado pelas poucas saídas que pegam uma interrupção longa: a amostra de durações da STM tem paradas de horas.
- Não entram ônibus de substituição, caminhada até a plataforma nem lotação.

Tempo de execução nesta máquina: 0,8 min (um processo).
