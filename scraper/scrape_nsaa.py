import json, time, re
from pathlib import Path
from bs4 import BeautifulSoup
import requests

CLASS_URLS = {
    "A":   "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbA.html",
    "B":   "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbB.html",
    "C1":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbC1.html",
    "C2":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbC2.html",
    "D1":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbD1.html",
    "D2":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbD2.html",
    "D6":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbD6.html",
}

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "football.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def clean_text(t):
    return re.sub(r"\s+", " ", t).strip()

def normalize_team(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())

def parse_table(html, cls_code):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        return []
    headers = []
    header_row = table.find("tr")
    if header_row:
        for th in header_row.find_all(["th", "td"]):
            headers.append(clean_text(th.get_text()))
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = [clean_text(td.get_text()) for td in tr.find_all("td")]
        if not cells:
            continue
        row = {}
        for i, val in enumerate(cells):
            key = headers[i] if i < len(headers) else f"col_{i}"
            row[key] = val
        row["_class"] = cls_code
        team_key = None
        for h in headers:
            if re.search(r"(school|team|name)", h, re.I):
                team_key = h
                break
        if team_key and row.get(team_key):
            row["_team_key"] = row[team_key]
            row["_team_norm"] = normalize_team(row[team_key])
        else:
            row["_team_key"] = cells[0]
            row["_team_norm"] = normalize_team(cells[0])
        rows.append(row)
    return rows

def main():
    combined = {
        "updated_epoch": int(time.time()),
        "updated_human": time.strftime("%Y-%m-%d %H:%M:%S"),
        "classes": {}
    }
    by_team = {}
    for cls, url in CLASS_URLS.items():
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        rows = parse_table(res.text, cls)
        combined["classes"][cls] = rows
        for r in rows:
            key = r.get("_team_norm")
            if key:
                by_team.setdefault(key, []).append(r)
    combined["by_team"] = by_team
    OUT_PATH.write_text(json.dumps(combined, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
