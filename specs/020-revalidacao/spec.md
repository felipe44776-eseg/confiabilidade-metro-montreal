# 020 — Revalidação dos parâmetros e revisão dos números publicados

**Status:** implementada com exceções
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
  - *Mudança registrada em 2026-11-10, ao implementar, antes dos resultados:*
    - o backtest refeito usa o modelo por família da spec 005 sobre os dados revistos (duração pela faixa oficial e exposição medida até 2026-09), não o modelo por fonte. Refazer as versões A a D por fonte exigiria uns dez modelos com bootstrap por versão;
    - a comparação entre a v1.1.0 e o modelo por fonte fica no teste de um ano de fora da spec 018 (`fora_da_amostra.py`), e o teste com meses que nenhum dos dois viu é o pré-registrado;
    - por família e 5 min ou mais saem só como intervalo (sem PIT), para não mudar a sequência de sorteio do alvo total;
    - 5 min ou mais e minutos por família contam só o primeiro ano do teste, como os minutos parados da spec 012.
- **Monte Carlo contra o histórico:** dados os parâmetros novos, quando simulados, então as médias anuais por linha × família (minutos parados, falhas, falhas de 5 min ou mais) ficam dentro do IC 95% por blocos semanais do observado em pelo menos 90% das comparações. A tolerância é declarada antes, e cada comparação fora aparece listada.
- **Indicador da STM:** dado o simulado, os dados abertos e o publicado, quando comparados por ano, então a diferença entre os três fica explicada ou declarada como exceção.
- **Antes e depois:** dada a v1.1.0 e a versão revista, quando comparadas, então `fontes/verificacao/revisao_2026-11.md` lista cada número publicado que mudou (spec, valor antigo, valor novo, motivo), gerado dos arquivos derivados das duas versões.
- **Specs e documentos marcados:**
  - Cada spec atingida ganha a seção "Revisão de 2026-11 (após a ressegmentação)", com o antes e o depois, e o resultado original fica.
  - O relatório, a apresentação, o painel, o guia, a arquitetura e o README avisam que os números foram revistos em 2026-11 e apontam para a v1.1.0.
- *Critérios acrescentados em 2026-11-10, depois da leitura das referências (D62) e antes de calcular:*
  - **Verificação exata do método de estados:** dado um grafo de três estações (A, M, B), com uma linha A–M–B, uma ligação nova A–B e um componente de dois estados por trecho (fora com probabilidade 0,01, 0,01 e 0,02), quando o método de estados da spec 014 roda com 200 mil amostras e números aleatórios comuns, então a indisponibilidade origem-destino sem e com a ligação e o ganho ficam a menos de 4 erros-padrão da enumeração exata dos 8 estados.
  - **Massa em zero por fonte e ano:** dados os eventos técnicos com a duração da spec 017, quando agrupados por fonte e por ano, então o relatório de distribuições traz a proporção de duração zero e de até 1 min, com IC de Clopper–Pearson, e o qui-quadrado de homogeneidade entre as fontes e entre os anos de cada fonte. A leitura fica fixada antes:
    - **parada segura com rearme rápido:** fontes heterogêneas (p < 0,01); a menor proporção de zero entre controle de trens (`aux_trains_*`) e frotas (`mr73`, `mpm10`) acima da maior entre via, estações e TCPE; e essas quatro fontes estáveis entre os anos (p ≥ 0,01 em cada uma);
    - **artefato de registro:** fontes homogêneas (p ≥ 0,01), ou um ano em que pelo menos metade das fontes tem o IC 95% inteiro acima ou inteiro abaixo da própria proporção no período todo;
    - **inconclusiva:** nenhum dos dois padrões. Se os dois aparecerem, a leitura diz isso.
    - `mr_outros` (51 falhas) fica fora das comparações. O salto de 2024 da via com sintoma de trem já é conhecido (D56) e conta como salto de uma fonte só.
    - "Controle de trens" é dedução até a STM responder o que é o Service aux trains.
  - **Escopo e vocabulário:** o relatório e o guia dizem que:
    - o que se mede é confiabilidade e disponibilidade do serviço diante de falhas de rotina, não resiliência a desastres nem segurança (estado inseguro);
    - os minutos de pares sem caminho são a área de perda da curva de resiliência;
    - verificação (motor contra contas) é separada de validação (contra o observado);
    - a duração é a da interrupção do serviço, não o reparo do equipamento, e os noves são de disponibilidade do serviço.
- **Revisão crítica:** dado o conjunto revisto, quando o agente crítico roda, então refaz os números dos documentos contra os arquivos gerados sem divergência aberta.

## Resultado (2026-11-11)

Relatórios: [`revalidacao.md`](../../fontes/verificacao/revalidacao.md) (simulador contra 2025, dispersão e indicador da STM), [`backtest.md`](../../fontes/verificacao/backtest.md) (refeito, pós-hoc), [`revisao_2026-11.md`](../../fontes/verificacao/revisao_2026-11.md) (antes e depois), [`distribuicoes.md`](../../fontes/verificacao/distribuicoes.md) (massa em zero) e `fontes/verificacao/preregistro/`.

| Critério | Resultado |
|---|---|
| Versão anterior acessível | **Atende**: etiqueta `v1.1.0` no commit e793bba, Release com o zip do site, servida em `/versoes/v1.1.0/` |
| Pré-registro antes de qualquer download de incidentes novos | **Atende**: v1 commitado em 4fe203d (2026-11-10); v2 congelado e commitado em 2026-11-11, com os 100 primeiros vetores do bootstrap de cada modelo (`modelo_v2.json`). O avaliador recusa rodar sem o arquivo ou com menos de 3 meses novos |
| Teste fora da amostra (3 meses novos) | **Pendente**: em 2026-11-10 o CSV de incidentes da STM não tinha mudado desde 2026-09-14 |
| Backtest refeito, marcado como posterior | **Atende**: A 65,3%, B 84,7%, C 87,5%, D 90,3% (oficial da v1.1.0: 66,7%, 81,9%, 84,7%, 90,3%). Por família, a versão A falha nos equipamentos fixos (65,3%) e não no material rodante (87,5%). Detalhe na spec 012 |
| Monte Carlo contra o histórico: médias anuais por linha × família dentro do IC 95% do observado em 2025 em pelo menos 90% das comparações | **Exceção**: 25 de 28 (89,3%), contra 21 de 28 da v1.1.0. Fora: equipamentos fixos da Amarela, falhas (40,5 simuladas contra 19 observadas; a média de 2019 a 2025 é 82,6) e minutos (143 contra 44), e minutos de causa comum da Azul (48 contra 2). Em 2025, a Amarela teve o menor número de falhas fixas da série, e o modelo não tem efeito de linha × ano. A tolerância de 15% da spec 009 fica em 12 de 28 |
| Dispersão (critério da spec 019) | **Exceção**: 9 de 12 dentro do IC por blocos (v1.1.0: 11 de 12); abaixo, os equipamentos fixos da Verde (1,06 contra 1,14–1,47). Ver a spec 019 |
| Indicador da STM | **Exceção declarada**: os dados abertos dão de 85% a 89% do indicador publicado de 5 min ou mais por milhão de km-carro, todos os anos de 2019 a 2025 (2025: 9,89 contra 11,66). A STM não publica a regra de contagem; a pergunta está no pedido da equipe à STM. Só falhas técnicas: 2,46 nos dados abertos de 2025 e 2,61 no simulado |
| Antes e depois | **Atende**: `revisao_2026-11.md`, gerado por `pipeline/compara_versoes.py` dos arquivos das duas versões |
| Specs e documentos marcados | **Atende**: seção "Revisão de 2026-11 (após a ressegmentação)" nas specs 001, 004 a 009, 011, 012 e 014 a 016; relatório, apresentação, painel, guia, arquitetura, README, FONTES e dicionário com o aviso e o link para a v1.1.0 |
| Verificação exata do método de estados (D62) | **Atende**: a menos de 4 erros-padrão da enumeração dos 8 estados, sem e com a ligação (`app/tests/motor/expansao.test.ts`) |
| Massa em zero por fonte e ano (D62), leitura fixada antes | **Inconclusiva**: as fontes diferem (p < 0,0001), mas o padrão não é o de parada segura com rearme (o MR-73 tem a menor proporção, 25%) nem o de mudança de registro (nenhum ano com salto comum). A via com sintoma de trem sobe de 17% (2019) para 98% (2025) e o MPM-10 de 21% para 66%, cada uma por conta própria |
| Escopo e vocabulário | **Atende** no relatório e no guia |
| Revisão crítica | Ver `fontes/verificacao/critica_2026-11-11.md` |

*Mudança registrada em 2026-11-10, depois de ver (D63):* a exposição dos dias de greve. Ver a spec 018.

## Fora de escopo

- Novas perguntas (Birnbaum, cenário 2031): specs 021 e 022.

## Riscos e dependências

- A STM pode demorar a publicar os meses novos. O critério fora da amostra fica pendente, e a revisão sai com o backtest marcado como posterior.
- A STM pode revisar meses antigos na publicação nova. Os meses sobrepostos são comparados com o retrato antes da avaliação.
