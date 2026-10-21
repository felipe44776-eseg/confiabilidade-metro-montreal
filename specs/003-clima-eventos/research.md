# 003 — Pesquisa: clima horário e eventos

Achados da pesquisa de 2026-10-20 (agente de pesquisa, somente leitura). Cada item diz se foi verificado pela pesquisa ou não. Nada aqui foi baixado para o repositório ainda.

## Clima horário do ECCC

- URL testada: `https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={ID}&Year={A}&Month={M}&Day=1&timeframe=1&submit=Download+Data`. Um CSV por mês, 31 colunas. Licença: Licença de Governo Aberto do Canadá. Verificado pela pesquisa de 2026-10-20.
- Colunas principais: `Date/Time (LST)`, `Temp (°C)`, `Dew Point`, `Rel Hum`, `Precip. Amount (mm)`, `Wind Dir/Spd`, `Visibility`, `Stn Press`, `Hmdx`, `Wind Chill`, `Weather`.
- Estação 51157 (MONTREAL INTL A): precipitação vazia em todas as horas dos meses de junho testados (2019, 2022, 2025, 2026). Temperatura e vento completos. `Weather` preenchido em cerca de 40 a 55% das horas, com "Freezing Rain" confirmado em 2023-04-05 das 09h às 20h. Verificado pela pesquisa de 2026-10-20.
- Estações com precipitação horária completa, testadas de 2019 a 2026-06: 30165 (MONTREAL/PIERRE ELLIOTT TRUDEAU INTL), 10761 (MCTAVISH, centro da cidade) e 48374 (ST-HUBERT, com `Weather` parcial). Também tem precipitação a 5237 (L'ASSOMPTION). Nenhuma das três primeiras tem `Weather`. Verificado pela pesquisa de 2026-10-20.
- Fuso: LST, ou seja UTC−5 o ano todo. No horário de verão é preciso tirar 1 h da hora local do incidente antes de juntar.

## Alternativas de clima

- Open-Meteo, `https://archive-api.open-meteo.com/v1/archive`: precipitação, chuva, neve, profundidade de neve, código de tempo e vento por hora, de 2019-01-01 a 2026-06-30. Licença CC BY 4.0. Plano gratuito não comercial: 600 chamadas por minuto, 5.000 por hora, 10.000 por dia, 300.000 por mês. É reanálise: marcou chuva comum no dia da chuva congelante de 2023. Verificado pela pesquisa de 2026-10-20. Termos: https://open-meteo.com/en/terms
- Pluviômetros da Ville de Montréal, conjunto `pluviometrie-quantite-precipitation`, de 2004 até hoje, CC BY 4.0. Só os metadados foram confirmados; o CSV deu 403 por linha de comando. Não verificado.

## Eventos extremos

- Datamart e HPFX do ECCC guardam cerca de 50 dias (o HPFX começava em 2026-08-30). Não há arquivo público de alertas. Verificado pela pesquisa de 2026-10-20.
- Limiares oficiais de evento extremo: não verificados.

## Greves da STM (fonte: imprensa)

- 9 a 17 de junho de 2025, manutenção, com pausa de 13 a 15 para o GP. Dias 9 a 11 e 16 a 17: serviço das 6h30 às 9h38, das 14h45 às 17h48 e das 23h à 1h. Dia 12: 6h30 às 10h38, 14h45 às 18h48 e 23h à 1h. Fonte: https://www.noovo.info/nouvelle/horaire-complet-du-metro-et-des-bus-de-la-stm-pendant-la-greve.html
- 22 de setembro a 5 de outubro de 2025, só segundas, quartas e sextas: 6h30 às 9h30, 14h45 às 17h45 e 23h até cerca de 1h15. Fonte: https://www.timeout.com/fr/montreal/nouvelles/stm-prevoit-une-nouvelle-greve-a-montreal-avec-dimportantes-interruptions-de-service-et-des-entrees-de-stations-bloquees-091125
- Novembro de 2025: greve a partir de 31/10 às 22h, com faixas de 6h30 às 9h30, 14h45 às 17h45 e 23h ao fechamento; em 01/11 não houve serviço; suspensa em 12/11 às 6h. Fontes: https://www.timeout.com/fr/montreal/nouvelles/greve-de-la-stm-a-montreal-en-novembre-horaires-heures-de-service-et-fermetures-de-stations-aucune-circulation-pendant-une-journee-103125 e https://www.timeout.com/fr/montreal/nouvelles/cest-officiel-la-greve-a-la-stm-se-termine-a-montreal-avec-reprise-progressive-mais-un-service-zero-possible-ce-week-end-111225
- 11/12/2025 a 11/01/2026: greve de horas extras, com horário normal do metrô. Fonte: https://www.narcity.com/fr/montreal/greve-employes-entretien-stm-decembre-janvier
- Acordo com os motoristas: https://www.noovo.info/nouvelle/reprise-du-service-entente-de-principe-entre-les-conducteurs-de-bus-et-de-metro-et-la-stm.html
- Greves depois de janeiro de 2026: não verificado.

## Grandes eventos

- Jogos do Canadiens: `https://api-web.nhle.com/v1/club-schedule-season/MTL/20242025` funciona e traz `gameDate`, `startTimeUTC`, `venue` e `gameType` (2 temporada regular, 3 playoffs). 47 jogos em casa em 2024-25; testada de 2018-19 a 2025-26. API não documentada, sem licença explícita. Verificado pela pesquisa de 2026-10-20.
- GP de F1: `https://api.jolpi.ca/ergast/f1/circuits/villeneuve/races.json`, datas 2019-06-09, 2022-06-19, 2023-06-18, 2024-06-09, 2025-06-15 e 2026-05-24; sem GP em 2020 e 2021. Verificado pela pesquisa de 2026-10-20.
- Eventos públicos da Ville de Montréal, conjunto `evenements-publics`, de 2023 até hoje, CC BY 4.0: é o calendário municipal, não os festivais. Download bloqueado por linha de comando (403). Só metadados.
- Festivais (Jazz, Juste pour rire, Osheaga): sem fonte estruturada. Não verificado.

## Fechamentos, energia e demanda

- Fechamentos planejados do metrô: não há lista histórica, só comunicados avulsos.
- Quedas de energia da Hydro-Québec: só o mapa ao vivo; histórico só por pedido de acesso à informação. Exemplo de resposta: https://pannes.hydroquebec.com/data/loi-sur-acces/pdf/DAI-2025-0083-lettre-reponse.pdf
- Passageiros: tabela 23-10-0307-01 da Statistique Canada, viagens mensais da STM (ônibus e metrô juntos, em milhares), de 2023-01 a 2026-07; exemplo 2026-06 = 36.464,5. Obtida pela WDS com a coordenada `1.6.1.2.0.0.0.0.0.0`. Verificado pela pesquisa de 2026-10-20. A tabela 23-10-0251 começa em 2017, mas só por região.
- Passageiros diários: não existe série pública.
- Calendário universitário: a McGill mostra só 2026-27; UdeM e Concordia não verificados.
