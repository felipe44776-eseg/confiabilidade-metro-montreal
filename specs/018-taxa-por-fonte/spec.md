# 018 — Taxa, renovação e duração por fonte de falha

**Status:** implementada com exceções
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
  - *Mudança registrada em 2026-11-10, ao implementar, antes dos resultados finais:*
    - no modelo reduzido, o efeito do ano também vem da família, porque com poucas falhas por ano o efeito próprio não se estima;
    - abaixo de 100 falhas no painel, só a linha entra (é o caso de `mr_outros`, com 40).
    - Contagem no painel, que exclui as horas sem serviço programado: `aux_stations` 388 e `tcpe` 132 ficaram reduzidas.
- **Binomial negativa contra Poisson:** dada cada fonte com modelo próprio, quando ajustada, então a comparação por AIC e razão de verossimilhança do α é publicada, como na spec 005.
- **IC pareado entre fontes:** dado o bootstrap em blocos semanais, quando roda, então as mesmas semanas sorteadas valem para todas as fontes, e as razões entre fontes têm IC.
- **Melhora fora da amostra:** dado o modelo v1.1.0 e o novo, quando comparados por AIC e deixando um ano de fora de cada vez, então o relatório mostra o desvio do log(observado ÷ esperado) por linha e ano no ano deixado de fora, nas duas versões.
- **De onde vem cada efeito:** dados os multiplicadores por fonte, quando publicados, então o relatório responde de quais fontes vêm a abertura, o calor de 25 °C ou mais e a neve no solo. A falha de energia na abertura é lida como probabilidade por abertura do serviço.
- **Renovação e duração por fonte:** dadas as fontes, quando ajustadas, então cada linha × fonte tem a forma da renovação no tempo reescalado e a duração (massa em zero e amostra). Estrato com menos de 30 falhas herda da mesma fonte na rede.
- **Causa comum:** dados os 45 eventos, quando o β é calculado, então o denominador é o da família (trem ou fixo) de cada evento.
- **Contrato v2:** dado o `parametros.json`, quando gerado, então traz a lista de fontes por linha com base já multiplicada pela parcela, multiplicadores, renovação, duração, locais e a parcela da frota com status. Cada parâmetro leva valor, IC, n, método, fontes e status.
- **Pré-registro:** dado o modelo novo, quando pronto, então suas previsões para os meses depois do retrato ficam congeladas e commitadas (spec 020) antes de qualquer download de incidentes novos.

## Resultado (2026-11-11)

Código em `pipeline/exposicao.py` (parcela diária da frota), `pipeline/modelo_taxa.py` (MR empilhado por frota, fontes fixas, reduzidos, bootstrap com B = 200 e as mesmas semanas em todos os modelos), `pipeline/diagnostico_taxa.py` (mistura de frotas por faixa), `pipeline/fora_da_amostra.py`, `pipeline/distribuicoes.py` e `pipeline/parametros.py` (contrato v2). Relatórios: [`taxa_por_fonte.md`](../../fontes/verificacao/taxa_por_fonte.md), [`fora_da_amostra.md`](../../fontes/verificacao/fora_da_amostra.md), [`modelo_taxa_por_faixa.md`](../../fontes/verificacao/modelo_taxa_por_faixa.md) e [`distribuicoes.md`](../../fontes/verificacao/distribuicoes.md).

| Critério | Resultado |
|---|---|
| Exposição por frota, medida até o fim do arquivo | **Atende**: parcela diária de cada frota pelo km real até 2026-06 (`frota_diaria.csv`). A dedução pelas falhas rotuladas não foi necessária: nenhum mês ficou sem medida |
| Parcela igual entre as horas (hipótese), testada pela mistura de frotas por faixa nas falhas da Verde | **Exceção**: a hipótese é rejeitada (qui-quadrado 58,2 com 5 graus de liberdade, p = 2,8e-11). A fração do MR-73 nas falhas das duas frotas é 0,85 e 0,87 nos picos, contra 0,80 prevista, e 0,58 a 0,66 na abertura, à noite e no fim do serviço, contra 0,78 a 0,80: o MR-73 roda mais nos picos. O km real da STM é diário, então a parcela por hora não se mede; a razão entre as frotas fica com essa ressalva |
| Razão MR-73 ÷ MPM-10 na Verde com IC 95% | **Atende**: 8,89 (6,61–11,23) por trem-hora da frota em 2025; entre os anos, de 6,06 (2020) a 15,54 (2022) |
| A linha ainda pesa dentro de cada frota? | **Atende** (a pergunta tem resposta): sim. Razão de verossimilhança 131,5 com 3 graus de liberdade, p = 2,5e-28. Por trem-hora da frota em 2025, nas condições de referência: MR-73 0,0046 na Verde, 0,0044 na Amarela e 0,0031 na Azul; MPM-10 0,00052 na Verde e 0,00078 na Laranja |
| Referência por fonte; taxa-base só onde a parcela é maior que zero | **Atende**: nenhuma falha de frota ficou sem exposição da frota no dia ou no mês |
| Modelos dos equipamentos fixos | **Atende**: modelo próprio em `aux_trains_sintoma_fixo` (1.500 falhas no painel), `voie_sintoma_fixo` (924), `voie_sintoma_trem` (785) e `aux_trains_sintoma_trem` (694); reduzido em `aux_stations` (388) e `tcpe` (132); `mr_outros` (40), só a linha |
| Horas de serviço como sensibilidade da exposição dos equipamentos fixos | **Não feita nesta rodada**: fica como tarefa aberta. A exposição continua trens-hora (D17) |
| Binomial negativa contra Poisson por fonte | **Atende**: a binomial negativa vence nas quatro fontes com modelo próprio (α de 2,85 a 19,99) e no MR empilhado (α = 2,03; p = 8,7e-34). O α de `aux_trains_sintoma_trem` (19,99) e o de `voie_sintoma_trem` (15,70) ficam perto do teto da busca (20): são as fontes mais em rajadas. Nas três reduzidas, a Poisson tem AIC menor |
| IC pareado entre fontes | **Atende**: as mesmas semanas sorteadas em todos os modelos (`vetores_bootstrap.json.gz`), B = 200 |
| Melhora fora da amostra (um ano de fora, v1.1.0 contra por fonte) | **Atende**: a raiz do erro quadrático do log(observado ÷ esperado) por linha e ano cai de 0,308 para 0,247 no material rodante e de 0,646 para 0,589 nos equipamentos fixos (28 casos em cada). Onde a frota mudou, o ganho é grande: na Verde, material rodante, 2019 vai de 2,04 para 0,94 e 2024–2025 de 0,67–0,69 para 1,04–1,05. Nenhum dos dois prevê a Amarela de 2024 nos equipamentos fixos (7,9 e 9,2): é o surto de registros de terminal |
| De onde vem cada efeito | **Atende**: a abertura eleva todas as fontes (3,1 a 3,8 nas fixas com modelo próprio; 2,64 no material rodante); na TCPE, 8,5 (5,4–13,7), lido como probabilidade de falha por abertura do serviço, ao energizar a rede (dedução). O calor de 25 °C ou mais vem da via (2,23 e 2,70) e do "Service aux trains" com sintoma fixo (1,39); no material rodante não há efeito (1,08; 0,84–1,36). A neve no solo acima de 10 cm pesa no material rodante (1,31; 1,02–1,62); em cada fonte fixa o intervalo contém 1, e só a família (1,37) o separa de 1 |
| Renovação e duração por fonte | **Atende**: 32 estratos linha × fonte. Renovação própria em 25, herdada da rede em 7; duração própria em 17, herdada em 15 (na renovação, estratos com menos de 30 intervalos; na duração, com menos de 30 durações positivas, como `laranja · voie_sintoma_trem`, com 351 falhas e quase todas de zero minuto). A forma da Weibull fica sempre abaixo de 1, de 0,37 (Azul, via com sintoma de trem) a 0,83 (Verde, MR-73) |
| β da causa comum pelo denominador da família | **Atende**: 40 dos 45 eventos são de equipamento fixo. Verde com Laranja nas falhas fixas: β da Verde 0,022 (0,015–0,031), contra 0,011 com o denominador de todas as falhas |
| Contrato v2 | **Atende**: 9 fontes, 32 pares linha × fonte, `frota_por_linha` com status; `codigo_commit` = SHA-256 dos scripts do contrato, que passam a incluir `normaliza.py`, `exposicao.py` e `duracao.py` |
| Pré-registro do modelo novo | Ver a spec 020 (`fontes/verificacao/preregistro/modelo_v2.json`) |

*Mudança registrada em 2026-11-10, depois de ver (D63):* com o km real medido em 2025, o multiplicador de dia de greve saiu 1,73 (material rodante) por contagem dupla da redução do serviço na exposição. O ajuste completo foi parado, a exposição dos dias de greve passou ao fator típico nas horas com serviço, e o multiplicador voltou a 1,16 (0,55–2,23), com intervalo que contém 1, como na v1.1.0.

## Fora de escopo

- Modelo da gravidade em função do clima (logística de 5 min ou mais).
- β por setor: com 45 eventos, o intervalo não serve.
- Modo de condução manual (CMC): só há exposição no km real até 2023-09. Fica como pergunta aberta da 005.

## Riscos e dependências

- Fontes pequenas (`aux_stations`, `tcpe`, `mr_outros`) têm intervalos largos. O modelo reduzido evita multiplicadores sem sentido.
- A soma de fontes independentes agrupa menos que o total observado. O critério de dispersão fica na spec 019.
- Os critérios comparam versões fora da amostra porque, na própria amostra, mais parâmetros sempre se ajustam melhor.
