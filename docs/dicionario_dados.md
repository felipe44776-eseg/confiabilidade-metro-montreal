# Dicionário de dados

Colunas dos derivados em `dados/derivados/`. Os CSVs usam `;` como separador e quebra de linha `\n`. Todo derivado é regenerado por um script do `pipeline/` e confere com o hash do manifesto (`fontes/fontes_manifesto.json`).

**Regra geral:** campo vazio quer dizer "sem medição" e nunca "zero". Um zero no arquivo é um zero medido.

## Fatores ausentes

Fatores que podem afetar a taxa de falha ou a oferta, mas que não têm fonte pública. Ficam **ausentes** em todos os modelos, nunca preenchidos com zero.

| Fator | Situação | Onde procuramos | Efeito no projeto |
|---|---|---|---|
| Passageiros diários por linha ou estação | ausente | Portal de dados abertos da STM, relatórios anuais (só total anual por estação), Google Mobility (até 2022-10, índice e não contagem) | A rede é ponderada pela oferta (trens-hora), não por passageiros (specs 009 e 014) |
| Fechamentos planejados (obras de fim de semana) | ausente | Avisos da STM (só os atuais, sem histórico) | Um fechamento planejado pode aparecer como hora sem falha. Risco declarado na spec 005 |
| Quedas de energia (Hydro-Québec) | ausente | Hydro-Québec publica só as interrupções em curso | Entram de forma indireta, pelas falhas de equipamento fixo registradas pela STM |
| Alertas meteorológicos históricos | ausente | ECCC guarda cerca de 50 dias | Usamos limiares próprios, declarados na spec 005 |
| Posição das subestações de tração | ausente | OpenStreetMap e STM | 4,8% dos locais de falha ficam sem coordenada (spec 002) |
| Festivais e eventos sem fonte estruturada | ausente | — | Só jogos do Canadiens e GP de F1 entram |
| Tempo de reparo na oficina | ausente | Arquivo de incidentes da STM (só traz o tempo até o serviço voltar) | Hipótese ajustável de 0,5 a 4 dias, com análise de sensibilidade (spec 008) |
| Aparelhos de mudança de via (posição) | não verificado | OpenStreetMap (`railway=switch` incompleto no túnel) | Retorno parcial só nos terminais, como hipótese (spec 008) |
| Blocos de trem (`block_id`) e frequências | ausente | GTFS da STM | Trens seguem viagens individuais do horário (spec 007) |
| Demanda por par origem-destino | ausente | STM, ARTM | Disponibilidade por par ponderada pela oferta (specs 009 e 014) |
| Condição do tempo em todas as horas | parcial (45,8% das horas de operação) | ECCC 51157 | Categoria `sem_dado` no modelo, nunca "seco" (spec 005) |

## `eventos/` (spec 001, `pipeline/normaliza.py`)

Um registro por incidente do arquivo de incidentes da STM, com horário normalizado.

| Coluna | Significado |
|---|---|
| `id` | Número do incidente na STM |
| `linha` | Linha única (`verde`, `laranja`, `amarela`, `azul`) ou vazio se o incidente cita várias |
| `linhas` | Todas as linhas citadas, separadas por `,` |
| `causa` | `MR` (material rodante), `EF` (equipamento fixo) ou outra causa da STM, traduzida |
| `causa_secundaria`, `sintoma`, `tipo` | Campos originais da STM |
| `frota` | `MR-73`, `MPM-10` ou vazio |
| `fonte` | Fonte de falha (spec 017, D56): `mr73`, `mpm10`, `mr_outros` (veículos de trabalho, causa genérica e frota com menos de 2% dos km da linha) no material rodante; `voie_sintoma_trem`, `voie_sintoma_fixo`, `aux_trains_sintoma_trem`, `aux_trains_sintoma_fixo`, `aux_stations` e `tcpe` nos equipamentos fixos. Os nomes seguem as etiquetas da STM |
| `data_servico` | Dia de serviço da STM (um serviço que passa da meia-noite pertence ao dia anterior) |
| `inicio_local`, `fim_local` | Início e retomada na hora de Montreal, sem o deslocamento no texto (`AAAA-MM-DDTHH:MM`). O fim usa `duracao_min` |
| `inicio_utc`, `fim_utc` | Mesmos instantes em UTC |
| `duracao_min` | Minutos até o serviço voltar, depois da regra da faixa oficial (D55, `pipeline/duracao.py`): vale a calculada, salvo quando ela cai fora da faixa oficial e da vizinha; aí vale uma duração sorteada entre as coerentes da mesma faixa e família (revisão de 2026-11) |
| `duracao_calculada_min` | Retomada menos início, como na v1.1.0. Se a retomada passa da meia-noite sem data, soma-se 1.440 |
| `duracao_ponto_medio_min` | Sensibilidade: o centro da faixa oficial nas exceções |
| `regra_duracao` | `calculada` ou `faixa` (exceção em que vale a faixa oficial) |
| `faixa_oficial` | Faixa de duração publicada pela STM (`Incident en minutes`) |
| `na_faixa`, `na_faixa_vizinha` | `1` se a duração calculada cai na faixa oficial ou na faixa ao lado |
| `virada_de_dia` | `1` se a retomada cai no dia civil seguinte |
| `classe_gravidade`, `classe_faixa_oficial` | Classe pelos limites da STM (D58): `menos_de_5`, `5_a_10`, `10_a_30`, `30_ou_mais`; pela `duracao_min` e pela faixa oficial |
| `veiculo`, `local_codigo`, `evacuacao` | Campos originais da STM |
| `cat`, `porta`, `kfs`, `urgencia`, `dano` | `1` ou `0`: corte de tração (CAT), porta, KFS, urgência metrô e dano material, campos originais da STM |
| `tipo_materiel` | Campo original `Type de matériel` (`73`, `10`, `Non affecté`), segunda fonte da frota |
| `motivo` | Só em `excecoes.csv`: por que o registro não passou na conferência |

Arquivos: `eventos_tecnicos.csv` (MR e EF de uma linha), `eventos_causa_comum.csv` (mais de uma linha), `eventos_sem_linha.csv`, `excecoes.csv`, `resumo_normalizacao.json`.

## `clima/` (spec 003, `pipeline/clima_eventos.py`)

### `painel_horario.csv`: uma linha por hora de 2019-01-01 a 2026-06-30

| Coluna | Significado |
|---|---|
| `inicio_utc` | Início da hora em UTC. A sequência é contínua, sem hora repetida nem faltando |
| `local` | O mesmo instante na hora de Montreal, com o deslocamento. Na volta do horário de verão a 01:00 aparece duas vezes, com `-0400` e `-0500` |
| `data_servico`, `hora_servico` | Dia e hora de serviço da STM. De 00h a 03h a hora conta no dia anterior como 24 a 27 |
| `temp_c`, `sensacao_c`, `vento_kmh` | Estação 51157 (MONTREAL INTL A). A temperatura usa a 30165 e a 10761 de reserva. Sensação térmica é o wind chill ou o humidex do ECCC, ou a temperatura se nenhum vier |
| `precip_mm` | Precipitação da hora. Estação 10761 (McTavish), com a 30165 (aeroporto) de reserva |
| `estacao_precip` | Qual estação deu a precipitação daquela hora |
| `condicao` | Campo `Weather` do ECCC (51157), preenchido em cerca de 46% das horas |
| `chuva`, `neve`, `chuva_congelante` | `1` ou `0` a partir de `condicao`. Vazios quando `condicao` está vazia |
| `neve_solo_cm` | Neve no solo do dia (clima diário da 51157) |
| `jogo_canadiens` | `1` de 1 h antes a 3 h 30 depois do início de um jogo em casa (janela é hipótese) |
| `gp_f1_fim_de_semana` | `1` de sexta a domingo do GP no circuito Gilles-Villeneuve |
| `feriado` | Feriado nacional ou do Quebec (Nager.Date, `CA-QC`) |
| `fracao_servico` | Fração da hora com serviço. Abaixo de 1 só em dias de greve. Hora com 0 vira exposição zero, não "hora sem falha" |

**Fuso:** o ECCC publica em hora padrão local (LST, UTC−5 fixo). O painel converte LST para UTC e depois para a hora de Montreal com `tzdata`. O episódio de chuva congelante de 2023-04-05, das 09h às 20h em LST, aparece das 10h às 21h na hora local (horário de verão).

### `eventos_externos.csv`

| Coluna | Significado |
|---|---|
| `tipo` | `greve_stm`, `jogo_canadiens` ou `gp_f1` |
| `data_servico`, `inicio_local`, `fim_local` | Data e faixa horária do evento |
| `fonte_url` | Origem do dado |
| `status` | `verificado` (API oficial da liga) ou `não verificado` (imprensa, base comunitária) |
| `observacao` | Hipóteses usadas, como a janela em volta do jogo |

## `exposicao/` (spec 004, `pipeline/exposicao.py`)

| Arquivo e coluna | Significado |
|---|---|
| `perfil_horario.csv`: `linha`, `tipo_dia`, `hora`, `trens_hora`, `trem_km`, `fonte` | Trens em viagem e trem-km por hora num dia típico, a partir do GTFS da STM |
| `exposicao_diaria.csv`: `fator` | Quanto o dia rodou em relação ao molde do GTFS |
| `exposicao_diaria.csv`: `status` | `medido` (km real da STM; até 2026-06 desde a revisão de 2026-11, até 2023-09 na v1.1.0) ou `estimado` (molde do GTFS) |
| `frota_diaria.csv`: `linha`, `data_servico`, `frota`, `km_carro`, `parcela_km_linha` | Km-carro de cada frota no dia e a parcela dela nos km da linha (spec 018). A taxa do material rodante usa trens-hora × parcela |
| `frota_mensal.csv`: `parcela_km_linha`, `status`, `fonte` | O mesmo por mês, com o status. Com o km real até 2026-09, todos os meses são `medido`; a dedução pelas falhas rotuladas, prevista na spec 018 para meses sem medida, não foi necessária |
| `exposicao_diaria.csv`: `greve`, `janelas_com_servico` | Dias de greve e faixas com serviço |
| `calibracao_mensal.csv`: `erro_relativo` | (estimado − real) / real por linha e mês |

## Outros derivados

| Pasta | Conteúdo | Script |
|---|---|---|
| `geo/` | Traçado das linhas, estações e locais de falha com coordenadas | `pipeline/geo_base.py` (spec 002) |
| `gtfs/` | Recorte do GTFS da STM só com o metrô | `pipeline/extrai_gtfs_metro.py` |
| `painel/` | Tabelas do painel de confiabilidade | `pipeline/analise_confiabilidade.py` |
| `modelos/` | Modelos de taxa e distribuições: `taxa_MR.json` e `taxa_EF.json` (por família), `taxa_fontes.json` (por fonte, revisão de 2026-11), `vetores_bootstrap.json.gz` (réplicas com as mesmas semanas em todos os modelos), `distribuicoes.json`, `painel_modelo.csv.gz` | `pipeline/modelo_taxa.py`, `pipeline/distribuicoes.py` (specs 005, 006 e 018) |
| `simulador/` | `rede.json` (estações e horário), `parametros.json` (contrato v2 desde a revisão de 2026-11: `fontes[]` por linha e `frota_por_linha`; esquema em `contratos/parametros.schema.json`) e `revalidacao.json` (spec 020) | `pipeline/horario_simulador.py`, `pipeline/parametros.py`, `app/relatorios/revalidacao.relatorio.ts` |
