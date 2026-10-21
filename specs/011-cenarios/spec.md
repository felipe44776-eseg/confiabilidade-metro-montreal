# 011 — Cenários e parâmetros ajustáveis

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 005, 006, 008, 009

## Pergunta de engenharia
A equipe consegue mudar clima, eventos, frota e políticas, rodar o cenário e compartilhá-lo de forma que outra pessoa obtenha exatamente os mesmos números? O número que responde é a igualdade dos resultados de um mesmo link aberto em dois computadores.

## Contexto
- Os parâmetros vêm de três tipos de origem: ajustados aos dados (com intervalo de confiança), deduzidos (como os códigos de local) e hipóteses (como o tempo de reparo na oficina, entre 0,5 e 4 dias).
- Fatores de cenário disponíveis: hora do dia, mês, temperatura, neve, chuva e chuva congelante (spec 003), greves com faixas de serviço, jogos e grandes eventos, frota por linha (MPM-10 e MR-73), número de trens de reserva, políticas da spec 008.
- Não há passageiros diários: nenhum cenário pode trazer número de passageiros inventado.

## Critérios de aceite
- Dado um cenário montado na página, quando a pessoa copia o link, então o link guarda todos os parâmetros e a semente, e abrir o link em outro computador produz os mesmos números.
- Dado cada parâmetro na tela, quando mostrado, então traz o valor ajustado com intervalo de 95%, ou o rótulo "hipótese", "deduzido" ou "não verificado", com link para a fonte.
- Dado um parâmetro alterado fora do intervalo observado nos dados, quando o cenário roda, então a página avisa que está extrapolando.
- Dados dois cenários, quando comparados, então a página mostra a diferença de cada métrica com intervalo de 95%.
- Dado um cenário de clima (por exemplo, dia de chuva congelante), quando escolhido, então muda a taxa de falha pelos multiplicadores da spec 005, e não por um número escolhido à mão.
- Dado o cenário padrão, quando a página abre, então já mostra um resultado pronto, sem exigir configuração.
- *Acrescentado em 2026-10-21, a pedido da equipe (decisão D50):* dado um cenário, quando aplicado, então a página mostra o que está valendo (destacando o que difere do padrão), as falhas esperadas por dia no cenário e no padrão e, nos dias tocados no mapa, a contagem de falhas sorteadas para comparar com o esperado.

## Resultado (2026-10-21)

Página `/simulador/` (abas dia, muitos dias, comparação, expansão e parâmetros); testes em `app/tests/simulador/`.

| Critério | Resultado |
|---|---|
| O link guarda parâmetros e semente e reproduz os mesmos números | **Atende** (teste de ida e volta e de determinismo com o mesmo link) |
| Cada parâmetro com IC 95% ou o rótulo de status, com link para a fonte | **Atende** |
| Aviso de extrapolação | **Atende**: a partir das horas observadas em cada combinação de condições e das faixas das hipóteses |
| Diferença entre dois cenários com IC 95% | **Atende**: comparação pareada com números aleatórios comuns |
| Clima muda a taxa só pelos multiplicadores da spec 005 | **Atende** (teste do mapeamento) |
| Resultado pronto ao abrir | **Atende**: 1.000 dias no cenário padrão, rodados ao abrir |
| Mostrar o cenário que está valendo e o efeito nas falhas esperadas (acrescentado em 2026-10-21, D50) | **Atende**: faixa "Cenário aplicado" acima do mapa. A média de 2.000 dias sorteados fica a menos de 5% do esperado (`app/tests/simulador/efeito.test.ts`). No site publicado, chuva congelante com mais de 10 cm de neve no solo levou o esperado de 3,35 para 3,52 falhas por dia (×1,05) e marcou os dois itens como diferentes do padrão (`fontes/verificacao/navegador_2026-10-21.json`) |
| Mudança registrada em 2026-10-21 | Depois da revisão crítica, a greve passou a atuar só pela oferta (viagens fora das faixas com serviço): o simulador aplicava o multiplicador de dia de greve (1,17 e 1,11), cujo intervalo de 95% contém 1 (spec 005). Decisão D42 em `docs/decisoes/registro_de_decisoes.md`; teste em `pipeline/tests/test_modelos.py` |

## Fora de escopo
- Salvar cenários num servidor ou em conta de usuário: o compartilhamento é pelo link.
- Edição livre das distribuições (forma da curva) pela página; só os parâmetros previstos.

## Riscos e dependências
- Links muito longos podem quebrar em alguns aplicativos de mensagem. Mitigação: compactar os parâmetros no link.
- Mudança de versão dos parâmetros publicados quebra links antigos. Mitigação: o link leva a versão dos parâmetros.

## Perguntas em aberto
- Quais cenários prontos oferecer: inverno típico, greve de 2025, dia de jogo, chuva congelante de abril de 2023?
- Permitir sortear um dia real do histórico como cenário?
