import json, time, re
from pathlib import Path
from bs4 import BeautifulSoup
import requests

CLASS_URLS = {
    "A":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbA.html",
    "B":  "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbB.html",
    "C1": "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbC1.html",
    "C2": "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbC2.html",
    "D1": "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbD1.html",
    "D2": "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbD2.html",
    "D6": "https://nsaa-static.s3.amazonaws.com/calculate/showclassfbD6.html",
}

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "football.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

KEEP_COLS = ["Date","Opponent","Class","W-L","Div","W/L","Score","Points","Home/Away","Site","Time"]

def clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\xa0"," ")).strip()

def strip_record(name_with_record: str) -> str:
    # "Wahoo (0-0)" -> "Wahoo"
    return re.sub(r"\s*\([^)]*\)\s*$", "", clean(name_with_record))

def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def parse_class_page(html: str, cls_code: str):
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for table in soup.find_all("table"):
        cap = table.find("caption")
        if not cap:
            continue
        team_full = clean(cap.get_text())          # e.g., "Wahoo (0-0)"
        team = strip_record(team_full)             # "Wahoo"
        key = norm(team)                           # "wahoo"

        # find header row that contains "Date" and "Opponent"
        header_tr = None
        for tr in table.find_all("tr"):
            cells = [clean(td.get_text()) for td in tr.find_all("td")]
            if cells and "Date" in cells and "Opponent" in cells:
                header_tr = tr
                headers = cells
                break
        if not header_tr:
            continue

        rows = []
        for tr in header_tr.find_next_siblings("tr"):
            if tr.find("hr"):
                continue
            text = tr.get_text(" ", strip=True)
            if "Total Points:" in text:   # stop before totals block
                break
            tds = tr.find_all("td")
            if not tds:
                continue
            cells = [clean(td.get_text()) for td in tds]
            if not cells or cells[0] == "Date":
                continue
            # map only kept columns (and only as many cells as present)
            row = {}
            for i in range(min(len(headers), len(cells))):
                h = headers[i]
                if h in KEEP_COLS:
                    row[h] = cells[i]
            if row:
                row["_team"] = team
                row["_team_display"] = team_full
                row["_class"] = cls_code
                rows.append(row)

        if rows:
            out.setdefault(key, []).extend(rows)

    return out

def main():
    by_team = {}
    for cls, url in CLASS_URLS.items():
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        team_rows = parse_class_page(r.text, cls)
        # merge into by_team
        for k, rows in team_rows.items():
            by_team.setdefault(k, []).extend(rows)

    payload = {"updated": int(time.time()), "by_team": by_team}
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, separators=(",",":")))
    print(f"Wrote {OUT_PATH} (minified, {sum(len(v) for v in by_team.values())} rows)")

if __name__ == "__main__":
    main()
