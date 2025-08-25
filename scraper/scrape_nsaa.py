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

# write to ROOT/data (GitHub Pages serves from root)
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "football.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# keep ONLY these common/useful columns (order = preference)
PREFERRED_COLS = [
    "Date", "Opponent", "Class", "W-L", "Div", "W/L", "Score", "Points",
    "Home/Away", "Site", "Time"  # optional extras if present
]

def clean_text(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "")).strip()

def normalize_team(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())

def pick_team_header(headers):
    for h in headers:
        if re.search(r"(school|team|name)", h, re.I):
            return h
    # fallback to first column name
    return headers[0] if headers else None

def parse_table(html, cls_code):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        return []

    # headers
    header_row = table.find("tr")
    headers = []
    if header_row:
        for th in header_row.find_all(["th", "td"]):
            headers.append(clean_text(th.get_text()))

    team_header = pick_team_header(headers)

    # rows
    out_rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue
        cells = [clean_text(td.get_text()) for td in tds]

        # map row to header -> value
        row_map = {}
        for i, val in enumerate(cells):
            key = headers[i] if i < len(headers) else f"col_{i}"

            # only keep preferred columns to keep file tiny
            if key in PREFERRED_COLS:
                row_map[key] = val

        # figure team name for this row (for grouping)
        if team_header and team_header in headers:
            idx = headers.index(team_header)
            team_val = cells[idx] if idx < len(cells) else (cells[0] if cells else "")
        else:
            team_val = cells[0] if cells else ""

        team_val = clean_text(team_val)
        if not team_val:
            continue

        # add metadata (kept tiny)
        row_map["_team"]  = team_val
        row_map["_class"] = cls_code

        out_rows.append(row_map)

    return out_rows

def main():
    by_team = {}
    for cls, url in CLASS_URLS.items():
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        rows = parse_table(r.text, cls)
        for row in rows:
            k = normalize_team(row.get("_team", ""))
            if not k:
                continue
            by_team.setdefault(k, []).append(row)

    # minimal top-level object; no pretty-print, no extra keys
    # keep a small timestamp for the footer
    payload = {
        "updated": int(time.time()),
        "by_team": by_team
    }

    # MINIFIED JSON (no spaces/newlines) for maximum shrink
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    print(f"Wrote {OUT_PATH} (minified)")

if __name__ == "__main__":
    main()
