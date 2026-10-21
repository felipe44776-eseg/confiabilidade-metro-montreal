import json, sys, urllib.parse, urllib.request
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for alvo in sys.argv[1:]:
    q = urllib.parse.urlencode({"url": alvo, "output": "json", "fl": "timestamp,statuscode", "filter": "statuscode:200", "limit": "150000"})
    try:
        req = urllib.request.Request("http://web.archive.org/cdx/search/cdx?" + q, headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(req, timeout=120))
    except Exception as e:
        print(alvo, "ERR", e); continue
    ts = [r[0] for r in d[1:]]
    por_ano = Counter(t[:4] for t in ts)
    dias = len({t[:8] for t in ts})
    print(f"{alvo}\n   capturas={len(ts)} dias_distintos={dias} | " + " ".join(f"{a}:{n}" for a, n in sorted(por_ano.items())))
