# Candidatas de expansão do metrô de Montreal (spec 014)

Arquivo: `dados/manuais/candidatas_expansao.csv`. Montado em 2026-10-21 (UTC). Todas as consultas e páginas usadas estão salvas em `dados/brutos/expansao/`, com URL, data e hash em `dados/brutos/expansao/manifesto.json`. Nenhuma coordenada foi digitada de memória: cada uma foi lida pelo script de montagem de uma resposta salva do Overpass (OSM, ODbL) ou do Wikidata (CC0).

## Formato do CSV

Separador `;`, UTF-8 sem BOM, fim de linha LF, 47 linhas de dados. Nenhum campo contém `;` nem aspas duplas. Dentro de um campo, `|` separa URLs e `·` separa observações.

Colunas: `candidata;tipo;proponente;ano;ordem;estacao;lat;lon;liga_a_existente;fonte_coord;fonte_url;status;observacao`.

- **ordem:** posição da estação no traçado (1 = a ponta indicada no resumo de cada candidata).
- **liga_a_existente:** nome da estação atual ligada a esta linha. Há dois casos:
  - **ponta:** `estacao` é diferente de `liga_a_existente`. Existe um trecho novo entre as duas (ex.: Vertières → Saint-Michel).
  - **correspondência no mesmo local:** `estacao` é igual a `liga_a_existente` (Mont-Royal, Place-des-Arts e Vendôme na Rosa). O nó deve ser fundido com a estação atual.
  - **Exceção:** `Vertières` na Rosa liga-se à Vertières da candidata `azul_anjou`, que ainda não existe. Ela só vira correspondência se a Azul estiver ativa no cenário.
- **Nomes das estações atuais** em `liga_a_existente`, com a `chave` correspondente em `dados/derivados/geo/estacoes.geojson`:

  | Nome | chave |
  |---|---|
  | Saint-Michel | STMICHEL |
  | Côte-Vertu | COTEVERTU |
  | Montmorency | MONTMORENCY |
  | Longueuil–Université-de-Sherbrooke | LONGUEUILUNIVERSITEDESHERBROOKE |
  | Mont-Royal | MONTROYAL |
  | Place-des-Arts | PLACEDESARTS |
  | Vendôme | VENDOME |

  Os nomes do GTFS diferem na grafia (ex.: "Berri-Uqam"); por isso a junção deve usar a chave.
- **fonte_coord:**
  - `osm:node/<id>`: nó exato, por exemplo o cruzamento de duas vias.
  - `osm:way/<id> (ponto)`: centróide de um polígono, ou ponto calculado sobre uma via.
  - `osm:relation/<id> (ponto)`: centro devolvido pelo Overpass.
  - `wikidata:Q…`: propriedade P625 do item.
- **status:**
  - `em obras (OSM)`: o canteiro está mapeado no OSM.
  - `hipótese de traçado`: o local vem de um texto que nomeia o lugar.
  - `hipótese de traçado (ponto derivado)`: a fonte só nomeia uma via ou um bairro, e o ponto saiu de uma regra geométrica descrita na observação.

## Método

1. Os documentos foram lidos por WebFetch ou baixados com curl, via Wayback Machine quando o site original não responde (o stm.info recusou a conexão; montrealgazette.com e web.archive.org bloqueiam o WebFetch). As citações entre aspas nas observações foram conferidas no HTML salvo.
2. As coordenadas vieram de 7 consultas Overpass (POST, com User-Agent do projeto) e de 1 consulta SPARQL ao Wikidata (itens ligados à rede Q392377 sem data de abertura anterior a 2027). Elas estão em `overpass_*.json` e `wikidata_*.json`, e a consulta exata de cada uma está no `.meta.json` ao lado.
3. A regra de coordenada depende da candidata:
   - **Azul:** centróide do polígono do canteiro de obra da estação (`landuse=construction`, "Station … - Ligne Bleue"). O item do Wikidata serviu de conferência.
   - **Rosa:** o Wikidata tem itens para as 29 estações. A coordenada do Wikidata foi aceita quando ficou a até 300 m da referência OSM do lugar citado pela Radio-Canada (cruzamento, estação de trem, prédio ou via homônima). Todas passaram; a maior distância foi a de Ville Saint-Pierre, 266 m. A estação 12 cita duas vias: o item fica a 315 m do cruzamento com De Lorimier e a 16 m do cruzamento com Papineau, e vale a menor.
   - **Amarela:** nó OSM do cruzamento citado pela RTL.
   - **Laranja:** nó OSM do cruzamento ou da estação REM. Para "Gouin", "Chomedey" e "Notre-Dame", usou-se um ponto derivado (regra na observação de cada linha).
4. **Extensão:** soma das distâncias geodésicas (Vincenty, WGS84) entre estações consecutivas, incluindo o trecho até a estação atual de cada ponta. É uma aproximação em linha reta: o túnel real é mais longo e inclui rabichos e garagens.

## Candidatas incluídas

### 1. `azul_anjou`: prolongamento da Linha Azul (Saint-Michel → Anjou)

- **Resumo:** obra em curso com 5 estações na rua Jean-Talon Est. A ordem a partir da ponta ligada a Saint-Michel é:
  1. Vertières (Pie-IX)
  2. Mary-Two-Axe-Earley (Viau)
  3. Césira-Parisotto (Lacordaire)
  4. Madeleine-Parent (Langelier)
  5. Anjou (cruzamento das autoroutes 40 e 25, terminal)

  Os nomes e cruzamentos estão no comunicado de 2025-09-09. Inauguração prevista para 2031, custo de 7,6 bilhões de dólares canadenses (Frequency News).
- **Responsáveis:** STM, com MTMD, ARTM, Ville de Montréal e SQI ("cinq organismes responsables", segundo o comunicado).
- **Fontes:**
  - https://montreal.ca/communiques-de-presse/les-femmes-et-les-communautes-seront-honorees-sur-le-futur-troncon-de-la-ligne-bleue
  - https://www.frequencynews.ca/news/montreal-announces-five-new-blue-line-stations/
  - OSM: https://www.openstreetmap.org/way/492375119 e https://www.openstreetmap.org/way/661617959 (túnel `railway=construction`, `construction=subway`, `opening_date`/`start_date=2031`)
  - Canteiros das estações: ways 1318477080, 1272359314, 1152539302, 1312128641 e 1311144318
- **Extensão estimada:** 5,72 km, aproximação. Por trecho: 1,14 + 0,94 + 1,03 + 1,18 + 1,44 km. O comunicado fala em 6 km; os dois ways de túnel no OSM somam 5,56 km, sem rabicho nem garagem.
- **Status:** em obras (OSM).
- **Ressalvas:**
  - O centróide do canteiro principal de Vertières fica a 100 m do eixo do túnel; as outras estações, a 24–46 m.
  - O item Wikidata de Anjou (Q52186144) está a **625 m** do canteiro OSM. O canteiro é coerente com o comunicado e com o túnel (30 m), por isso foi usado o OSM.
  - É um ramal: não cria caminho alternativo entre estações existentes.

### 2. `rosa_2017`: Linha Rosa (Projet Montréal)

- **Resumo:** 29 estações de Montréal-Nord (1, Léger/Langelier) a Lachine (29, Victoria/32e Avenue), na ordem e com os locais da Radio-Canada (2017-11-07).
- **Correspondências declaradas:**
  - Mont-Royal (Laranja, estação 13);
  - Place-des-Arts (Verde, estação 16);
  - Vertières, "connecterait la future station de la ligne bleue" (estação 7);
  - gare Vendôme (estação 22), integrada à estação de metrô Vendôme. A correspondência com a Laranja está explícita na en.wikipedia, não na Radio-Canada.
- **Proponente:** Projet Montréal. Proposta pela primeira vez por Sylvain Ouellet em 2011 e adotada por Valérie Plante na campanha de 2017.
- **Fontes:**
  - https://ici.radio-canada.ca/nouvelle/1065916/stations-ligne-rose-metro-localisation-projet-montreal-plante-ouellet (lista de estações)
  - https://fr.wikipedia.org/wiki/Ligne_rose_du_m%C3%A9tro_de_Montr%C3%A9al
  - https://en.wikipedia.org/wiki/Pink_Line_(Montreal_Metro)
  - Coordenadas: itens Wikidata Q52158653 a Q52158790
- **Extensão estimada:** 29,46 km, aproximação (a fr.wikipedia dá 29 km).
- **Status:** hipótese de traçado.
- **Ressalvas:**
  - A Radio-Canada avisa que "les lieux choisis sont sujets à changement".
  - Duas estações sem correspondência declarada ficam perto de linhas atuais: Greene a 155 m de Lionel-Groulx e Gare Centrale a 218 m de Bonaventure. Elas não foram marcadas como ligação. Se a equipe quiser testar, é uma hipótese a mais.
  - A Vertières da Rosa (Wikidata) fica a cerca de 140 m do canteiro da Vertières azul. As duas devem ser fundidas pelo nome.

### 3. `amarela_longueuil`: prolongamento da Linha Amarela em Longueuil

- **Resumo:** 6 estações, na ordem a partir da ponta ligada a Longueuil–Université-de-Sherbrooke:
  1. Joliette (Longueuil): Saint-Charles / Joliette
  2. Vieux-Longueuil: Saint-Charles / Saint-Sylvestre
  3. Chambly / Gentilly (cégep Édouard-Montpetit)
  4. Roland-Therrien / Gentilly
  5. Curé-Poirier / Roland-Therrien
  6. Jacques-Cartier / Roland-Therrien (terminal)

  É o traçado preliminar do estudo que a agglomération de Longueuil e a RTL entregaram à AMT em 2010 (10 sítios estudados, 6 retidos).
- **Fontes:**
  - https://web.archive.org/web/20120120003003/http://www.rtl-longueuil.qc.ca/pages/pr_LIGNE_4.htm
  - Contexto: https://web.archive.org/web/20121102021903/http://plan2020.amt.qc.ca/Major+projects (gabinete de projeto MTQ/AMT estudando a Amarela em Longueuil)
- **Extensão estimada:** 6,03 km, aproximação. A RTL cita uma estimativa de 2008 de "six kilomètres et quatre stations" até Roland-Therrien/Jacques-Cartier, e o estudo AMT de 2001 previa 4 estações em 4,7 km.
- **Status:** hipótese de traçado.
- **Ressalvas:**
  - "Joliette" é homônima da estação Joliette da Verde, daí o sufixo "(Longueuil)".
  - Em 2013 a STM estudou 6 estações com traçado "un peu différent", passando pela pointe de la Voie maritime (La Presse, 2013-05-30, https://web.archive.org/web/20171012065335/http://www.lapresse.ca/actualites/grand-montreal/201305/30/01-4655829-prolongement-du-metro-de-montreal-la-ligne-jaune-longueuil.php). Esse traçado não tem lista de locais.
  - A mesma reportagem diz que o prolongamento "n'est donc pas exploitable" sem aliviar Berri-UQAM.
  - É um ramal.

### 4. `laranja_bois_franc`: Laranja de Côte-Vertu a Bois-Franc

- **Resumo:** 2 estações, Poirier (Poirier / Marcel-Laurin) e Bois-Franc (correspondência com o REM).
- **Histórico:**
  - Plan de transport da Ville de Montréal (2008): "Prolonger la ligne 2 (orange) de Côte-Vertu à Bois-Franc".
  - AMT (2008): "une station" até o setor Bois-Franc.
  - Prefeita Plante (2020): "a 2.2-kilometre extension that stops at Poirier and at Bois-Franc".
  - Global News (2022): 1 km de túnel já escavado e 1,2 km restante. O ministro Bonnardel mandou estudar a ligação.
- **Fontes:**
  - https://web.archive.org/web/20120306064540/http://ville.montreal.qc.ca/portal/page?_pageid=4577,7769586&_dad=portal&_schema=PORTAL
  - https://web.archive.org/web/20080421231402/http://www.radio-canada.ca/regions/Montreal/2008/04/18/002-AMT-metro-prolongement_n.shtml
  - https://journalmetro.com/local/saint-laurent/2427050/reactions-to-plantes-orange-line-proposal/
  - https://globalnews.ca/news/8912676/orange-metro-line-extension-bois-franc-rem-station-closer
- **Extensão estimada:** 2,49 km, aproximação (Côte-Vertu–Poirier 1,38 km, Poirier–Bois-Franc 1,11 km). As fontes dizem 2,2 km.
- **Status:** hipótese de traçado.
- **Ressalvas:** é um ramal. A ligação com o REM fica fora da rede simulada.

### 5. `laranja_anel_artm_2019`: anel da Laranja Côte-Vertu → Montmorency (ARTM)

- **Resumo:** relatório da ARTM aprovado em 2019-06-18, com 5 estações. Na ordem a partir de Côte-Vertu:
  1. Poirier
  2. Bois-Franc
  3. Gouin
  4. Chomedey (Laval)
  5. Notre-Dame, perto da A-15 (Laval)

  O anel fecha em Montmorency. A Gazette cita custo de 4,3 bilhões de dólares canadenses e horizonte aproximado de 2031.
- **Fonte:** https://web.archive.org/web/20191010182703/https://montrealgazette.com/news/local-news/completing-montreal-metros-orange-line-loop-will-cost-an-estimated-4-3b (o relatório não foi acessado diretamente).
- **Extensão estimada:** 8,24 km, aproximação. Contando a partir de Poirier, onde termina o túnel já existente segundo o prefeito DeSousa, são 6,86 km. A Gazette fala em 6,4 km.
- **Status:**
  - hipótese de traçado: Poirier e Bois-Franc;
  - hipótese de traçado (ponto derivado): Gouin, Chomedey e Notre-Dame.
- **Regras dos pontos derivados:**
  - **Gouin:** ponto do boulevard Gouin Ouest sobre a reta Bois-Franc–Chomedey, a 3 m dela.
  - **Chomedey:** nó OSM `place=suburb` "Chomedey".
  - **Notre-Dame:** vértice do boulevard Notre-Dame a 4 m da A-15.
- **Ressalvas:**
  - É a única candidata oficial que fecha um ciclo grande entre estações existentes. A Laranja vira um anel.
  - Em 2013 a STM avaliou que um anel exigiria dividir a linha 2 em duas, por causa dos "événements perturbateurs" (falhas menores, portas bloqueadas, objetos na via). Segundo ela, "le prolongement de la ligne accentue la probabilité d'occurrences d'événements" (La Presse, https://web.archive.org/web/20171110214425/http://www.lapresse.ca/actualites/grand-montreal/201305/30/01-4655828-prolongement-du-metro-la-ligne-orange-montreal-et-laval.php). Isso é relevante para a modelagem de falhas da spec 014.

## Não incluídas

| Proposta | Motivo |
|---|---|
| Laranja via Carrefour Laval (Ville de Laval, infográfico do prefeito Boyer, 2026-07-27; https://www.narcity.com/fr/laval/prolongement-ligne-orange-laval-maire-partage-visuel) | O prefeito diz que o infográfico "ne constitue pas un tracé officiel". As estações do lado oeste são descritas só por boulevard ("sur les boulevards Curé-Labelle et Chomedey"), sem cruzamento. As duas vias passam a 468 m e 508 m da reta Carrefour Laval–Bois-Franc, então não há regra geométrica defensável. A ordem também diverge da versão CBC 2025 citada pela en.wikipedia, um vídeo não verificado. Topologicamente é o mesmo ciclo de `laranja_anel_artm_2019`. O lado leste é localizável no OSM: Centre Laval (relation 15607282), Centropolis (way 182703100) e Carrefour Laval (way 1130952604). O way OSM 1447753874 ("Prolongement Ligne Orange", `railway=proposed`, 2 nós, sem `source`) fica entre o Centropolis e o Carrefour Laval. |
| Anel da Laranja, cenário STM 2013 (8 estações, 42 km de linha, 40 estações) | Só Souvenir e Saint-Martin são nomeadas (La Presse 2013). |
| Propostas de Laval de 2007 (Vaillancourt, 6 estações) e 2011 (8 estações) | Citadas na en.wikipedia (Courrier Laval), mas as fontes não foram acessadas. |
| Amarela Berri-UQAM → McGill (AMT 2008; STM 2013; Québec solidaire 2018) | Duas estações sem nome nem local. É a proposta que fecha o ciclo Berri-UQAM–McGill com a Verde. **Recomendação:** avaliar como candidata livre Berri-UQAM ↔ McGill. Fontes: https://web.archive.org/web/20080421231402/http://www.radio-canada.ca/regions/Montreal/2008/04/18/002-AMT-metro-prolongement_n.shtml e a La Presse 2013 acima. |
| Amarela em Longueuil, versão da prefeitura (6,8 km, 6 estações, CJAD) | A página da CJAD não carregou (só navegação). Não verificada. |
| Linhas 3, 6 e 7 | O Wikidata as marca "annulé/abandonné"; não há proposta atual. |
| REM, REM de l'Est / Projet structurant de l'Est, tramway Centre–Lachine | Não são metrô STM: outra rede ou outro modo. |
| Azul até Pie-IX, uma estação (AMT 2008) | Substituída pela `azul_anjou`. |

## Divergências entre fontes

- **Azul:**
  - Extensão: 6 km (comunicado de 2025) contra 5,8 km (Gazette 2019), 5,56 km de túnel no OSM e 5,72 km calculados.
  - Custo e prazo: 4,5 bilhões de dólares canadenses e conclusão em 2026 (Gazette 2019) contra 7,6 bilhões e 2031 (Frequency News 2025 e OSM).
  - Anjou no Wikidata está 625 m fora do canteiro.
- **Rosa:**
  - A fr.wikipedia e o Wikidata dão outros nomes a pontos da lista da Radio-Canada: "Cégep Marie-Victorin" para Léger/Langelier (80 m), "Maurice-Duplessis" para Rolland, "Boulevard" para Jean-Talon/Pie-IX, "Métropolitaine" para Jarry/Pie-IX. A fr.wikipedia chama a estação 15 de "Stade Percival-Molson"; a Radio-Canada e o Wikidata, de "Jeanne-Mance".
  - Status: segundo a fr.wikipedia, Plante abandonou o projeto em 2021-10-06 em favor do REM. Segundo a en.wikipedia, ele seguia no plano oficial "as late as 2024".
  - Custo: 5,9 bilhões (en.wikipedia), 6 bilhões (fr.wikipedia) e "au bas mot cinq milliards" (Radio-Canada, citando 2011).
- **Anel da Laranja:**
  - Extensão: 6,4 km (Gazette) contra 8,24 km calculados.
  - Custo: 4,3 bilhões (título da Gazette) contra 4,5 bilhões (texto da en.wikipedia).
  - Estações novas: 5 (ARTM 2019), 8 (STM 2013) e 5 mais Bois-Franc (Laval 2026).
- **Bois-Franc:** 2,2 km (Plante 2020) contra 1 + 1,2 km (Global News 2022) e 2,49 km calculados. Em 2008, a AMT falava de uma estação; em 2020, eram duas.

## Nota para a spec 014

Pelo critério da spec (caminhos alternativos), `azul_anjou`, `amarela_longueuil` e `laranja_bois_franc` são ramais: o ganho esperado entre estações já existentes é **zero**, o que serve de teste de sanidade do método.

As candidatas que criam ciclos são:

- `laranja_anel_artm_2019`: anel Côte-Vertu–Montmorency;
- `rosa_2017`: ciclos Mont-Royal–Place-des-Arts–Vendôme com a Laranja e a Verde, e mais um com a Azul se `azul_anjou` estiver ativa;
- a candidata livre sugerida Berri-UQAM ↔ McGill.
