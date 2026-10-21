"""Testa uma página publicada num navegador sem janela (Edge ou Chrome), pelo protocolo DevTools.

Uso: python testa_navegador.py <pasta_saida>   (variáveis: URL, SO=celular|notebook, ESPERA=segundos)
Precisa do pacote `websocket-client` (pip install websocket-client, num ambiente à parte: não é dependência do projeto)
e do Edge ou do Chrome instalados. Mede, em tamanho de celular (390x844) e de notebook (1366x768): rolagem lateral,
WebGL, quadros por segundo do mapa, erros no console; grava capturas e resultado.json na pasta de saída.
Rode um tamanho por vez (SO=...): reaproveitar a aba entre tamanhos perde o contexto WebGL por software.
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
                         "--no-first-run", "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader", "--ignore-gpu-blocklist", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(60):
        try:
            alvos = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/json", timeout=5))
            pagina = next(a for a in alvos if a["type"] == "page")
            break
        except Exception:
            time.sleep(0.5)
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
        medidas = avalia("""(() => {
          const d = document.documentElement;
          const txt = document.body.innerText;
          const largos = [...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > d.clientWidth + 1).length;
          return {scrollWidth: d.scrollWidth, clientWidth: d.clientWidth, elementosAlemDaLargura: largos,
                  temMapa: !!document.querySelector('canvas.maplibregl-canvas'), webgl2: !!document.createElement('canvas').getContext('webgl2'), fps: (document.body.innerText.match(/(\S+) fps/) || [''])[0],
                  textoMC: (txt.match(/(\\d[\\d.]*) dias[^\\n]{0,80}/) || [''])[0],
                  amostraTexto: txt.slice(0, 300)};
        })()""")
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
