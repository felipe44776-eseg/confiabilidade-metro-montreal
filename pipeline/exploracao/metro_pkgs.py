import json, sys, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = "https://transparencia.metrosp.com.br/api/3/action/package_show?id="
names = sys.argv[1:]
for n in names:
    url = BASE + urllib.parse.quote(n)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(req, timeout=40))["result"]
        d = d[0] if isinstance(d, list) else d
    except Exception as e:
        print("ERR", n, e)
        continue
    rs = d.get("resources", [])
    print("=" * 60)
    print(n, "|", d.get("title"), "| recursos:", len(rs), "| mod:", (d.get("metadata_modified") or "")[:10])
    for r in rs:
        print("  -", (r.get("name") or "")[:70], "|", r.get("format"), "|", r.get("url"))
