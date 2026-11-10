# 019 — Simulador com várias fontes de falha por linha

**Status:** especificada
**Fase:** revisão de 2026-11
**Depende de:** 007, 008, 009, 018
**Revisa:** 007 (motor), 008 (políticas), 009 (Monte Carlo), 011 (cenários), 014 (expansão), 016 (linhas novas)
**Origem:** revalidação de 2026-11-10 (decisão D59)

## Pergunta de engenharia

O simulador reproduz as falhas e os minutos parados de cada linha quando cada frota e cada setor do equipamento fixo é uma fonte própria, com a sua taxa, a sua duração e o seu efeito na operação?

## Contexto

- O motor da v1.1.0 tem duas causas fixas por linha (MR, EF) e a causa comum. A taxa, a renovação, a duração, os locais, as políticas, os fluxos de sorteio e as métricas são presos a esse par.
- A spec 018 gera parâmetros por fonte (contrato v2).
- Somar fontes independentes agrupa menos as falhas do que o total observado, que mostrou sobredispersão (α de 1,8 a 5,5) e efeito da hora anterior.

## Critérios de aceite

- **Mesmos números antes da troca de parâmetros:** dado o motor reorganizado para uma lista de fontes, quando roda com os parâmetros do contrato v1, então dias simulados, viagens com linhas novas e avaliação de expansão saem idênticos, bit a bit, à referência gravada antes da mudança (`app/tests/fixtures/referencia_v1.json`), e toda a suíte passa.
- **Fontes do contrato v2:** dado o `parametros.json` v2, quando o contexto é preparado, então cada linha tem as fontes do arquivo, cada uma com a sua taxa, renovação, duração e locais. A falta de duração ou de renovação de uma fonte é erro, não valor padrão.
- **Efeito por tipo de fonte:** dada uma falha, quando acontece, então:
  - fonte de trem para o trem no sentido;
  - fonte fixa bloqueia o trecho sorteado entre os locais da linha × fonte;
  - causa comum para as linhas do grupo.
- **Políticas por efeito:** dada a retirada do trem, quando ligada, então vale para as fontes de trem; dada a operação degradada, então vale para as fontes fixas. A lista fica nas hipóteses e aparece na página.
- **Sorteio estável:** dado o contrato v2, quando uma fonte é acrescentada ou retirada, então os instantes, as durações e os locais das outras fontes não mudam (fluxo de cada fonte pelo nome da linha e da fonte).
- **Soma das fontes:** dado o contrato v2, quando simulados muitos dias, então as falhas por dia de cada linha × família (trem, fixo) reproduzem o esperado pelos parâmetros dentro do IC 95%.
- **Dispersão:** dados os dias simulados e os observados, quando comparada a variância ÷ média das falhas por dia e por mês de cada linha × família, então a simulada fica dentro do IC por blocos da observada. Se ficar abaixo, entra um fator diário comum por família e o critério é refeito.
- **Métricas:** dada uma rodada, quando agregada, então há minutos e falhas por fonte, por família (MR, EF, CC, como antes) e por classe de gravidade (menos de 5, 5 a 10, 10 a 30, 30 min ou mais).
- **Página:** dada a aba Parâmetros, quando aberta, então mostra uma tabela por fonte. O peso de cada variável (spec 011) continua por família. O mapa e o registro nomeiam a fonte de cada falha.
- **Link com versão:** dado um link de cenário da v1.1.0, quando aberto, então a página avisa que os números foram revistos em 2026-11 e leva à cópia em `/versoes/v1.1.0/`; os links novos levam a versão.

## Fora de escopo

- Troca de frota numa linha como cenário (Verde só com MR-73 em 2031): spec 022. O motor guarda a parcela da frota para isso, mas a página não a expõe.
- Importância de Birnbaum por fonte e trecho: spec 021.

## Riscos e dependências

- A igualdade bit a bit depende de manter os mesmos sub-fluxos, a ordem das fontes (desempate da fila), os rótulos do registro e a mesma aritmética da taxa.
- O hash do registro não basta, porque as rodadas de Monte Carlo e as viagens não registram eventos. A referência guarda também o vetor de métricas e os bloqueios do grafo.
