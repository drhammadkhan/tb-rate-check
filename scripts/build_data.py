"""Download WHO TB estimates and write data.json (latest year per country)."""
import csv, io, json, urllib.request

URL = "https://extranet.who.int/tme/generateCSV.asp?ds=estimates"
req = urllib.request.Request(URL, headers={"User-Agent": "tb-lookup-site/0.1"})
rows = csv.DictReader(io.StringIO(urllib.request.urlopen(req, timeout=60).read().decode("utf-8-sig")))
best = {}
for r in rows:
    if r["e_inc_100k"] and (r["country"] not in best or int(r["year"]) > int(best[r["country"]]["year"])):
        best[r["country"]] = r
out = [{"country": c, "iso3": r["iso3"], "year": int(r["year"]), "rate": float(r["e_inc_100k"]),
        "lo": float(r["e_inc_100k_lo"]), "hi": float(r["e_inc_100k_hi"])} for c, r in sorted(best.items())]
json.dump(out, open("data.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "countries, latest year", max(o["year"] for o in out))
