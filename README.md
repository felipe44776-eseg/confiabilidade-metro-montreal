# Confiabilidade do Metrô de Montreal

Projeto da disciplina Sistemas Tolerantes a Falhas (Engenharia de Produção, ESEG, 2026). Mede a confiabilidade das quatro linhas do metrô de Montreal com dados públicos reais e está construindo um simulador espacial de tolerância a falhas.

| Página | Endereço |
|---|---|
| Painel de confiabilidade | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/ |
| Mapa das linhas e dos locais de falha | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/mapa/ |
| Fontes e verificação automática | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/fontes/ |
| Especificações (SDD) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/specs/ |

## Por que confiar nos números

Cada número publicado pode ser refeito por qualquer pessoa, sem confiar em quem o calculou:

- [`fontes/FONTES.md`](fontes/FONTES.md) lista cada fonte com link, licença e SHA-256, as APIs acessadas e de onde sai cada número.
- A Release [`dados-2026-10-20`](https://github.com/felipe44776-eseg/confiabilidade-metro-montreal/releases/tag/dados-2026-10-20) guarda a cópia exata dos dados brutos.
- `pipeline/verifica_fontes.py` confere os hashes e recalcula os números com código próprio, independente do pipeline.
- Cada publicação do site roda essa verificação, e um erro impede a publicação.
- Uma auditoria independente refez os números e não encontrou divergência.

```bash
python -I pipeline/verifica_fontes.py --baixa-release --recalcula
```

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `specs/` | Especificações SDD: ciclo, princípios e uma pasta por parte do projeto |
| `fontes/` | Documentação das fontes, manifesto de hashes e relatórios de verificação |
| `pipeline/` | Python: verificação, extrações, análise de confiabilidade e base geoespacial |
| `dados/derivados/` | Tabelas e GeoJSON gerados pelo pipeline (versionados) |
| `dados/brutos/` | Dados brutos, fora do git: baixe com `--baixa-release` |
| `painel/` | Painel de confiabilidade (página única com d3) |
| `app/` | Mapa e, nas próximas fases, o simulador (TypeScript + Vite) |
| `publicacao/` | Montagem do site publicado |
| `docs/decisoes/` | Registros de decisão de arquitetura |

## Reproduzir tudo

Requisitos: Python 3.11 e Node 22.

```bash
python -I pipeline/verifica_fontes.py --baixa-release              # dados brutos da Release, com hashes conferidos
python -I pipeline/extrai_gtfs_metro.py dados/brutos/gtfs/gtfs_stm_mdb-2126_latest.zip
python -I pipeline/analise_confiabilidade.py                      # 17 tabelas do painel
python -I pipeline/geo_base.py                                    # traçado, estações, locais e validação
cd app && npm ci && npm test && npm run build && cd ..
python -I publicacao/monta_site.py                                # site completo em _site/
```

A extração da mobilidade do Google (`pipeline/extrai_mobilidade.py`) precisa do arquivo baixado da origem, que não está na Release.

## Dados e licenças

- **Incidentes, quilometragem e GTFS:** Société de transport de Montréal (STM), dados abertos, CC BY 4.0.
- **Clima:** Environment and Climate Change Canada, Licença de Governo Aberto do Canadá.
- **Traçado das linhas:** © colaboradores do OpenStreetMap, ODbL. O arquivo derivado `dados/derivados/geo/linhas.geojson` também é ODbL.
- **Coordenadas de referência:** Wikidata, CC0.
- **Mobilidade:** Google LLC, COVID-19 Community Mobility Reports.

Os resultados são análise própria e não representam a STM.
