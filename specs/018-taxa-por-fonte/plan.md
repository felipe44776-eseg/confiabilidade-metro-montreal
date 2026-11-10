# 018 — Taxa, renovação e duração por fonte: plano

## Método

| Peça | Como funciona | Arquivo |
|---|---|---|
| Parcela da frota | Km real diário por linha × frota (`Type matériel`) do arquivo de 2026-10-23. Se faltar medida, a parcela da Verde é deduzida das falhas por frota, com as taxas das linhas de frota única | `pipeline/exposicao.py` → `dados/derivados/exposicao/frota_diaria.csv` |
| Painel | Uma linha por linha × dia × hora, com `y_<fonte>` e `y_MR`/`y_EF` (família) mantidos | `pipeline/modelo_taxa.py` (`monta_painel`) |
| MR empilhado | Linhas linha × dia × hora × frota (só onde a parcela é maior que 0); deslocamento log(trens-hora × parcela); covariáveis da spec 005 mais frota e frota × linha; referência laranja/MPM-10 | `modelo_taxa.py` |
| EF por fonte | Uma binomial negativa por fonte com 400 falhas ou mais; reduzido abaixo disso (linha, faixa, ano; clima da família como deslocamento) | `modelo_taxa.py` |
| Bootstrap | Índices de semana sorteados uma vez (semente 20261021, B = 200) e passados a todas as fontes | `modelo_taxa.py` |
| Fora da amostra | Para cada ano de 2019 a 2025: ajusta sem ele e mede observado ÷ esperado por linha no ano deixado de fora, v1.1.0 e novo | `pipeline/diagnostico_taxa.py` |
| Renovação e duração | Reescala por linha × fonte com o μ do modelo da fonte; forma da Weibull; massa em zero e amostra das durações (regra da 017); herança abaixo de 30 | `pipeline/distribuicoes.py` |
| β | Denominador da família de cada evento | `distribuicoes.py` |
| Contrato v2 | `versao: 2`; `fontes[]`; `frota_por_linha`; `SCRIPTS_DO_CONTRATO` com `normaliza.py`, `exposicao.py`, `duracao.py` | `pipeline/parametros.py`, `contratos/parametros.schema.json` |
| Pré-registro v2 | Congela os vetores do bootstrap e as amostras por fonte; o avaliador soma as fontes por família | `pipeline/preregistro.py` |

## Escolhas

- **MR num modelo só.** Com uma regressão por frota, a referência laranja não existe no MR-73, e a razão entre frotas sairia de dois modelos. Empilhar dá a razão com o mesmo clima e o mesmo IC pareado.
- **EF em trens-hora.** As horas de serviço só diferem dos trens-hora dentro de cada linha × faixa × tipo de dia. A comparação ficaria dominada pelas greves, então a exposição da D17 continua.
- **Herança do clima no modelo reduzido.** Uma fonte com 142 falhas não sustenta 41 termos. O clima vem da família, que tem milhares.
