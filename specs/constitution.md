# Princípios

Valem para toda spec, plano, tarefa, script e página. Mudar um princípio é decisão da equipe, registrada aqui com data.

## Dados e números

1. **Todo número é rastreável.** Cada número publicado aponta para a fonte (URL e data de acesso), o arquivo (SHA-256 no manifesto), o script e o commit que o produziram.
2. **Fato, dedução e hipótese ficam separados.** Todo parâmetro leva um status: `ajustado` (estimado dos dados), `deduzido` (interpretação nossa, testada), `hipótese` (escolha do autor, sem dado) ou `não verificado`. A interface mostra o status ao lado do número.
3. **Reprodutibilidade.** Mesmas entradas e mesma semente dão o mesmo resultado, byte a byte. Versões de bibliotecas fixadas; nenhum arquivo derivado carrega a data em que foi gerado.
4. **Duas implementações independentes** para os números-chave. A verificação (`pipeline/verifica_fontes.py`) recalcula com código próprio, sem importar o pipeline.
5. **Estimativa vem com incerteza.** Toda taxa, média ou probabilidade estimada traz intervalo de confiança ou, quando não der, o tamanho da amostra.
6. **Dado ausente nunca vira zero.** Falta de dado aparece como falta (vazio, "sem posição", "não verificado"), nunca como valor.
7. **Critério não se ajusta ao resultado.** Critério de aceite é escrito antes. Se o resultado não atende, vira exceção documentada.

## Fontes e terceiros

8. **Licença e atribuição conferidas** antes de usar ou redistribuir. Só vai na Release o que a licença permite (STM CC BY 4.0, ECCC Licença de Governo Aberto, OpenStreetMap ODbL, Wikidata CC0). O resto se baixa da origem.
9. **Teto de tempo em toda chamada externa.** Downloads, APIs e ferramentas de linha de comando podem pendurar sem avisar.
10. **Uso educado de serviços públicos.** Uma consulta por necessidade, com identificação (User-Agent) e respeito aos limites publicados (Overpass, Nominatim, Wikidata, Open-Meteo).

## Simulação

11. **A simulação reproduz o que sabemos antes de prever.** Sem falhas, reproduz o horário do GTFS; com falhas, reproduz o histórico de 2019 a 2024 antes de prever 2025 e 2026.
12. **Hipótese aparece como hipótese.** O que não vem dos dados (tempo de reparo na oficina, posição de aparelhos de mudança de via) entra como parâmetro ajustável, marcado, e com análise de sensibilidade.
13. **Nada de passageiros inventados.** Sem dado diário de passageiros, as métricas são ponderadas pela oferta (trens e lugares programados), e o texto diz isso.

## Publicação

14. **O site é estático e público.** Tudo roda no navegador; nada exige conta ou servidor próprio.
15. **Publicar exige verificação verde.** O deploy só acontece se a integridade e o recálculo passarem.
16. **Acessível e leve.** Funciona em celular mediano, respeita `prefers-reduced-motion`, e o que importa está escrito no HTML.
