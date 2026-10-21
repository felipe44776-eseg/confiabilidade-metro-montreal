# 014 — Expansão da rede: que linha construir para a rede ficar mais confiável

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 002, 006, 007, 009
**Origem:** pedido da equipe em 2026-10-21

## Pergunta de engenharia

Entre as ligações que podem ser construídas, qual aumenta mais a confiabilidade da rede como sistema? O número que responde é o ganho de disponibilidade por par origem-destino (ponderada pela oferta) e a redução dos minutos de par interrompido por ano, com intervalo de 95%, também dividido pelo km construído.

## Contexto

- **Rede atual:** quatro linhas e quatro estações de correspondência (Lionel-Groulx, Berri-UQAM, Snowdon, Jean-Talon). Só o centro tem caminho alternativo: a Verde e a Laranja ligam Lionel-Groulx a Berri-UQAM.
- **Painel:** o caminho alternativo derruba a indisponibilidade do corredor de 1.797 para 6,9 minutos por ano se as falhas forem independentes, mas a causa comum a mantém em 107 (FONTES.md).
- **Interpretação:** em confiabilidade de redes, uma nova ligação vale pelos caminhos alternativos que cria, não só pela cobertura.

## Critérios de aceite

- **Candidatas oficiais e propostas:** dado o conjunto de candidatas publicadas (projetos e propostas da STM, da cidade ou do governo), quando avaliado, então cada uma tem traçado aproximado, fonte e status "hipótese de traçado".
- **Candidatas livres:** dadas duas estações escolhidas na interface, quando ligadas por uma candidata livre, então a avaliação roda do mesmo jeito.
- **Busca:** dada a lista de todas as ligações possíveis entre pares de estações até uma distância máxima, quando a busca roda, então o resultado é um ranking por ganho de disponibilidade e por ganho por km.
- **Parâmetros de falha:** dada uma candidata, quando simulada, então seus trechos herdam taxas de falha e tempos até restabelecer ajustados nas linhas existentes, por km e por trem-hora, com status "hipótese".
- **Causa comum:** dada a causa comum, quando a candidata compartilha alimentação ou controle com outra linha, então o efeito pode ser ligado ou desligado, e o relatório mostra o ganho com e sem causa comum.
- **Ranking:** dado o ranking, quando publicado, então cada candidata mostra o ganho com intervalo de 95%, o número de rodadas, a semente e as hipóteses usadas.
- **Validação:** dada a rede atual sem candidata, quando avaliada pelo mesmo método, então a disponibilidade por linha bate com a do simulador (spec 009) a até 0,1 ponto percentual.

## Resultado (2026-10-21)

Código em `app/src/motor/expansao.ts` e `grafo.ts`, conversão das candidatas em `app/src/simulador/candidatas.ts`; relatório [`expansao.md`](../../fontes/verificacao/expansao.md) gerado por `app/relatorios/expansao.relatorio.ts`; candidatas em `dados/manuais/candidatas_expansao.csv` (LEIAME com as fontes).

| Critério | Resultado |
|---|---|
| Candidatas oficiais e propostas com traçado aproximado, fonte e status | **Atende**: 5 candidatas, 47 estações com coordenadas de consultas salvas ao OSM e ao Wikidata; Azul até Anjou "em obras (OSM)", as demais "hipótese de traçado" |
| Candidata livre entre duas estações | **Atende** na aba Expansão |
| Busca exaustiva com ranking por ganho e por ganho/km | **Atende**: 298 ligações até 3 km em linha reta |
| Trechos novos herdam taxas e durações das linhas existentes, como hipótese | **Atende** |
| Causa comum compartilhada liga e desliga | **Atende**: o ganho sai com e sem |
| Ranking com IC 95%, sorteios, semente e hipóteses | **Atende** |
| Rede atual: disponibilidade por linha bate com o simulador diário a até 0,1 p.p. | **Atende, no limite na Azul**: Verde 0,020, Laranja −0,009, Amarela 0,010 e Azul −0,095 p.p. com o `parametros.json` real (4.000 dias úteis contra 200 mil sorteios); a camada diária da Azul tem intervalo largo por causa das interrupções de quase 20 horas |

Resposta à pergunta (dia útil, métrica de pares de estações atuais ponderados pela oferta): a melhor ligação nova é Atwater (Verde) – Université-de-Montréal (Azul), porque a Azul hoje só se liga à rede pela Laranja. Entre as candidatas oficiais, a Linha Rosa e o anel da Laranja criam caminhos alternativos e dão ganho; os ramais (Azul até Anjou, Amarela em Longueuil, Laranja até Bois-Franc) não dão ganho de redundância e, sem retorno parcial, reduzem a disponibilidade. O resultado depende da hipótese de retorno parcial: com ela, Rosa com a Azul até Anjou fica em primeiro. Fora do escopo: cobertura de bairros novos e demanda (não há dado de passageiros).

## Fora de escopo

- Custo de construção em dinheiro: o ganho é dividido por km como medida aproximada de custo.
- Demanda induzida pela nova linha: não há dados de passageiros.
- Engenharia de traçado e geotecnia.

## Riscos e dependências

- **Traçados:** o prolongamento da Linha Azul está no OpenStreetMap como obra (`railway=construction`, `opening_date=2031`; consulta de 2026-10-21 em `dados/brutos/osm/overpass_expansao.json`), com status "em obras (OSM)". O prolongamento da Laranja aparece só como um trecho proposto de dois pontos. As demais propostas vêm de documentos públicos e ficam com status "hipótese de traçado".
- **Ponderação:** pela oferta, não por passageiros. Pode subestimar ligações em áreas de muita demanda e pouca oferta.

## Perguntas em aberto

- Quais candidatas oficiais entram? Proposta inicial: prolongamento da Azul até Anjou, linha Rosa, prolongamento da Laranja após Côte-Vertu e ligações livres que fecham ciclos entre as linhas existentes.
