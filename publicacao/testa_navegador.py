"""Testa uma página publicada num navegador sem janela (Edge ou Chrome), pelo protocolo DevTools.

Uso: python testa_navegador.py <pasta_saida>   (variáveis: URL, SO=celular|notebook, ESPERA=segundos)
Precisa do pacote `websocket-client` (pip install websocket-client, num ambiente à parte: não é dependência do projeto)
e do Edge ou do Chrome instalados. Mede, em tamanho de celular (390x844) e de notebook (1366x768): rolagem lateral,
WebGL, quadros por segundo com a animação parada e tocando a 300×, 1 h/s, 10 h/s e 1 dia/s (com a ocupação da thread
da página em cada uma), o resultado do Monte Carlo de abertura,
os erros no console e, a 1 dia/s, os eventos vermelhos, os dias emendados e o placar (decisão D49); depois muda o clima
e confere que a faixa "Cenário aplicado" e o peso da neve no solo mudaram (decisões D50 e D51), abre a nota do método
e captura o painel do cenário. Grava capturas e resultado.json na pasta de saída.
Rode um tamanho por vez (SO=...): reaproveitar a aba entre tamanhos perde o contexto WebGL por software.
A aba é trazida para a frente (Page.bringToFront): sem isso, o navegador sem janela deixa a página oculta, o
requestAnimationFrame não roda e o contador de fps da página fica parado no último valor (revisão crítica de
2026-10-21, rodada 3). Os quadros são contados por requestAnimationFrame durante 3 s, com teto de 8 s.
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request

import websocket

EDGE = os.environ.get("NAVEGADOR", next((c for c in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
       r"C:\Program Files\Google\Chrome\Application\chrome.exe", "/usr/bin/google-chrome", "/usr/bin/chromium") if os.path.exists(c)), "msedge"))
URL = os.environ.get("URL", "https://felipe44776-eseg.github.io/confiabilidade-metro-montreal/simulador/")
SAIDA = sys.argv[1]
PORTA = 9333
perfil = os.path.join(SAIDA, "perfil_edge")
proc = subprocess.Popen([EDGE, "--headless=new", f"--remote-debugging-port={PORTA}", f"--user-data-dir={perfil}",
                         "--no-first-run", "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
                         "--disable-background-timer-throttling", "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader", "--ignore-gpu-blocklist", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    pagina = None
    for _ in range(60):
        try:
            alvos = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/json", timeout=5))
            pagina = next(a for a in alvos if a["type"] == "page")
            break
        except Exception:
            time.sleep(0.5)
    if pagina is None:
        sys.exit(f"o navegador ({EDGE}) não abriu a porta {PORTA} de depuração em 30 s")
    ws = websocket.create_connection(pagina["webSocketDebuggerUrl"], timeout=120, suppress_origin=True)
    seq = [0]
    eventos = []

    def cmd(metodo, **params):
        seq[0] += 1
        ws.send(json.dumps({"id": seq[0], "method": metodo, "params": params}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == seq[0]:
                return m.get("result", m)
            eventos.append(m)

    def avalia(expr):
        return cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)["result"].get("value")

    def espera(segundos):
        fim = time.time() + segundos
        ws.settimeout(1)
        while time.time() < fim:
            try:
                eventos.append(json.loads(ws.recv()))
            except Exception:
                pass
        ws.settimeout(120)

    # Quadros por segundo contados direto por requestAnimationFrame durante 3 s; teto de 8 s (página oculta não conta quadros)
    QUADROS = """Promise.race([
      new Promise(q => setTimeout(() => q({quadros_por_s: null, motivo: 'requestAnimationFrame parado', visibilidade: document.visibilityState}), 8000)),
      new Promise(r => { let n = 0; const t0 = performance.now();
        function f() { n++; if (performance.now() - t0 < 3000) requestAnimationFrame(f);
          else r({quadros_por_s: Math.round(n * 1000 / (performance.now() - t0)), contador_da_pagina: document.getElementById('fps')?.textContent,
                  relogio: document.getElementById('t-relogio')?.textContent, visibilidade: document.visibilityState}); }
        requestAnimationFrame(f); })])"""

    # Durante 6 s: pulsos vermelhos criados no mapa, dias avançados, lista de eventos, placar e marcas na barra
    EVENTOS = """new Promise(r => { let n = 0;
      const ob = new MutationObserver(ms => { for (const m of ms) for (const x of m.addedNodes) if (x.classList && x.classList.contains('pulso-falha')) n++; });
      ob.observe(document.body, {childList: true, subtree: true});
      const d0 = Number(document.getElementById('t-dia').value);
      setTimeout(() => { ob.disconnect(); r({pulsos_em_6_s: n, dias_avancados: Number(document.getElementById('t-dia').value) - d0,
        eventos_na_lista: document.querySelectorAll('#eventos li').length, primeiro_evento: document.querySelector('#eventos li')?.textContent,
        placar: document.getElementById('aplicado-placar')?.textContent, marcas_na_barra: document.querySelectorAll('#t-marcas i').length}); }, 6000); })"""

    CENARIO = """(async () => { const antes = document.getElementById('aplicado-efeito').textContent;
      const pesoNeveAntes = document.getElementById('p-neve').textContent;
      for (const [id, v] of [['c-cond', 'chuva_congelante'], ['c-neve', 'acima_10']]) {
        const s = document.getElementById(id); s.value = v; s.dispatchEvent(new Event('change', {bubbles: true})); }
      await new Promise(q => setTimeout(q, 1500));
      return {antes: antes.slice(0, 100), depois: document.getElementById('aplicado-efeito').textContent.slice(0, 100),
              mudados: [...document.querySelectorAll('#aplicado-itens li.mudou')].map(li => li.textContent),
              quando: document.getElementById('aplicado-quando').textContent,
              peso_neve_antes: pesoNeveAntes, peso_neve_depois: document.getElementById('p-neve').textContent}; })()"""

    # nota do método e peso de cada variável no painel do cenário (decisão D51)
    PESOS = """(() => { const corpo = document.getElementById('m-corpo');
      const a = document.querySelector('.painel').getBoundingClientRect();
      return {resumo: document.getElementById('m-resumo').textContent.slice(0, 160),
              passos: corpo.querySelectorAll('ol li').length, faixas_na_tabela: corpo.querySelectorAll('tbody tr').length,
              resumo_do_ajuste_carregou: corpo.textContent.includes('semente'),
              pesos: Object.fromEntries([...document.querySelectorAll('.painel .peso')].map(p => [p.id, p.textContent])),
              painel: {x: a.left + scrollX, y: a.top + scrollY, w: a.width, h: a.height}}; })()"""

    cmd("Runtime.enable")
    cmd("Log.enable")
    cmd("Page.enable")
    resultado = {}
    tamanhos = {"celular": (390, 844, True), "notebook": (1366, 768, False)}
    for nome, (w, h, movel) in [(k, v) for k, v in tamanhos.items() if os.environ.get("SO", k) == k]:
        eventos.clear()
        cmd("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=movel)
        cmd("Page.navigate", url=URL)
        espera(int(os.environ.get('ESPERA', '45')))  # dados, mapa e o Monte Carlo de abertura (1.000 dias em workers)
        cmd("Page.bringToFront")  # depois de carregar: sem isto a página fica oculta e o requestAnimationFrame não roda
        cmd("Emulation.setFocusEmulationEnabled", enabled=True)  # rodada 3, parte C: só bringToFront volta a 'hidden' em segundos
        medidas = avalia("""(() => {
          const d = document.documentElement;
          const txt = document.body.innerText;
          const largos = [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > d.clientWidth + 1).length;
          return {scrollWidth: d.scrollWidth, clientWidth: d.clientWidth, elementosAlemDaLargura: largos,
                  temMapa: !!document.querySelector('canvas.maplibregl-canvas'), webgl2: !!document.createElement('canvas').getContext('webgl2'),
                  visibilidade: document.visibilityState,
                  textoMC: document.getElementById('s-mc')?.textContent || '',
                  amostraTexto: txt.slice(0, 300)};
        })()""")
        medidas["fps_parado"] = avalia(QUADROS)
        # Quadros por segundo e ocupação da thread da página em cada velocidade (decisão D49): se a thread tem folga e os
        # quadros caem, o limite é o desenho (aqui, WebGL por software), não o cálculo da página
        cmd("Performance.enable")
        medidas["por_velocidade"] = {}
        for vel in (300, 3600, 36000, 86400):
            avalia(f"""(() => {{ const v = document.getElementById('t-vel'); v.value = '{vel}'; v.dispatchEvent(new Event('change'));
                          const b = document.getElementById('b-play'); if (b.textContent.trim() === '▶') b.click(); return 1; }})()""")
            espera(1.5)
            m0 = {x["name"]: x["value"] for x in cmd("Performance.getMetrics")["metrics"]}
            t0 = time.time()
            q = avalia(QUADROS)
            m1 = {x["name"]: x["value"] for x in cmd("Performance.getMetrics")["metrics"]}
            q["thread_ocupada_ms_por_s"] = round((m1["TaskDuration"] - m0["TaskDuration"]) * 1000 / (time.time() - t0), 1)
            medidas["por_velocidade"][str(vel)] = q
        medidas["fps_tocando_300x"] = medidas["por_velocidade"]["300"]
        # 1 dia/s (a última da varredura): dias emendados, eventos vermelhos e placar (decisão D49)
        medidas["a_1_dia_por_s"] = avalia(EVENTOS)
        shot = cmd("Page.captureScreenshot", format="png")
        open(os.path.join(SAIDA, f"site_{nome}_1dia.png"), "wb").write(base64.b64decode(shot["data"]))
        # cenário: chuva congelante e muita neve no solo mudam o esperado e marcam os itens (decisão D50)
        medidas["cenario_aplicado"] = avalia(CENARIO)
        pesos = avalia(PESOS)
        r = pesos.pop("painel")
        shot = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                   clip={"x": r["x"], "y": r["y"], "width": r["w"], "height": min(r["h"], 1600), "scale": 1})
        open(os.path.join(SAIDA, f"site_{nome}_painel.png"), "wb").write(base64.b64decode(shot["data"]))
        # a nota do método aberta
        r = avalia("""(() => { document.getElementById('m-detalhes').open = true;
          const a = document.querySelector('.metodo-peso').getBoundingClientRect();
          return {x: a.left + scrollX, y: a.top + scrollY, w: a.width, h: a.height}; })()""")
        espera(0.5)
        shot = cmd("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                   clip={"x": r["x"], "y": r["y"], "width": r["w"], "height": min(r["h"], 2400), "scale": 1})
        open(os.path.join(SAIDA, f"site_{nome}_nota_metodo.png"), "wb").write(base64.b64decode(shot["data"]))
        medidas["peso_das_variaveis"] = pesos
        erros = [e for e in eventos if e.get("method") == "Runtime.exceptionThrown"
                 or (e.get("method") == "Runtime.consoleAPICalled" and e["params"].get("type") == "error")
                 or (e.get("method") == "Log.entryAdded" and e["params"]["entry"].get("level") == "error")]
        textos_erro = []
        for e in erros[:5]:
            p = e["params"]
            if "exceptionDetails" in p:
                textos_erro.append(p["exceptionDetails"].get("exception", {}).get("description", p["exceptionDetails"].get("text", ""))[:200])
            elif "entry" in p:
                textos_erro.append(p["entry"].get("text", "")[:200] + " " + p["entry"].get("url", ""))
            else:
                textos_erro.append(" ".join(str(a.get("value", a.get("description", ""))) for a in p.get("args", []))[:200])
        shot = cmd("Page.captureScreenshot", format="png")
        open(os.path.join(SAIDA, f"site_{nome}.png"), "wb").write(base64.b64decode(shot["data"]))
        medidas["erros_console"] = textos_erro
        resultado[nome] = medidas
    open(os.path.join(SAIDA, "resultado.json"), "w", encoding="utf-8").write(json.dumps(resultado, ensure_ascii=False, indent=1))
    print("ok")
finally:
    proc.kill()
