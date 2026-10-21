# 013 — Publicação, verificação periódica e novas versões de dados

**Status:** implementada
**Fase:** F6 (semana 10 em diante)
**Depende de:** 000 e todas as anteriores

## Pergunta de engenharia
Quando a STM publicar dados novos, o site é atualizado sem passo manual e sem perder a rastreabilidade? O número que responde é a quantidade de passos manuais para publicar uma nova versão de dados: deve ser zero além de aprovar.

## Contexto
- O site público fica no GitHub Pages e é montado por automação a cada mudança no repositório.
- Os dados brutos estão numa Release com data (`dados-2026-10-20`), com SHA-256 de cada arquivo no manifesto (FONTES.md).
- A STM atualiza a base de incidentes por mês. GTFS, OpenStreetMap, Wikidata e clima do ano corrente também mudam com o tempo.
- Uma rotina agendada fica desativada se o repositório passar 60 dias sem atividade.

## Critérios de aceite
- Dada uma mudança no repositório, quando a publicação roda, então ela confere a integridade dos dados, recalcula os números publicados e roda os testes; qualquer falha impede a publicação.
- Dada a verificação semanal das fontes na origem, quando uma fonte muda, então isso vira aviso, não erro, porque vale o snapshot da Release, e o relatório datado fica salvo no repositório.
- Dado um arquivo novo da STM, quando aprovado, então vira uma nova Release com data e manifesto novo, e o site passa a mostrar a data do snapshot usado.
- Dado o pipeline, quando refeito do zero numa máquina limpa, então os arquivos derivados batem com os publicados, com tolerância declarada para cálculos numéricos.
- Dado o fim do semestre, quando a versão final é congelada, então recebe uma etiqueta no repositório, e o site daquela versão fica acessível.
- Dado o site, quando aberto, então o rodapé de cada página mostra a versão dos dados e o link para as fontes.

## Resultado (2026-10-21)

Workflows em `.github/workflows/` (`deploy.yml`, `verifica-fontes.yml`, `reproduz.yml`); comparador `pipeline/compara_derivados.py`; plano e tarefas nesta pasta.

| Critério | Resultado |
|---|---|
| A publicação confere integridade, recalcula e roda os testes; falha impede a publicação | **Atende**: Release, 25 números recalculados, pytest e vitest antes do build |
| Verificação semanal na origem vira aviso, com relatório datado no repositório | **Atende** (`verifica-fontes.yml`, toda segunda-feira) |
| Dado novo vira Release com data e manifesto; o site mostra a data do snapshot | **Atende**: Release `dados-2026-10-21`; o rodapé de cada página lista as Releases em uso |
| Pipeline refeito do zero numa máquina limpa bate com os publicados, com tolerância declarada | **Atende**: execução 39546898051 do `reproduz.yml` (Release e origem baixadas, pipeline e relatórios do simulador refeitos, comparação com tolerância de 1e-9, e 1e-3 nos modelos com bootstrap): 45 arquivos derivados idênticos byte a byte, 8 dentro da tolerância (os modelos com bootstrap e otimização) e 0 fora. A 1ª execução (39542896386) já reproduziu todos os resultados e só acusou 3 metadados (commit e tempo de execução gravados nos relatórios, contagem de meses do clima), corrigidos no comparador e no script |
| Versão final congelada com etiqueta e site acessível | **Atende**: `v1.0.0` (Release com o zip do site), servida em `/versoes/v1.0.0/` |
| Rodapé com versão dos dados e link para as fontes | **Atende** |

## Fora de escopo
- Dados em tempo real da STM: exigem chave de API e servidor (decisão em docs/decisoes/0001-hospedagem-github-pages.md).
- Hospedagem fora do GitHub.

## Riscos e dependências
- A rotina agendada pode ser desativada por inatividade. Mitigação: o commit semanal do relatório de verificação conta como atividade (a confirmar).
- Uma mudança de formato da STM quebra o pipeline. Mitigação: a verificação falha cedo e explica a coluna que mudou.

## Perguntas em aberto
- A nova Release deve ser criada automaticamente ou só depois de revisão humana?
- Por quanto tempo manter as Releases antigas?
