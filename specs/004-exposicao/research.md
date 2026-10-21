# 004 — Pesquisa: geografia, operação e frota

Achados da pesquisa de 2026-10-20 (agente de pesquisa, somente leitura sobre o GTFS local, o km real e a web). Cada item diz se foi verificado ou não.

## GTFS da STM (feed 20261007130000_26N)

- `shapes.txt` tem um ponto por estação: a geometria é uma poligonal reta entre estações. Comprimento calculado: Verde 20,07 km, Laranja 28,26, Amarela 3,83, Azul 9,50, contra 22,1 / 30,0 / 4,25 / 9,7 km oficiais (91%, 94%, 90%, 98%). Verificado pela pesquisa de 2026-10-20. Por isso o traçado da spec 002 vem do OpenStreetMap.
- A Laranja tem viagens curtas Côte-Vertu↔Henri-Bourassa (shapes 2_238 e 2_239, 5 por sentido em dia útil) e Henri-Bourassa→Montmorency (2_166).
- Não há `frequencies.txt`: os horários estão explícitos em `stop_times`, arredondados ao minuto.
- Intervalo mediano em dia útil (serviço `26N-GLOBAUX-01-S`), em minutos:

| Linha | 05:00–06:30 | Pico manhã 7–9 | Entrepico 10–15 | Pico tarde 16–18 | Noite 20–23 | Após 23h | Ponta a ponta |
|---|---|---|---|---|---|---|---|
| Verde | 7 | 3 | 6 | 3 | 6 | 8 | 36–38 |
| Laranja | 6 | 3 | 6 | 3 | 6 | 8 | 46–49 |
| Amarela | 10 | 5 | 10 | 5 | 10 | 10 | 6–7 |
| Azul | 6–7 | 4 | 7 | 5 | 7 | 8 | 15–17 |

- Sábado e domingo: 6 a 10 minutos. Serviço das 05:30 até 00:30 a 01:30.
- Trens em viagem às 08:00 (sem contar os parados nos terminais): 26, 32, 2 e 9.
- Velocidade comercial calculada (km oficial dividido pelo tempo): 35, 38, 42 e 36 km/h. A Wikipedia em francês dá de 34 (Verde) a 51 (Amarela) km/h.

## OpenStreetMap

- Uma consulta à Overpass API (https://overpass-api.de/api/interpreter) achou 8 relações `route=subway` (2 por linha) e 137 vias `railway=subway`, com 69 nós de estação. Licença ODbL. Verificado pela pesquisa de 2026-10-20 e baixado depois pela spec 002.

## Frota e operação

- MPM-10 (Azur): 71 trens de 9 vagões (639 vagões). MR-73: cerca de 360 vagões em blocos de 3. Total de 999 vagões segundo a Wikipedia em inglês. Fontes: https://fr.wikipedia.org/wiki/M%C3%A9tro_de_Montr%C3%A9al e https://en.wikipedia.org/wiki/Montreal_Metro
- Por linha, pelo km real de 2023 e outras fontes: a Laranja roda com Azur; a Verde é mista (Azur 15,6 milhões de km-vagão, MR-73 6,0 milhões); a Azul roda MR-73 com 2 blocos (6 vagões); a Amarela roda MR-73 com 3 blocos (9 vagões), segundo https://en.wikipedia.org/wiki/Yellow_Line_(Montreal_Metro)
- Plano de frota e distância média entre falhas segundo a imprensa (Azur cerca de 1,9 milhão de km, MR-73 cerca de 164.500 km): https://www.narcity.com/fr/montreal/ligne-verte-trains-azur-mr73-stm . Fonte de imprensa, não oficial.
- Número oficial de trens por linha: não verificado. Aproximação pelo km real (composições distintas por dia útil em 2023, mediana): Verde 50, Laranja 47, Azul 15, Amarela 6.
- Garagens: Angrignon, Beaugrand, Saint-Charles, Montmorency, Côte-Vertu (inaugurada em 2022), oficinas Plateau d'Youville e Duvernay. Coordenadas exatas não verificadas. Côte-Vertu: https://www.masstransitmag.com/technology/facilities/press-release/21271639/societe-de-transport-de-montreal-stm-stm-inaugurates-cote-vertu-underground-garage
- Velocidade máxima de 72 km/h; em condução manual, 40 km/h.

## Campos do km real

- `Code dégradation` é o tipo de condução, segundo a ficha https://www.donneesquebec.ca/recherche/dataset/vmtl-stm-kilometrage-realise-par-les-voitures-de-metro-de-la-stm (trecho visto só em resultado de busca): PA (pilotage automatique) em 88% do km; CMC (conduite manuelle contrôlée, sigla deduzida), com a Amarela em 97% CMC; CD em só 6 linhas, significado não verificado.
- `Période exploitation` é a "période de liste", 5 por ano: J (jan a mar), M (mar a jun), U (jun a ago), S (ago a out), N (out a jan). É a mesma nomenclatura do GTFS ("26N"). O sufixo B ou V usado desde 2021 tem significado não verificado; "#" marca ausente (80.275 linhas).
- Cobertura: 2019-01 a 2023-09.
