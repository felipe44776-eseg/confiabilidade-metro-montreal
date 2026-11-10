# 020 — Revalidação dos parâmetros e revisão dos números publicados

**Status:** especificada
**Fase:** revisão de 2026-11
**Depende de:** 012, 017, 018, 019
**Revisa:** 009 (Monte Carlo), 012 (backtest) e os documentos (relatório, apresentação, painel, guia, arquitetura)
**Origem:** pedido de 2026-11-10 ("validar se os parâmetros do treino e da simulação ainda se mantêm"; "pode revisar tudo, só avisa que foi após a revisão para termos no histórico do projeto") e decisões D60 e D61

## Pergunta de engenharia

Depois da ressegmentação, os parâmetros ajustados e o simulador preveem o que não viram, e quais números publicados mudaram, de quanto?

## Contexto

- O backtest pré-registrado da spec 012 (versão A) cobriu 66,7% dos casos (critério: 80% a 98%). O previsto para os minutos parados ficou acima do observado em todas as linhas: a Azul com 2.962 min/ano contra 708 observados.
- A explicação publicada era "2024 atípico". A revalidação de 2026-11-10 encontrou duas causas concretas:
  - 516 falhas de via de quase zero minuto nos terminais, de maio a dezembro de 2024;
  - durações de cerca de 19 h que contradizem a faixa oficial (spec 017).
- O CSV de incidentes da STM não mudou desde o retrato (2026-06-30). Um teste de verdade fora da amostra precisa esperar os meses seguintes, e por isso o modelo é congelado antes.
- O indicador da STM "incidents de 5 minutes et plus par million de km" (km-carro) dá de 11% a 15% a mais que a contagem nos dados abertos (2019: 10,6 contra 9,09).

## Critérios de aceite

- **Versão anterior acessível:** dada a revisão, quando publicada, então a versão v1.1.0 (etiqueta no commit e793bba, Release com o zip do site) continua servida em `/versoes/v1.1.0/`.
- **Pré-registro:** dados os modelos v1.1.0 e novo, quando congelados (`pipeline/preregistro.py`), então os arquivos ficam commitados antes de qualquer download de incidentes posteriores a 2026-06-30, e o avaliador recusa rodar sem eles.
- **Teste fora da amostra:** dados pelo menos 3 meses novos publicados pela STM, quando avaliados, então o relatório traz, por versão do modelo:
  - a cobertura do intervalo de 90% (falhas técnicas e falhas de 5 min ou mais), com critério de 80% a 98%;
  - o PIT;
  - o escore logarítmico médio, com IC pareado entre as versões.
  
  Até haver 3 meses, este critério fica pendente.
- **Backtest refeito, marcado como posterior:** dadas as versões A a D da spec 012, quando refeitas com o modelo novo, então trazem os alvos total, 5 min ou mais e por família, marcados "após a revisão (pós-hoc)". O resultado oficial original da spec 012 fica registrado.
- **Monte Carlo contra o histórico:** dados os parâmetros novos, quando simulados, então as médias anuais por linha × família (minutos parados, falhas, falhas de 5 min ou mais) ficam dentro do IC 95% por blocos semanais do observado em pelo menos 90% das comparações. A tolerância é declarada antes, e cada comparação fora aparece listada.
- **Indicador da STM:** dado o simulado, os dados abertos e o publicado, quando comparados por ano, então a diferença entre os três fica explicada ou declarada como exceção.
- **Antes e depois:** dada a v1.1.0 e a versão revista, quando comparadas, então `fontes/verificacao/revisao_2026-11.md` lista cada número publicado que mudou (spec, valor antigo, valor novo, motivo), gerado dos arquivos derivados das duas versões.
- **Specs e documentos marcados:**
  - Cada spec atingida ganha a seção "Revisão de 2026-11 (após a ressegmentação)", com o antes e o depois, e o resultado original fica.
  - O relatório, a apresentação, o painel, o guia, a arquitetura e o README avisam que os números foram revistos em 2026-11 e apontam para a v1.1.0.
- **Revisão crítica:** dado o conjunto revisto, quando o agente crítico roda, então refaz os números dos documentos contra os arquivos gerados sem divergência aberta.

## Fora de escopo

- Novas perguntas (Birnbaum, cenário 2031): specs 021 e 022.

## Riscos e dependências

- A STM pode demorar a publicar os meses novos. O critério fora da amostra fica pendente, e a revisão sai com o backtest marcado como posterior.
- A STM pode revisar meses antigos na publicação nova. Os meses sobrepostos são comparados com o retrato antes da avaliação.
