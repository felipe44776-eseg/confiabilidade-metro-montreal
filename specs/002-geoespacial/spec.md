# 002 — Base geoespacial

**Status:** implementada com exceções
**Fase:** F0 (S1)
**Depende de:** 000

## Pergunta de engenharia

A rede pode ser posta num mapa real com precisão suficiente para a simulação: linhas no traçado verdadeiro, estações no lugar certo, cada falha no local onde ocorreu? Os números que respondem são a diferença de comprimento entre o traçado e o oficial, a distância das estações a duas referências independentes e a parcela das falhas com posição.

## Contexto

- O GTFS da STM tem as estações com coordenadas, mas o desenho das linhas (`shapes.txt`) só liga estações em linha reta, de 2% a 10% mais curto que o oficial.
- O OpenStreetMap tem o traçado real: 8 relações, duas por linha.
- A base de incidentes não tem coordenadas, só o código de local. Os códigos são:
  - nome de estação;
  - código de plataforma (`xSyy`), não documentado pela STM;
  - trecho entre estações (`INTER.A/B`);
  - garagem, arrière-gare ou subestação.

## Critérios de aceite

- Dado o traçado de cada linha, quando se mede o comprimento, então ele fica a ±3% do oficial.
- Dadas as estações do GTFS, quando comparadas aos nós de estação do OpenStreetMap, então todas ficam a menos de 100 m.
- Dadas as estações, quando comparadas ao Wikidata, então todas ficam a menos de 100 m.
- Dados os códigos `xSyy`, quando se compara a linha deduzida com a registrada no incidente, então a coerência é de pelo menos 95% em cada código.
- Dadas as 8.530 falhas técnicas de uma linha, quando se conta quantas têm posição (verificada, deduzida ou aproximada), então são pelo menos 95%, e a parcela de cada status é publicada.
- Dado qualquer local no mapa, quando se clica nele, então aparecem o código, o tipo, o status da posição e o método usado.
- Dado o mesmo conjunto de entradas, quando o script roda duas vezes, então os arquivos gerados são idênticos.

## Resultado (2026-10-21)

Relatório completo: [`fontes/verificacao/validacao_geo.md`](../../fontes/verificacao/validacao_geo.md).

| Critério | Resultado |
|---|---|
| Comprimento ±3% | **Atende**: Verde +0,0%, Laranja −2,1%, Amarela +1,1%, Azul +0,3% |
| Estações a menos de 100 m do OSM | **Exceção**: 68 de 73 atendem. Beaudry, Laurier, Rosemont, Fabre e D'Iberville ficam de 104 a 142 m do nó do OSM, mas de 7 a 78 m do Wikidata. A diferença vem de onde o nó foi posto no OSM |
| Estações a menos de 100 m do Wikidata | **Atende**: máxima de 97 m |
| Coerência dos códigos `xSyy` ≥ 95% | **Atende**: 100% nos 5 códigos |
| Falhas com posição ≥ 95% | **Exceção**: 94,0%. Os 6% restantes são sobretudo subestações de energia (4,8%), cuja posição a STM não publica |
| Mapa com código, tipo, status e método | **Atende**: página `/mapa/` |
| Arquivos idênticos ao repetir | **Atende** |

## Fora de escopo

- Posição exata de pátios, garagens e aparelhos de mudança de via. Garagens e arrière-gares ficam na estação de mesmo nome, com status "aproximado".
- Geometria por sentido de circulação. O traçado é o mesmo nos dois sentidos.

## Riscos e dependências

- **Códigos `xSyy`:** a interpretação é dedução nossa. A coerência de 100% com a linha registrada sustenta a dedução, mas não substitui a documentação da STM.
- **OpenStreetMap:** muda com o tempo. Vale a consulta guardada na Release, com o timestamp da base.

## Perguntas em aberto

- A STM informaria, por pedido de acesso à informação, a posição das subestações de energia? Isso levaria a cobertura acima de 98%.
