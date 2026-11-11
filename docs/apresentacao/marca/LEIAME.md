# Identidade visual da ESEG nas apresentações

O `gera_deck.py` embute estes arquivos nos decks, que continuam autocontidos (sem CDN). Baixados em 2026-11-11.

| Arquivo | Origem | SHA-256 | Licença |
|---|---|---|---|
| `eseg-logo-branco.svg` | https://eseg.edu.br/wp-content/uploads/2024/06/Logo.svg | `619f49bba5e489f465ebbb10263e49b64e5bfdd741b1687fc029bb6cea1f5a91` | Marca da Faculdade ESEG, fora da licença MIT do repositório. Usada só para identificar o trabalho da disciplina |
| `eseg-logo-marinho.svg` | https://eseg.edu.br/wp-content/uploads/2024/06/Logo-black.svg | `a946af8a7de9c75855f2e2b7f48c017f44b5b475dbdc6459cf94262e80622687` | Idem |
| `public-sans-latin-wght.woff2` | `@fontsource-variable/public-sans@5.2.7`, arquivo `files/public-sans-latin-wght-normal.woff2` (jsDelivr) | `5ed4d31c988e73b258894244f209069ebe77dc7e564861954b21198b6de90d68` | SIL Open Font License 1.1 (`OFL-public-sans.txt`) |

## Cores e tipografia

As cores e a fonte vêm do kit global do site da ESEG (`eseg.edu.br/wp-content/uploads/elementor/css/post-8.css`, lido em 2026-11-11):

| Papel no deck | Variável do site | Cor |
|---|---|---|
| Marinho: títulos, capa, divisórias, logo | `--e-global-color-primary` | `#08223D` |
| Turquesa: marcas de destaque nos gráficos, fios | `--e-global-color-secondary` | `#00A1B8` |
| Ouro: etiquetas e a resposta | `--e-global-color-text` | `#F1B634` |
| Cinzas: texto, rótulos, grades e fundos | `--e-global-color-0ab3fca`, `9dec319`, `a1428c0`, `f5c8e45`, `5029fff`, `89039f1`, `2293dc0` | `#0F1322`, `#333643`, `#474A56`, `#999BA1`, `#C2C3C7`, `#E5E6E7`, `#FAFAFA` |

A fonte do site é a Public Sans, com títulos em peso 600.

A turquesa sobre branco tem contraste de 3:1, que basta para gráficos mas não para texto pequeno. Por isso o texto de destaque fica em marinho, e a turquesa só aparece em texto sobre o marinho.

As cores das linhas do metrô (Verde, Laranja, Amarela, Azul) são dados, não marca: seguem as da STM.
