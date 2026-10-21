# 011 — Cenários e parâmetros ajustáveis: tarefas

- [x] `app/src/simulador/cenario.ts`: estado da página, cenário do motor, greve pelo horário, link (testes de ida e volta, de valores inválidos e de determinismo com o mesmo link e a mesma semente).
- [x] Teste do mapeamento: cada escolha da página vira o multiplicador certo, hora a hora (jogo só nas horas 18 a 22); cenário padrão = multiplicador 1.
- [x] `app/src/simulador/extrapolacao.ts` e `observado.ts`: avisos a partir das horas observadas e das faixas das hipóteses (testes: neve no solo em julho, chuva congelante a 25 °C, poucos dados, hipótese fora da faixa, feriado em dia útil).
- [x] `app/src/simulador/ab.ts`, `pool_ab.ts` e `trabalhador_ab.ts`: comparação com números aleatórios comuns (testes: mesma semente nas duas versões; cenários iguais dão diferença exatamente zero; o lado A não muda com B).
- [x] Página `/simulador/` com abas: dia no mapa, muitos dias (PoolMC, progresso, cancelar, estimativa do ano), comparação, expansão e parâmetros.
- [x] Cada parâmetro com IC 95% ou status e link para a fonte; hipóteses em controles deslizantes com a faixa.
- [x] Resultado pronto ao abrir (1.000 dias no cenário padrão).
- [x] Teste de ponta a ponta no Chrome sem janela (2026-10-21): 1.000 dias em 3,8 s com 12 workers; comparação de 500 dias pareados em 2,1 s; avisos de extrapolação para chuva congelante em outubro; nenhum erro no console.
- [x] Peso de cada variável e nota do método no painel do cenário (2026-10-21, decisão D51): `app/src/simulador/pesos.ts`; testes em `app/tests/simulador/pesos.test.ts`; conferência no navegador em `publicacao/testa_navegador.py`.
- [ ] Cenários prontos (inverno típico, greve de 2025, dia de jogo, chuva congelante de abril de 2023): hoje montados à mão pelo formulário e guardados no link.
- [ ] Sortear um dia real do histórico como cenário (pergunta em aberto).
