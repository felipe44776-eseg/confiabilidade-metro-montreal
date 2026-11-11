# 011 — Cenários e parâmetros ajustáveis

**Status:** implementada
**Fase:** F4 (semanas 6 a 8)
**Depende de:** 005, 006, 008, 009

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** O link do cenário ganhou versão, a aba Parâmetros ganhou a tabela por fonte e a D42 foi retestada. Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

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
- *Acrescentado em 2026-10-21, a pedido da equipe (decisão D51):* dado o painel do cenário, quando a página abre ou o cenário muda, então cada variável mostra o seu peso no modelo de taxa (o multiplicador, com intervalo de 95%, para material rodante e equipamentos fixos) e o painel traz uma nota do método que calculou esses pesos, com os números tirados dos arquivos gerados.

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
| Peso de cada variável e nota do método no painel (acrescentado em 2026-10-21, D51) | **Atende** nos testes (`app/tests/simulador/pesos.test.ts`: cada texto traz o multiplicador e o intervalo do `parametros.json`, e a nota cita as contagens, o AIC, o α e o bootstrap do resumo do ajuste). No site publicado (commit 2009763), em tamanho de celular e de notebook: nota com os 6 passos e a tabela das 6 faixas do dia, resumo do ajuste carregado, peso em cada campo, e o peso da neve no solo passou de "1 (referência)" para "MR ×1,37 (1,10–1,67) · EF ×1,38 (1,10–1,70)" ao escolher mais de 10 cm; sem rolagem lateral e sem erro no console (`fontes/verificacao/pesos_painel_2026-10-21.json`) |
| Mudança registrada em 2026-10-21 | Depois da revisão crítica, a greve passou a atuar só pela oferta (viagens fora das faixas com serviço): o simulador aplicava o multiplicador de dia de greve (1,17 e 1,11), cujo intervalo de 95% contém 1 (spec 005). Decisão D42 em `docs/decisoes/registro_de_decisoes.md`; teste em `pipeline/tests/test_modelos.py` |

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D42, D59 e D63; spec 019).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **Link com versão (D28, D59):** o link do cenário passa a levar `v=2`. Um link sem versão é de antes da revisão: abre o mesmo cenário com os números revistos e mostra no topo um aviso com o link para o mesmo cenário em `/versoes/v1.1.0/simulador/`. O teste de ida e volta e o de determinismo continuam passando (`app/tests/simulador/cenario.test.ts`).
- **Aba Parâmetros:** ganhou a tabela por fonte (taxa-base com IC 95%, fração sem interrupção, duração média quando para, forma da renovação). O peso de cada variável no painel continua por família, como antes.
- **Greve (reteste da D42):** com a exposição medida em 2025, o multiplicador de dia de greve chegou a sair 1,73 no material rodante, por contagem dupla da redução do serviço (D63, depois de ver). Corrigida a exposição, ele fica em 1,16 (0,55–2,23) no material rodante e 1,10 (0,52–1,72) nos equipamentos fixos, ambos com intervalo que contém 1. A D42 se mantém: a greve só corta as viagens fora das faixas com serviço.

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| Multiplicador de greve, material rodante | 1,17 (0,56–2,24) | 1,16 (0,55–2,23) |
| Multiplicador de greve, equipamentos fixos | 1,11 (0,52–1,73) | 1,10 (0,52–1,72) |
| Peso da neve no solo acima de 10 cm, no painel | MR ×1,37 (1,10–1,67) · EF ×1,38 (1,10–1,70) | MR ×1,37 (1,09–1,67) · EF ×1,37 (1,09–1,69) |

## Fora de escopo
- Salvar cenários num servidor ou em conta de usuário: o compartilhamento é pelo link.
- Edição livre das distribuições (forma da curva) pela página; só os parâmetros previstos.

## Riscos e dependências
- Links muito longos podem quebrar em alguns aplicativos de mensagem. Mitigação: compactar os parâmetros no link.
- Mudança de versão dos parâmetros publicados quebra links antigos. Mitigação: o link leva a versão dos parâmetros.

## Perguntas em aberto
- Quais cenários prontos oferecer: inverno típico, greve de 2025, dia de jogo, chuva congelante de abril de 2023?
- Permitir sortear um dia real do histórico como cenário?
