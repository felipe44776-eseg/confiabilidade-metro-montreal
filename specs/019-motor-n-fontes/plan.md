# 019 — Simulador com várias fontes por linha: plano

## Passo 1: reorganizar sem mudar números

| Peça | Mudança | Arquivo |
|---|---|---|
| Tipos | `FonteFalha` ganha `id`, `familia` (`MR` \| `EF`), `efeito` (`trem` \| `trecho`) e os sub-fluxos explícitos (`subInstantes`, `subDuracao`, `subEscolha`, `subPolitica`). `Causa` continua como a família | `app/src/motor/tipos.ts`, `contexto.ts` |
| Adaptador v1 | Contrato v1: duas fontes por linha, na mesma ordem de hoje, com os sub-fluxos de hoje (`li`; `li*2` e `li*2+1`; `li` e `50+li`; `li`) e os mesmos rótulos (`falhas_mr`/`falhas_ef`, textos do `detalhe`) | `contexto.ts` |
| Despacho | `dia.ts` usa `efeito` no lugar de `causa === 'MR'`; o `Pendente` leva o índice da fonte (fim do `find` em `duracaoDaFonte`) | `app/src/motor/dia.ts` |
| Prova | `tests/motor/referencia_v1.test.ts` idêntico; relatórios do app regenerados sem diferença no git | — |

## Passo 2: contrato v2

| Peça | Mudança | Arquivo |
|---|---|---|
| Fontes do arquivo | `parametros.fontes[]`: uma `FonteFalha` por linha × fonte, com taxa (`base` × multiplicadores da fonte), renovação, duração e locais próprios | `contexto.ts`, `taxas.ts` |
| Fluxos | `hash30("linha|fonte")` em `prng.ts` (movido de `linhas_novas.ts`); fluxos `falhas`, `duracoes`, `escolha`, `politicas` com esse sub-índice | `prng.ts`, `dia.ts` |
| Políticas | Retirada: fontes `efeito = trem`; degradada: `efeito = trecho`; lista em `hipoteses` | `dia.ts`, `politicas.ts` |
| Métricas | `minutosPorFonte`, `falhasPorFonte`, minutos por classe de gravidade; nomes MR/EF/CC mantidos; métricas novas no fim do vetor | `dia.ts`, `mc/rodadas.ts` |
| Consumidores | `expansao.ts` e `linhas_novas.ts` somam as fontes por efeito (fim do `find` por causa); `efeito.ts`, `pesos.ts`, `extrapolacao.ts`, `animacao.ts` (id da fonte), `main.ts` | `app/src/motor`, `app/src/simulador` |
| Link | Parâmetro `v=2`; sem ele, aviso e link para `/versoes/v1.1.0/` | `app/src/simulador/cenario.ts`, `main.ts` |
| Dispersão | Teste com a variância ÷ média por dia e por mês, simulada contra a histórica | `app/tests/motor/dispersao.test.ts`, `app/relatorios/` |
