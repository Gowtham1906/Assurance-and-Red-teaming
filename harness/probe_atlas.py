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
for tid in ("AML.T0051", "AML.T0054", "AML.T0057", "AML.T0080", "AML.T0086", "AML.T0101"):
    print(f"  {tid}: {by_id.get(tid, 'NOT FOUND')}")
