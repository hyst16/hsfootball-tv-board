import csv
import json
import re
import time
from datetime import datetime
from io import StringIO
from pathlib import Path

import requests

YEAR = 2026

CLASSES = [
    "A",
    "B",
    "C1",
    "C2",
    "D1",
    "D2",
    "D3",
    "D6",
]

BASE_URL = (
    "https://secure.nsaahome.org/"
    "wildcards/schedules/export.php"
)

OUTFILE = Path("data/football.json")


def normalize_team(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def convert_date(value):
    value = value.strip()

    try:
        dt = datetime.strptime(value, "%a %d %b")
        dt = dt.replace(year=YEAR)
        return dt.strftime("%m/%d/%y")
    except Exception:
        return value


def parse_result(score):
    if not score:
        return "", "-"

    score = (
        score.replace("&ndash;", "-")
        .replace("–", "-")
        .strip()
    )

    m = re.match(r"(\\d+)\\-(\\d+)", score)

    if not m:
        return "", score

    left = int(m.group(1))
    right = int(m.group(2))

    if left > right:
        return "W", score

    if left < right:
        return "L", score

    return "T", score


def download_class(class_name):
    response = requests.get(
        BASE_URL,
        params={
            "sport": "fb",
            "class": class_name
        },
        timeout=60
    )

    response.raise_for_status()

    return response.text


def main():
    by_team = {}

    for class_name in CLASSES:
        print(f"Downloading class {class_name}")

        csv_text = download_class(class_name)

        reader = csv.DictReader(StringIO(csv_text))

        for row in reader:

            school = row.get("School", "").strip()

            if not school:
                continue

            key = normalize_team(school)

            score = row.get("Score", "").strip()

            wl, score = parse_result(score)

            wins = row.get("Wins", "").strip()
            losses = row.get("Losses", "").strip()

            record = "-"

            if wins and losses:
                record = f"{wins}-{losses}"

            game = {
                "Date": convert_date(row["Date"]),
                "Opponent": row["Opponent"].strip(),
                "Class": row["Class"].strip(),
                "W-L": record,
                "Div": row["Division"].strip() or "-",
                "W/L": wl,
                "Score": score or "-",
                "Points": row["Points"].strip() or "-",
                "_team": school,
                "_team_display": school,
                "_class": class_name,
            }

            by_team.setdefault(key, []).append(game)

    payload = {
        "updated": int(time.time()),
        "by_team": by_team,
    }

    OUTFILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))

    print(
        f"Wrote football.json for "
        f"{len(by_team)} teams"
    )


if __name__ == "__main__":
    main()
