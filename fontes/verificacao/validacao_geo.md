# Validação da base geoespacial (spec 002)

Gerado por `pipeline/geo_base.py` em 2026-10-21T01:15:32+00:00. OpenStreetMap consultado em 2026-10-21T01:07:06Z (Overpass API).

## Comprimento das linhas

| Linha | Traçado OSM (km) | Oficial (km) | Diferença | Critério ±3% | Pontos | Relação OSM |
|---|---|---|---|---|---|---|
| verde | 22.11 | 22.1 | +0.0% | atende | 418 | 58433 |
| laranja | 29.36 | 30.0 | -2.1% | atende | 362 | 270251 |
| amarela | 4.29 | 4.25 | +1.1% | atende | 49 | 270252 |
| azul | 9.73 | 9.7 | +0.3% | atende | 110 | 270255 |

Comprimento oficial: tabela "Lignes du métro de Montréal" em https://fr.wikipedia.org/wiki/M%C3%A9tro_de_Montr%C3%A9al (acesso 2026-10-20). O `shapes.txt` do GTFS liga as estações em linha reta e fica 2% a 10% abaixo do oficial (pesquisa de 2026-10-20).

## Estações

- Estações por linha no GTFS (sentido 0): verde 27, laranja 31, amarela 3, azul 12.
- Distância GTFS → nó de estação do OSM: 73 de 73 casadas pelo nome; máxima 142 m; mediana 32 m. Sem par no OSM: nenhuma.
- Distância GTFS → Wikidata (rede Q392377): 73 de 73 casadas; máxima 97 m; mediana 24 m. Sem par: nenhuma.
- Distância da estação ao traçado OSM: máxima 129 m; mediana 10 m.
- Critério da spec (todas a menos de 100 m do OSM): NÃO atende: Beaudry (verde) 118 m do OSM e 11 m do Wikidata; Laurier (laranja) 141 m do OSM e 24 m do Wikidata; Rosemont (laranja) 104 m do OSM e 78 m do Wikidata; Fabre (azul) 142 m do OSM e 21 m do Wikidata; Iberville (azul) 124 m do OSM e 7 m do Wikidata.
  As exceções ficam perto do Wikidata; a diferença vem de onde o nó da estação foi posto no OSM (entrada ou edifício). Ficam registradas como exceção, sem mudar o critério.

## Códigos de local dos incidentes técnicos

Base: 8530 falhas técnicas de uma única linha. Códigos distintos: 201.

| Status | Falhas | Parcela |
|---|---|---|
| verificado | 6165 | 72.3% |
| deduzido | 1077 | 12.6% |
| aproximado | 772 | 9.1% |
| desconhecido | 516 | 6.0% |

Georreferenciadas (qualquer status, exceto desconhecido): 94.0%. Critério da spec (≥95%): NÃO atende.

### Coerência da dedução dos códigos xSyy

Parcela dos incidentes de cada código cuja linha registrada é a linha deduzida. Critério: ≥95%.

| Código | Estação deduzida | Linha deduzida | Incidentes | Coerência | Critério |
|---|---|---|---|---|---|
| 2S46 | Lionel-Groulx | laranja | 28 | 100.0% | atende |
| 2S60 | Berri-Uqam | laranja | 69 | 100.0% | atende |
| 4S50 | Berri-Uqam | amarela | 561 | 100.0% | atende |
| 5S32 | Snowdon | azul | 361 | 100.0% | atende |
| 5S48 | Jean-Talon | azul | 58 | 100.0% | atende |

### Códigos sem localização

| Código | Linha mais frequente | Falhas |
|---|---|---|
| POSTE DE REDR.VERSAILLES | verde | 35 |
| POSTE DE REDR.DES SEIGNEURS | laranja | 29 |
| POSTE DE REDR.AHUNTSIC | laranja | 26 |
| 2999 | laranja | 19 |
| POSTE DE REDR.METCALFE | verde | 19 |
| 1999 | verde | 19 |
| POSTE DE REDR.CLARK | verde | 18 |
| POSTE DE REDR.HOGAN | verde | 16 |
| POSTE DE DISTRICT DICKSON | verde | 15 |
| POSTE DE REDR.PLESSIS | verde | 14 |
| 5999 | azul | 14 |
| POSTE DE REDR.UNIVERSITE | laranja | 13 |
| POSTE DE REDR.FAILLON | laranja | 13 |
| POSTE DE REDR.JARRY | azul | 12 |
| POSTE DE REDR.ILE NOTRE-DAME | amarela | 12 |
| POSTE DE REDR.DULUTH | laranja | 12 |
| POSTE DE REDR.ANDERSON | laranja | 12 |
| POSTE DE REDR.DECELLES | azul | 11 |
| POSTE DE REDR.ARAGON | verde | 11 |
| POSTE DE REDR.BELLECHASSE | laranja | 11 |
| POSTE DE REDR.RICHELIEU | laranja | 10 |
| POSTE GROUPES ELECTROGENES PROVIDENCE | laranja | 10 |
| POSTE DE REDR.ST-MATHIEU | verde | 9 |
| POSTE DE REDR.ST-GREGOIRE | laranja | 9 |
| POSTE DE REDR.COTE VERTU | laranja | 9 |
