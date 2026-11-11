# Confiabilidade do Metrô de Montreal

Projeto da disciplina Sistemas Tolerantes a Falhas (Engenharia de Produção, ESEG, 2026). Mede a confiabilidade das quatro linhas do metrô de Montreal com dados públicos reais e está construindo um simulador espacial de tolerância a falhas.

**Equipe** (Engenharia de Produção): Ana Paula Duanetti, Felipe Marins, Lorena Feitosa de Freitas e Sophia Braz.

> **Revisão de 2026-11 (após a ressegmentação).** As falhas passaram a ser separadas por frota (MR-73, MPM-10) e por setor do equipamento fixo, a duração segue a faixa oficial da STM quando a calculada pelos horários a contradiz, e a exposição é medida em todo o período (km real republicado pela STM em 2026-10-23). Specs 017 a 020; decisões D55 a D63. A versão anterior continua em [`/versoes/v1.1.0/`](https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/versoes/v1.1.0/), e cada número que mudou está em [`revisao_2026-11.md`](fontes/verificacao/revisao_2026-11.md).

| Página | Endereço |
|---|---|
| Painel de confiabilidade | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/ |
| Mapa das linhas e dos locais de falha | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/mapa/ |
| Fontes e verificação automática | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/fontes/ |
| Especificações (SDD) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/specs/ |
| Simulador | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/simulador/ |
| Relatório do trabalho | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/relatorio/ |
| Apresentação executiva (para a turma) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/apresentacao/ |
| Apresentação interna (para a equipe: tudo o que foi feito) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/apresentacao/interna.html |
| Registro de decisões | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/decisoes/ |
| Guia do simulador | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/docs/guia/ |
| Arquitetura e manutenção | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/docs/arquitetura/ |
| Versão congelada v1.0.0 | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/versoes/v1.0.0/ |
| Versão congelada v1.1.0 (antes da revisão de 2026-11) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/versoes/v1.1.0/ |
| Versão de entrega v1.2.0 (após a revisão de 2026-11) | https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/versoes/v1.2.0/ |

## Documentação

| Documento | Para quem | Arquivo |
|---|---|---|
| Relatório acadêmico | professor e turma | [`docs/relatorio/relatorio.md`](docs/relatorio/relatorio.md) |
| Apresentação executiva (deck HTML e PDF) | a turma, em aula | [`docs/apresentacao/index.html`](docs/apresentacao/index.html) |
| Apresentação interna (deck HTML e PDF) | a equipe: o projeto inteiro, com roteiro e perguntas prováveis | [`docs/apresentacao/interna.html`](docs/apresentacao/interna.html) |
| Registro de decisões, com motivo e alternativas | quem quer saber por que | [`docs/decisoes/registro_de_decisoes.md`](docs/decisoes/registro_de_decisoes.md) |
| Guia do simulador | quem vai usar a página | [`docs/guia_simulador.md`](docs/guia_simulador.md) |
| Arquitetura e manutenção | quem vai mexer no código | [`docs/arquitetura.md`](docs/arquitetura.md) |
| Dicionário de dados | quem vai usar as tabelas | [`docs/dicionario_dados.md`](docs/dicionario_dados.md) |
| Fontes e rastreabilidade | quem duvida de um número | [`fontes/FONTES.md`](fontes/FONTES.md) |
| Agente crítico (Claude Code) | revisão antes de entregar | [`.claude/agents/critico-stf.md`](.claude/agents/critico-stf.md) |

## Por que confiar nos números

Cada número publicado pode ser refeito por qualquer pessoa, sem confiar em quem o calculou:

- [`fontes/FONTES.md`](fontes/FONTES.md) lista cada fonte com link, licença e SHA-256, as APIs acessadas e de onde sai cada número.
- As Releases [`dados-2026-10-20`](https://github.com/felipe44776-eseg/confiabilidade-metro-montreal/releases/tag/dados-2026-10-20), [`dados-2026-10-21`](https://github.com/felipe44776-eseg/confiabilidade-metro-montreal/releases/tag/dados-2026-10-21) e [`dados-2026-11`](https://github.com/felipe44776-eseg/confiabilidade-metro-montreal/releases/tag/dados-2026-11) (km real republicado pela STM em 2026-10-23) guardam a cópia exata dos dados brutos.
- As previsões para os meses que a STM ainda vai publicar ficaram congeladas antes desses dados existirem (`fontes/verificacao/preregistro/`, spec 020).
- `pipeline/verifica_fontes.py` confere os hashes e recalcula os números com código próprio, independente do pipeline.
- Cada publicação do site roda essa verificação, e um erro impede a publicação.
- Uma auditoria independente refez os números e não encontrou divergência.

```bash
python -I pipeline/verifica_fontes.py --baixa-release --recalcula
```

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `specs/` | Especificações SDD: ciclo, princípios e uma pasta por parte do projeto (000 a 020) |
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

Requisitos: Python 3.11 e Node 22. O workflow `.github/workflows/reproduz.yml` faz o mesmo numa máquina limpa e compara o resultado com os arquivos publicados. Ele só roda quando disparado à mão: a última execução com sucesso é a do commit a7f0594 (2026-10-21), e a de 2026-11-01 falhou porque a API da NHL mudou a resposta (D65). Depois da revisão de 2026-11, a reprodução não foi refeita.

```bash
python -I pipeline/verifica_fontes.py --baixa-release --baixa-origem --completo   # dados brutos com hashes conferidos
python -m pip install -r pipeline/requirements.txt                                 # versões fixadas
python -I pipeline/extrai_gtfs_metro.py dados/brutos/gtfs/gtfs_stm_mdb-2126_latest.zip
python -I pipeline/extrai_mobilidade.py dados/brutos/google/google_Region_Mobility_Report_CSVs.zip
for s in monta_painel analise_confiabilidade geo_base normaliza exposicao baixa_clima_eventos clima_eventos \
         horario_simulador candidatas modelo_taxa diagnostico_taxa fora_da_amostra distribuicoes parametros backtest; do python -I pipeline/$s.py; done
python -m pytest pipeline/tests -q
cd app && npm ci && npm test && npx vitest run --config vitest.relatorios.config.ts && npm run build && cd ..
python -I publicacao/monta_site.py                                                  # site completo em _site/
python -I pipeline/compara_versoes.py                                               # números antes e depois da revisão de 2026-11
```

Os ajustes com bootstrap levam tempo: `modelo_taxa` cerca de 80 minutos (famílias e 9 fontes, B = 200), `backtest` cerca de 20 e `distribuicoes` cerca de 1 (medidos em 2026-11-11). Rode um de cada vez: juntos, passam de 4 GB de memória.

## Dados e licenças

- **Código e textos escritos pela equipe:** licença MIT ([`LICENSE`](LICENSE)). Os dados abaixo não mudam de licença por estarem aqui: cada um segue a da sua fonte.
- **Artigos de referência:** só o da RESS está no repositório (CC BY 4.0); os da IEEE ficam fora (`dados/manuais/LEIAME.md`).
- **Identidade visual das apresentações:** o logo da ESEG é marca da instituição, fora da licença MIT, usado só para identificar o trabalho da disciplina. A fonte Public Sans segue a SIL Open Font License (`docs/apresentacao/marca/LEIAME.md`).
- **Incidentes, quilometragem e GTFS:** Société de transport de Montréal (STM), dados abertos, CC BY 4.0.
- **Clima:** Environment and Climate Change Canada, Licença de Governo Aberto do Canadá.
- **Traçado das linhas:** © colaboradores do OpenStreetMap, ODbL. O arquivo derivado `dados/derivados/geo/linhas.geojson` também é ODbL.
- **Coordenadas de referência:** Wikidata, CC0.
- **Mobilidade:** Google LLC, COVID-19 Community Mobility Reports.

Os resultados são análise própria e não representam a STM.
