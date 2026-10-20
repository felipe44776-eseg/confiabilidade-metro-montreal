# Confiabilidade do Metrô de Montreal

Painel de confiabilidade e tolerância a falhas das quatro linhas do metrô de Montreal, feito para a disciplina Sistemas Tolerantes a Falhas (Engenharia de Produção, ESEG, 2026).

**Página:** https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/

## O que a página mostra

- Tempo médio entre falhas (MTBF), tempo até o serviço voltar (MTTR), disponibilidade e dias sem falha por linha.
- Ajuste exponencial, Weibull e lognormal do tempo entre falhas, com a curva de confiabilidade R(t).
- Comparação das frotas MR-73 e MPM-10 em km-carro por falha.
- Falhas por hora do dia, mês, temperatura e neve; locais com mais falhas; mapa das estações.
- Linha como sistema em série, corredor Verde ∥ Laranja em paralelo com causa comum (fator β), simulação Monte Carlo e frota reserva k-de-n (Markov).

## Arquivos

| Caminho | Conteúdo |
|---|---|
| `index.html` | Página autocontida: d3 7.9.0, dados e gráficos num arquivo só |
| `dados/*.json` | As 17 tabelas calculadas que a página usa |
| `scripts/analise_confiabilidade.py` | Cálculo de todas as tabelas, em Python puro (sem bibliotecas externas) |

O script lê os dados brutos de uma pasta `dados/` com esta estrutura:

- `stm_montreal/incidents_metro.csv`: https://donneesouvertes.stm.info/fichiers/Incidents%20m%C3%A9tro.csv
- `stm_montreal/km_reel.csv`: https://donneesouvertes.stm.info/fichiers/Kilom%C3%A9trage%20r%C3%A9el.csv
- `clima_montreal/eccc_diario_AAAA.csv`: clima diário do Environment and Climate Change Canada, `stationID=51157`, de 2019 a 2026
- `mobilidade_google/google_mobilidade_montreal_2020_2022.csv`: Google COVID-19 Community Mobility Reports, região Montreal
- `gtfs_stm/metro_sequencias.csv`: sequência das estações extraída do GTFS da STM

## Fontes e licenças

- Société de transport de Montréal (STM), dados abertos, CC BY 4.0.
- Environment and Climate Change Canada, Licença de Governo Aberto do Canadá.
- Google LLC, Google COVID-19 Community Mobility Reports.

Os resultados são análise própria e não representam a STM.
