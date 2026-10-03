"""Download WHO TB estimates and write data.json.

Each country gets one record for the newest year in the file, with a status:
  ok          - incidence estimate available for the newest year
  unavailable - WHO publishes the country but no incidence estimate (e.g. DPR Korea)
  historical  - entity has no row in the newest year (e.g. Netherlands Antilles)
"""
import csv, io, json, urllib.request
from datetime import datetime, timezone

URL = "https://extranet.who.int/tme/generateCSV.asp?ds=estimates"
req = urllib.request.Request(URL, headers={"User-Agent": "tb-lookup-site/0.2"})
rows = list(csv.DictReader(io.StringIO(urllib.request.urlopen(req, timeout=60).read().decode("utf-8-sig"))))
if len(rows) < 3000:
    raise SystemExit("Unexpectedly small WHO file (%d rows) - refusing to overwrite data.json" % len(rows))

newest = max(int(r["year"]) for r in rows)
latest = {}
for r in rows:
    c = r["country"]
    if c not in latest or int(r["year"]) > int(latest[c]["year"]):
        latest[c] = r

countries = []
for c, r in sorted(latest.items()):
    year = int(r["year"])
    rec = {"country": c, "iso3": r["iso3"], "year": year}
    if year < newest:
        rec["status"] = "historical"
    elif not r["e_inc_100k"]:
        rec["status"] = "unavailable"
    else:
        rec.update(status="ok", rate=float(r["e_inc_100k"]), lo=float(r["e_inc_100k_lo"]), hi=float(r["e_inc_100k_hi"]))
    countries.append(rec)

out = {
    "meta": {
        "retrieved": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": URL,
        "indicator": "e_inc_100k",
        "data_year": newest,
        "source_rows": len(rows),
    },
    "countries": countries,
}
json.dump(out, open("data.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
n = lambda s: sum(c["status"] == s for c in countries)
print(f"{len(countries)} entities: {n('ok')} ok, {n('unavailable')} unavailable, {n('historical')} historical; data year {newest}")
