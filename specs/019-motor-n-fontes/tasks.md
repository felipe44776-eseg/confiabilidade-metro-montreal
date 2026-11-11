# 019 — Simulador com várias fontes por linha: tarefas

- [x] Referência do motor gravada antes de qualquer mudança (`app/tests/motor/referencia_v1.test.ts`, `app/tests/fixtures/referencia_v1.json`; 2026-11-10, commit e793bba, parâmetros reais e fixture).
- [x] Passo 1 (2026-11-10): fonte com id, índice e sub-fluxos próprios; adaptador v1 com os sub-fluxos de antes; índice da fonte no pendente (fim do `find` da duração); locais por fonte opcionais. Os 198 casos da referência (fixture e parâmetros reais da v1.1.0) saíram idênticos. Depois, a fixture foi refeita a partir do painel revisto pela 017 e a referência gravada de novo, como base do passo 2.
- [x] Passo 2: contrato v2 (fontes na ordem do arquivo, sub-fluxo pelo nome da linha e da fonte, taxa e renovação por fonte, falta vira erro), métricas por fonte e por classe de gravidade; referência v1 ainda idêntica.
- [x] Consumidores: expansão e linhas novas pela soma da família; tabela por fonte na aba Parâmetros; aviso e link para a v1.1.0 em links sem versão.
- [x] Testes: `fontes_v2.test.ts` (fontes, soma, sorteio estável, contagens por fonte e classe, erro sem duração ou renovação).
- [x] Relatórios do app (políticas, expansão, viagem, linhas novas e revalidação) regenerados com o v2 em 2026-11-11 (spec 020).
- [x] Conferência da página no navegador (2026-11-11, site montado localmente da branch): celular e notebook sem rolagem lateral, WebGL, sem erro no console, 1.000 dias em 1,5 e 1,7 s; aviso do link antigo com o link para a v1.1.0; tabela por fonte na aba Parâmetros (`fontes/verificacao/navegador_2026-11-11.json`). No site publicado (deploy de 5a665a4), o mesmo: 1.000 dias em 1,4 e 1,8 s, sem erro, aviso do link antigo e `/versoes/v1.1.0/simulador/` respondendo.
- [ ] Fator diário comum por família nos equipamentos fixos (critério de dispersão: Verde abaixo do IC em 2025), com a variância estimada fora do ano de validação.
- [ ] Dispersão por mês, além da diária.
- [x] Critério "Soma das fontes" com o contrato v2 real (`app/tests/motor/soma_fontes.test.ts`, 2026-11-11): 20.000 dias úteis, 8 de 8 dentro do IC 95% com o erro-padrão entre os dias; o sorteio conserva o esperado nas 32 fontes. Os 9% abaixo da Azul EF na crítica eram acaso de amostra (Azul EF: z = 0,40).
- [ ] Versionar o `parametros.json` da v1.1.0 como fixture, para o CI guardar os 198 casos da referência v1 (hoje guarda os 99 da fixture; os 198 foram conferidos à parte).
