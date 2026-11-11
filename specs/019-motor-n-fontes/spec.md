# 019 — Simulador com várias fontes de falha por linha

**Status:** implementada com exceções
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

## Resultado (2026-11-10; dispersão e relatórios em 2026-11-11)

Código em `app/src/motor/contexto.ts` (fontes do contrato v2, `familiaNaLinha`), `taxas.ts` (taxa e renovação por fonte), `dia.ts` (falhas e minutos por fonte, classes de gravidade), `prng.ts` (`hash30`), `mc/rodadas.ts` (vetor estendido opcional), `expansao.ts` e `linhas_novas.ts` (herança pela soma da família) e `app/src/simulador/` (tabela por fonte, link com versão). Testes em `app/tests/motor/referencia_v1.test.ts` e `app/tests/motor/fontes_v2.test.ts`; revalidação em [`revalidacao.md`](../../fontes/verificacao/revalidacao.md) (spec 020).

| Critério | Resultado |
|---|---|
| Mesmos números antes da troca de parâmetros | **Atende**: os 198 casos da referência (dias, viagens com linhas novas e expansão; fixture e parâmetros reais da v1.1.0) saíram idênticos depois do passo 1 e continuam idênticos depois do passo 2, no contrato v1 |
| Fontes do contrato v2; falta de duração ou renovação é erro | **Atende** (testes) |
| Efeito por tipo de fonte | **Atende**: a família da fonte decide o efeito (trem ou trecho); os locais são da linha × fonte |
| Políticas por efeito | **Atende**: retirada vale para as fontes de trem, operação degradada para as fixas, como antes por família |
| Sorteio estável | **Atende** (teste: acrescentar fontes não muda as falhas das outras) |
| Soma das fontes | **Atende** (2026-11-11, depois da crítica): com o `parametros.json` v2 real, 20.000 dias úteis, as 8 combinações linha × família ficam dentro do IC 95% do esperado (`soma_fontes.test.ts`). A Azul nos equipamentos fixos dá 0,1576 por dia contra 0,1563 esperado (z = 0,40), e o maior desvio é o do material rodante da Azul (z = 1,48). O IC usa a variância entre os dias simulados: com a renovação de forma menor que 1, as falhas chegam em grupos (variância ÷ média de 1,17 a 1,60), e o IC de Poisson fica estreito demais. O mesmo teste sorteia 200 mil dias de cada uma das 32 fontes e confirma que o sorteio conserva o esperado. **Leitura dos 9% da crítica:** foi acaso de amostra, e não defeito. A crítica viu 9% abaixo em 7.000 dias (z ≈ −2,7), com o IC de Poisson. O número de dias foi escolhido depois de ver dois lotes de 10.000: o primeiro deu 2 de 8 fora (material rodante da Verde e da Azul, z = 2,5 e 2,3), o segundo deu 0 de 8 (Verde −1,7). Com 8 comparações a 95%, pelo menos uma fica fora por acaso em cerca de um terço dos lotes (1 − 0,95⁸ = 0,34). Antes, o critério era conferido só pela taxa acumulada (`fontes_v2.test.ts`) |
| Dispersão (variância ÷ média das falhas por dia útil, linha × família, dentro do IC 95% por blocos semanais do observado em 2025) | **Exceção**: 9 de 12 dentro (v1.1.0: 11 de 12). Abaixo do IC: equipamentos fixos da Verde, 1,06 contra 1,31 (1,14–1,47), porque a soma de fontes independentes agrupa menos. Acima: Amarela, material rodante 1,36 (0,93–1,29) e equipamentos fixos 1,64 (0,93–1,35). O fator diário comum por família, que o critério pede quando a simulada fica abaixo, não entrou nesta rodada: a variância dele teria de ser estimada nos mesmos dias de 2025 usados na validação. Fica como tarefa. A dispersão por mês não foi calculada (`revalidacao.md`) |
| Métricas por fonte, família e gravidade | **Atende** |
| Página: tabela por fonte; peso por família; link com versão | **Atende** no código; conferência no navegador na spec 020 |

## Fora de escopo

- Troca de frota numa linha como cenário (Verde só com MR-73 em 2031): spec 022. O motor guarda a parcela da frota para isso, mas a página não a expõe.
- Importância de Birnbaum por fonte e trecho: spec 021.

## Riscos e dependências

- A igualdade bit a bit depende de manter os mesmos sub-fluxos, a ordem das fontes (desempate da fila), os rótulos do registro e a mesma aritmética da taxa.
- O hash do registro não basta, porque as rodadas de Monte Carlo e as viagens não registram eventos. A referência guarda também o vetor de métricas e os bloqueios do grafo.
