# Revisão crítica (2026-10-21, rodada 3)

Feita pelo agente `.claude/agents/critico-stf.md`, passos 1 a 9, incluindo 7 (site e navegador) e 7b (apresentação), sobre o commit 8e38e82 (publicado). Durante a revisão, a sessão principal publicou o b38f340, que só muda o próprio agente.

## Resumo

- Testes verdes antes e depois das correções: pytest 55/55, vitest 87/87, `tsc` e build sem erro, 25 números recalculados com 0 diferenças, manifesto com 0 problemas. Os sete scripts rápidos e o `gera_deck.py` deram arquivos idênticos byte a byte.
- O teste do navegador media a página oculta e com a animação parada: o "60 fps" publicado não era medida da animação. Com a aba visível e a animação tocando a 300× no pico, o Edge sem janela deu 34 fps em tela de notebook e 60 em tela de celular. Script e textos corrigidos (D46).
- 16 achados: 0 altos, 1 médio, 15 baixos. 5 corrigidos, 2 em parte, 9 ficam como proposta. Nenhum critério de spec, número de modelo ou arquivo de `dados/derivados/` mudou.

## Achados

| # | Gravidade | Arquivo e linha | Evidência reproduzida | Correção | Corrigido |
|---|---|---|---|---|---|
| 1 | média | `publicacao/testa_navegador.py:61-79` (antes da correção); `specs/010-mapa/spec.md:31`; `specs/010-mapa/plan.md:34`; `docs/guia_simulador.md:62` | O teste nunca traz a aba para a frente: `document.visibilityState` dá "hidden" e `hasFocus()` dá false. Assim o `requestAnimationFrame` não roda: uma contagem de quadros de 3 s não terminou em 120 s, e com teto de 6 s voltou sem nenhum quadro. O "60 fps" lido é o contador congelado. O teste também não liga a animação (a captura mostra ▶ e 07:30). Tocando a 300× por 10 s com a aba oculta, o relógio andou de 07:30 para 07:31, e a captura mostrava "1 fps". Com `Page.bringToFront` e a animação tocando a 300×, contagem direta: 34 fps (notebook, 1366×768; contador da página: 33) e 60 fps (celular, 390×844); parada, 60 nos dois | `testa_navegador.py` traz a aba para a frente depois de carregar, conta os quadros por `requestAnimationFrame` (3 s, teto de 8 s) parada e tocando a 300×, e lê o Monte Carlo de abertura. Spec 010, plano 010 e guia citam a medida nova; a antiga fica como registro. D46 | sim |
| 2 | baixa | `specs/009-monte-carlo/spec.md:34` | "12.000 dias em 9,0 s"; o `politicas.md` publicado diz "Tempo: 7,8 s para 12000 dias numa thread" (o relatório foi refeito no ba19e74) | Copiado de `politicas.md`: 7,8 s | sim |
| 3 | baixa | `specs/000-proveniencia/spec.md:34` | "45 fontes primárias e 48 derivados"; o manifesto tem 45 fontes e 53 derivados, os mesmos 53 arquivos de `git ls-files dados/derivados` (D45 incluiu 5 do GTFS) | 53, com a nota da D45 | sim |
| 4 | baixa | `docs/decisoes/registro_de_decisoes.md:232` (D36) | "Commit e tempo de execução gravados nos relatórios são ignorados"; `compara_derivados.py:19` ignora só `bootstrap_segundos` e `segundos` desde a D45 | Texto diz que era assim até a D45 | sim |
| 5 | baixa | `docs/relatorio/relatorio.md:75`; D15; deck, slide 14 (`gera_deck.py:771`) | "45,8% das horas". `resumo_clima.json` dá 0,4581 nas horas de operação; em todas as 65.717 horas, 29.875 têm condição (45,46%) | "das horas de operação" no relatório e na D15. O deck fica como proposta, para não refazer o PDF por isso | em parte |
| 6 | baixa | `publicacao/testa_navegador.py:28-35` (antes) | Se o navegador não abre a porta de depuração em 30 s, `pagina` não existe e o erro é `NameError`, sem a causa | Sai com mensagem que cita o navegador e a porta | sim |
| 7 | baixa | `app/src/simulador/main.ts:361-382`; `app/simulador/index.html:79` | O contador ("Quadros por segundo da animação") conta os quadros da página também com a animação parada: parada, mostrou 60; tocando em notebook, 33 | Mostrar "parado" ou "—" quando a animação não toca, ou mudar o título | sim (parte A, D47) |
| 8 | baixa | deck, slide 3 (`gera_deck.py:523` e `530`) | O slide cita a 2ª execução do `reproduz.yml` (45 idênticos, 8 na tolerância). A spec 013 e a D36 citam a do ba19e74 (48 idênticos, 5 na tolerância, 0 fora). O slide não está errado, mas está atrás | Citar a execução do ba19e74 e refazer `index.html` e PDF | não (proposta) |
| 9 | baixa | deck, slide 4 (`gera_deck.py:849` e `1073`) | No PDF renderizado, o rodapé da direita quebra em duas linhas ("dados 2026-10-20 e 2026-10-21" e "· 4"), porque a fonte da esquerda ocupa duas linhas. Não invade o conteúdo | `white-space: nowrap` no `.pg`, ou encurtar a fonte do slide 4 | não (proposta) |
| 10 | baixa | deck, slide 13 (`gera_deck.py:755`) | O slide traz 23% a 29%, 26% e 3,4 vezes; o rodapé não cita `fontes/verificacao/duracoes.md`, de onde as razões saem desde a D45 | Acrescentar `duracoes.md` ao rodapé | não (proposta) |
| 11 | baixa | `docs/relatorio/relatorio.md:118`; deck, slide 9 (`gera_deck.py:649`); `specs/009-monte-carlo/spec.md:34` | "1.000 dias em cerca de 3 s" e "2,6 a 3,8 s com 12 workers" são medições à mão, sem arquivo gerado. Hoje a página mostrou "1.000 dias em 1,3 s com 12 worker(s)" (celular) e "1,4 s" (notebook) | A spec 009 registra a medição nova. Proposta: versionar um resultado datado do teste do navegador, ou tirar o tempo dos textos | em parte |
| 12 | baixa | `specs/008-politicas/spec.md:32`; `relatorio.md:118`; deck, slide 9 (`gera_deck.py:659`) | Os valores simulados 0,674, 0,939 e 0,992 só existem no `plan.md` 008, digitados de uma execução do teste. `frota.test.ts` só exige a diferença até 5 p.p. e não grava os valores | `politicas.relatorio.ts` gravar a tabela da reserva contra o Markov em `politicas.md` | não (proposta) |
| 13 | baixa | `app/relatorios/politicas.relatorio.ts:65` | A meia-largura com 50.000 dias usa os literais `5` e `50_000`; o teto do Monte Carlo é `MAX_RODADAS` em `app/src/mc/rodadas.ts:179`. Se o teto mudar, o relatório não acompanha | Importar `MAX_RODADAS` e dar nome à meta de 5% | sim (parte A, D47) |
| 14 | baixa | `pipeline/compara_derivados.py:85-106` | O comparador só percorre a pasta publicada. Teste: pasta refeita com um arquivo a mais (`novo.json`) deu "0 arquivo(s) fora da tolerância" e saída 0 | Percorrer também a pasta refeita e acusar o que sobra. Antes, conferir que nenhum script grava arquivo não versionado em `dados/derivados/` (pode quebrar o `reproduz.yml`) | sim (parte A, D47) |
| 15 | baixa | `app/simulador/index.html:15` e `111` | "Mude o cenário à esquerda": no celular o painel do cenário fica acima do mapa (captura de 390×844) | "no painel do cenário" | sim (parte A, D47) |
| 16 | baixa | `specs/013-publicacao/spec.md` (Resultado) e `tasks.md` | Status "implementada"; o critério "versão final congelada" aparece como atendido pela `v1.0.0` (commit 6196ad2, antes das correções D41 a D46), mas `tasks.md` mantém aberta "Congelar a versão de entrega no fim do semestre". O mecanismo está provado; a versão final ainda não existe | Escrever na linha do critério que a versão de entrega fica pendente, ou congelar a v1.x | sim (parte A, D47) |

Pendentes de rodadas anteriores, sem mudança: achado 11 da rodada 2 em parte (o `codigo_commit` identifica os scripts no momento em que `parametros.py` roda, não os que geraram `taxa_*.json` e `distribuicoes.json`; desde a D45 o comparador o confere, e no `reproduz.yml` tudo é refeito do zero) e achado 14 (número da conta do GitHub, decisão da equipe).

## Resultado de cada passo

### 1. Contexto

15 specs. Implementadas: 000, 003, 005, 006, 007, 008, 011, 013 e 014. Implementadas com exceções: 001, 002, 004, 009, 010 e 012. Li README, `specs/README.md`, a constituição, `docs/arquitetura.md`, o relatório da rodada 2 e o que mudou de 62d1c14 a 8e38e82 (40 arquivos). Das propostas da rodada 2 aplicadas pela sessão principal (D45), conferi: `duracoes.md` (razões iguais às da rodada 2), meia-largura de 9,2% em `politicas.md`, tempo fora do JSON, `codigo_commit` comparado (teste novo em `test_compara.py`), GTFS no manifesto.

### 2. Testes

| Comando | Antes | Depois |
|---|---|---|
| `.venv/Scripts/python.exe -m pytest pipeline/tests -q` | 55 passaram | 55 passaram |
| `python -I pipeline/verifica_fontes.py --recalcula` | 0 problemas; 25 números, 0 diferenças | igual |
| `npx tsc --noEmit` | sem erro | sem erro |
| `npm test` | 17 arquivos, 87 testes | 17 arquivos, 87 testes |
| `npm run build` | sem erro (aviso do Vite sobre `__dirname`) | sem erro |

### 3. Reprodutibilidade barata

Rodei de novo `normaliza`, `exposicao`, `clima_eventos`, `horario_simulador`, `candidatas`, `parametros` (que também grava `duracoes.md`) e `diagnostico_taxa`. `git status` ficou vazio. `verifica_fontes.py` sem argumentos: 0 problemas. O `codigo_commit` (`sha256-scripts:70cf9c002aa2ba0a`) é igual ao SHA-256 dos três scripts lidos dos blobs do HEAD. `gera_deck.py` refez o `index.html` com o mesmo SHA-256 (`16c83e0d…`).

API pública do GitHub: o último "Reproduzir o pipeline" é o 39556506384, no ba19e74, com sucesso nos 11 passos; o passo de comparação usa `shell: bash`, que no Actions roda com `pipefail`, então uma diferença faria o passo falhar. Do ba19e74 ao b38f340 só mudaram documentos e o agente. O artefato com a comparação exige login: não li as contagens 48, 5 e 0.

### 4. Números dos documentos

| Número | Onde | Origem | Valor na origem | Igual? |
|---|---|---|---|---|
| Multiplicadores da tabela §4.1 (18 valores com IC), α 1,83 e 5,47, p < 10⁻³⁰ | relatório, spec 005, deck 6 | `modelo_taxa.md` | iguais; p 3,6e-33 e 4,4e-206 | sim |
| Resíduos 0,000 e 1,00; faixas 0,98 a 1,01, abertura EF 0,91 ("9% acima") | relatório, spec 005 | `modelo_taxa.md`, `modelo_taxa_por_faixa.md` | 0,0004; 1,0003 e 1,0012; 0,983 a 1,008; 0,914 | sim |
| Razão 1,39 (1,22–1,66) e 0,74 (0,63–0,89); ×1,95 e ×2,75 com IC | relatório, spec 005, deck 7 | `modelo_taxa.md` | iguais | sim |
| Weibull em 23 de 29 (gama 4, lognormal 2); 14 de 29 passam nos dois testes | relatório, spec 006, deck 7 | `distribuicoes.md` (contei as linhas) | 23, 4, 2; 14 | sim |
| Formas 0,44 a 0,80; médias reescaladas 0,97 a 1,03; p de 1e-8 a 1e-90 | relatório, D23, spec 006, deck 7 | `distribuicoes.md` | 0,4387 a 0,8017; 0,9719 a 1,0298; 1,2e-8 a 2e-90 | sim |
| Sem interrupção 20% a 42% (MR) e 58% a 67% (EF); evacuação 2,92 (2,73–3,13); via 2,30; R² 0,23 | relatório, spec 006 | `distribuicoes.md` | 19,9% a 42,1%; 57,9% a 66,8%; iguais | sim |
| Causa comum: 45 eventos, 7 grupos, 12/10/10/8/3/1/1, 31 com Verde e Laranja, β 0,011 (0,007–0,015), 22,4 min, Laranja em 44 | relatório, spec 006, deck 8 | `distribuicoes.md` | iguais | sim |
| Razões das durações 23% a 29%, 26%, 3,4 vezes | relatório, D25, spec 006, deck 13 | `duracoes.md` | 1,228 e 1,291; 1,262; 3,384 | sim |
| Políticas: −7,8 (−9,7 a −5,9), −16,4, +0,35; −1,1; −0,8; −0,63; +32,5 e +58; +0,21; +0,01 | relatório, spec 008, deck 10 | `politicas.md` | iguais (−16,37; 58,2; 0,205; 0,012) | sim |
| 1.704 (1.528–1.881), 1.797, 1.852; 99,5% a 99,9%; 168.183; 9,2% | relatório, specs 009, deck 9 e 15 | `politicas.md`, `painel/corredor.json` | iguais | sim |
| Tempo de 12.000 dias | spec 009 | `politicas.md` | 7,8 s | não: 9,0 (achado 2, corrigido) |
| Expansão: 99,236%, Rosa +0,021, Rosa+Azul +0,003, anel +0,0002, −0,005, −0,035, −0,075, com retorno +0,053/+0,019/+0,011, Atwater +0,085, 298 ligações, −0,095 na Azul | relatório, spec 014, D32, deck 11 | `expansao.md` | iguais | sim |
| Backtest A/B/C/D: 66,7 (54,6–77,3), 81,9, 84,7, 90,3 (81,0–96,0); KS 2,4e-11, 0,06, 0,01, 0,16; 22 de 24 abaixo; greve 56,2% e 93,8%; minutos parados | relatório, spec 012, D35, deck 12 | `backtest.md` | iguais | sim |
| 8.530, 8.619, 45, 31, 44, 224, 3.982 e 4.548, por linha | relatório, FONTES, deck 4 | `resumo_normalizacao.json`, recálculo | iguais | sim |
| 98,83% (8.430); 100 exceções; máxima 1.170 min | spec 001, D14, deck 13 | saída de `normaliza.py` | 0,9883; 8.430; 100; 1.170 | sim |
| Comprimentos e ±3%; 68 de 73; 104 a 142 m; 7 a 78 m do Wikidata; 94,0%; 4,8% de subestações; 10% das EF sem posição | spec 002, relatório, D26, FONTES | `validacao_geo.md`, `locais.json`, `parametros.json` | iguais; 407 de 8.530 = 4,77%; 469 de 4.548 = 10,3% | sim |
| 65.717 horas; 99,99%; 99,3%; 348 eventos; 45,8%; 90 meses | relatório, spec 003, D15, D18, deck 4 e 14 | `resumo_clima.json`, `eventos_externos.csv` | iguais; 45,8% é das horas de operação | sim (achado 5 no texto) |
| 26, 31, 2, 9; 0,44%; 216 de 220; −10,75%; 22 registros e 15,7 km; 411,63 | specs 004 e 007, relatório, deck 4 | `exposicao.md`, `calibracao_mensal.csv` | iguais (−0,1075) | sim |
| Painel: falhas por dia, MTBF, MTTR, disponibilidade, min/ano, mediana 3 min, 3,1 falhas/dia, 6,42 h | deck 5 | `painel/linhas.json` | iguais | sim |
| 1.880 e 1.797 min/ano com 100,3 de causa comum | FONTES §5 | `painel/corredor.json`, `causa_comum.json` | 1.880,14; 1.797,04; 100,3 | sim |
| 8 relações e 69 estações (OSM); 102 (Wikidata); 974 dias; NHL 1.330.464 bytes; F1 20.467; greves 6.520; expansão 16.487; zips do clima horário; 62 a 65 KB por ano; 17 tabelas | FONTES | arquivos brutos e `verifica_fontes.py` | iguais | sim |
| 45 fontes e 53 derivados | spec 000 | manifesto | 45 e 53 | não: 48 (achado 3, corrigido) |
| 0,674/0,939/0,992 e 0,671/0,938/0,992 | relatório, spec 008, deck 9 | `specs/008-politicas/plan.md` (digitado) | iguais | sem arquivo gerado (achado 12) |
| 1.000 dias em cerca de 3 s; 2,6 a 3,8 s | relatório, deck 9, spec 009 | nenhum | página hoje: 1,3 e 1,4 s | sem arquivo gerado (achado 11) |
| 60 fps | spec 010, plano 010, guia | teste do navegador | página oculta, contador parado | não (achado 1, corrigido) |
| 14 hipóteses do motor | `hipoteses.ts`, contrato | `parametros.json` | mesmos nomes, valores e faixas; todas com status | sim |

### 5. Critérios das specs

Conferi cada linha das tabelas de Resultado das 15 specs contra os relatórios e testes citados (tabela do passo 4). Resultado: os critérios batem, com quatro ressalvas. Spec 000: contagem de derivados desatualizada (achado 3). Spec 009: tempo desatualizado (achado 2). Spec 010: o "60 fps" não media a animação; com a medida correta (34 fps em notebook) o critério de 30 fps segue atendido no teste disponível, com pouca folga, e a spec já estava "com exceções" (achado 1). Spec 013: o critério da versão final é atendido pelo mecanismo, mas a versão de entrega ainda não foi congelada (achado 16). A spec 011 ("resultado pronto ao abrir") foi confirmada no navegador: "1.000 dias em 1,3 s com 12 worker(s); semente 20261021", sem clicar em nada.

### 6. Código

- Exceções: `modelo_taxa.py:190` e `backtest.py:90` descartam a reamostra que falha, mas o número de reamostras válidas fica no arquivo (em `taxa_*.json`, só os níveis ausentes na reamostra têm menos de 200). `verifica_fontes.py` conta cada erro como problema. `main.ts:942` só troca a mensagem do link.
- Sorteio: só `analise_confiabilidade.py` usa `random`, com `random.seed(20261020)`; os demais usam `np.random.default_rng(SEMENTE)`. Nenhum `Math.random`.
- Hipóteses: os 14 nomes de `hipoteses.ts` estão no contrato, com o mesmo valor, faixa e status "hipótese". Nenhum `valor` do contrato sem `status`.
- Dado ausente: os `?? 0` restantes (`extrapolacao.ts:25`, `expansao.ts:131`, `contexto.ts:112`) tratam ausência como "nada observado" ou deslocamento zero, coerentes com o uso. Sem efeito com os dados publicados.
- Constantes: `politicas.relatorio.ts:65` repete o teto do Monte Carlo (achado 13).
- Caminhos e rede: só `testa_navegador.py` tem caminho do Windows, com alternativas para o Chrome no Linux e a variável `NAVEGADOR`. Toda chamada de rede tem teto. Os testes do CI não leem `dados/brutos/` fora da Release.
- Comparador da reprodução: não acusa arquivo novo (achado 14).

### 7. Site

Todas as páginas pedidas responderam 200: `/`, `/simulador/`, `/mapa/`, `/relatorio/`, `/decisoes/`, `/decisoes/0001/`, `/apresentacao/`, `apresentacao.pdf`, `/docs/guia/`, `/docs/arquitetura/`, `/docs/dicionario/`, `/fontes/`, `/fontes/documentacao/`, `/specs/`, `/versoes/v1.0.0/`, `/versoes/v1.0.0/simulador/`, `parametros.json`, o manifesto e os 11 relatórios de `/fontes/verificacao/*.html`. A pasta `/fontes/verificacao/` não tem índice (404); os relatórios são ligados a partir de `/fontes/`. O `politicas.html` publicado já traz o hash `70cf9c002aa2ba0a`, a coluna da meia-largura e "7,8 s".

Montagem local (`npm run build` e `monta_site.py`): 24 páginas, 185 links locais, 0 quebrados, 0 âncoras inexistentes; os 71 links `blob/main` e `tree/main` para o GitHub existem no HEAD. Nos 70 arquivos Markdown do repositório, 43 links relativos, 0 quebrados.

Navegador (Edge sem janela, WebGL por software, `ESPERA=50`, um tamanho por vez; processos encerrados depois de cada teste). Com o script corrigido:

| Medida | Celular (390×844) | Notebook (1366×768) |
|---|---|---|
| Rolagem lateral (`scrollWidth` contra `clientWidth`) | 390 e 390; 0 elementos além da largura | 1351 e 1351; 0 elementos |
| Mapa (canvas do MapLibre) e WebGL2 | sim e sim | sim e sim |
| Quadros por segundo, parado | 60 | 60 |
| Quadros por segundo, tocando a 300× (07:30 a 07:44/07:45) | 60 | 34 (contador da página: 33) |
| Monte Carlo de abertura | 1.000 dias em 1,3 s com 12 worker(s); semente 20261021 | 1.000 dias em 1,4 s com 12 worker(s) |
| Erros no console | nenhum | nenhum |

Olhei as capturas: mapa desenhado com as quatro linhas e os trens, atribuição visível, controles legíveis; no celular, o painel do cenário fica acima do mapa (achado 15). A aba "Muitos dias" mostra a tabela por linha e o gráfico com IC 95%.

### 7b. Apresentação

Renderizei as 16 páginas de `docs/apresentacao/apresentacao.pdf` (960×540 pt, criado em 2026-10-21 06:33 UTC) e olhei todas. Nenhum conteúdo cortado, nenhum texto ilegível, rodapé fora do conteúdo em todas. Os gráficos têm legenda ou rótulo direto (linhas por nome, símbolos explicados no subtítulo). Defeitos: rodapé do slide 4 quebrado em duas linhas (achado 9), slide 3 com a execução antiga da reprodução (achado 8), rodapé do slide 13 sem `duracoes.md` (achado 10), "45,8% das horas" no slide 14 (achado 5). Conferi os números de cada slide contra os arquivos do rodapé (tabela do passo 4): todos batem. Não mudei `gera_deck.py`; o PDF não precisou ser refeito.

### 9. Correções feitas

| Arquivo | Mudança |
|---|---|
| `publicacao/testa_navegador.py` | Aba trazida para a frente depois de carregar; quadros contados por `requestAnimationFrame`, parada e tocando a 300×, com teto; Monte Carlo lido de `#s-mc`; erro claro se o navegador não abrir |
| `specs/010-mapa/spec.md`, `specs/010-mapa/plan.md` | fps com a animação tocando (34 e 60), registro da medida antiga e da causa; rolagem lateral zero no navegador sem janela |
| `docs/guia_simulador.md` | Mesma medida e o que o contador mostra com a animação parada |
| `specs/009-monte-carlo/spec.md` | 7,8 s, copiado de `politicas.md`; medição de hoje do tempo na página |
| `specs/000-proveniencia/spec.md` | 53 derivados no manifesto |
| `docs/decisoes/registro_de_decisoes.md` | D36 com a regra atual do comparador; "horas de operação" na D15; D46 |
| `docs/relatorio/relatorio.md` | "horas de operação" na condição do tempo |
| `docs/arquitetura.md` | O que o teste do navegador mede e como rodar |

Nada em `dados/derivados/` mudou; o manifesto não precisou ser regerado.

## O que não consegui verificar

- `modelo_taxa`, `distribuicoes` e `backtest` não foram rodados (regra da rodada). Também não rodei os relatórios do simulador (`vitest.relatorios.config.ts`): pesados para esta máquina e regravariam o tempo no `politicas.md`.
- O artefato do `reproduz.yml` (contagens 48, 5 e 0) exige login; vi só a conclusão de cada passo pela API pública.
- Só testei o Edge sem janela, com WebGL por software. Faltam o Chrome, o Firefox, o Safari, um notebook com placa de vídeo e um celular de verdade.
- Se o número da conta do GitHub é o RA (achado 14 da rodada 2).

## Aplicação das propostas, parte A

Feita na mesma data, a pedido da sessão principal. Cada achado foi reproduzido antes da correção. Decisão D47 no registro.

| Achado | Reprodução | O que mudou | Teste |
|---|---|---|---|
| 7 | `laco()` em `app/src/simulador/main.ts` contava todo quadro da página, tocando ou não; parado, a captura da rodada 3 mostrou 60 fps | Função pura `textoFps` e constante `FPS_PARADO` em `app/src/simulador/animacao.ts`. Parado, o contador mostra "parado" e zera a contagem; só mede enquanto toca. Texto inicial e título do elemento em `app/simulador/index.html` | `tests/simulador/animacao.test.ts`, "contador de quadros" |
| 13 | `app/relatorios/politicas.relatorio.ts:65` usava `5` e `50_000` | Importa `MAX_RODADAS` e `PRECISAO_ALVO` de `app/src/mc/rodadas.ts`; `META_PCT = 100 * PRECISAO_ALVO`. Chave do JSON e cabeçalho da tabela montados das constantes. `rodadasParaPrecisao` usa `PRECISAO_ALVO` como padrão em vez de `0.05`. Com os valores atuais, a chave (`meia_largura_pct_com_50000_dias`) e o texto ("5%", "50.000") saem iguais; `100 * 0.05 === 5` conferido no Node. Relatório não rodado, como pedido | `tsc` com `relatorios/politicas.relatorio.ts` incluído (tsconfig temporário em `app/`, apagado depois): 0 erros. O `tsconfig.json` do app não inclui `relatorios/` |
| 14 | Pasta refeita com `novo.json` a mais dava "0 arquivo(s)" e saída 0 (rodada 3) | `pipeline/compara_derivados.py`: funções `relativos` e `percorre`; percorre a união das duas pastas e acusa `FALTA` e `SOBRA`. Depois: `SOBRA novo.json`, "1 arquivo(s)", saída 1. Conferência prévia: 53 arquivos em `dados/derivados/` no disco, 53 no git e 53 no manifesto, sem diferença entre os conjuntos; os scripts de `pipeline/` e os dois relatórios do app gravam só saídas com nome fixo, todas versionadas | `pipeline/tests/test_compara.py`, `test_arquivo_que_falta_ou_sobra_na_refeita_e_problema` |
| 15 | `app/simulador/index.html:15` e `:111` diziam "à esquerda" | "no painel do cenário" nos dois lugares | não cabe (texto) |
| 16 | `specs/013-publicacao/spec.md` dava "Atende" com a `v1.0.0`; `tasks.md` mantém aberta a versão de entrega | Linha do resultado: "Mecanismo atende; versão de entrega pendente", com o commit 6196ad2 e a referência ao `tasks.md`. A redação do critério não mudou. O status da spec ficou "implementada": a condição do critério (fim do semestre) ainda não chegou. A sessão principal pode preferir "implementada com exceções" | não cabe (texto) |

Testes depois das correções, um por vez:

- `.venv/Scripts/python.exe -m pytest pipeline/tests -q`: 56 passaram.
- `npx tsc --noEmit` (em `app/`): saída 0, sem erros.
- `npm test` (em `app/`): 17 arquivos, 88 testes, todos passaram.

Não rodado, como pedido: navegador, `npm run build`, `modelo_taxa`, `distribuicoes`, `backtest` e o relatório das políticas. Nenhum arquivo de `dados/derivados/` mudou, então o manifesto não foi regerado.

Não verificado:

- O contador "parado" na página real (sem navegador). `publicacao/testa_navegador.py` só registra o texto do contador, não o compara, então não quebra; a medida "fps_parado" passa a ler "parado".
- O `reproduz.yml` com o comparador novo. Risco: se algum passo do CI gravar arquivo em `dados/derivados/` que a máquina local não grava, a execução passa a falhar com `SOBRA`. A conferência local não achou nenhum.


## Aplicação das propostas, parte B

Feita na mesma data, a pedido da sessão principal. Só a apresentação. Nenhum número de modelo, critério de spec ou arquivo de `dados/derivados/` mudou. É mudança de texto do deck, sem mudança de comportamento; por isso não há decisão nova no registro.

| Achado | Conferência na origem | O que mudou em `docs/apresentacao/gera_deck.py` | Como foi conferido |
|---|---|---|---|
| 5 (parte do deck) | `resumo_clima.json`: `pct_horas_operacao_com_condicao` = 0.4581 | Slide 14: "45,8% das horas" virou "45,8% das horas de operação" | Página 14 do PDF renderizada e lida |
| 8 | `specs/013-publicacao/spec.md` (Resultado) e D36: no ba19e74, execução 39556506384, 48 idênticos, 5 na tolerância, 0 fora | Slide 3: etiqueta do item 5 cita o ba19e74 (48, 5, 0). A nota do apresentador mantém a 2ª execução (45 e 8) e acrescenta a do ba19e74. Rodapé passa a citar `specs/013-publicacao/spec.md (Resultado) e tasks.md` | Página 3 do PDF renderizada e lida |
| 9 | Rodapé da direita quebrava em duas linhas no slide 4 | `.slide > footer .pg` ganhou `white-space:nowrap;flex:none` | Páginas 4 e 13 (fonte da esquerda em duas linhas): "dados 2026-10-20 e 2026-10-21 · N" numa linha só |
| 10 | `fontes/verificacao/duracoes.md`: razões 1,228 e 1,291 (Laranja), 1,262 (Verde · EF), 3,384 (Azul · EF), que dão 23% a 29%, 26% e 3,4 vezes | Slide 13: rodapé cita `fontes/verificacao/duracoes.md (razões das médias)` | Página 13 do PDF renderizada e lida |

Regerado:

- `python -I docs/apresentacao/gera_deck.py`: 16 slides, `index.html` com 99 KB.
- PDF pelo Edge sem janela (`--headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf`): 687.708 bytes, 16 páginas de 960 × 540 pt.
- As 16 páginas renderizadas em PNG (PyMuPDF, 110 dpi, pasta temporária fora do repositório). Li as páginas 3, 4, 13 e 14 e uma folha com as 16. Nenhum bloco de texto passa da borda da página (conferido por script). Nenhum conteúdo cortado. O rodapé da direita fica numa linha em todas. A fonte da esquerda ocupa duas linhas nos slides 4 e 13, dentro da faixa do rodapé, sem invadir o conteúdo.

Testes depois da parte B: `pytest pipeline/tests` 56 passaram; `verifica_fontes.py` sem argumentos, 0 problema. Não rodados: `npx tsc`, `npm test` e `npm run build` (nenhum arquivo de `app/` mudou) e o teste do navegador.

Situação dos achados 5, 8, 9 e 10: corrigidos. A tabela de achados acima fica como estava na rodada, para registro.

## Aplicação das propostas, parte C (navegador no site publicado)

Site publicado no commit `a7f0594`. `publicacao/testa_navegador.py`, Edge sem janela, `ESPERA=50`, um tamanho por vez, saída em pasta temporária fora do repositório, `msedge.exe` encerrado depois de cada rodada.

**Defeito novo (média, corrigido).** `publicacao/testa_navegador.py`: só `Page.bringToFront` não basta. Na 1ª rodada no celular, a página estava `visible` na leitura das medidas e voltou a `hidden` segundos depois. As duas medidas de quadros saíram `null`, com motivo "requestAnimationFrame parado". Correção: flags `--disable-backgrounding-occluded-windows`, `--disable-renderer-backgrounding` e `--disable-background-timer-throttling` na abertura do navegador e `Emulation.setFocusEmulationEnabled` depois do `bringToFront`. Muda só a ferramenta de teste; nada do site nem do modelo.

| Medida | Celular 390×844, antes da correção | Celular, depois | Notebook 1366×768, depois |
|---|---|---|---|
| `scrollWidth` / `clientWidth` | 390 / 390 | 390 / 390 | 1351 / 1351 |
| Elementos além da largura | 0 | 0 | 0 |
| Canvas do mapa / WebGL2 | sim / sim | sim / sim | sim / sim |
| Monte Carlo de abertura | 1.000 dias em 1,5 s, 12 workers, semente 20261021 | 1.000 dias em 2,2 s, 12 workers, semente 20261021 | 1.000 dias em 1,7 s, 12 workers, semente 20261021 |
| Parado: quadros/s (rAF), contador, relógio | null (página `hidden`) | 61, "parado", 07:30 | 60, "parado", 07:30 |
| Tocando a 300×: quadros/s, contador, relógio | null (página `hidden`) | 60, "60 fps", 07:45 | 33, "34 fps", 07:44 |
| Erros no console | 0 | 0 | 0 |

Capturas olhadas com a ferramenta Read. Celular: cabeçalho, abas em duas linhas e painel do cenário, sem corte nem rolagem lateral (o mapa fica abaixo da dobra). Notebook: mapa desenhado com as quatro linhas e os trens, botão de pausa (animação tocando), 300×, relógio 07:45, contador "34 fps". A atribuição do mapa ocupa duas linhas no notebook e cobre a borda de baixo do mapa; não esconde estação. Baixa, sem correção.

Conferido: rolagem lateral zero nos dois tamanhos; mapa com WebGL; nenhum erro no console; contador "parado" com a animação parada e um número de quadros a 300×; Monte Carlo de abertura terminado. No notebook, a 300×, o fps cai para cerca de 33 (WebGL por software, SwiftShader). Não é medida de máquina real.

Testes depois da parte C: só `publicacao/testa_navegador.py` mudou, e ele não é coberto por `pytest pipeline/tests` nem pelo `app/`. Rodado de novo nos dois tamanhos, com o resultado da tabela.
