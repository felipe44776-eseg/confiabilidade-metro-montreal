# 014 — Expansão da rede: que linha construir para a rede ficar mais confiável

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 002, 006, 007, 009
**Origem:** pedido da equipe em 2026-10-21

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** Com a duração pela faixa oficial e as taxas por fonte, a Rosa com a Azul até Anjou passa a liderar as candidatas oficiais também sem retorno parcial, e a validação da Azul sai do limite. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

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

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D56, D57, D59 e D62; specs 019 e 020).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **O que mudou na entrada:**
  - nas 100 falhas em que a duração calculada contradiz a faixa oficial da STM, vale a faixa (D55; minutos das falhas técnicas de 43.971 para 33.404). Das 7 interrupções de quase 20 h em Saint-Michel (outubro de 2024), as 6 com faixa oficial "02 min et moins" saem da amostra de durações da Azul; fica a de 1.170 min, de faixa "30 min et plus" (spec 001);
  - as taxas vêm de 9 fontes (3 frotas no trem, 6 setor × sintoma no equipamento fixo; D56), ajustadas com a exposição medida até 2026-06 (D57, spec 018). O `parametros.json` passa de `sha256-scripts:70cf9c002aa2ba0a` para `sha256-scripts:489914bafbbe991e`.
- **O que mudou no método:**
  - cada trecho, da rede atual ou da candidata, recebe por família (trem e fixo) a soma das taxas das fontes da linha e a duração média das fontes ponderada pela taxa de cada uma (`familiaNaLinha` e `duracaoMediaMistura`; spec 019). Com os parâmetros da v1.1.0, a avaliação de expansão sai idêntica à referência gravada antes da mudança (spec 019): as diferenças abaixo vêm dos parâmetros;
  - *verificação exata (D62):* num grafo de três estações, com a linha A–M–B, a ligação nova A–B e trechos fora com probabilidade 0,01, 0,01 e 0,02, o método de estados com 200 mil amostras dá a indisponibilidade sem e com a ligação e o ganho a menos de 4 erros-padrão da enumeração dos 8 estados. O teste (`app/tests/motor/expansao.test.ts`) passou.
- **O que não mudou:** as 5 candidatas e os traçados, as 298 ligações até 3 km, a semente 20261021, os sorteios (200 mil por candidata, 50 mil por ligação da busca), os pesos pela oferta e as hipóteses de retorno parcial e de causa comum.

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| Disponibilidade origem-destino da rede atual | 99,236% (99,203 a 99,269) | 99,425% (99,397 a 99,453) |
| Minutos de par interrompido por ano, rede atual | 3.341 (3.196 a 3.485) | 2.515 (2.393 a 2.637) |
| *Ganho sem retorno parcial (p.p., IC 95%):* Rosa com a Azul até Anjou | +0,0028 (−0,0059 a 0,0116) | +0,0361 (0,0295 a 0,0427) |
| Rosa | +0,0208 (0,0197 a 0,0219) | +0,0165 (0,0156 a 0,0175) |
| Anel da Laranja | +0,0002 (0,0002 a 0,0002) | +0,0002 (0,0001 a 0,0002) |
| Amarela em Longueuil | −0,0054 (−0,0062 a −0,0047) | −0,0053 (−0,0060 a −0,0046) |
| Laranja até Bois-Franc | −0,0347 (−0,0420 a −0,0273) | −0,0288 (−0,0359 a −0,0218) |
| Azul até Anjou | −0,0753 (−0,0811 a −0,0695) | −0,0323 (−0,0362 a −0,0283) |
| *Ganho com retorno parcial (p.p., IC 95%):* Rosa com a Azul até Anjou | +0,0528 (0,0496 a 0,0559) | +0,0381 (0,0348 a 0,0414) |
| Anel da Laranja | +0,0186 (0,0162 a 0,0210) | +0,0211 (0,0191 a 0,0231) |
| Rosa | +0,0112 (0,0105 a 0,0120) | +0,0084 (0,0077 a 0,0091) |
| Os três ramais (Azul até Anjou, Amarela em Longueuil, Laranja até Bois-Franc) | 0,0000 | 0,0000 |
| Melhor ligação da busca: Atwater – Université-de-Montréal, ganho | +0,0850 (0,0771 a 0,0930) | +0,0629 (0,0541 a 0,0716) |
| Atwater – Université-de-Montréal, ganho por km | 0,02387 p.p./km | 0,01765 p.p./km |
| Segunda faixa da busca (ligações Verde–Laranja, ganho igual entre elas) | +0,0154 (0,0138 a 0,0169) | +0,0116 (0,0104 a 0,0128) |
| *Validação, estados menos camada diária (p.p.):* Verde | +0,020 | −0,013 |
| Laranja | −0,009 | −0,063 |
| Amarela | +0,010 | −0,018 |
| Azul | −0,095 | −0,025 |
| Meia largura do IC 95% da camada diária na Azul | 0,118 p.p. | 0,023 p.p. |

Detalhe em [`expansao.md`](../../fontes/verificacao/expansao.md) e `dados/derivados/simulador/expansao.json`.

- **Candidatas oficiais, busca, causa comum e ranking:** continuam atendendo. Nada disso depende das taxas.
- **Candidata livre:** continua atendendo no código da aba Expansão; a conferência no navegador fica com a spec 020.
- **Parâmetros de falha:** continua atendendo. Os trechos novos herdam a soma das fontes de cada família, com status "hipótese".
- **Validação:** passa a atender com folga na Azul. Sem as interrupções de quase 20 h que contradiziam a faixa, a diferença vai de −0,095 para −0,025 p.p., e o intervalo da camada diária encolhe de ±0,118 para ±0,023 p.p. A maior diferença passa a ser a da Laranja, −0,063 p.p., dentro do limite de 0,1. Os quatro sinais ficam negativos (o método de estados dá um pouco menos que a camada diária), e na Laranja os dois IC 95% não se sobrepõem por pouco: 99,560 a 99,617% no método de estados, 99,618 a 99,685% na camada diária.

**Resposta à pergunta, após a revisão.** A melhor ligação nova continua sendo Atwater (Verde) – Université-de-Montréal (Azul), pelo mesmo motivo: a Azul só se liga à rede pela Laranja. O ganho cai de +0,0850 para +0,0629 p.p., mas fica acima de todas as candidatas oficiais, com e sem retorno parcial, e ela continua primeira por km. Os ramais continuam sem ganho de redundância: zero com retorno parcial e perda sem ele, com IC inteiro abaixo de zero. O que muda é a ordem das oficiais sem retorno parcial: a Rosa com a Azul até Anjou passa de +0,0028, com IC que cruzava zero, para +0,0361 (0,0295 a 0,0427), e fica à frente da Rosa sozinha (+0,0165). Com a Azul sem as interrupções de quase 20 h que contradiziam a faixa, o prolongamento até Anjou perde menos (−0,0323 contra −0,0753 p.p.). Assim, o primeiro lugar entre as oficiais deixa de depender da hipótese de retorno parcial. O segundo ainda depende: a Rosa sem ela, o anel da Laranja com ela (+0,0211, o maior ganho por km entre as oficiais com retorno parcial, 0,00214 p.p./km). Com a rede atual mais disponível, a Rosa sozinha e as ligações da busca ganham menos; o anel da Laranja com retorno parcial ganha um pouco mais (+0,0186 para +0,0211).

## Fora de escopo

- Custo de construção em dinheiro: o ganho é dividido por km como medida aproximada de custo.
- Demanda induzida pela nova linha: não há dados de passageiros.
- Engenharia de traçado e geotecnia.

## Riscos e dependências

- **Traçados:** o prolongamento da Linha Azul está no OpenStreetMap como obra (`railway=construction`, `opening_date=2031`; consulta de 2026-10-21 em `dados/brutos/osm/overpass_expansao.json`), com status "em obras (OSM)". O prolongamento da Laranja aparece só como um trecho proposto de dois pontos. As demais propostas vêm de documentos públicos e ficam com status "hipótese de traçado".
- **Ponderação:** pela oferta, não por passageiros. Pode subestimar ligações em áreas de muita demanda e pouca oferta.

## Perguntas em aberto

- Quais candidatas oficiais entram? Proposta inicial: prolongamento da Azul até Anjou, linha Rosa, prolongamento da Laranja após Côte-Vertu e ligações livres que fecham ciclos entre as linhas existentes.
