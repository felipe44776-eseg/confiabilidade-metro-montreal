// Spec 011: cenário da página → cenário do motor, link compartilhável e determinismo.
import { describe, expect, it } from 'vitest';
import { agrega, nomesMetricas, rodaRodadas } from '../../src/mc/rodadas';
import { preparaContexto } from '../../src/motor/contexto';
import { montaRede, trensProgramados } from '../../src/motor/rede';
import { condicoesDaHora, multiplicador } from '../../src/motor/taxas';
import type { Parametros } from '../../src/motor/tipos';
import type { EstadoCenario } from '../../src/simulador/cenario';
import { aplicaGreve, chaveCenario, copia, desserializa, HORAS_JOGO, NIVEIS, PADRAO, paraCenarioMotor, serializa } from '../../src/simulador/cenario';
import { carregaFixture, carregaRede, carregaRedeJson } from '../motor/apoio';

function cenarioVariado(): EstadoCenario {
  const e = copia(PADRAO);
  e.tipoDia = 'sabado';
  e.mes = 1;
  e.temp = 'abaixo_-15';
  e.precip = 'ate_1mm';
  e.cond = 'neve';
  e.neveSolo = 'acima_10';
  e.jogo = true;
  e.feriado = true;
  e.greve = 'set_out_2025';
  e.politicas.reservaFria = true;
  e.politicas.rotaAlternativa = true;
  e.hipoteses = { reparo_oficina_dias: 2.5, intervalo_minimo_s: 120 };
  e.semente = 4242;
  e.rodadas = 5000;
  e.dia = 17;
  return e;
}

describe('link compartilhável', () => {
  it('ida e volta: serializa → desserializa devolve o mesmo cenário', () => {
    for (const e of [copia(PADRAO), cenarioVariado()]) {
      const volta = desserializa(`#${serializa(e)}`);
      expect(volta).toEqual(e);
      expect(serializa(volta)).toBe(serializa(e));
    }
  });

  it('todas as combinações de níveis sobrevivem ao link', () => {
    for (const t of NIVEIS.temp)
      for (const c of NIVEIS.cond) {
        const e = { ...copia(PADRAO), temp: t, cond: c };
        expect(desserializa(serializa(e))).toEqual(e);
      }
  });

  it('valor inválido no link volta ao padrão sem quebrar', () => {
    const e = desserializa('#d=feriadao&m=13&t=quente&p=x&c=granizo&n=99&gr=z&pol=1&s=-1&r=7&dia=abc&h=reparo_oficina_dias:abc,ok_nome:3');
    expect(e.tipoDia).toBe(PADRAO.tipoDia);
    expect(e.mes).toBe(PADRAO.mes);
    expect(e.temp).toBe(PADRAO.temp);
    expect(e.cond).toBe(PADRAO.cond);
    expect(e.greve).toBe('nao');
    expect(e.semente).toBe(PADRAO.semente);
    expect(e.rodadas).toBe(PADRAO.rodadas);
    expect(e.politicas.reservaFria).toBe(true);
    expect(e.politicas.retiradaTrem).toBe(false);
    expect(e.hipoteses).toEqual({ ok_nome: 3 });
  });

  it('a viagem de A a B vai no link e não muda a chave do cenário (spec 015)', () => {
    const e = copia(PADRAO);
    e.viagemDe = 'STATION_M222';
    e.viagemPara = 'STATION_M454';
    const volta = desserializa(`#${serializa(e)}`);
    expect(volta.viagemDe).toBe('STATION_M222');
    expect(volta.viagemPara).toBe('STATION_M454');
    expect(chaveCenario(e)).toBe(chaveCenario(PADRAO));
    // id inválido no link volta ao padrão
    const ruim = desserializa('#vo=<script>&vd=');
    expect(ruim.viagemDe).toBe(PADRAO.viagemDe);
    expect(ruim.viagemPara).toBe(PADRAO.viagemPara);
  });

  it('as linhas novas da viagem vão no link e não mudam a chave do cenário (spec 016)', () => {
    const e = copia(PADRAO);
    e.linhasNovas = ['rosa_2017', 'azul_anjou'];
    e.linhasDesenhadas = [['STATION_M134', { lat: 45.50123, lon: -73.61234 }, 'STATION_M536'], ['STATION_M118', 'STATION_M236']];
    e.ccNova = true;
    const volta = desserializa(`#${serializa(e)}`);
    expect(volta.linhasNovas).toEqual(e.linhasNovas);
    expect(volta.linhasDesenhadas).toEqual(e.linhasDesenhadas);
    expect(volta.ccNova).toBe(true);
    expect(chaveCenario(e)).toBe(chaveCenario(PADRAO));
    // copia não compartilha os pontos
    const c = copia(e);
    (c.linhasDesenhadas[0][1] as { lat: number }).lat = 0;
    expect((e.linhasDesenhadas[0][1] as { lat: number }).lat).toBe(45.50123);
    // pontos inválidos, fora de Montreal ou linha de um ponto só: a linha cai, o resto fica
    const ruim = desserializa('#ln=rosa_2017,<x>&ld=STATION_M134~%4010.0,-73.6|STATION_M118|STATION_M118~STATION_M236');
    expect(ruim.linhasNovas).toEqual(['rosa_2017']);
    expect(ruim.linhasDesenhadas).toEqual([['STATION_M118', 'STATION_M236']]);
    expect(desserializa('#').linhasDesenhadas).toEqual([]);
  });

  it('mesmo link e mesma semente: os mesmos números', () => {
    const rede = carregaRede();
    const p = carregaFixture();
    const link = serializa({ ...cenarioVariado(), greve: 'nao' });
    const roda = () => {
      const e = desserializa(link);
      const ctx = preparaContexto(rede, p, paraCenarioMotor(e));
      return agrega(rodaRodadas(Array.from({ length: 40 }, (_, i) => i), ctx, e.politicas, e.semente), nomesMetricas(rede.ids), e.semente);
    };
    expect(roda()).toEqual(roda());
  });
});

describe('cenário do motor', () => {
  // multiplicadores distintos por nível, para conferir que cada escolha da página vira o fator certo
  function parametrosMarcados(): Parametros {
    const p = carregaFixture();
    let k = 1.01;
    for (const causa of ['MR', 'EF'] as const) {
      for (const niveis of Object.values(p.taxas[causa].multiplicadores)) {
        for (const par of Object.values(niveis)) {
          par.valor = k;
          k += 0.01;
        }
      }
    }
    return p;
  }

  it('o clima muda a taxa só pelos multiplicadores do parametros.json', () => {
    const p = parametrosMarcados();
    const e = cenarioVariado();
    const cen = paraCenarioMotor(e);
    const m = p.taxas.MR.multiplicadores;
    for (const hora of [10, 19]) {
      const cond = condicoesDaHora(cen, hora);
      let esperado = 1;
      esperado *= m.faixa[cond.faixa].valor;
      esperado *= m.tipo_dia.sabado.valor;
      esperado *= m.estacao.inverno.valor;
      esperado *= m.temp['abaixo_-15'].valor;
      esperado *= m.precip.ate_1mm.valor;
      esperado *= m.cond.neve.valor;
      esperado *= m.neve_solo.acima_10.valor;
      esperado *= m.feriado['1'].valor;
      expect(m.greve, 'greve não entra na taxa (D42)').toBeUndefined();
      if (HORAS_JOGO.includes(hora)) esperado *= m.jogo['1'].valor; // jogo só nas horas 18 a 22
      expect(multiplicador(p.taxas.MR, cond), `hora ${hora}`).toBeCloseTo(esperado, 12);
    }
  });

  it('cenário padrão = condições de referência (multiplicador 1 fora da faixa e do tipo de dia)', () => {
    const p = carregaFixture();
    const cond = condicoesDaHora(paraCenarioMotor(PADRAO), 12);
    expect(cond).toMatchObject({ estacao: 'outono', temp: '5a15', precip: '0', cond: 'seco_ou_outro', neve_solo: '0', jogo: '0', greve: '0' });
    expect(multiplicador(p.taxas.MR, cond)).toBeCloseTo(1, 12);
  });

  it('hipóteses alteradas vão para o cenário do motor', () => {
    const cen = paraCenarioMotor(cenarioVariado());
    expect(cen.hipoteses).toEqual({ reparo_oficina_dias: 2.5, intervalo_minimo_s: 120 });
    expect(paraCenarioMotor(PADRAO).hipoteses).toBeUndefined();
  });

  it('greve: só as viagens que partem nas faixas com serviço', () => {
    const json = carregaRedeJson();
    const g = montaRede(aplicaGreve(json, 'set_out_2025'));
    const normal = carregaRede();
    expect(trensProgramados(g.horarios.util, 'laranja', 12 * 3600)).toBe(0);
    expect(trensProgramados(g.horarios.util, 'laranja', 8 * 3600)).toBe(trensProgramados(normal.horarios.util, 'laranja', 8 * 3600));
    expect(aplicaGreve(json, 'nao')).toBe(json);
  });
});
