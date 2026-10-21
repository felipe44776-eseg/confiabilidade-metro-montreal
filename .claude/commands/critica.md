---
description: Roda o agente crítico (critico-stf) no projeto e publica as correções aprovadas
---

Delegue ao agente `critico-stf` (definido em `.claude/agents/critico-stf.md`) a revisão completa do repositório, do passo 1 ao 9 do método dele. Foco extra, se houver: $ARGUMENTS

Quando ele terminar:

1. Leia `fontes/verificacao/critica_<data de hoje>.md`.
2. Resuma para mim os achados por gravidade e o que ele corrigiu.
3. Rode de novo os testes: `.venv/Scripts/python.exe -m pytest pipeline/tests -q` e, dentro de `app/`, `npm test` e `npm run build`.
4. Se tudo passar, antes de qualquer commit confira a conta `felipe44776-eseg` (`GH_CONFIG_DIR=~/.config/gh-esg`) e o e-mail da ESEG. Só então pergunte se pode fazer o commit e o push.
