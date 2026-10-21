# Revisão crítica (2026-10-21, rodada 2)

Feita pelo agente `.claude/agents/critico-stf.md`, passos 1 a 9, sobre o commit 62d1c14 (já publicado). Foco: (a) conferir os 13 achados da rodada 1 marcados como aplicados; (b) procurar defeitos novos trazidos por essas correções; (c) conferir no site publicado `/apresentacao/`, `/decisoes/`, `/relatorio/`, `/docs/guia/` e `/simulador/`.

## Resumo

- Testes verdes antes e depois: pytest 55/55, vitest 86/86 antes e 87/87 depois (1 teste novo), `tsc` e build sem erro, 25 números recalculados com 0 diferenças, manifesto com 0 problemas. Os sete scripts rápidos deram arquivos idênticos byte a byte, inclusive o `parametros.json` com o novo `codigo_commit`.
- Dos 13 achados aplicados, 9 estão completos e 4 ficaram incompletos (12, 13, 18 e 19). O site publicado é igual à montagem local do 62d1c14 em todas as páginas conferidas.
- 14 achados novos: 0 altos, 2 médios, 12 baixos. 7 corrigidos no todo ou em parte; 7 ficam como proposta. Nenhum número de modelo mudou e nenhum arquivo de `dados/derivados/` foi tocado.

## Achados

| # | Gravidade | Arquivo e linha | Evidência reproduzida | Correção | Corrigido |
|---|---|---|---|---|---|
| 1 | média | `specs/011-cenarios/plan.md:25`; `specs/011-cenarios/spec.md` | O plano dizia "o indicador de greve também entra no multiplicador". O contrato publicado não tem mais `greve` nos multiplicadores (conferido em MR e EF), e o motor só multiplica os fatores do contrato (`taxas.ts`, função `multiplicador`). A D42 é mudança "depois de ver", mas nenhuma spec a registrava com data, como pede o invariante 2 | Plano 011 descreve a greve só pela oferta, com data e D42. Linha "Mudança registrada em 2026-10-21" no Resultado da spec 011 | sim |
| 2 | média | `app/src/motor/taxas.ts:51` | `base_por_trem_hora[linha]?.valor ?? 0`: sem taxa-base no contrato, a linha fica com taxa zero, nunca falha e aparece 100% disponível, sem erro. Reproduzido com um teste (contrato sem a taxa-base de MR): a função devolveu a taxa acumulada zerada em vez de falhar. Fere o invariante 3. Com os dados publicados não acontece: as quatro linhas têm taxa | O motor para com erro que cita a causa e a linha. Teste novo `app/tests/motor/taxas.test.ts`. Decisão D44 | sim |
| 3 | baixa | `app/tests/simulador/cenario.test.ts:108`; `app/tests/fixtures/gera_parametros_teste.mjs:45` | Nenhum teste travava a D42. O teste de cenário ainda exige o multiplicador de greve, que vem do fixture e não existe mais no contrato real. Tirar o `continue` de `parametros.py` passaria por todos os testes | Asserção no teste do contrato (`pipeline/tests/test_modelos.py`): não há `greve` nos multiplicadores. Conferi que ela falha no contrato do 6196ad2. Falta tirar `greve` do fixture e do teste de cenário | em parte |
| 4 | baixa | `specs/009-monte-carlo/spec.md:34` | "12.000 dias em 11,7 s ... cerca de 5 s para 5.000". O relatório gerado (`politicas.md`, execução publicada) diz 9,0 s. O tempo mudou quando os relatórios foram refeitos no 62d1c14 | Texto copiado de `politicas.md` (9,0 s), com a nota de que o tempo muda a cada execução. Saiu a conta "cerca de 5 s", que não está em arquivo gerado | sim |
| 5 | baixa | `specs/013-publicacao/spec.md` (Resultado, linha da reprodução) | A spec virou "implementada" com a execução 39546898051 do `reproduz.yml`, feita no a276b56. O 62d1c14 mudou `parametros.json` (D42 e D43), `politicas.json` e `expansao.json`. Pela API pública do GitHub, não há `reproduz.yml` no 62d1c14 (só "Publicar site", com sucesso). Localmente, refiz o `parametros.json` byte a byte | Disparar o `reproduz.yml` no commit atual e citar a nova execução na spec | não (proposta) |
| 6 | baixa | `pipeline/verifica_fontes.py:253` | A página `/fontes/` publicada mostra "Download da Release dados-2026-10-20", mas a verificação baixa as duas Releases (cada fonte usa a sua). Quem confere a spec 000 lê que só uma Release foi baixada | O cabeçalho lista todas as Releases do manifesto. Testado com a função isolada (uma e duas Releases); nenhum script lê esse texto | sim |
| 7 | baixa | `fontes/FONTES.md:62`; deck, slide 13 (`docs/apresentacao/gera_deck.py:741`) | Achado 18 da rodada 1 aplicado só na D25. "97,95% com tolerância de 1 minuto" e "de 1.433 min/ano" seguem sem arquivo gerado e sem marca. Refiz o 97,95% de `eventos_tecnicos.csv` (8.355 de 8.530); o valor está certo | FONTES.md marca o número como conferência pontual sem arquivo gerado. O deck fica como proposta: `gera_deck.py` está sendo editado por outra sessão | em parte |
| 8 | baixa | `docs/relatorio/relatorio.md:120`, D25, spec 006, deck (slide 13), `app/relatorios/politicas.relatorio.ts:118` | Achado 13 aplicado só no texto. As razões estão certas: média observada ÷ média da lognormal em `parametros.json` dá 1,228 e 1,291 (Laranja), 1,262 (Verde EF) e 3,384 (Azul EF). Mas nenhum arquivo gerado publica essas razões (invariante 1) | `parametros.py` ou `diagnostico_taxa.py` gravar a tabela de razões num relatório de `fontes/verificacao/` | não (proposta) |
| 9 | baixa | `specs/009-monte-carlo/spec.md:30` | "Com 50 mil dias, a meia-largura da Azul fica perto de 9%" não está em arquivo gerado. Sai de 5% vezes a raiz de 168.183 ÷ 50.000 (9,2%) | Gravar a meia-largura com 50.000 dias em `politicas.md`, ou citar a conta | não (proposta) |
| 10 | baixa | `specs/008-politicas/plan.md:39`; `app/src/simulador/main.ts:175`; `app/tests/fixtures/gera_parametros_teste.mjs:85` | Achado 19 incompleto. O plano 008 ainda sugeria "trocar por `tempo_ativacao_degradada_min`", troca já feita. `main.ts` filtra `duracao_degradada_min`, que não existe mais. O fixture ainda a cria | Plano 008 atualizado, com data. Tirar o filtro morto e a entrada do fixture fica como proposta | em parte |
| 11 | baixa | `pipeline/parametros.py:37-46`; `pipeline/compara_derivados.py:19` | D43: o hash conferiu (`e05a311efcb01915`, igual ao SHA-256 dos blobs do git com fim de linha LF). Mas ele identifica os scripts no momento em que `parametros.py` roda, não os que geraram as entradas: `distribuicoes.py` mudou no 62d1c14 e `distribuicoes.json` é do 6196ad2. E o comparador ainda ignora `codigo_commit`, que agora é determinístico e poderia acusar contrato gerado com código fora do commit | Cada ajuste grava o hash do próprio script no seu JSON e `parametros.py` combina os três; tirar `codigo_commit` do `IGNORAR` | não (proposta) |
| 12 | baixa | `app/relatorios/politicas.relatorio.ts:63`; `dados/derivados/simulador/politicas.json` | `segundos_para_3x_rodadas` é tempo de relógio dentro de um derivado com hash no manifesto: mudou de 11,69 para 8,95 no 62d1c14 sem mudar nenhum resultado. Rodar o relatório de novo quebra o hash (invariante 4; a exceção declarada vale só para os modelos com bootstrap). O comparador ignora a chave `segundos` | Deixar o tempo só no `politicas.md` ou no log, fora do JSON | não (proposta) |
| 13 | baixa | `dados/derivados/gtfs/` | 53 arquivos versionados em `dados/derivados/`, 48 no manifesto. Fora dele: `agency.txt`, `calendar.txt`, `calendar_dates.txt`, `feed_info.txt` e `routes.txt`. Nenhum script os lê e o site não os publica, por isso o critério da spec 000 ("usado pelo site") continua atendido | Tirar da extração em `extrai_gtfs_metro.py` ou pôr no manifesto | não (proposta) |
| 14 | baixa | `pipeline/baixa_clima_eventos.py:23` e todo endereço do projeto | Achado 4 da rodada 1: o número do e-mail institucional saiu do User-Agent, mas o mesmo número está no nome da conta do GitHub. Por isso aparece em toda URL do repositório e do site, inclusive no novo User-Agent, e no autor de cada commit. Não se sabe se é o RA (a dúvida está registrada fora do repositório) | Decisão da equipe: confirmar se é o RA. Se for, só uma conta nova resolve | não (decisão da equipe) |

## Situação dos 13 achados aplicados pela sessão principal

| Achado | Conferência | Situação |
|---|---|---|
| 12 (greve) | Contrato sem `greve` em MR e EF; guia e D42 corretos; `politicas.json` e `expansao.json` mudaram só em `codigo_parametros` e no tempo, como a D42 diz | incompleto: plano 011 e registro na spec (achado 1), sem teste (achado 3) |
| 13 (23% a 29%) | Texto certo nos cinco lugares; razões refeitas de `parametros.json` | incompleto: número sem arquivo gerado (achado 8) |
| 15 (`codigo_commit`) | Hash refeito dos blobs do git; `parametros.py` rodado de novo dá o mesmo arquivo | completo (ressalvas no achado 11) |
| 16 (113 eventos-par) | 31 + 18 + 12 + 21 + 21 + 10 = 113 em `distribuicoes.md` | completo |
| 17 (98,5%) | Refeito de `eventos_tecnicos.csv`: 8.404 de 8.530 (98,52%) entre 05:00 e 01:59 | completo |
| 18 (números sem arquivo) | Marcado na D25 | incompleto: FONTES.md:62 e deck (achado 7) |
| 19 (comentários e planos) | `hipoteses.ts`, `expansao.ts`, planos 007 e 014 corretos; os 14 nomes do motor batem com os 14 do contrato, com o mesmo valor e a mesma faixa | incompleto: plano 008, `main.ts` e fixture (achado 10) |
| 20 (spec 000) | Tabela presente; 45 fontes e 48 derivados no manifesto, todos com SHA-256, script e origem | completo |
| 21 (rodapé do deck) | 16 slides com "dados 2026-10-20 e 2026-10-21", lido do manifesto; o PDF de 03:01 também traz | completo |
| 22 (Mermaid) | Nota na página e link "Gerado de" para o GitHub no fim | completo |
| 23 (quase triplica) | Relatório e deck | completo |
| 24 (duas definições) | Nota no relatório §7 e "(simulador)" no título do slide 15 | completo |
| 25 (reamostras válidas) | Código grava o mínimo entre MR e EF, coerente com o corte de caminhos; `backtest.json` publicado: 100 × 20 = 2.000 em A, B, C e D | completo |

## Resultado de cada passo

### 1. Contexto

15 specs. Implementadas: 000, 003, 005, 006, 007, 008, 011, 013 e 014. Implementadas com exceções: 001, 002, 004, 009, 010 e 012. Li README, `specs/README.md`, a constituição, `docs/arquitetura.md` e o relatório da rodada 1.

Durante a revisão, outra sessão editava a árvore: favicon em `app/mapa/index.html`, `app/simulador/index.html`, `painel/gera_site.py`, `publicacao/monta_site.py` e `docs/apresentacao/gera_deck.py`; CSS das abas; `publicacao/testa_navegador.py` (novo); um parágrafo em `docs/arquitetura.md`; e o próprio agente. Não toquei nesses arquivos, exceto uma linha de `docs/arquitetura.md` (contagem de testes). Nota: na árvore atual, `gera_deck.py` já gera o favicon, mas o `index.html` versionado não; regerar o deck antes do commit.

### 2. Testes

| Comando | Antes | Depois |
|---|---|---|
| `.venv/Scripts/python.exe -m pytest pipeline/tests -q` | 55 passaram | 55 passaram (uma asserção nova no teste do contrato) |
| `python -I pipeline/verifica_fontes.py --recalcula` | 0 problemas; 25 números, 0 diferenças | igual |
| `npx tsc --noEmit` | sem erro | sem erro |
| `npm test` | 16 arquivos, 86 testes | 17 arquivos, 87 testes |
| `npm run build` | sem erro (aviso do Vite sobre `__dirname`) | sem erro |

### 3. Reprodutibilidade barata

Rodei de novo, com o Python do `.venv`, `normaliza`, `exposicao`, `clima_eventos`, `horario_simulador`, `candidatas`, `parametros` e `diagnostico_taxa`. `git status` ficou vazio: todas as saídas idênticas byte a byte. `verifica_fontes.py` sem argumentos: 0 problemas. O `codigo_commit` refeito (`sha256-scripts:e05a311efcb01915`) é igual ao SHA-256 dos três scripts lidos dos blobs do git, que não têm CR; o resultado não depende do fim de linha do Windows.

`gera_deck.py` rodado duas vezes: o mesmo SHA-256 do `index.html` versionado (antes da edição do favicon pela outra sessão).

Pela API pública do GitHub: o último `reproduz.yml` é o 39546898051 (a276b56), com sucesso. Não há execução no 62d1c14 (achado 5). O "Publicar site" do 62d1c14 (39553235081) terminou com sucesso.

### 4. Números dos documentos

Conferi os números que mudaram depois da rodada 1. Os arquivos gerados que os sustentam só mudaram em metadados no 62d1c14 (`codigo_parametros` e tempo), então os cerca de 150 números conferidos na rodada 1 continuam valendo.

| Número | Onde | Origem | Valor na origem | Igual? |
|---|---|---|---|---|
| 23% a 29% (Laranja), 26% (Verde EF), 3,4 vezes (Azul EF) | relatório, D25, spec 006, deck | `parametros.json` (`media_min` contra exp(μ + σ²/2)) | 1,228 e 1,291; 1,262; 3,384 | sim, mas sem arquivo gerado (achado 8) |
| 113 eventos-par | D24 | `distribuicoes.md` | soma dos 6 pares = 113 | sim |
| 98,5% entre 05:00 e 01:59 | D12, FONTES | `eventos_tecnicos.csv` | 98,52% | sim |
| 97,5% (8.319 de 8.530); 97,95% com 1 minuto | FONTES.md:62 | `resumo_normalizacao.json`; `eventos_tecnicos.csv` | 8.319; 8.355 de 8.530 = 97,95% | sim; o segundo sem arquivo gerado (achado 7) |
| 1,17 (0,56–2,24) e 1,11 (0,52–1,73) | guia, relatório, spec 011 | `modelo_taxa.md` | iguais | sim |
| 11,7 s para 12.000 dias | spec 009 | `politicas.md` | 9,0 s | não (corrigido) |
| perto de 9% | spec 009 | nenhum | 9,2% pela conta | sem arquivo (achado 9) |
| 1.433 min/ano | deck slide 13, spec 009, D25 | nenhum (registro histórico na D25) | — | sem arquivo (achado 7) |
| 99,5% a 99,9% num dia útil | relatório §7, deck slide 15 | `politicas.md` | 99,504% a 99,892% | sim |
| 45 fontes e 48 derivados | spec 000 | `fontes_manifesto.json` | 45 e 48 | sim |
| 45 idênticos e 8 na tolerância | spec 013 | arquivos em `dados/derivados/` | 53 arquivos | sim na contagem; o log exige login |
| 100 vetores × 20 = 2.000 caminhos | achado 25 | `backtest.json` | iguais em A, B, C e D | sim |
| 55 e 86 testes | `docs/arquitetura.md` | pytest e vitest | 55 e 86 antes; 87 depois do teste novo | corrigido para 87 |
| Tamanho e SHA-256 de 10 arquivos (incidentes, km real, GTFS, mobilidade, 3 zips horários, F1, greves, OSM de expansão) | `fontes/FONTES.md` | arquivos e manifesto | iguais | sim |
| 25 dias de greve, 6.520 bytes | FONTES.md | `greves_stm.csv` | 25; 6.520 | sim |
| Releases 2026-10-20 e 2026-10-21 | rodapé do deck | manifesto | iguais | sim |
| 1× a 300×; até 16 workers; 251, 52 e 62 dias | guia | `simulador/index.html`, `pool.ts`, `rodadas.ts` | iguais | sim |

### 5. Critérios das specs

As tabelas de Resultado mudadas depois da rodada 1 (000, 006, 009, 011, 012 e 013) batem com os arquivos citados, com três ressalvas: o tempo da spec 009 (achado 4, corrigido); a prova da spec 013 é de um commit anterior às mudanças D42 e D43 (achado 5); e a D42 não estava registrada na spec 011 (achado 1, corrigido). A linha da spec 012 sobre minutos parados confere com `backtest.md` (versões B e C em 2025 e D em 2023, as quatro linhas dentro; versão A com Verde e Amarela fora).

### 6. Código

- `parametros.py`: a greve sai do contrato por um `continue` com comentário e data. O motor trata fator ausente como 1 (só itera os fatores do contrato). `extrapolacao.ts:73` procura `greve` no contrato com encadeamento opcional: sem erro, só deixa de avisar incerteza de um multiplicador que não é mais aplicado.
- Dado ausente que vira valor: a taxa-base (achado 2, corrigido). Outros padrões latentes, sem efeito com os dados publicados: `locais_ef_sem_posicao?.[linha] ?? 0` em `contexto.ts:112` e `renovacaoDe` em `taxas.ts`, que usa forma 1 quando falta a renovação. Ficam como observação.
- `publicacao/md.py`: tabelas, links e âncoras corretos em todas as páginas montadas. Não trata `\|` dentro de célula nem URL com parênteses; nenhum documento usa. Não há ids repetidos.
- Sorteio: só `analise_confiabilidade.py` usa `random`, com semente fixa. Nenhum `Math.random`.
- Teto de tempo: todas as chamadas de rede têm. `publicacao/testa_navegador.py` (novo, fora do CI) tem teto nas conexões; o caminho do Edge é do Windows, mas o script também procura o Chrome no Linux e aceita a variável `NAVEGADOR`.
- Exceções: `backtest.py:90` descarta a reamostra com erro, mas agora o número válido fica no arquivo (achado 25 da rodada 1).

### 7. Site

| Página publicada | HTTP | Igual à montagem local do 62d1c14? |
|---|---|---|
| `/`, `/mapa/`, `/specs/`, `/versoes/v1.0.0/`, `/versoes/v1.0.0/simulador/` | 200 | `/specs/` sim; os outros não comparei |
| `/simulador/` | 200 | sim |
| `/relatorio/` | 200 | sim |
| `/decisoes/`, `/decisoes/0001/` | 200 | `/decisoes/` sim |
| `/docs/guia/`, `/docs/arquitetura/`, `/docs/dicionario/` | 200 | guia e arquitetura sim |
| `/apresentacao/` e `apresentacao.pdf` | 200 | sim, os dois |
| `/fontes/`, `/fontes/documentacao/` | 200 | documentação sim; `/fontes/` só difere no bloco da verificação do CI ("sem problemas", 0 problemas, 0 diferenças) |
| `/fontes/verificacao/` (crítica, distribuições, políticas, backtest e SVG) | 200 | distribuições e políticas sim |
| `/dados/simulador/parametros.json`, `/fontes/fontes_manifesto.json` | 200 | sim |

Nas páginas publicadas estão D42, D43, "entre 05:00 e 01:59", "113 eventos-par", "registro histórico", "2% a 10%", a greve só pela oferta no guia, "quase triplica", "26% nos equipamentos", a nota das duas definições, o rodapé com as Releases nos 16 slides e a nota do Mermaid.

Montagem local (`npm run build` e `monta_site.py`): 22 páginas, 368 links, 0 tabelas com número de células diferente do cabeçalho, 0 links relativos quebrados, 0 âncoras inexistentes. Os 69 caminhos de `github.com/.../blob/main/` e `tree/main/` existem no HEAD.

### 9. Correções feitas

| Arquivo | Mudança |
|---|---|
| `app/src/motor/taxas.ts` | Taxa-base ausente vira erro, não zero |
| `app/tests/motor/taxas.test.ts` (novo) | Teste do item acima; falhou antes da correção e passa depois |
| `pipeline/tests/test_modelos.py` | Asserção: contrato sem multiplicador de greve (D42) |
| `pipeline/verifica_fontes.py` | Cabeçalho do download lista todas as Releases |
| `specs/011-cenarios/plan.md`, `specs/011-cenarios/spec.md` | Greve só pela oferta, com data e D42 |
| `specs/009-monte-carlo/spec.md` | 9,0 s, copiado de `politicas.md` |
| `specs/008-politicas/plan.md` | Sugestão já aplicada vira registro com data |
| `fontes/FONTES.md` | 97,95% marcado como conferência pontual sem arquivo gerado |
| `docs/arquitetura.md` | 87 testes no vitest |
| `docs/decisoes/registro_de_decisoes.md` | D44 |

Nada em `dados/derivados/` mudou; o manifesto não precisou ser regerado.

## O que não consegui verificar

- `modelo_taxa`, `distribuicoes` e `backtest` não foram rodados (regra da rodada). Também não rodei os relatórios do simulador (`vitest.relatorios.config.ts`): eles regravam `politicas.json` com outro tempo e quebrariam o hash (achado 12).
- O log do `reproduz.yml` exige login, e `gh` está fora do escopo. Vi só a conclusão na API pública, e não há execução no 62d1c14.
- O texto de 5 das 16 páginas do PDF não foi extraído (erro de fonte no `pypdf`); conferi as outras 11 e a data de criação (03:01, depois das correções).
- Se o número da conta do GitHub é o RA (achado 14).
- Desempenho e aparência no navegador: não abri navegador.

## O que a sessão principal fez com as propostas (2026-10-21)

A sessão do agente foi encerrada pelo Claude Code por falta de memória na máquina depois de gravar este relatório; as propostas abaixo foram aplicadas pela sessão principal (decisão D45).

| Achado | Decisão | Onde |
|---|---|---|
| 3 (greve sem teste) | Aplicado: a fixture não tem mais o multiplicador de greve, e o teste de cenário exige que ele não exista | `gera_parametros_teste.mjs`, `parametros_teste.json`, `cenario.test.ts` |
| 5 (reprodução no commit atual) | Aplicado: `reproduz.yml` disparado de novo depois da publicação; a spec 013 cita a nova execução | spec 013 |
| 7 (números sem arquivo no deck) | Aplicado: "1.433 min/ano" marcado como registro histórico no slide 13 | `gera_deck.py` |
| 8 (razões sem arquivo gerado) | Aplicado: `parametros.py` grava `fontes/verificacao/duracoes.md` | relatório, D25 |
| 9 (meia-largura com 50 mil dias) | Aplicado: o relatório das políticas grava a meia-largura esperada (Azul 9,2%) | `politicas.relatorio.ts`, spec 009 |
| 10 (resto do achado 19) | Aplicado: filtro morto saiu de `main.ts`; a hipótese sem uso saiu da fixture | `main.ts`, fixture |
| 11 (comparador ignora o código) | Aplicado: `codigo_commit` e `codigo_parametros` voltam a ser comparados; o teste do comparador cobre o caso | `compara_derivados.py`, `test_compara.py` |
| 12 (tempo de relógio no JSON) | Aplicado: o tempo fica só no `politicas.md` | `politicas.relatorio.ts` |
| 13 (GTFS fora do manifesto) | Aplicado: os cinco arquivos entraram no manifesto | `verifica_fontes.py` |
| 14 (número da conta do GitHub) | Decisão da equipe: confirmar se é o RA | — |
