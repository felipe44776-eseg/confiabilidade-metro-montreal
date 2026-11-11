# 017 — Fontes de falha e durações pela faixa oficial

**Status:** implementada
**Fase:** revisão de 2026-11
**Depende de:** 000, 001
**Revisa:** 001 (normalização)
**Origem:** reunião de 2026-10-27 (perguntas: fabricantes, via ou trem, tipo de falha, sistemas separados) e revalidação de 2026-11-10 (decisões D55, D56 e D58)

## Pergunta de engenharia

De que parte do sistema vem cada falha técnica (frota do trem ou setor do equipamento fixo) e quanto tempo ela parou o serviço, quando a duração calculada pelos horários contradiz a faixa oficial da STM?

## Contexto

- Até a v1.1.0, cada falha técnica tinha só a causa primária, MR (material rodante) ou EF (equipamentos fixos). O CSV da STM tem mais:
  - a causa secundária: no MR, a frota (MR-73, MPM-10, veículos de trabalho); no EF, o setor (Service de la voie, Service aux trains, Service aux stations, Service TCPE);
  - o sintoma, isto é, a causa atribuída na hora, antes da análise (dicionário nos metadados CKAN do conjunto);
  - as marcas de corte de tração (CAT), porta, freio de emergência (KFS), equipe de urgência e dano.
- A duração vem dos horários de início e de retomada do "délai service clientèle". Em 100 das 8.530 falhas (1,2%), ela cai fora da faixa oficial "Incident en minutes" e da faixa vizinha, e essas 100 somam 25% de todos os minutos (11.129 de 43.971).
  - Exemplo: 7 falhas de 1.140 a 1.170 min em Saint-Michel (Azul, outubro de 2024), 6 delas com faixa oficial "02 min et moins".
  - Com elas, a média por falha de equipamento fixo da Azul é 21,9 min; pela faixa oficial, 6,0.
  - O critério da spec 001 media as exceções por contagem e não viu o peso em minutos.
- Os indicadores da STM só contam interrupções de 5 minutos ou mais. Os outros limites publicados são alerta aos usuários acima de 10 min e ônibus substituto acima de 30 min.
- Em 2024, 516 falhas de via com sintoma de material rodante, quase todas de zero minuto, concentraram-se nos terminais de maio a dezembro. Nos demais anos foram de 6 a 139.

## Critérios de aceite

- **Fonte de cada falha:** dada cada falha técnica de uma linha e cada evento de causa comum, quando normalizados, então recebem uma fonte pela regra da D56:
  - trem: `mr73` e `mpm10`; e `mr_outros` para veículos de trabalho, causa secundária genérica e frota fora da sua linha (parcela abaixo de 2% do km da linha);
  - fixo: cada setor se divide em sintoma de trem e sintoma fixo quando cada parte tem 400 falhas ou mais, e fica inteiro se não tiver.
  
  A soma das fontes é igual ao total, e continuam 8.530 falhas de uma linha, 45 de causa comum (31 com Verde e Laranja) e 44 sem linha.
- **Frota:** dado o campo da causa secundária, quando comparado ao campo "Type de matériel", então as discordâncias são contadas e listadas no relatório.
- **Virada de dia:** dada uma falha cuja retomada cai no dia seguinte, quando normalizada, então ela fica marcada.
  - Na conferência de 2026-11-10 eram 27: 19 coerentes com a faixa oficial (falhas que cruzam a meia-noite) e 8 fora dela, já cobertas pela regra de exceção.
  - A marca não muda a duração.
- **Duração pela faixa oficial (D55):**
  - Dada uma falha fora da faixa oficial e da vizinha, quando a duração é definida, então ela é sorteada, com semente fixa, entre as durações coerentes da mesma faixa oficial e da mesma família (trem ou fixo), zeros incluídos.
  - Na faixa "30 min et plus", vale a calculada; as de 300 min ou mais aparecem listadas no relatório.
  - A duração calculada continua guardada.
- **Peso das exceções em minutos:** dado o relatório, quando publicado, então mostra o número de exceções e os minutos delas antes e depois da regra, por linha e família.
- **Sensibilidade:** dado o total de minutos por linha × família, quando calculado com a regra, com o ponto médio da faixa e com a duração calculada (v1.1.0), então as três versões aparecem lado a lado.
- **Gravidade (D58):** dada cada falha, quando normalizada, então recebe a classe pelos limites da STM (menos de 5, 5 a 10, 10 a 30, 30 min ou mais), pela duração final, e a classe pela faixa oficial. As duas contagens aparecem por fonte.
- **Mesma duração em todo lugar:** dado o painel do site e os números do `FONTES.md`, quando recalculados, então usam a mesma regra de duração do simulador.
- **Conferência independente (princípio IV):** dada a verificação das fontes, quando roda com `--recalcula`, então refaz com código próprio os minutos por linha pela regra e as contagens por fonte, sem diferença.

## Resultado (2026-11-10)

Código em `pipeline/duracao.py` (regra da faixa e classes), `pipeline/normaliza.py` (fontes, colunas e relatório) e `pipeline/km_real.py` (leitor dos dois formatos do km real). O painel do site (`monta_painel.py`, `analise_confiabilidade.py`) usa a mesma duração. Testes em `pipeline/tests/test_normaliza.py`; relatório [`fontes_e_duracoes.md`](../../fontes/verificacao/fontes_e_duracoes.md).

| Critério | Resultado |
|---|---|
| Fonte de cada falha; a soma é o total; contagens mantidas | **Atende**. 9 fontes: `mr73` 2.740, `mpm10` 1.191, `mr_outros` 51, `voie_sintoma_fixo` 969, `voie_sintoma_trem` 788, `aux_trains_sintoma_fixo` 1.534, `aux_trains_sintoma_trem` 695, `aux_stations` 420, `tcpe` 142. A regra dividiu a via e o Service aux trains; aux stations (0 com sintoma de trem) e TCPE (7) ficaram inteiros. Continuam 8.530, 45, 31 e 44 |
| Frota: causa secundária contra "Type de matériel" | **Atende**: nenhuma discordância (MR-73 = 73 nas 2.761; MPM-10 = 10 nas 1.196; veículos de trabalho e causa genérica = "Non affecté") |
| Virada de dia marcada | **Atende**: 27 (19 coerentes com a faixa, 8 exceções) |
| Duração pela faixa oficial | **Atende** (teste: toda exceção fica na própria faixa oficial; as demais mantêm a calculada). As 100 exceções passam de 11.129 a 562 minutos |
| Peso das exceções em minutos, por linha e família | **Atende** (relatório) |
| Sensibilidade: calculada, regra, ponto médio | **Atende**: 43.971, 33.404 e 33.476 minutos na rede |
| Gravidade pela duração e pela faixa oficial | **Atende**: 5 min ou mais em 1.983 falhas pela regra e 1.956 pela faixa oficial |
| Mesma duração no painel e no simulador | **Atende**: `duracao.py` usado pelos três scripts |
| Conferência independente | **Atende**: `verifica_fontes.py --recalcula` refaz os minutos por linha e as 9 contagens por fonte com código próprio, 0 diferenças |

## Fora de escopo

- Modelos de taxa e de duração por fonte: spec 018.
- Significado definitivo de "Service aux trains" e "Service TCPE": a STM não publica a definição, e o pedido a ccia@stm.info foi cancelado em 2026-11-11 (D65). As fontes usam as etiquetas da STM, e "controle de trens" e "energia" aparecem como dedução.

## Riscos e dependências

- A regra de divisão pelo sintoma e o limite de 400 foram escritos depois de ver as contagens por setor (D56, marcada assim). O limite vale para todos os setores, sem escolha caso a caso.
- O sorteio dentro da faixa repete durações da amostra. Por isso a versão com o ponto médio fica como sensibilidade.
