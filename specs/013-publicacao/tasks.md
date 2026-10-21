# 013 — Publicação: tarefas

- [x] `deploy.yml`: Release, hashes e recálculo (25 números), pytest com as versões fixadas, vitest e build; erro bloqueia a publicação.
- [x] `verifica-fontes.yml`: semanal, relatório datado com commit automático; mudança na origem é aviso.
- [x] Release `dados-2026-10-21` (clima horário e expansão), com o hash de cada arquivo nas notas; cada fonte guarda a tag da sua Release no manifesto.
- [x] `verifica_fontes.py --baixa-origem`: baixa as fontes sem licença de redistribuição.
- [x] `reproduz.yml` e `pipeline/compara_derivados.py`: pipeline do zero numa máquina limpa e comparação com tolerância declarada (testes em `pipeline/tests/test_compara.py`).
- [x] Rodapé com equipe, versão dos dados (Releases) e link para as fontes em todas as páginas.
- [x] Versões congeladas: o deploy desempacota o zip do site de cada Release `v*` em `/versoes/<etiqueta>/`.
- [x] Execução do `reproduz.yml` no GitHub Actions: a 1ª (39542896386) acusou só metadados; a 2ª (39546898051) passou.
- [x] Nova execução no commit ba19e74 (39556506384), depois das revisões críticas: 48 idênticos, 5 na tolerância, 0 fora.
- [x] `v1.0.0` congelada em 2026-10-21 (etiqueta no commit 6196ad2, Release com o zip do site, `/versoes/v1.0.0/`).
- [ ] Congelar a versão de entrega no fim do semestre (v1.x).
