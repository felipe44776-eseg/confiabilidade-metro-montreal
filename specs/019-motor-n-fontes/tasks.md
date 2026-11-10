# 019 — Simulador com várias fontes por linha: tarefas

- [x] Referência do motor gravada antes de qualquer mudança (`app/tests/motor/referencia_v1.test.ts`, `app/tests/fixtures/referencia_v1.json`; 2026-11-10, commit e793bba, parâmetros reais e fixture).
- [x] Passo 1 (2026-11-10): fonte com id, índice e sub-fluxos próprios; adaptador v1 com os sub-fluxos de antes; índice da fonte no pendente (fim do `find` da duração); locais por fonte opcionais. Os 198 casos da referência (fixture e parâmetros reais da v1.1.0) saíram idênticos. Depois, a fixture foi refeita a partir do painel revisto pela 017 e a referência gravada de novo, como base do passo 2.
- [ ] Passo 2: contrato v2 (fontes, fluxos por nome, políticas por efeito, métricas por fonte e gravidade).
- [ ] Consumidores: expansão, linhas novas, página (Parâmetros, legendas, registro), link com versão.
- [ ] Testes: fontes do v2, sorteio estável, soma das fontes, dispersão; fixture regenerada.
- [ ] Relatórios do app (políticas, expansão, viagem, linhas novas) regenerados com o v2.
