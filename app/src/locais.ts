// Tipos e funções puras do mapa de incidentes (spec 002). Ficam fora do código do mapa para serem testadas.

export type Status = 'verificado' | 'deduzido' | 'aproximado' | 'desconhecido';

export interface Local {
  codigo: string;
  linha: string;
  n_tecnicos: number;
  tipo: string;
  status: Status;
  lat: number | null;
  lon: number | null;
  km_linha: number | null;
  estacoes: string[];
  metodo: string;
}

export const ROTULO_STATUS: Record<Status, string> = {
  verificado: 'Verificado',
  deduzido: 'Deduzido',
  aproximado: 'Aproximado',
  desconhecido: 'Sem posição',
};

export const ROTULO_TIPO: Record<string, string> = {
  estacao: 'Estação',
  plataforma_correspondencia: 'Plataforma de correspondência',
  interestacao: 'Trecho entre estações',
  garagem: 'Garagem',
  arriere_gare: 'Arrière-gare (manobra após o terminal)',
  subestacao: 'Subestação de energia',
  linha_sem_posicao: 'Linha, sem posição',
  outro: 'Outro',
  desconhecido: 'Desconhecido',
};

/** Raio do círculo em pixels: área proporcional ao número de falhas, de 3 px até `max` px. */
export function raio(n: number, nMax: number, max = 22): number {
  if (n <= 0 || nMax <= 0) return 0;
  return 3 + (max - 3) * Math.sqrt(n / nMax);
}

/** Soma das falhas por status, para a legenda e para conferir contra o relatório de validação. */
export function somaPorStatus(locais: Local[]): Record<Status, number> {
  const total: Record<Status, number> = { verificado: 0, deduzido: 0, aproximado: 0, desconhecido: 0 };
  for (const l of locais) total[l.status] += l.n_tecnicos;
  return total;
}

/** Converte os locais com coordenada em pontos GeoJSON. Locais sem posição ficam de fora do mapa, nunca em (0, 0). */
export function paraGeoJSON(locais: Local[]): GeoJSON.FeatureCollection<GeoJSON.Point> {
  return {
    type: 'FeatureCollection',
    features: locais
      .filter((l) => l.lat !== null && l.lon !== null)
      .map((l) => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [l.lon as number, l.lat as number] },
        properties: { codigo: l.codigo, status: l.status, n: l.n_tecnicos },
      })),
  };
}
