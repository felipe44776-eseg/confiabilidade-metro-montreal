# 004 — Exposição: tarefas

- [x] Perfil horário por linha, tipo de dia e hora a partir dos três moldes do GTFS.
- [x] Trens em viagem às 08:00: 26, 31, 2 e 9 (esperado 26, 32, 2 e 9, tolerância de 1); recálculo independente em `verifica_fontes.py`.
- [x] Erro mensal: 216 de 220 meses-linha até 10% (98,2%); erro mediano 0,44%. Exceções: Verde, Azul e Laranja em 2020-04 (+17%, +16%, +16%) e Amarela em 2019-06 (−10,75%).
- [x] Status "medido" (6.936 dias-linha) e "estimado" (4.016), com a fonte de cada fator.
- [x] Greves de 2025 reduzem a oferta pela fração da hora com serviço (25 dias).
- [x] Km por frota: MPM-10 e MR-73 somam o total menos os 22 registros do tipo 63 (15,7 km), no relatório `fontes/verificacao/exposicao.md`.
- [x] Testes em `pipeline/tests/test_exposicao.py`.
- [ ] Investigar a Amarela em 2019-06 (possível obra ou fechamento planejado sem fonte).
