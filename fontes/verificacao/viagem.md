# Confiabilidade de uma viagem (spec 015)

Gerado por `app/relatorios/viagem.relatorio.ts` com o `parametros.json` real (código sha256-scripts:70cf9c002aa2ba0a). Cenário padrão (dia útil, condições de referência do modelo), 1.000 dias por viagem, semente 20261021: os mesmos dias da aba "Muitos dias" com essa semente. Média e intervalo de 95%.

Disponibilidade: fração da janela de serviço da rede em que o caminho existe, a partir dos bloqueios do dia no grafo das estações (o mesmo método da disponibilidade origem-destino da spec 009). "Produto" é o valor em série, multiplicando as disponibilidades dos trechos como se as linhas falhassem de forma independente. Atraso: saídas a cada 10 minutos; para cada uma, a chegada mais cedo com os trens simulados do dia contra a mesma saída num dia sem falhas.

## Angrignon → Saint-Michel

Caminho de sempre: Verde de Angrignon a Berri-Uqam, baldeação, Laranja de Berri-Uqam a Jean-Talon, baldeação, Azul de Jean-Talon a Saint-Michel.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Verde 99,54% (99,44% a 99,64%); Laranja 99,46% (99,28% a 99,63%); Azul 99,43% (99,08% a 99,77%) |
| Produto dos trechos (série) | 98,43% |
| Viagem inteira, simulada | 98,46% (98,06% a 98,86%) |
| Minutos por dia sem caminho | 18,4 (13,6 a 23,2) |
| Dias com ao menos uma interrupção no caminho | 75,2% (72,5% a 77,9%) |
| Chance de chegar mais de 5 min atrasado | 1,29% (0,84% a 1,74%) |
| Chance de chegar mais de 15 min atrasado | 0,85% (0,44% a 1,26%) |
| Chance de chegar mais de 60 min atrasado | 0,62% (0,22% a 1,01%) |
| Chance de não chegar até o fim do serviço | 0,0053% (0,0000% a 0,0142%) |
| Atraso médio por viagem (min) | 3,27 (0,87 a 5,67) |
| Com rota alternativa: viagem inteira | 98,46% (98,06% a 98,86%) |
| Com rota alternativa: chance de mais de 5 min | 1,08% (0,66% a 1,51%) |
| Com rota alternativa: atraso médio (min) | 3,17 (0,79 a 5,56) |

## Côte-Vertu → Montmorency

Caminho de sempre: Laranja de Côte-Vertu a Snowdon, baldeação, Azul de Snowdon a Jean-Talon, baldeação, Laranja de Jean-Talon a Montmorency.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Laranja 99,46% (99,28% a 99,63%); Azul 99,43% (99,08% a 99,77%); Laranja 99,46% (99,28% a 99,63%) |
| Produto dos trechos (série) | 98,35% |
| Viagem inteira, simulada | 98,90% (98,51% a 99,29%) |
| Minutos por dia sem caminho | 13,2 (8,5 a 17,8) |
| Dias com ao menos uma interrupção no caminho | 54,6% (51,5% a 57,7%) |
| Chance de chegar mais de 5 min atrasado | 0,71% (0,45% a 0,96%) |
| Chance de chegar mais de 15 min atrasado | 0,37% (0,18% a 0,56%) |
| Chance de chegar mais de 60 min atrasado | 0,17% (0,01% a 0,33%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,60 (0,00 a 1,29) |
| Com rota alternativa: viagem inteira | 99,46% (99,28% a 99,63%) |
| Com rota alternativa: chance de mais de 5 min | 0,71% (0,45% a 0,96%) |
| Com rota alternativa: atraso médio (min) | 0,60 (0,00 a 1,29) |

## Longueuil- U. De Sherbrooke → Snowdon

Caminho de sempre: Amarela de Longueuil- U. De Sherbrooke a Berri-Uqam, baldeação, Laranja de Berri-Uqam a Snowdon.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Amarela 99,90% (99,87% a 99,93%); Laranja 99,46% (99,28% a 99,63%) |
| Produto dos trechos (série) | 99,36% |
| Viagem inteira, simulada | 99,36% (99,18% a 99,54%) |
| Minutos por dia sem caminho | 7,6 (5,5 a 9,8) |
| Dias com ao menos uma interrupção no caminho | 45,8% (42,7% a 48,9%) |
| Chance de chegar mais de 5 min atrasado | 0,78% (0,57% a 0,98%) |
| Chance de chegar mais de 15 min atrasado | 0,33% (0,16% a 0,51%) |
| Chance de chegar mais de 60 min atrasado | 0,16% (0,01% a 0,32%) |
| Chance de não chegar até o fim do serviço | 0,0009% (0,0000% a 0,0026%) |
| Atraso médio por viagem (min) | 0,59 (0,00 a 1,27) |
| Com rota alternativa: viagem inteira | 99,36% (99,18% a 99,54%) |
| Com rota alternativa: chance de mais de 5 min | 0,76% (0,56% a 0,97%) |
| Com rota alternativa: atraso médio (min) | 0,54 (0,00 a 1,15) |

## Lionel-Groulx → Berri-Uqam

Caminho de sempre: Verde de Lionel-Groulx a Berri-Uqam.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Verde 99,54% (99,44% a 99,64%) |
| Produto dos trechos (série) | 99,54% |
| Viagem inteira, simulada | 99,54% (99,44% a 99,64%) |
| Minutos por dia sem caminho | 5,5 (4,3 a 6,7) |
| Dias com ao menos uma interrupção no caminho | 45,2% (42,1% a 48,3%) |
| Chance de chegar mais de 5 min atrasado | 0,22% (0,11% a 0,34%) |
| Chance de chegar mais de 15 min atrasado | 0,14% (0,05% a 0,23%) |
| Chance de chegar mais de 60 min atrasado | 0,06% (0,00% a 0,13%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,15 (0,00 a 0,33) |
| Com rota alternativa: viagem inteira | 99,98% (99,97% a 100,00%) |
| Com rota alternativa: chance de mais de 5 min | 0,02% (0,00% a 0,04%) |
| Com rota alternativa: atraso médio (min) | 0,01 (0,01 a 0,02) |

## Atwater → Berri-Uqam

Caminho de sempre: Verde de Atwater a Berri-Uqam.

| Medida | Valor (IC 95%) |
|---|---|
| Trechos | Verde 99,54% (99,44% a 99,64%) |
| Produto dos trechos (série) | 99,54% |
| Viagem inteira, simulada | 99,54% (99,44% a 99,64%) |
| Minutos por dia sem caminho | 5,5 (4,3 a 6,7) |
| Dias com ao menos uma interrupção no caminho | 45,2% (42,1% a 48,3%) |
| Chance de chegar mais de 5 min atrasado | 0,22% (0,11% a 0,33%) |
| Chance de chegar mais de 15 min atrasado | 0,13% (0,05% a 0,22%) |
| Chance de chegar mais de 60 min atrasado | 0,06% (0,00% a 0,13%) |
| Chance de não chegar até o fim do serviço | 0,0000% (0,0000% a 0,0000%) |
| Atraso médio por viagem (min) | 0,15 (0,00 a 0,32) |
| Com rota alternativa: viagem inteira | 99,54% (99,44% a 99,64%) |
| Com rota alternativa: chance de mais de 5 min | 0,22% (0,11% a 0,33%) |
| Com rota alternativa: atraso médio (min) | 0,14 (0,00 a 0,30) |

## Como ler

- Se o produto dos trechos cai dentro do intervalo do simulado, as linhas do caminho falham quase de forma independente: a viagem é um sistema em série.
- Quando a mesma linha aparece em dois trechos (Côte-Vertu → Montmorency usa a Laranja duas vezes), uma falha nela para os dois ao mesmo tempo: os trechos não são independentes e o produto fica abaixo do simulado. Sem a política de retorno parcial, qualquer falha numa linha tira a linha inteira do caminho.
- Com a rota alternativa, a viagem só fica sem caminho quando nenhum caminho está livre (paralelo). A escolha supõe que a pessoa sabe quanto vai durar cada interrupção: é o limite otimista da política.
- O atraso médio é puxado pelas poucas saídas que pegam uma interrupção longa: a amostra de durações da STM tem paradas de horas.
- Não entram ônibus de substituição, caminhada até a plataforma nem lotação.

Tempo de execução nesta máquina: 1,2 min (um processo).
