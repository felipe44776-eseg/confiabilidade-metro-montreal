# Registro de decisões do projeto

Todas as decisões que moldaram o trabalho, em ordem de fase, com o motivo, as alternativas e onde está o registro detalhado. Decisões tomadas **depois de ver um resultado** estão marcadas assim, porque a regra do projeto é não ajustar o critério ao resultado (constituição, princípio 7): quando algo mudou depois de visto, a mudança ficou registrada com data e a versão anterior continua publicada.

Formato de cada item: **Decisão** · **Por quê** · **Alternativas** · **Consequência** · **Registro**.

---

## Fase de escolha do tema (2026-10-13 a 2026-10-20)

### D01 — Tema: metrô de Montreal (STM)

- **Decisão:** estudar a confiabilidade e a tolerância a falhas das quatro linhas do metrô de Montreal.
- **Por quê:** a STM publica em dados abertos (CC BY 4.0) cada incidente de 2019 a 2026 com dia, hora de início e de retomada, causa, linha, veículo e local. Poucas redes publicam isso de forma estruturada.
- **Alternativas:** trilhos de São Paulo (Metrô, CPTM e ViaQuatro só publicam PDF; a API Direto dos Trens exige token, pedido por e-mail); linha de produção com dados do Zenodo (plano B); outras redes europeias (sem série de falhas utilizável).
- **Consequência:** dados reais e verificáveis; a parte de passageiros fica sem dado diário.
- **Registro:** `ESTADO.md` (privado), memória do projeto, `fontes/FONTES.md`.

### D02 — Publicar o painel no GitHub Pages, não só no Claude

- **Decisão:** o painel de confiabilidade passou a ser um site público.
- **Por quê:** o artefato do Claude exigia conta para abrir; a equipe e o professor precisam de um link aberto.
- **Consequência:** repositório público `felipe44776-eseg/confiabilidade-metro-montreal`, na conta da ESEG.

### D03 — Proveniência verificável antes de qualquer modelo

- **Decisão:** documentar cada fonte com link, editor, licença e SHA-256 (`fontes/FONTES.md` e `fontes/fontes_manifesto.json`), e escrever uma segunda implementação independente que recalcula os números publicados direto dos dados brutos (`pipeline/verifica_fontes.py`, Python puro, sem importar o pipeline).
- **Por quê:** a equipe temia que os números fossem alucinação de IA.
- **Alternativas:** confiar no script de análise; auditoria manual.
- **Consequência:** 25 números recalculados a cada publicação; uma auditoria independente (um agente sem acesso aos scripts) refez os números e não achou divergência.
- **Registro:** `fontes/FONTES.md` (seção "Auditoria independente"), `specs/000-proveniencia/`.

---

## Fase 0: fundação (2026-10-21)

### D04 — Spec-Driven Development

- **Decisão:** cada parte do projeto tem `spec.md` (pergunta, critérios de aceite mensuráveis, sem tecnologia), `plan.md` e `tasks.md`, no formato do GitHub Spec Kit, e uma constituição com 16 princípios.
- **Por quê:** separar o que se quer medir de como medir, e impedir que o critério mude depois do resultado.
- **Consequência:** 15 specs; critério não atendido vira "implementada com exceções", nunca critério afrouxado.
- **Registro:** `specs/README.md`, `specs/constitution.md`.

### D05 — Site estático e simulação no navegador

- **Decisão:** tudo no GitHub Pages; motor do simulador em TypeScript rodando no navegador; Python só para dados e ajustes.
- **Por quê:** custo zero, sem servidor para manter, cenário compartilhado pelo link.
- **Alternativas:** servidor com Python; Python no navegador (Pyodide: 6,4 MB e 3 a 5 vezes mais lento); proxy em Cloudflare Worker.
- **Registro:** [`0001-hospedagem-github-pages.md`](0001-hospedagem-github-pages.md).

### D06 — Monorepo, com o que é privado fora do git

- **Decisão:** a pasta do projeto virou a raiz do repositório, preservando o histórico; `ESTADO.md`, dados brutos e outros temas pesquisados ficam fora (`.gitignore`).
- **Consequência:** specs, pipeline, app, painel e documentação num lugar só.

### D07 — Dados brutos em Releases, só os que a licença permite

- **Decisão:** cópia exata dos dados brutos em Releases do GitHub com data no nome; só vão as fontes com licença que permite redistribuir (STM CC BY 4.0, ECCC Licença de Governo Aberto, OpenStreetMap ODbL, Wikidata CC0). Google Mobility, Nager.Date, NHL, Jolpica e os relatórios da STM ficam como "origem" e são baixados na hora.
- **Por quê:** reprodutibilidade sem violar licença.
- **Consequência:** Releases `dados-2026-10-20` (fase 0) e `dados-2026-10-21` (fase 1); cada fonte guarda no manifesto a tag da sua Release.

### D08 — Bytes exatos: fim de linha fixo

- **Decisão:** `.gitattributes` marca `dados/**`, o manifesto e `painel/vendor/**` como `-text`; scripts gravam com LF.
- **Por quê (depois de ver):** a primeira publicação foi bloqueada porque o Windows converteu os CSV para CRLF e os hashes divergiram. A trava funcionou como devia.

### D09 — GTFS pelo espelho do Mobility Database

- **Decisão:** usar o feed `mdb-2126` do Mobility Database.
- **Por quê:** o endereço original da STM recusou a conexão desta máquina; o catálogo do espelho registra a STM como origem.

### D10 — Traçado do OpenStreetMap, não do GTFS

- **Decisão:** as linhas no mapa e o km ao longo da linha vêm das relações `route=subway` do OSM.
- **Por quê:** o `shapes.txt` do GTFS liga estações em linha reta e fica 2% a 10% mais curto que o traçado oficial; o do OSM fica a até 3%.
- **Registro:** `specs/002-geoespacial/`, `fontes/verificacao/validacao_geo.md`.

### D11 — Códigos `xSyy` deduzidos como plataforma da 2ª linha

- **Decisão:** os cinco códigos de local `xSyy` são tratados como a plataforma da segunda linha nas estações de correspondência, com status "deduzido".
- **Por quê:** lacunas na numeração do GTFS; teste de coerência deu 100%. A STM não documenta.

### D12 — Janela de operação de 20 horas

- **Decisão:** tempos em horas de operação, de 05:00 a 01:00.
- **Por quê:** inferida do horário dos incidentes (98,5% das falhas técnicas caem entre 05:00 e 01:59). É hipótese declarada.

---

## Fase 1: dados (2026-10-21)

### D13 — O que é falha técnica

- **Decisão:** falha técnica é a de causa primária "Matériel roulant" (MR) ou "Équipements fixes" (EF). Registro com mais de uma linha vira causa comum; "Non affecté" fica registrado, mas fora das métricas por linha.
- **Consequência:** 8.530 falhas de uma linha, 45 de causa comum, 44 sem linha.
- **Registro:** `specs/001-normalizacao/`.

### D14 — Hora depois da meia-noite e retomada sem data

- **Decisão:** horas 24:xx e 25:xx pertencem ao dia seguinte; duração = (fim − início) módulo 1.440 minutos; durações fora da faixa oficial vão para uma lista de exceções.
- **Consequência:** 98,83% na faixa ou na vizinha, contra 99% pedidos: exceção registrada.

### D15 — Três estações de clima e dado ausente como ausente

- **Decisão:** precipitação da estação McTavish (10761), com o aeroporto (30165) de reserva; temperatura e condição do tempo da 51157. Condição ausente fica vazia, nunca "seco".
- **Por quê:** a 51157 não tem precipitação horária; a 10761 não tem condição. Princípio 6.
- **Consequência:** condição só existe em 45,8% das horas de operação; o modelo tem a categoria "sem dado".

### D16 — Eventos externos com status

- **Decisão:** jogos do Canadiens (API da NHL, "verificado"), GP do Canadá (Jolpica, "não verificado") e greves de 2025 (imprensa, "não verificado"), cada um com URL. Janela do jogo de 1 h antes a 3 h 30 depois (hipótese).

### D17 — Exposição pela oferta do horário, calibrada pelo km real

- **Decisão:** trens em viagem por hora do molde do GTFS × fator do dia (km real ÷ km do molde); depois de 2023-09, sem km real, a mediana do fator do último ano medido, com status "estimado"; greve reduz a oferta pela fração da hora com serviço.
- **Consequência:** erro mensal mediano de 0,44%; 4 meses acima de 10% (exceção registrada).

### D18 — Zip determinístico e Release por fase

- **Decisão:** os 90 CSV mensais de cada estação vão num zip com data e ordem fixas; a fase 1 ganhou uma Release nova em vez de alterar a anterior.
- **Por quê:** o mesmo conteúdo precisa gerar o mesmo hash; Releases são imutáveis.

---

## Fase 2: modelos (2026-10-21)

### D19 — Binomial negativa, com α por verossimilhança perfilada

- **Decisão:** a taxa horária de falha segue uma binomial negativa com o log dos trens-hora como deslocamento; o α vem de uma grade de GLMs com α fixo.
- **Por quê:** a binomial negativa vence a Poisson por AIC e razão de verossimilhança nas duas causas; o ajuste direto do statsmodels não convergiu nesta base.
- **Registro:** `specs/005-modelo-taxa/`, `fontes/verificacao/modelo_taxa.md`.

### D20 — Bootstrap em blocos semanais, pareado entre causas

- **Decisão:** intervalos por bootstrap de semanas inteiras (B = 200), com a mesma semente para material rodante e equipamentos fixos.
- **Por quê (depois de ver):** a spec pede comparar o efeito do frio e do pico entre as causas; com sementes diferentes, a razão entre causas não teria intervalo válido. A execução foi refeita.
- **Consequência:** o pico da tarde eleva mais o material rodante; a abertura do serviço eleva mais os equipamentos fixos; para o frio, não há diferença detectável.

### D21 — Níveis "sem dado" fora do contrato do simulador

- **Decisão:** as categorias de dado ausente ficam no ajuste, mas não vão para o `parametros.json`.
- **Por quê (depois de ver):** com poucas horas, o multiplicador de "temperatura sem dado" ia a zero, e um cenário com ele zeraria a taxa. Não são cenários possíveis.

### D22 — Taxa-base do simulador no ano de 2025

- **Decisão:** o simulador parte das condições de referência no último ano completo.

### D23 — Renovação Weibull no tempo reescalado

- **Decisão:** o simulador sorteia as falhas como renovação Weibull medida no tempo acumulado da taxa, com escala normalizada para média 1.
- **Por quê:** o teste de reescala rejeitou o processo de Poisson nas 8 combinações de linha e causa; a forma da Weibull (0,44 a 0,80) mostra agrupamento além do que hora, clima e oferta explicam.
- **Registro:** `specs/006-tbf-ttr-causa-comum/`, `fontes/verificacao/distribuicoes.md`.

### D24 — Causa comum sorteada por grupo de linhas

- **Decisão:** cada evento multilinha entra num único grupo, o conjunto exato de linhas que parou (7 grupos, 45 eventos); o fator β por par fica só no relatório.
- **Por quê (depois de ver):** o simulador sorteava por par e contava duas ou três vezes os eventos que param três ou quatro linhas (os 6 pares de linhas somam 113 eventos-par para 45 eventos).

### D25 — Duração pela amostra observada

- **Decisão:** o simulador e o backtest sorteiam a duração positiva da amostra observada (massa em zero + reamostragem); a lognormal ficou para o modelo de fatores (tempo acelerado).
- **Por quê (depois de ver):** ao validar o simulador, a Laranja deu 1.433 min/ano, fora do intervalo do painel (execução de 2026-10-21 antes da correção; registro histórico, o relatório daquela execução foi substituído). A média observada das durações era maior que a da lognormal: 23% a 29% na Laranja (material rodante e equipamentos fixos) e 26% nos equipamentos fixos da Verde, e 3,4 vezes nos equipamentos fixos da Azul, por poucas interrupções de quase 20 horas (razões em `fontes/verificacao/duracoes.md`). Com a amostra, deu 1.704 (IC 1.528 a 1.881), que contém 1.797 e 1.852. Quantis interpolados foram testados antes e perdiam 3% a 5% da média (conferência feita na sessão, registro histórico).

### D26 — Local das falhas de equipamento fixo

- **Decisão:** a falha de equipamento fixo é sorteada entre os locais históricos com posição na linha; uma estação de correspondência citada por falha de outra linha usa o km da estação naquela linha.
- **Consequência:** 10% das falhas de equipamento fixo ficam sem posição (sobretudo subestações) e não entram no sorteio do local; a taxa total não muda.

---

## Fases 3 e 4: simulador, políticas e expansão (2026-10-21)

### D27 — Motor de eventos discretos com bloqueio por trecho

- **Decisão:** cada trecho entre estações, por sentido, admite um trem por vez; separação mínima de 90 s (hipótese); o bloco inclui a plataforma de chegada; o atraso se propaga aos trens de trás.
- **Por quê:** simplificação suficiente para reproduzir o horário exato sem falhas e a propagação de atraso.
- **Registro:** `specs/007-motor-des/plan.md`.

### D28 — Sorteio reprodutível em qualquer número de processos

- **Decisão:** gerador xoshiro128** com um fluxo por fonte de sorteio e semente derivada do índice da rodada.
- **Consequência:** o mesmo resultado com 1 ou 8 processos; o link do cenário reproduz os mesmos números em outro computador.

### D29 — Monte Carlo até a precisão, com teto

- **Decisão:** rodar lotes até a meia-largura do IC 95% ficar em 5% da média, com teto de 50.000 dias.
- **Consequência:** a Azul precisaria de cerca de 168 mil dias por causa da cauda das durações: exceção registrada na spec 009.

### D30 — Retorno parcial só nas pontas de viagem

- **Decisão:** a política de retorno parcial usa só os pontos onde o horário já termina viagens.
- **Por quê:** a posição dos aparelhos de mudança de via não está verificada. Resultado marcado como hipótese.

### D31 — Métricas ponderadas pela oferta

- **Decisão:** disponibilidade por par de estações ponderada pelas viagens programadas que servem o par.
- **Por quê:** não há passageiros diários. Nenhum número de passageiros foi inventado (princípio 13).
- **Consequência:** estações de uma mesma linha pesam igual, e ligações entre as mesmas duas linhas empatam no ranking da expansão.

### D32 — Expansão pelo método de estados, validado contra o simulador diário

- **Decisão:** avaliar cada candidata sorteando 200 mil estados dos trechos e medindo a disponibilidade dos pares de estações atuais; o ganho é pareado com a rede atual.
- **Por quê:** rápido o bastante para a busca exaustiva (298 ligações) e validado contra a camada diária a até 0,1 ponto percentual (Azul no limite, −0,095).
- **Candidatas:** coordenadas só de consultas salvas ao OSM e ao Wikidata; fontes em `dados/manuais/candidatas_expansao_LEIAME.md`. O anel da Laranja virou uma linha nova com as taxas da Laranja; a Rosa com a Azul até Anjou é avaliada como projeto conjunto, porque a Vertières só vira correspondência com a Azul pronta.
- **Registro:** `specs/014-expansao-rede/`, `fontes/verificacao/expansao.md`.

### D33 — Toda hipótese do motor no contrato, com faixa

- **Decisão:** reparo na oficina, probabilidade de retirada, tempos de retirada e de marcha lenta, redução de causa comum, fator de traçado e outras hipóteses entram no `parametros.json` com status "hipótese" e uma faixa. Na página, o controle vai meia faixa além de cada ponta, para permitir testar extrapolações, e um valor fora da faixa gera aviso (D34).

### D34 — Aviso de extrapolação pelo que foi observado

- **Decisão:** a página avisa quando o cenário combina condições com poucas horas observadas (ex.: neve no solo em julho, chuva congelante a 25 °C) ou quando uma hipótese sai da faixa.

---

## Fase 5: validação contra o histórico (2026-10-21)

### D35 — Backtest pré-registrado, com variante registrada depois

- **Decisão:** a versão oficial (A) foi definida antes de ver o teste: treino até 2024-12, efeito do ano de 2024 no teste. A versão B (treino até 2023-09) também foi pré-registrada.
- **Resultado:** A cobriu 66,7% dos casos, contra 80% a 98% pedidos.
- **Depois de ver:** 2024 foi atípico (cerca de 1.000 falhas no 2º semestre, contra cerca de 500 nos vizinhos). A variante C sorteia o efeito do ano entre os anos de treino; como a spec manda, ela foi testada de novo noutro período (D: treino até 2022-12, teste de 2023-01 a 2024-06) e cobriu 90,3%. O resultado oficial continua sendo o de A.
- **Registro:** `specs/012-backtest/`, `fontes/verificacao/backtest.md`.

---

## Fase 6: publicação (2026-10-21)

### D36 — Reprodução do zero com tolerância declarada

- **Decisão:** um workflow mensal (`reproduz.yml`) baixa as Releases e as fontes de origem, refaz o pipeline e os relatórios do simulador numa máquina limpa e compara com os publicados: tolerância relativa de 1e-9, e de 1e-3 nos modelos com bootstrap e otimização. Commit e tempo de execução gravados nos relatórios eram ignorados; desde a D45, só o tempo é ignorado, e o hash do código (`codigo_commit`, D43) é comparado.
- **Por quê (depois de ver):** a primeira execução reproduziu todos os resultados e só acusou esses metadados e uma contagem de meses que olhava uma pasta ausente no CI.
- **Resultado:** a segunda execução passou: 45 arquivos derivados idênticos byte a byte, 8 dentro da tolerância e 0 fora. No commit ba19e74, com o hash do código também comparado (D45): 48 idênticos, 5 na tolerância e 0 fora. No commit a7f0594, com o comparador que também acusa arquivo a mais (D47): 48 idênticos, 5 na tolerância e 0 fora, faltando ou sobrando.

### D37 — Versão congelada servida com a própria base

- **Decisão:** a `v1.0.0` tem build próprio com base `/versoes/v1.0.0/`, zipado na Release; cada publicação desempacota as versões congeladas.
- **Por quê:** o Vite grava caminhos absolutos; sem isso, a versão antiga carregaria o código da atual.

### D38 — RA fora do repositório público

- **Decisão:** nomes e curso da equipe no site e no README (`docs/equipe.json`); o RA só no relatório de entrega.
- **Por quê:** o RA é dado pessoal e o repositório é público.

### D39 — Referências conferidas

- **Decisão:** cada referência do relatório tem o DOI conferido na API do Crossref; a NUREG/CR-4780 ficou marcada como "não conferida".

### D40 — Ajustes pesados um de cada vez

- **Decisão:** os ajustes com bootstrap rodam sozinhos na máquina; após cada ajuste, o coletor de lixo libera o ciclo modelo↔resultado do statsmodels; em falta de memória, a mesma reamostra é repetida.
- **Por quê (depois de ver):** duas execuções caíram por falta de memória, e uma reamostra descartada tornaria o resultado irreprodutível.

### D41 — Correções da revisão crítica de 2026-10-21

- **Decisão:** corrigir os textos que não batiam com o código ou com os arquivos gerados (guia do simulador, D10, D33, relatório, spec 012) e três saídas de publicação: a ordem das estações de correspondência no deck passou a ser fixa, as tabelas de `fontes/verificacao/distribuicoes.md` deixaram de usar `|` dentro das células e a página `/fontes/` passou a ligar os arquivos do repositório ao GitHub. O User-Agent de `pipeline/baixa_clima_eventos.py` passou a identificar o projeto pelo endereço do repositório, sem o e-mail de um integrante (D38); o e-mail continua no histórico do git.
- **Por quê (depois de ver):** a revisão reproduziu cada defeito com um comando. Nenhum critério de spec nem número de modelo mudou; o relatório das distribuições foi refeito do `distribuicoes.json` publicado.
- **Registro:** `fontes/verificacao/critica_2026-10-21.md`.

### D42 — Greve no simulador só pela oferta

- **Decisão:** o contrato `parametros.json` não leva o multiplicador de dia de greve; no simulador, a greve só corta as viagens fora das faixas com serviço.
- **Por quê (depois de ver):** a revisão crítica mostrou que o simulador aplicava 1,17 e 1,11, embora a spec 005 tenha concluído que a greve atua só pela exposição (o intervalo de 95% dos dois multiplicadores contém 1). A mudança alinha a implementação à spec; os cenários sem greve, entre eles os dos relatórios de políticas e de expansão, não mudam.
- **Registro:** `pipeline/parametros.py`, `docs/guia_simulador.md`, `fontes/verificacao/critica_2026-10-21.md` (achado 12).

### D43 — Identificação do código que gerou o contrato

- **Decisão:** o campo `codigo_commit` do `parametros.json` passou a ser o SHA-256 dos scripts que geram o contrato (`modelo_taxa.py`, `distribuicoes.py` e `parametros.py`), com fim de linha normalizado.
- **Por quê (depois de ver):** o hash do commit do git mudava a cada commit, mesmo sem mudança no código, e quebrava a reprodução byte a byte (achado 15).

### D44 — Correções da revisão crítica de 2026-10-21, rodada 2

- **Decisão:** o motor para com erro quando o `parametros.json` não tem a taxa-base de uma linha (antes, a taxa virava zero e a linha nunca falhava); um teste do contrato garante que o multiplicador de greve ficou fora (D42); a verificação passa a citar todas as Releases que baixa. Textos alinhados: plano e spec 011 (greve só pela oferta, com data), plano 008, tempo medido na spec 009 e a conferência de 97,95% no `fontes/FONTES.md`.
- **Por quê (depois de ver):** a revisão reproduziu cada defeito com um teste ou um comando. Com os dados publicados, as quatro linhas têm taxa-base, então nenhum número muda.
- **Registro:** `fontes/verificacao/critica_2026-10-21_rodada2.md`.

### D45 — Propostas da rodada 2 aplicadas pela sessão principal

- **Decisão:** a fixture de testes e o teste de cenário deixam de ter o multiplicador de greve (D42) e a hipótese sem uso; as razões entre a média observada e a da lognormal saem de um relatório gerado (`fontes/verificacao/duracoes.md`); o relatório das políticas grava a meia-largura esperada com 50.000 dias e tira o tempo de relógio do JSON versionado; o comparador da reprodução passa a comparar o `codigo_commit`, que agora é determinístico; os cinco arquivos do GTFS que estavam fora do manifesto entraram nele.
- **Por quê:** achados 3, 7, 8, 9, 10, 11, 12 e 13 da rodada 2. Nenhum número de modelo mudou.
- **Registro:** `fontes/verificacao/critica_2026-10-21_rodada2.md`.

### D46 — Correções da revisão crítica de 2026-10-21, rodada 3

- **Decisão:** `publicacao/testa_navegador.py` traz a aba para a frente depois de carregar a página, conta os quadros por `requestAnimationFrame` durante 3 s (com teto de 8 s), com a animação parada e tocando a 300×, e lê o resultado do Monte Carlo de abertura. A spec 010 e o guia passam a citar os quadros por segundo com a animação tocando. Textos alinhados aos arquivos gerados: contagem de derivados no manifesto (spec 000), tempo da execução publicada (spec 009), regra do comparador na D36 e "horas de operação" na condição do tempo.
- **Por quê (depois de ver):** o teste abria a página oculta (`visibilityState` "hidden"): o `requestAnimationFrame` não rodava e o contador da página ficava parado em "60 fps"; a animação também não era ligada. Com a aba na frente e a animação tocando, o Edge sem janela com WebGL por software deu 34 fps em tela de notebook e 60 em tela de celular. O critério de 30 fps continua atendido no teste disponível, com pouca folga. Nenhum critério de spec nem número de modelo mudou.
- **Registro:** `fontes/verificacao/critica_2026-10-21_rodada3.md`.

### D47 — Propostas da rodada 3, parte A

- **Decisão:** o contador de quadros do simulador mostra "parado" quando a animação não toca e só mede enquanto ela toca. O comparador da reprodução (`pipeline/compara_derivados.py`) acusa também o arquivo que sobra na pasta refeita (gerado e não publicado), além do que falta. O relatório das políticas usa `MAX_RODADAS` e `PRECISAO_ALVO` em vez dos literais `50_000` e `5`. A página do simulador diz "no painel do cenário" em vez de "à esquerda". Na spec 013, o critério da versão final passa a dizer que o mecanismo atende e que a versão de entrega está pendente.
- **Por quê (depois de ver):** achados 7, 13, 14, 15 e 16 da rodada 3. Parado, o contador mostrava 60 fps, que não era a taxa da animação. Uma pasta refeita com um arquivo a mais dava saída 0. Antes de mudar o comparador, os 53 arquivos de `dados/derivados/` no disco, no git e no manifesto conferem, e os scripts só gravam saídas com nome fixo. Nenhum critério de spec nem número de modelo mudou. A redação do critério da spec 013 não muda: muda a linha do resultado.
- **Registro:** `fontes/verificacao/critica_2026-10-21_rodada3.md`, seção "Aplicação das propostas, parte A".

### D48 — Teste de navegador mantém a aba em primeiro plano

- **Decisão:** `publicacao/testa_navegador.py` abre o Edge ou o Chrome com opções que impedem pôr a aba em segundo plano e simula o foco na página logo depois de trazê-la para a frente.
- **Por quê (depois de ver):** na parte C da rodada 3, a medida de quadros por segundo no celular saiu vazia: a aba voltava a ficar oculta segundos depois e a animação parava. Só a ferramenta de teste mudou; site e modelo, não.
- **Resultado:** no site publicado (commit a7f0594), rolagem lateral zero, WebGL, Monte Carlo de abertura em cerca de 2 s, contador "parado" com a animação parada, 60 quadros por segundo no celular e 33 a 34 no notebook tocando a 300× (WebGL por software), nenhum erro no console.
- **Registro:** `fontes/verificacao/critica_2026-10-21_rodada3.md` (parte C).

### D49 — Velocidades até 1 dia/s, dias emendados e evento vermelho por falha

- **Decisão:** o controle de velocidade passa a ter 1 h/s, 10 h/s e 1 dia/s (antes, o máximo era 300×). Com a animação tocando, ao fim do dia ela segue para o próximo dia sorteado do mesmo cenário (opção que pode ser desligada) e conta os dias completos e as falhas sorteadas neles. Cada falha vira um evento vermelho: um pulso no local que dura 2,6 segundos de relógio em qualquer velocidade, um item na lista de eventos sobre o mapa e um risco na barra de tempo. O círculo vermelho grande fica enquanto a linha está parada; depois, um ponto vermelho menor marca a falha até o fim do dia.
- **Por quê (depois de ver):** a equipe viu que as falhas quase não apareciam. A taxa está certa: a rede teve 3,1 falhas por dia de 2019 a 2026 (`painel/linhas.json`), e a 300× um dia de operação leva 4 minutos de relógio; a marca de uma falha sem interrupção durava 300 s simulados, isto é, 1 segundo de relógio. Medir a duração do evento em tempo de relógio deixa a falha visível em qualquer velocidade. Um dia com trajetórias custa cerca de 3 ms para sortear, e o cenário preparado fica guardado entre os dias, então 1 dia/s cabe na página.
- **Alternativas consideradas:** aumentar a taxa de falha para "aparecer mais" (rejeitada: mudaria o modelo); marca de duração fixa em tempo simulado (rejeitada: some em alta velocidade).
- **Resultado (site publicado, commit abbe2ec):** a 1 dia/s, 7 dias emendados e cerca de 20 eventos vermelhos em 6 segundos; sem placa de vídeo, 28 a 33 quadros por segundo em tamanho de notebook em todas as velocidades, com a thread da página ocupada de 22% a 35% do tempo (o limite é o desenho por software). Duas tentativas de aliviar o desenho (pulso sem sombra e textos atualizados 10 vezes por segundo) não mudaram a medida e foram desfeitas.
- **Registro:** spec 010 (critérios acrescentados em 2026-10-21); testes em `app/tests/simulador/animacao.test.ts`; medida em `fontes/verificacao/navegador_2026-10-21.json`, gerada por `publicacao/testa_navegador.py`.

### D50 — Faixa "Cenário aplicado" e falhas esperadas por dia

- **Decisão:** acima do mapa, a página mostra o cenário que está valendo, item a item, destacando o que difere do padrão, e as falhas esperadas por dia nesse cenário e no padrão, com a razão entre elas e o valor por linha. A faixa pisca e mostra a hora quando o cenário muda. Com a animação emendando os dias, mostra também os dias completos e a média de falhas sorteadas, para comparar com o esperado. A aba "Muitos dias" passa a mostrar o cenário da rodada e a coluna "Esperado pelo modelo" ao lado das falhas por dia simuladas.
- **Por quê:** a equipe perguntou como saber que o cenário está sendo aplicado. O esperado é a taxa acumulada do dia, a mesma que o motor usa no sorteio (`app/src/simulador/efeito.ts`); um teste confere que a média de 2.000 dias sorteados fica a menos de 5% dele. Trocar só o dia mostrado deixou de ser tratado como mudança de cenário: o aviso de "resultado desatualizado" da aba "Muitos dias" não aparece mais por isso.
- **O que a faixa mostra com os dados publicados:** no modelo ajustado (spec 005, `dados/derivados/simulador/parametros.json`), alguns fatores de clima aumentam a taxa e outros a diminuem: neve no solo acima de 10 cm multiplica por 1,37 (material rodante) e 1,38 (equipamentos fixos); 25 °C ou mais, por 1,07 e 1,83; chuva congelante, por 0,89 e 0,69. Combinados, podem quase se cancelar, e a faixa mostra o efeito líquido no dia. O tipo de dia e a greve também mudam quantos trens circulam. As políticas, exceto o tratamento da causa comum, não mudam quantas falhas ocorrem, e sim quanto elas param a linha (abas "Muitos dias" e "Comparar cenários").
- **Registro:** spec 011 (critério acrescentado em 2026-10-21); testes em `app/tests/simulador/efeito.test.ts`.
