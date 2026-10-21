# Dados manuais

Tabelas montadas à mão a partir de fontes citadas linha a linha. Não são dados oficiais: cada linha tem `status` e `fonte`.

| Arquivo | Conteúdo | Fonte | Status |
|---|---|---|---|
| `greves_stm.csv` | Dias de greve da STM em 2025 e as janelas em que o metrô funcionou (hora do dia de operação; 25:00 = 01:00 do dia seguinte). Dia sem linha na tabela = serviço normal | Imprensa (Noovo, Time Out), URL em cada linha | imprensa |

Regras:
- **Janela vazia:** dia sem serviço.
- **Greve de horas extras:** de 11/12/2025 a 11/01/2026 o metrô manteve o horário normal, então esses dias não entram.
- **Serviço parcial fora das faixas:** a imprensa cita 50% do serviço fora das faixas em 12, 16 e 17/06/2025. Não foi modelado, porque é hipótese conservadora.
