# SDD: como conduzimos o projeto

Spec-Driven Development: a especificação é a fonte de verdade; o código é derivado dela. O layout é o do GitHub Spec Kit (`specs/NNN-nome/` com `spec.md`, `plan.md`, `tasks.md` e, quando houver pesquisa, `research.md`). Adotar a ferramenta depois não exige mover nada.

## Ciclo

| Etapa | Arquivo | Responde | Quem aprova |
|---|---|---|---|
| 0. Princípios | [`constitution.md`](constitution.md) | O que vale para tudo, sempre | Equipe |
| 1. Especificar | `specs/NNN-nome/spec.md` | O quê e por quê: pergunta de engenharia, critérios de aceite mensuráveis | Equipe |
| 2. Pesquisar | `specs/NNN-nome/research.md` | Que dados e métodos existem, com URL e data | Quem implementa |
| 3. Planejar | `specs/NNN-nome/plan.md` | Como: componentes, dados, contratos, pontos de falha | Quem implementa |
| 4. Quebrar | `specs/NNN-nome/tasks.md` | Tarefas pequenas, ordenadas, cada uma verificável | Quem implementa |
| 5. Implementar | código, testes, relatórios | — | Revisão contra a spec |

## Regras

- `spec.md` não fala de tecnologia. `plan.md` não muda o que a spec pede; se precisar, volta-se à spec.
- Toda spec tem uma **pergunta de engenharia** e o número que a responde.
- Critério de aceite é mensurável e vira teste automatizado ou relatório datado em `fontes/verificacao/`.
- Critério não atendido não se apaga nem se afrouxa depois de ver o resultado: registra-se como exceção, com explicação.
- Mudança de rumo se registra na spec, com data, antes de mexer no código.

## Status

| Status | Significa |
|---|---|
| especificada | `spec.md` escrita e revisada |
| em andamento | `plan.md` e `tasks.md` prontos, implementação começou |
| implementada | todos os critérios de aceite atendidos |
| implementada com exceções | entregue; algum critério não foi atendido e a exceção está documentada |

## Mapa das specs

| Nº | Nome | Fase |
|---|---|---|
| 000 | [Proveniência](000-proveniencia/spec.md) | F0 |
| 001 | [Normalização dos incidentes](001-normalizacao/spec.md) | F1 |
| 002 | [Base geoespacial](002-geoespacial/spec.md) | F0 |
| 003 | [Clima e eventos](003-clima-eventos/spec.md) | F1 |
| 004 | [Exposição](004-exposicao/spec.md) | F1 |
| 005 | [Modelo da taxa de falha](005-modelo-taxa/spec.md) | F2 |
| 006 | [Tempo entre falhas, tempo até restabelecer e causa comum](006-tbf-ttr-causa-comum/spec.md) | F2 |
| 007 | [Motor de simulação](007-motor-des/spec.md) | F3 |
| 008 | [Políticas de tolerância a falhas](008-politicas/spec.md) | F4 |
| 009 | [Monte Carlo e métricas](009-monte-carlo/spec.md) | F3 |
| 010 | [Mapa e animação](010-mapa/spec.md) | F4 |
| 011 | [Cenários](011-cenarios/spec.md) | F4 |
| 012 | [Validação contra o histórico](012-backtest/spec.md) | F5 |
| 013 | [Publicação](013-publicacao/spec.md) | F6 |

Decisões de arquitetura ficam em [`../docs/decisoes/`](../docs/decisoes/).
