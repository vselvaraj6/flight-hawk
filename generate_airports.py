"""
Downloads the mwgg/Airports dataset and extracts commercial airports with IATA codes.
Outputs a clean airports.json sorted by city name.
"""
import json
import urllib.request

URL = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"

print("Downloading airport data...")
with urllib.request.urlopen(URL) as resp:
    raw = json.loads(resp.read().decode())

print(f"Total airports in dataset: {len(raw)}")

# Filter: must have a valid 3-letter IATA code and a city name
airports = []
seen_codes = set()
for icao, info in raw.items():
    iata = info.get("iata", "").strip()
    city = info.get("city", "").strip()
    name = info.get("name", "").strip()
    country = info.get("country", "").strip()
    
    # Must have valid IATA code (3 letters), city, and name
    if len(iata) != 3 or not city or not name:
        continue
    # Skip duplicates
    if iata in seen_codes:
        continue
    # Skip codes that look invalid (numbers, weird chars)
    if not iata.isalpha():
        continue
    
    seen_codes.add(iata)
    airports.append({
        "code": iata,
        "name": name,
        "city": city,
        "country": country
    })

# Sort by city name
airports.sort(key=lambda a: a["city"].lower())

print(f"Filtered to {len(airports)} airports with valid IATA codes")

# Write output
output_path = "/home/vslevaraj/.gemini/antigravity/scratch/flight-tracker/airports.json"
with open(output_path, "w") as f:
    json.dump(airports, f, indent=2, ensure_ascii=False)

print(f"Written to {output_path}")

# Verify Reykjavik is included
kef = [a for a in airports if "eykjav" in a["city"].lower() or a["code"] == "KEF"]
print(f"Reykjavik airports found: {kef}")
