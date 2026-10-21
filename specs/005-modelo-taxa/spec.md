# 005 — Modelo da taxa horária de falha

**Status:** implementada
**Fase:** F2 (semanas 3 a 5)
**Depende de:** 001, 003, 004

## Pergunta de engenharia
Quanto a taxa de falha de cada linha muda com a hora do dia, o clima, a frota e os eventos, medida por unidade de exposição? O número que responde é o multiplicador de cada fator, com intervalo de confiança de 95%.

## Contexto
- 8.530 falhas técnicas de uma linha, de 2019-01-01 a 2026-06-30: 3.982 de material rodante e 4.548 de equipamentos fixos (FONTES.md).
- O painel atual mostra padrões sem controle de fatores: picos de falha na abertura e nos horários de ponta; taxa de material rodante maior no fim do inverno (8,8 por milhão de km-carro em fevereiro) e menor em outubro (4,4); mais alta em dias abaixo de 10 °C.
- A frota pesa muito: o MR-73 roda cerca de 60.595 km-carro por falha e o MPM-10 cerca de 372.008 (2019 a 2023-09).
- O tempo entre falhas tem coeficiente de variação entre 1,44 e 1,71 por linha: as falhas vêm agrupadas, o que sugere sobredispersão.

## Critérios de aceite
- Dada a contagem de falhas por linha, hora e causa, com a exposição da spec 004, quando os modelos são ajustados, então são comparados um modelo de Poisson e um binomial negativo, ambos com a exposição como deslocamento, por AIC e por teste de razão de verossimilhança do parâmetro de dispersão.
- Dado o modelo escolhido, quando os multiplicadores são estimados, então cada um tem intervalo de confiança de 95% obtido por bootstrap em blocos semanais, para respeitar a dependência entre horas vizinhas.
- Dado o modelo escolhido, quando os resíduos são examinados, então o relatório traz resíduos quantílicos e um gráfico de contagens observadas contra esperadas por faixa.
- Dadas as causas material rodante e equipamentos fixos, quando modeladas em separado, então o relatório responde se frio e horário de ponta elevam mais a primeira que a segunda.
- Dadas as greves, quando entram no modelo, então atuam pela exposição reduzida, e o relatório mostra que a taxa por exposição não muda só por causa delas.
- Dado cada parâmetro publicado, quando vai para o simulador, então leva valor, intervalo, número de observações, método, fontes e status.

## Resultado (2026-10-21)

Scripts `pipeline/modelo_taxa.py` e `pipeline/diagnostico_taxa.py`; testes em `pipeline/tests/test_modelos.py`; relatórios [`modelo_taxa.md`](../../fontes/verificacao/modelo_taxa.md) e [`modelo_taxa_por_faixa.md`](../../fontes/verificacao/modelo_taxa_por_faixa.md).

| Critério | Resultado |
|---|---|
| Poisson contra binomial negativa, com a exposição como deslocamento, por AIC e razão de verossimilhança | **Atende**: binomial negativa nas duas causas (MR: α = 1,83, p = 3,6e-33; EF: α = 5,47, p = 4,4e-206) |
| IC 95% por bootstrap em blocos semanais | **Atende**: B = 200, mesmas semanas para as duas causas |
| Resíduos quantílicos e observado contra esperado | **Atende**: média 0,000 e desvio 1,00 nas duas causas; rootograma; por faixa do dia, observado/esperado entre 0,98 e 1,01, exceto EF na abertura (0,91) |
| Frio e ponta elevam mais MR que EF? | **Respondido**: pico da tarde eleva mais o material rodante (razão 1,39; IC 1,22–1,66); abertura eleva mais os equipamentos fixos (0,74; 0,63–0,89); pico da manhã e frio sem diferença detectável |
| Greves só pela exposição | **Atende**: multiplicador da taxa por trem-hora em dia de greve com IC contendo 1 (MR 1,17; 0,56–2,24 e EF 1,11; 0,52–1,73) |
| Parâmetro com valor, IC, n, método, fontes e status | **Atende**: `dados/derivados/simulador/parametros.json` (contrato `contratos/parametros.schema.json`) |

Achados: mais de 10 cm de neve no solo eleva as duas causas em cerca de 37%; 25 °C ou mais eleva os equipamentos fixos em 83%; uma falha na hora anterior dobra (MR) ou quase triplica (EF) a taxa na hora seguinte, sinal do agrupamento tratado na spec 006. O ajuste direto do `statsmodels.discrete.NegativeBinomial` não convergiu; o α vem de verossimilhança perfilada (plan.md).

## Fora de escopo
- Modelos de aprendizado de máquina sem interpretação de cada fator.
- Previsão para datas futuras: o backtest fica na spec 012.

## Riscos e dependências
- Depois de 2023-09 a exposição é estimada (spec 004). O modelo deve ser ajustado também só no período com km real, e as duas versões comparadas.
- Fatores correlacionados (inverno, neve e frio) podem dividir o efeito entre si. O relatório deve mostrar a correlação entre eles.

## Perguntas em aberto
- A taxa da hora seguinte depende de ter havido falha na hora anterior? Se sim, entra um termo de defasagem.
- O modo de condução manual (CMC) muda a taxa? Só se o significado do código for confirmado.
