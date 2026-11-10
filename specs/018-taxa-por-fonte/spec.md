# 018 — Taxa, renovação e duração por fonte de falha

**Status:** especificada
**Fase:** revisão de 2026-11
**Depende de:** 003, 004, 017
**Revisa:** 004 (exposição), 005 (modelo da taxa), 006 (tempo entre falhas, duração e causa comum)
**Origem:** reunião de 2026-10-27 ("fabricantes são diferentes?", "variável do trem e do equipamento de via", "regressão binomial negativa", "separar trem, linha etc. como sistemas separados") e revalidação de 2026-11-10 (decisões D56 e D57)

## Pergunta de engenharia

Quanto cada frota e cada setor do equipamento fixo contribui para a taxa de falha de cada linha, e os multiplicadores de hora, clima e eventos são os mesmos para todas as fontes ou vêm de uma só?

## Contexto

- **Frota confundida com a linha.** O modelo da spec 005 tem a linha como covariável e não tem a frota. A Laranja é quase só MPM-10; a Amarela e a Azul, só MR-73; a Verde tem as duas.
  - Na Verde, com o mesmo trilho, o MR-73 falha 8,1 vezes mais por km-carro que o MPM-10 (IC 6,95–9,54; 2019 a 2023-09).
  - O MPM-10 foi de 39% (2019) a 79% (2021–22) dos km da Verde.
  - Observado ÷ esperado do modelo na Verde: 1,17 em 2019 e de 0,87 a 0,95 depois.
  - Depois de 2023-09, a parcela da frota era suposta igual à do último ano medido. O ano-base do simulador, 2025, cai nesse período.
- **EF mistura setores com perfis diferentes.** Exemplos:
  - 30% das falhas de "Service TCPE" (energia, por dedução) acontecem às 5 h, contra 5% a 9% nos outros setores;
  - o surto de 2024 é só da via com sintoma de material rodante.
- **β da causa comum.** O denominador somava MR e EF, mas 40 dos 45 eventos são de equipamentos fixos.
- **Dado novo.** A STM republicou o km real em 2026-10-23 (Release `dados-2026-11`), o que pode estender a exposição e a parcela da frota medidas para depois de 2023-09.

## Critérios de aceite

- **Exposição por frota:** dado o km real diário por frota, quando a exposição é montada, então cada linha × dia tem a parcela medida de cada frota, até o fim do arquivo.
  - Onde não houver medida, a parcela da Verde é deduzida das falhas rotuladas por frota, com as taxas de cada frota tiradas das linhas de frota única, e leva status "deduzido" e IC.
  - A distribuição igual da parcela entre as horas é hipótese, testada pela mistura de frotas por faixa do dia nas falhas da Verde.
- **Modelo do material rodante:** dado o painel por linha × dia × hora × frota, com deslocamento log(trens-hora × parcela), quando ajustado, então:
  - a razão MR-73 ÷ MPM-10 na Verde sai com IC 95%;
  - um teste de razão de verossimilhança diz se a linha ainda pesa dentro de cada frota;
  - a referência é por fonte, e só há taxa-base onde a parcela é maior que zero.
- **Modelos dos equipamentos fixos:**
  - Dada cada fonte fixa com 400 falhas ou mais no painel, quando ajustada, então tem binomial negativa própria, com as covariáveis da spec 005.
  - Abaixo disso, o modelo é reduzido: linha, faixa do dia e ano, com o efeito do clima e dos eventos da família como deslocamento (réplica b com réplica b do bootstrap).
  - A exposição continua trens-hora (D17). Horas de serviço entram como sensibilidade.
- **Binomial negativa contra Poisson:** dada cada fonte com modelo próprio, quando ajustada, então a comparação por AIC e razão de verossimilhança do α é publicada, como na spec 005.
- **IC pareado entre fontes:** dado o bootstrap em blocos semanais, quando roda, então as mesmas semanas sorteadas valem para todas as fontes, e as razões entre fontes têm IC.
- **Melhora fora da amostra:** dado o modelo v1.1.0 e o novo, quando comparados por AIC e deixando um ano de fora de cada vez, então o relatório mostra o desvio do log(observado ÷ esperado) por linha e ano no ano deixado de fora, nas duas versões.
- **De onde vem cada efeito:** dados os multiplicadores por fonte, quando publicados, então o relatório responde de quais fontes vêm a abertura, o calor de 25 °C ou mais e a neve no solo. A falha de energia na abertura é lida como probabilidade por abertura do serviço.
- **Renovação e duração por fonte:** dadas as fontes, quando ajustadas, então cada linha × fonte tem a forma da renovação no tempo reescalado e a duração (massa em zero e amostra). Estrato com menos de 30 falhas herda da mesma fonte na rede.
- **Causa comum:** dados os 45 eventos, quando o β é calculado, então o denominador é o da família (trem ou fixo) de cada evento.
- **Contrato v2:** dado o `parametros.json`, quando gerado, então traz a lista de fontes por linha com base já multiplicada pela parcela, multiplicadores, renovação, duração, locais e a parcela da frota com status. Cada parâmetro leva valor, IC, n, método, fontes e status.
- **Pré-registro:** dado o modelo novo, quando pronto, então suas previsões para os meses depois do retrato ficam congeladas e commitadas (spec 020) antes de qualquer download de incidentes novos.

## Fora de escopo

- Modelo da gravidade em função do clima (logística de 5 min ou mais).
- β por setor: com 45 eventos, o intervalo não serve.
- Modo de condução manual (CMC): só há exposição no km real até 2023-09. Fica como pergunta aberta da 005.

## Riscos e dependências

- Fontes pequenas (`aux_stations`, `tcpe`, `mr_outros`) têm intervalos largos. O modelo reduzido evita multiplicadores sem sentido.
- A soma de fontes independentes agrupa menos que o total observado. O critério de dispersão fica na spec 019.
- Os critérios comparam versões fora da amostra porque, na própria amostra, mais parâmetros sempre se ajustam melhor.
