# 000 — Proveniência: tarefas

- [x] Inventário de todos os arquivos baixados, com tamanho e SHA-256 (2026-10-20).
- [x] `verifica_fontes.py` com integridade, novo download na origem e recálculo independente.
- [x] Scripts de extração reproduzíveis (`extrai_gtfs_metro.py`, `extrai_mobilidade.py`), conferidos por hash: rodar de novo dá arquivos idênticos.
- [x] `FONTES.md` com fontes, APIs acessadas e origem de cada número.
- [x] Auditoria independente, feita por agente sem acesso aos scripts: nenhuma divergência; 6 ressalvas.
- [x] Correção das 6 ressalvas: 97,5% no lugar de 98%; exclusões declaradas; causa comum explicada no texto do painel; material tipo 63 registrado.
- [x] Reestruturação em monorepo, com dados brutos em `dados/brutos/` (fora do git) e derivados em `dados/derivados/`.
- [x] Manifesto com forma de distribuição (`release`, `origem`, `terceiros`) e modo `--baixa-release`.
- [x] Recálculo ampliado para a base geoespacial (estações e locais).
- [x] Criar a Release `dados-2026-10-20` com os brutos distribuíveis (15 arquivos; hashes conferidos depois do upload).
- [x] Workflow de publicação com verificação obrigatória. Provado na prática em 2026-10-21: o 1º deploy foi bloqueado porque o git do Windows mudou o fim de linha de 5 arquivos; corrigido com `.gitattributes`.
- [x] Workflow semanal `--online` com relatório datado (1ª execução em 2026-10-21: STM, GTFS, Nager, relatórios e d3 idênticos; OSM mudou, como esperado).
- [x] Conferir no site público a página `/fontes/` com o resultado da verificação feita pelo Actions: "sem problemas".
- [x] Falsos alarmes da 1ª verificação semanal tratados: o ECCC às vezes devolve HTML no lugar do CSV, e o Wikidata devolveu HTTP 429. O download agora valida o conteúdo e tenta de novo com espera.
