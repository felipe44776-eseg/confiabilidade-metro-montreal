# 002 — Base geoespacial: tarefas

- [x] Consulta Overpass guardada em `dados/brutos/osm/overpass_metro_mtl.json` (8 relações, 69 estações; base de 2026-10-21 01:07 UTC).
- [x] Consulta SPARQL ao Wikidata guardada em `dados/brutos/wikidata/estacoes_metro_mtl.json`.
- [x] Comprimento oficial conferido na Wikipedia francesa (22,1 / 30,0 / 4,25 / 9,7 km).
- [x] `pipeline/geo_base.py`: traçado, estações com km, locais com status e relatório de validação.
- [x] Tabela de apelidos (7 entradas) para grafias divergentes entre GTFS, OSM, Wikidata e incidentes; 73 de 73 estações casadas com OSM e Wikidata.
- [x] Teste de coerência dos `xSyy`: 100% nos 5 códigos.
- [x] Reprodutibilidade: duas execuções seguidas dão arquivos idênticos.
- [x] Recálculo independente em `verifica_fontes.py`: 73 estações, 8.530 falhas somadas em `locais.json`, 561 falhas no 4S50.
- [x] Página `/mapa/` com testes (`app/tests/locais.test.ts`: soma de 8.530, nenhum ponto em (0, 0), status coerente).
- [ ] Publicar no site e conferir a página `/mapa/` no endereço público.
- [ ] Pedir à STM a posição das subestações (opcional; levaria a cobertura acima de 98%).
