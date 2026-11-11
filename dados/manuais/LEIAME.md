# Dados manuais

Tabelas montadas à mão a partir de fontes citadas linha a linha. Não são dados oficiais: cada linha tem `status` e `fonte`.

| Arquivo | Conteúdo | Fonte | Status |
|---|---|---|---|
| `greves_stm.csv` | Dias de greve da STM em 2025 e as janelas em que o metrô funcionou (hora do dia de operação; 25:00 = 01:00 do dia seguinte). Dia sem linha na tabela = serviço normal | Imprensa (Noovo, Time Out), URL em cada linha | imprensa |

Regras:
- **Janela vazia:** dia sem serviço.
- **Greve de horas extras:** de 11/12/2025 a 11/01/2026 o metrô manteve o horário normal, então esses dias não entram.
- **Serviço parcial fora das faixas:** a imprensa cita 50% do serviço fora das faixas em 12, 16 e 17/06/2025. Não foi modelado, porque é hipótese conservadora.

## Referências acadêmicas (PDF)

Artigos que a equipe recebeu da faculdade em 2026-11-10, para estudo. O que entrou no método está na decisão D62. Os DOIs foram conferidos no Crossref (`fontes/verificacao/referencias_crossref.json`).

- **No repositório:** só o artigo da RESS, redistribuído sem alteração sob a licença CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), com a autoria e o DOI da tabela abaixo.
- **Fora do repositório:** os quatro da IEEE, que são cópias com licença institucional, ficam só na pasta local de quem os recebeu (`.gitignore`). Baixe pelo DOI, com o acesso da faculdade.
- **Resumo de estudo:** `Resumo_5_artigos.docx` resume os cinco artigos (conceitos, fórmulas, resultados, limitações, glossário e perguntas) e liga cada um ao nosso método no capítulo 7.

| Arquivo | Referência | DOI | Direitos |
|---|---|---|---|
| `Resilience_of_Transportation_Systems_Concepts_and_Comprehensive_Review.pdf` | Zhou, Wang e Yang, IEEE Trans. Intelligent Transportation Systems, 2019 | 10.1109/TITS.2018.2883766 | © IEEE, cópia com licença institucional |
| `A_Review_of_Resilient_Transportation_Systems_in_the_Last_Five_Years.pdf` | Chen et al., ICTIS, 2023 | 10.1109/ICTIS60134.2023.10243879 | © IEEE, cópia com licença institucional |
| `Software_Safety_in_Subway_and_Air_Traffic_Control_Applications.pdf` | Almeida Jr., Camargo Jr. e Cugnasca, IEEE Latin America Transactions, 2008 | 10.1109/TLA.2008.4461639 | © IEEE, cópia com licença institucional |
| `Performability_Evaluation_of_Railway_Systems_A_Study_on_the_Impact_of_Adding_Alternative_Routes.pdf` | Marinho, Callou, Melo e Andrade, IEEE Latin America Transactions, 2023 | 10.1109/TLA.2023.10015219 | © IEEE, cópia com licença institucional |
| `Infrastructure availability and urban railway performability.pdf` | dos Santos Neto e Callou, Reliability Engineering & System Safety, 2027 (online em 2026) | 10.1016/j.ress.2026.113439 | CC BY 4.0 (acesso aberto) |
