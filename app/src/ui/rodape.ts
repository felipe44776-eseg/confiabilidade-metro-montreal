// Rodapé comum do /mapa/ e do /simulador/ (spec 013): equipe, versão dos dados e links.

export const REPO = 'https://github.com/felipe44776-eseg/confiabilidade-metro-montreal';

export function textoEquipe(nomes: readonly string[] = __EQUIPE__): string {
  if (nomes.length <= 1) return nomes.join('');
  return `${nomes.slice(0, -1).join(', ')} e ${nomes[nomes.length - 1]}`;
}

function link(href: string, texto: string): HTMLAnchorElement {
  const a = document.createElement('a');
  a.href = href;
  a.textContent = texto;
  return a;
}

/** Monta o rodapé no elemento dado. `base` é o BASE_URL do site (termina em /). */
export function montaRodape(destino: HTMLElement, base: string): void {
  destino.replaceChildren();
  destino.classList.add('rodape-site');
  const p1 = document.createElement('p');
  p1.append(`Sistemas Tolerantes a Falhas, Engenharia de Produção, ESEG, 2026. Equipe: ${textoEquipe()}.`);
  const p2 = document.createElement('p');
  p2.append('Versão dos dados: ');
  __RELEASES__.forEach((r, i) => {
    if (i > 0) p2.append(i === __RELEASES__.length - 1 ? ' e ' : ', ');
    p2.append(link(`${REPO}/releases/tag/${r}`, r));
  });
  p2.append('. ');
  const links: [string, string][] = [
    [base, 'Painel'],
    [`${base}mapa/`, 'Mapa'],
    [`${base}simulador/`, 'Simulador'],
    [`${base}fontes/`, 'Fontes e verificação'],
    [`${base}specs/`, 'Especificações'],
    [REPO, 'Repositório'],
  ];
  links.forEach(([href, texto], i) => {
    if (i > 0) p2.append(' · ');
    p2.append(link(href, texto));
  });
  const p3 = document.createElement('p');
  p3.textContent =
    'Dados: Société de transport de Montréal (STM), CC BY 4.0; traçado © colaboradores do OpenStreetMap, ODbL; clima: Environment and Climate Change Canada. Os resultados são análise própria e não representam a STM.';
  destino.append(p1, p2, p3);
}
