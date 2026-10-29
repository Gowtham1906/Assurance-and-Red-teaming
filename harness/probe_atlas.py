"""Fetch the latest MITRE ATLAS data release and verify version, counts and IDs."""
import requests
import yaml

rel = requests.get("https://api.github.com/repos/mitre-atlas/atlas-data/releases/latest",
                   timeout=30).json()
print("latest release tag:", rel.get("tag_name"), "| published:", rel.get("published_at"))

url = "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/dist/ATLAS.yaml"
data = yaml.safe_load(requests.get(url, timeout=60).text)
print("ATLAS.yaml version:", data.get("version"))
matrix = data["matrices"][0]
tactics = matrix.get("tactics", [])
techniques = matrix.get("techniques", [])
top = [t for t in techniques if t["id"].count(".") == 1]   # AML.T0051
subs = [t for t in techniques if t["id"].count(".") == 2]  # AML.T0051.000
print(f"tactics: {len(tactics)} | techniques: {len(top)} | sub-techniques: {len(subs)}")
by_id = {t["id"]: t["name"] for t in techniques}

import csv  # noqa: E402
from pathlib import Path  # noqa: E402

out = Path("redteam/atlas_v2026.10_techniques.csv")
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "tactics"])
    for t in sorted(techniques, key=lambda x: x["id"]):
        w.writerow([t["id"], t["name"], ";".join(t.get("tactics", []))])
print("wrote", out, len(techniques), "rows")
for tid in ("AML.T0051", "AML.T0054", "AML.T0057", "AML.T0080", "AML.T0086", "AML.T0101"):
    print(f"  {tid}: {by_id.get(tid, 'NOT FOUND')}")
