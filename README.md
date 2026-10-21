# Confiabilidade do Metrô de Montreal

Projeto da disciplina Sistemas Tolerantes a Falhas (Engenharia de Produção, ESEG, 2026). Mede a confiabilidade das quatro linhas do metrô de Montreal com dados públicos reais e está construindo um simulador espacial de tolerância a falhas.

**Equipe** (Engenharia de Produção): Ana Paula Duanetti, Felipe Marins, Lorena Feitosa de Freitas e Sophia Braz.

| Página | Endereço |
|---|---|
| Painel de confiabilidade | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/ |
| Mapa das linhas e dos locais de falha | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/mapa/ |
| Fontes e verificação automática | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/fontes/ |
| Especificações (SDD) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/specs/ |
| Simulador | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/simulador/ |
| Relatório do trabalho | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/relatorio/ |
| Apresentação | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/apresentacao/ |
| Registro de decisões | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/decisoes/ |
| Guia do simulador | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/docs/guia/ |
| Arquitetura e manutenção | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/docs/arquitetura/ |
| Versão congelada v1.0.0 | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/versoes/v1.0.0/ |

## Documentação

| Documento | Para quem | Arquivo |
|---|---|---|
| Relatório acadêmico | professor e turma | [`docs/relatorio/relatorio.md`](docs/relatorio/relatorio.md) |
| Apresentação (deck HTML) | apresentação em aula | [`docs/apresentacao/index.html`](docs/apresentacao/index.html) |
| Registro de decisões, com motivo e alternativas | quem quer saber por que | [`docs/decisoes/registro_de_decisoes.md`](docs/decisoes/registro_de_decisoes.md) |
| Guia do simulador | quem vai usar a página | [`docs/guia_simulador.md`](docs/guia_simulador.md) |
| Arquitetura e manutenção | quem vai mexer no código | [`docs/arquitetura.md`](docs/arquitetura.md) |
| Dicionário de dados | quem vai usar as tabelas | [`docs/dicionario_dados.md`](docs/dicionario_dados.md) |
| Fontes e rastreabilidade | quem duvida de um número | [`fontes/FONTES.md`](fontes/FONTES.md) |
| Agente crítico (Claude Code) | revisão antes de entregar | [`.claude/agents/critico-stf.md`](.claude/agents/critico-stf.md) |

## Por que confiar nos números

Cada número publicado pode ser refeito por qualquer pessoa, sem confiar em quem o calculou:

- [`fontes/FONTES.md`](fontes/FONTES.md) lista cada fonte com link, licença e SHA-256, as APIs acessadas e de onde sai cada número.
- As Releases [`dados-2026-10-20`](https://github.com/felipe44776-eseg/confiabilidade-metro-montreal/releases/tag/dados-2026-10-20) e [`dados-2026-10-21`](https://github.com/felipe44776-eseg/confiabilidade-metro-montreal/releases/tag/dados-2026-10-21) guardam a cópia exata dos dados brutos.
- `pipeline/verifica_fontes.py` confere os hashes e recalcula os números com código próprio, independente do pipeline.
- Cada publicação do site roda essa verificação, e um erro impede a publicação.
- Uma auditoria independente refez os números e não encontrou divergência.

```bash
python -I pipeline/verifica_fontes.py --baixa-release --recalcula
```

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `specs/` | Especificações SDD: ciclo, princípios e uma pasta por parte do projeto (000 a 015) |
| `fontes/` | Documentação das fontes, manifesto de hashes e relatórios de verificação e validação (`fontes/verificacao/`) |
| `pipeline/` | Python: verificação independente, normalização, geografia, exposição, clima, modelos, parâmetros e backtest; testes em `pipeline/tests/` |
| `contratos/` | Contrato entre o pipeline e o simulador (`parametros.schema.json`) |
| `dados/derivados/` | Tabelas, GeoJSON e parâmetros gerados pelo pipeline (versionados) |
| `dados/manuais/` | Tabelas montadas à mão, com uma URL por linha (greves de 2025, linhas candidatas) |
| `dados/brutos/` | Dados brutos, fora do git: baixe com `--baixa-release` e `--baixa-origem` |
| `painel/` | Painel de confiabilidade (página única com d3) |
| `app/` | Mapa e simulador em TypeScript + Vite: motor por eventos discretos (`src/motor/`), Monte Carlo em Web Workers (`src/mc/`), testes (`tests/`) e relatórios com os dados reais (`relatorios/`) |
| `publicacao/` | Montagem do site publicado |
| `docs/` | Decisões de arquitetura, dicionário de dados, equipe e relatório acadêmico |

## Reproduzir tudo

Requisitos: Python 3.11 e Node 22. O workflow `.github/workflows/reproduz.yml` faz o mesmo numa máquina limpa e compara o resultado com os arquivos publicados.

```bash
python -I pipeline/verifica_fontes.py --baixa-release --baixa-origem --completo   # dados brutos com hashes conferidos
python -m pip install -r pipeline/requirements.txt                                 # versões fixadas
python -I pipeline/extrai_gtfs_metro.py dados/brutos/gtfs/gtfs_stm_mdb-2126_latest.zip
python -I pipeline/extrai_mobilidade.py dados/brutos/google/google_Region_Mobility_Report_CSVs.zip
for s in monta_painel analise_confiabilidade geo_base normaliza exposicao baixa_clima_eventos clima_eventos \
         horario_simulador candidatas modelo_taxa diagnostico_taxa distribuicoes parametros backtest; do python -I pipeline/$s.py; done
python -m pytest pipeline/tests -q
cd app && npm ci && npm test && npx vitest run --config vitest.relatorios.config.ts && npm run build && cd ..
python -I publicacao/monta_site.py                                                  # site completo em _site/
```

Os ajustes com bootstrap (`modelo_taxa`, `distribuicoes`, `backtest`) levam de 10 a 40 minutos cada. Rode um de cada vez: juntos, passam de 4 GB de memória.

## Dados e licenças

- **Incidentes, quilometragem e GTFS:** Société de transport de Montréal (STM), dados abertos, CC BY 4.0.
- **Clima:** Environment and Climate Change Canada, Licença de Governo Aberto do Canadá.
- **Traçado das linhas:** © colaboradores do OpenStreetMap, ODbL. O arquivo derivado `dados/derivados/geo/linhas.geojson` também é ODbL.
- **Coordenadas de referência:** Wikidata, CC0.
- **Mobilidade:** Google LLC, COVID-19 Community Mobility Reports.

Os resultados são análise própria e não representam a STM.
