# 000 — Proveniência: plano

## Componentes

| Componente | Arquivo | Papel |
|---|---|---|
| Manifesto | `fontes/fontes_manifesto.json` | Para cada fonte: id, editor, licença, URL, catálogo, forma de distribuição, bytes, SHA-256, linhas e colunas. Para cada derivado: fontes de origem, script e SHA-256 |
| Verificação | `pipeline/verifica_fontes.py` | Python puro, sem dependências. Modos: integridade (padrão), `--baixa-release`, `--online`, `--recalcula`, `--gera-manifesto`. Sai com código 1 em caso de problema |
| Documentação | `fontes/FONTES.md` | Texto para pessoas: fontes, APIs acessadas, origem de cada número, auditoria, limites |
| Release | GitHub Release `dados-2026-10-20` | Cópia exata dos dados brutos com licença que permite redistribuir |
| Publicação | `.github/workflows/deploy.yml` | Baixa a Release, verifica, recalcula, monta e publica; falha impede o deploy |
| Verificação semanal | `.github/workflows/verifica-fontes.yml` | `--online` toda segunda-feira; grava o relatório datado em `fontes/verificacao/` |
| Página | `/fontes/` (gerada por `publicacao/monta_site.py`) | Tabela das fontes e saída da última verificação |

## Distribuição dos dados brutos

| Tipo | Fontes | Onde ficam |
|---|---|---|
| `release` | STM (incidentes, km real, km planejado, km orçado, GTFS), ECCC (8 anos), OSM, Wikidata | Release do GitHub |
| `origem` | Google Mobility, Nager.Date, relatórios da STM | Baixar do endereço no manifesto |
| `terceiros` | d3 7.9.0 | No repositório (`painel/vendor/`) |

Os derivados pequenos (`dados/derivados/`) ficam versionados no repositório. Os brutos ficam fora do git (`.gitignore`), porque três deles passam de 50 MB.

## Por que duas implementações

O recálculo de `verifica_fontes.py` não importa nada de `pipeline/analise_confiabilidade.py` nem de `pipeline/geo_base.py`. Se um dos dois tiver um erro, os números divergem e a publicação para.

## Pontos de falha

| Falha | Efeito | Mitigação |
|---|---|---|
| Release apagada ou alterada | Deploy falha na verificação | Hashes no manifesto; a Release não é editada, só se cria outra |
| Fonte muda na origem | Aviso semanal | Vale o snapshot; nova Release se a equipe decidir |
| Origem fora do ar | Aviso no `--online` | A cópia da Release continua válida |
| Cron desativado após 60 dias sem atividade | Verificação semanal para | O próprio commit do relatório semanal é atividade (efeito não verificado na documentação do GitHub) |
