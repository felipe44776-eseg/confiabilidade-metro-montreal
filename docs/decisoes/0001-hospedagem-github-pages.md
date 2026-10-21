# ADR 0001 — Hospedagem no GitHub Pages, com simulação no navegador

**Data:** 2026-10-21
**Status:** aceita

## Contexto

O projeto precisa publicar um painel, um mapa e um simulador interativo do metrô de Montreal: trens animados no traçado real, falhas sorteadas de distribuições ajustadas, parâmetros alteráveis e Monte Carlo com milhares de rodadas. O repositório público `felipe44776-eseg/confiabilidade-metro-montreal` já servia o painel pelo GitHub Pages.

A pergunta era se tudo cabe num site estático ou se é preciso servidor. A pesquisa de viabilidade de 2026-10-20 respondeu com base na documentação oficial de cada serviço.

## Decisão

Todo o site fica no GitHub Pages, publicado por GitHub Actions. A simulação roda no navegador, com motor próprio de eventos discretos em TypeScript e Monte Carlo em processos paralelos do navegador. Python fica para o tratamento dos dados e o ajuste das distribuições, que geram arquivos de parâmetros versionados. Cenários são compartilhados pelo link, sem servidor.

## Alternativas consideradas

| Arquitetura | Custo | Tempo real | Compartilhar cenário | Complexidade |
|---|---|---|---|---|
| Pages 100% estático | 0 | não | pelo link | baixa |
| **Pages + rotina agendada no Actions** (escolhida) | 0 | atualização periódica | pelo link | baixa |
| Pages + Cloudflare Worker (proxy) | 0 na cota grátis | sim | banco do Worker | média |
| Servidor próprio rodando Python | servidor pago | sim | sim | alta |

- **Python no navegador (Pyodide):** descartado. A pesquisa achou 6,4 MB na primeira carga, 4 a 5 s para iniciar e 3 a 5 vezes mais lento que Python nativo, sem threads.
- **Servidor:** só seria necessário para dados em tempo real com chave de API da STM, ou para guardar cenários de vários usuários.

## Consequências

- Custo zero. Limites do Pages: 1 GB de site, 100 GB por mês de banda (limite suave), 100 MB por arquivo no git.
- O processamento pesado roda no computador de quem abre a página. A estimativa de 10 a 30 s para 5.000 rodadas precisa ser medida (spec 009).
- Uma rotina agendada fica desativada após 60 dias sem atividade no repositório.
- Os dados brutos grandes ficam fora do git, numa Release com hash no manifesto.
- O Pages não permite cabeçalhos personalizados; o projeto não depende deles.

## Evidências

- **Leitura parcial de arquivo no Pages**, testada em 2026-10-21 contra o site publicado:
  - GET com `Range: bytes=0-99` devolveu **HTTP 206**, com `Content-Range: bytes 0-99/479737`. Mapas em PMTiles hospedados no próprio Pages são viáveis.
  - HEAD com o mesmo cabeçalho devolveu 200; por isso o teste vale com GET.
- **Versões fixadas**, escolhidas com pelo menos duas semanas de publicação: maplibre-gl 6.11.2, vite 8.3.2, typescript 6.0.3, vitest 5.0.3, @types/node 22.20.5.
- **Actions**, consultadas na API do GitHub em 2026-10-21: `actions/checkout` v7, `actions/setup-python` v7, `actions/setup-node` v7, `actions/configure-pages` v6, `actions/upload-pages-artifact` v5, `actions/deploy-pages` v5.
- **npm:** o `npm install` exigiu `legacy-peer-deps=true` (arquivo `app/.npmrc`). Sem isso, o npm 10.9.4 falhou com "Cannot read properties of null (reading 'edgesOut')" ao resolver dependências opcionais do vitest.
- **Referências da pesquisa:**
  - limites do Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
  - publicação por Actions: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
  - rotinas agendadas: https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows
  - mapa de fundo OpenFreeMap: https://openfreemap.org/
  - PMTiles: https://docs.protomaps.com/pmtiles/cloud-storage
  - animação de trajetos: https://deck.gl/docs/api-reference/geo-layers/trips-layer
  - Pyodide: https://pyodide.org/en/stable/project/roadmap.html
  - Cloudflare Workers: https://developers.cloudflare.com/workers/platform/limits/
