# 020 — Revalidação e revisão: plano

| Peça | Como funciona | Arquivo |
|---|---|---|
| Versão congelada | Etiqueta `v1.1.0` no `e793bba`; Release com `site-v1.1.0.zip`, montado com `VITE_BASE=/confiabilidade-metro-montreal/versoes/v1.1.0/`; o deploy desempacota cada Release `v*` | `.github/workflows/deploy.yml` (D37) |
| Pré-registro v1 | Modelo da v1.1.0 ajustado em todos os dados até 2026-06-30, B = 100 vetores por causa, formas e amostras de duração; congelado antes de qualquer mudança | `pipeline/preregistro.py congela v1` → `fontes/verificacao/preregistro/modelo_v1.json` |
| Pré-registro v2 | O mesmo para o modelo da spec 018, logo que ele estiver pronto | `preregistro.py congela v2` |
| Avaliação | Só com o arquivo congelado e com pelo menos 3 meses depois do corte; casos linha × mês nas horas com serviço; alvos total e 5 min ou mais pela faixa oficial; regra do ano C (principal) e A; cobertura de 90%, PIT, escore logarítmico | `preregistro.py avalia <versão>` |
| Backtest pós-hoc | `backtest.py` com o modelo por fonte, as mesmas versões A a D, alvos total, 5 min ou mais e família | `pipeline/backtest.py` |
| Monte Carlo contra o histórico | Médias anuais simuladas por linha × família contra o IC por blocos semanais do observado | `app/relatorios/revalidacao.relatorio.ts` |
| Indicador da STM | Por ano: simulado, dados abertos (faixa ≥ 5 min / km-carro) e o publicado nos relatórios anuais | mesmo relatório |
| Antes e depois | Lê os derivados da etiqueta v1.1.0 (`git show v1.1.0:<arquivo>`) e os atuais, e lista os números que mudaram | `pipeline/compara_versoes.py` → `fontes/verificacao/revisao_2026-11.md` |
