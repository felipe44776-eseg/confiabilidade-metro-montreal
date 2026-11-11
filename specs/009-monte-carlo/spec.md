# 009 — Monte Carlo e métricas

**Status:** implementada com exceções
**Fase:** F3 (semanas 4 a 7)
**Depende de:** 006, 007

> **Revisão de 2026-11 (após a ressegmentação, decisões D55 a D63).** Com a duração pela faixa oficial e a taxa-base de 2025 por fonte, a Azul passa a atingir 5% de precisão antes dos 50 mil dias, e o IC da Laranja (1.215 a 1.422 min/ano) fica abaixo dos valores revistos do painel (1.601 e 1.639). Os resultados abaixo são os da versão v1.1.0, que continua publicada em `/versoes/v1.1.0/`; os revistos estão na seção "Revisão de 2026-11 (após a ressegmentação)", ao lado dos originais.

## Pergunta de engenharia
Com quantas rodadas a estimativa de disponibilidade fica precisa, e a simulação reproduz os números já validados no painel? O número que responde é a meia-largura do intervalo de 95% em relação à média.

## Contexto
- O painel atual tem um Monte Carlo do corredor: na Laranja sozinha, 1.852 minutos parados por ano simulados contra 1.797 pelo cálculo analítico (FONTES.md, tabela corredor).
- Não há passageiros diários. As métricas por par origem-destino são ponderadas pela oferta do horário, não por pessoas.
- A janela de operação é de 20 h por dia.

## Critérios de aceite
- Dado o mesmo conjunto de rodadas, quando executado em paralelo com 1 ou com 8 processos, então os resultados são idênticos.
- Dado o número de rodadas padrão, quando a disponibilidade de cada linha é estimada, então a meia-largura do intervalo de 95% fica em até 5% da média dos minutos parados.
- Dada a Laranja sem redundância e os parâmetros do painel, quando simulada, então o intervalo de 95% dos minutos parados por ano contém 1.852 (simulado no painel) ou 1.797 (analítico); se não contiver, o relatório explica a diferença.
- Dadas as métricas, quando publicadas, então incluem: disponibilidade por linha; disponibilidade por par origem-destino (fração do tempo com caminho, mais o tempo extra de viagem), ponderada pela oferta; trens-hora perdidos contra o horário; minutos de interrupção.
- Dada cada métrica, quando mostrada, então vem com intervalo de 95%, número de rodadas e semente.
- Dado um cenário, quando executado, então o tempo total para o número padrão de rodadas é medido e registrado, para confirmar a estimativa de 10 a 30 segundos para 5.000 rodadas.

## Resultado (2026-10-21)

Código em `app/src/mc/`; testes em `app/tests/motor/montecarlo.test.ts`; relatório [`politicas.md`](../../fontes/verificacao/politicas.md).

| Critério | Resultado |
|---|---|
| 1 ou 8 processos dão resultados idênticos | **Atende** (teste: 1 contra 8 lotes) |
| Meia-largura do IC 95% até 5% da média dos minutos parados | **Exceção na Azul**: o modo adaptativo para em 50.000 dias; Verde, Laranja e Amarela atingem 5% com 18 mil a 40 mil dias, mas a Azul precisaria de cerca de 168 mil, por causa de poucas interrupções de quase 20 horas na amostra observada. Com 50 mil dias, a meia-largura esperada da Azul é de 9,2% da média (`fontes/verificacao/politicas.md`) |
| Laranja: IC contém 1.852 ou 1.797 min/ano | **Atende**: 1.704 (1.528 a 1.881) contém os dois. Antes da correção da duração (lognormal) dava 1.433, fora do intervalo; a diferença foi explicada e corrigida em 2026-10-21 |
| Métricas: disponibilidade por linha e por par origem-destino (com tempo extra), trens-hora perdidos, minutos de interrupção | **Atende** |
| Cada métrica com IC 95%, número de rodadas e semente | **Atende** |
| Tempo de 5.000 rodadas medido | **Atende**: 12.000 dias (mais que as 5.000 pedidas) em 7,8 s numa thread, na execução publicada de `politicas.relatorio.ts` (o tempo muda a cada execução e com a máquina; ver `politicas.md`); na página, 1.000 dias em 2,6 a 3,8 s com 12 workers (medição manual de 2026-10-21; na revisão crítica de 2026-10-21, rodada 3, o navegador sem janela levou 1,3 a 1,4 s) |

## Revisão de 2026-11 (após a ressegmentação)

*Registrada em 2026-11-11 (decisões D55, D56, D57 e D59; specs 019 e 020).* Os critérios acima não mudam, e o resultado de 2026-10-21 continua sendo o da v1.1.0.

- **O que mudou na entrada:**
  - o `parametros.json` passa ao contrato v2 (`sha256-scripts:d2a89e7803552929`; v1.1.0: `70cf9c002aa2ba0a`), com 9 fontes por linha (D56, D59) e a taxa-base do ano 2025 por fonte, com a exposição medida até 2026-06 (D57, spec 018);
  - nas 100 falhas em que a duração calculada contradiz a faixa oficial, vale a faixa (D55). Isso tira da amostra de durações da Azul as interrupções de quase 20 h em Saint-Michel. Nas 11 exceções de equipamento fixo da Azul, 7.207 minutos calculados ficam 10 pela faixa (`fontes_e_duracoes.md`);
  - o painel revisto da Laranja sozinha dá 1.639 min/ano no Monte Carlo e 1.601 no analítico (`dados/derivados/painel/corredor.json`, cenário `so_laranja`).
- **O que mudou no método:** nada no experimento: 4.000 dias por tipo de dia, somados pelo calendário de 251, 52 e 62 dias, semente 20261021. O motor lê a lista de fontes e, com os parâmetros da v1.1.0, reproduz a referência anterior sem diferença (spec 019). As diferenças abaixo vêm, portanto, dos parâmetros.

| Número | v1.1.0 | Após a revisão |
|---|---|---|
| Minutos parados por ano, Laranja | 1.704 (1.528 a 1.881) | 1.319 (1.215 a 1.422) |
| Minutos parados por ano, Azul | 1.323 (967 a 1.678) | 675 (604 a 745) |
| Painel, Laranja sozinha: Monte Carlo e analítico | 1.852 e 1.797 | 1.639 e 1.601 |
| Dias para 5% de precisão no dia útil: Verde, Laranja e Amarela | 18.435, 25.097 e 40.288 | 21.291, 14.778 e 37.633 |
| Dias para 5% de precisão no dia útil: Azul | 168.183 | 26.056 |
| Meia-largura da Azul com 50.000 dias | 9,2% da média | 3,6% da média |
| Tempo de 12.000 dias numa thread (`politicas.relatorio.ts`) | 7,8 s | 17,0 s |

Não mudaram: a igualdade com 1 e 8 lotes, a semente (20261021), os 12.000 dias por cenário e a medição na página (2,6 a 3,8 s para 1.000 dias, de 2026-10-21).

| Critério | Após a revisão |
|---|---|
| 1 ou 8 processos dão resultados idênticos | **Continua atendendo** (teste) |
| Meia-largura do IC 95% até 5% da média dos minutos parados | **A exceção da Azul se resolveu**: a Azul precisa de 26.056 dias, abaixo do teto de 50.000 do modo adaptativo, e com 50.000 dias a meia-largura esperada fica em 3,6% da média. As quatro linhas atingem 5% com 14.778 a 37.633 dias. A causa da exceção eram as interrupções de quase 20 h, que a D55 tirou da amostra |
| Laranja: IC contém os valores do painel | **Não contém** os revistos (1.639 e 1.601), nem os da v1.1.0. O critério admite a saída "o relatório explica a diferença", e a explicação está abaixo |
| Métricas: disponibilidade por linha e por par origem-destino, trens-hora perdidos, minutos de interrupção | **Continua atendendo**; agora também por fonte e por classe de gravidade (spec 019) |
| Cada métrica com IC 95%, número de rodadas e semente | **Continua atendendo** |
| Tempo de 5.000 rodadas medido | **Continua atendendo**: 12.000 dias em 17,0 s numa thread. O tempo muda com a execução e a máquina; esta medição não separa o efeito das 9 fontes |

Por que o IC da Laranja fica abaixo do painel:

- O motor usa a taxa do ano-base 2025; o painel usa a média de 2019 a 2026.
- Em 2025, a Laranja parou menos que a média: 269 min de material rodante contra 493,1 na média de 2019 a 2025, e 742 de equipamentos fixos contra 987,3 (`revalidacao.md`).
- Na revalidação contra 2025 (spec 020), as 7 medidas simuladas da Laranja ficam dentro do IC 95% do observado naquele ano. O motor acompanha o ano-base, não a média do período.
- A v1.1.0 também usava 2025, mas os minutos de equipamento fixo simulados para a Laranja em 2025 eram 1.027,1, acima dos 742 observados; revistos, 643,7 (`revalidacao.md`).
- Continuam as diferenças de definição já listadas em `politicas.md`: o motor soma a causa comum de todos os grupos que incluem a Laranja (139 min/ano) e conta a união dos intervalos bloqueados.
- O texto gerado de `politicas.md` ainda compara com 1.852 e 1.797, os valores do painel da v1.1.0.

## Fora de escopo
- Otimização automática de parâmetros.
- Métricas de passageiros (lotação, tempo de espera por pessoa).

## Riscos e dependências
- Rodadas longas podem ficar lentas em computador fraco. Mitigação: mostrar o progresso e permitir menos rodadas, com o intervalo maior avisado.

## Perguntas em aberto
- Qual o número padrão de rodadas: fixo ou até atingir a precisão pedida?
- Os pares origem-destino devem ser todos (73 estações) ou só os de estações de correspondência?
