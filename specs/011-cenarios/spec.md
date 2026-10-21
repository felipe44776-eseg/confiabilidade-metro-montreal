# 011 — Cenários e parâmetros ajustáveis

**Status:** especificada
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

## Fora de escopo
- Salvar cenários num servidor ou em conta de usuário: o compartilhamento é pelo link.
- Edição livre das distribuições (forma da curva) pela página; só os parâmetros previstos.

## Riscos e dependências
- Links muito longos podem quebrar em alguns aplicativos de mensagem. Mitigação: compactar os parâmetros no link.
- Mudança de versão dos parâmetros publicados quebra links antigos. Mitigação: o link leva a versão dos parâmetros.

## Perguntas em aberto
- Quais cenários prontos oferecer: inverno típico, greve de 2025, dia de jogo, chuva congelante de abril de 2023?
- Permitir sortear um dia real do histórico como cenário?
