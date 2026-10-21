# 000 — Proveniência

**Status:** implementada
**Fase:** F0 (S1)
**Depende de:** nada

## Pergunta de engenharia

Uma pessoa de fora da equipe consegue refazer qualquer número publicado, partindo só do repositório público, sem confiar em quem o calculou? O número que responde é a quantidade de divergências encontradas na verificação automática: precisa ser zero.

## Contexto

A equipe temia que números calculados com ajuda de IA fossem inventados. Em 2026-10-20 foram feitos:
- **Documentação** de cada fonte, com link, licença e SHA-256 (`fontes/FONTES.md` e `fontes/fontes_manifesto.json`).
- **Novo download:** as 27 fontes então registradas foram baixadas de novo; 26 vieram idênticas byte a byte, e a 27ª (98 MB) foi conferida pelo tamanho.
- **Auditoria independente:** um agente, sem acesso aos scripts, refez os números com código próprio e não achou divergência. Deixou 6 ressalvas de apresentação, todas corrigidas.

## Critérios de aceite

- Dado um clone limpo do repositório, quando a verificação baixa os dados brutos da Release e confere os hashes, então todos os arquivos distribuídos batem com o manifesto.
- Dado o mesmo clone, quando a verificação recalcula os números publicados com código próprio, então não há nenhuma diferença.
- Dado qualquer arquivo de dados usado pelo site, quando se procura no manifesto, então ele tem editor, licença, URL de origem, SHA-256 e o script que o usa.
- Dado um push para a branch principal, quando a verificação falha, então o site não é publicado.
- Dada uma fonte que muda na origem (GTFS, OpenStreetMap, clima do ano corrente), quando a verificação semanal roda, então ela avisa da mudança sem quebrar, porque vale a cópia da Release.

## Fora de escopo

- Garantir que a STM não corrija dados antigos. Mudança na origem vira aviso e, se for o caso, uma nova Release.
- Verificar a correção dos dados da própria STM. Conferimos que usamos exatamente o que ela publicou.

## Riscos e dependências

- O site stm.info não responde desta máquina. Por isso o GTFS vem do espelho do Mobility Database e os relatórios vêm do Internet Archive.
- O Google e o Nager.Date não têm licença de redistribuição conferida. Ficam fora da Release e se baixam da origem.

## Perguntas em aberto

- Vale publicar uma nova Release a cada atualização mensal da STM, ou só quando o modelo for recalibrado? Decisão adiada para a spec 013.
