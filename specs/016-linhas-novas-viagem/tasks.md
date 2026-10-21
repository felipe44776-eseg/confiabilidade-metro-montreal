# 016 — Linhas novas numa viagem: tarefas

- [x] `app/src/motor/dia.ts` e `grafo.ts`: origem de cada bloqueio do grafo (causa, linha, trecho, sentidos); `sorteiaDuracao` no nível do módulo, para a linha nova sortear como o motor.
- [x] `app/src/motor/linhas_novas.ts`: partes de um conjunto de candidatas (com conflitos), grafo com as linhas novas, falhas próprias por trecho, trens próprios (prolongamento e linha nova), bloqueios refeitos e cortes nas conexões.
- [x] `app/src/motor/expansao.ts`: `candidataDesenhada` (linha por estações da rede e pontos do mapa); `linhasComCandidata` exportada.
- [x] `app/src/motor/viagem.ts`: avaliador com o grafo da variante, conexões com os trens novos e os cortes, intercalação com as conexões da rede atual, tempo médio da viagem, rodadas com várias versões da rede e diferenças pareadas.
- [x] Testes (`app/tests/motor/linhas_novas.test.ts`): caminho de sempre muda com a ligação; sem falhas, atraso zero e disponibilidade 1; falha injetada na linha nova sem e com rota alternativa; causa comum compartilhada; prolongamento segue as viagens do horário; falha no prolongamento sem e com retorno parcial; rede atual idêntica sozinha e com variantes; paralelo nunca piora em 40 dias; intercalação igual à montagem completa (com prolongamento pelo começo); linhas incompatíveis.
- [x] Escala (`app/src/ui/escala.ts`, testes em `app/tests/simulador/escala.test.ts`): noves, IC dos noves, razão pareada pelo método delta, texto da razão.
- [x] Gráfico de pontos em escala logarítmica (`app/src/ui/graficos.ts`).
- [x] Link: linhas propostas, linhas desenhadas e causa comum compartilhada no endereço, sem mudar a chave do cenário (`app/tests/simulador/cenario.test.ts`).
- [x] Página: caixas das propostas, desenho pela lista e pelo mapa, comparação pareada, leitura de cada linha nova, hipóteses; coluna de noves e gráfico logarítmico também na rede atual e na aba "Muitos dias".
- [x] Relatório (`app/relatorios/linhas_novas.relatorio.ts` → `fontes/verificacao/linhas_novas.md`).
- [x] Conferência no navegador local (celular e notebook): proposta marcada, linha desenhada pela lista e pelo toque no mapa, comparação, sem rolagem lateral e sem erro no console.
- [ ] Conferência no site publicado.
- [ ] Pontos de retorno nas linhas novas além das pontas (pergunta em aberto).
