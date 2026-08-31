import html
import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://secure.nsaahome.org/wildcards/schedules/index.php"
SPORT = "fb"
SEASON_YEAR = 2026

CLASS_CODES = [
    "A", "B", "C1", "C2", "D1", "D2", "D3", "D6"
]

OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "football.json"
)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (compatible; HSFootballTVBoard/2.0; "
        "+https://github.com/hyst16/hsfootball-tv-board)"
    )
})


def clean(value):
    value = html.unescape(value or "")
    value = value.replace("\xa0", " ")
    value = value.replace("–", "-")
    value = value.replace("—", "-")
    return re.sub(r"\s+", " ", value).strip()


def norm(value):
    return re.sub(r"[^a-z0-9]+", "", clean(value).lower())


def strip_record(value):
    return re.sub(
        r"\s*\(\d+\s*-\s*\d+(?:\s*-\s*\d+)?\)\s*$",
        "",
        clean(value),
    ).strip()


def convert_date(value, year):
    """
    Converts:
        Fri 28 Aug
    to:
        08/28/26
    """
    value = clean(value)

    for pattern in ("%a %d %b", "%A %d %b"):
        try:
            parsed = datetime.strptime(value, pattern)
            parsed = parsed.replace(year=year)
            return parsed.strftime("%m/%d/%y")
        except ValueError:
            pass

    raise ValueError(f"Unrecognized schedule date: {value!r}")


def request_page(payload=None):
    if payload:
        response = SESSION.post(
            BASE_URL,
            params={"sport": SPORT},
            data=payload,
            timeout=45,
        )
    else:
        response = SESSION.get(
            BASE_URL,
            params={"sport": SPORT},
            timeout=45,
        )

    response.raise_for_status()
    return response.text


def get_school_options(class_code):
    page = request_page({
        "year": str(SEASON_YEAR),
        "class": class_code,
    })

    soup = BeautifulSoup(page, "html.parser")
    select = soup.find("select", attrs={"name": "sid"})

    if select is None:
        raise RuntimeError(
            f"No school dropdown found for class {class_code}"
        )

    schools = []

    for option in select.find_all("option"):
        school_id = clean(option.get("value"))
        school_name = clean(option.get_text())

        if not school_id or school_name.lower() == "school":
            continue

        schools.append({
            "sid": school_id,
            "name": school_name,
        })

    if not schools:
        raise RuntimeError(
            f"No school IDs found for class {class_code}"
        )

    return schools


def find_team_heading(soup):
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = clean(heading.get_text())

        if re.search(
            r"\(\d+\s*-\s*\d+(?:\s*-\s*\d+)?\)\s*$",
            text,
        ):
 *          return text

    return *"


def find_schedule_table(soup):*    for table in soup.find_all("ta*le"):
        headers = [
            clean(cell.get_text())
        *   for cell in table.select("thead*th")
        ]

        if "Date" *n headers and "Opponent" in header*:
            return table, header*

    return None, []


def parse_*chool_page(page, class_code, expec*ed_name):
    soup = BeautifulSoup*page, "html.parser")

    team_dis*lay = find_team_heading(soup)
    *eam = strip_record(team_display) i* team_display else expected_name

*   table, headers = find_schedule_*able(soup)

    if table is None:
*       raise RuntimeError(
       *    f"No schedule table found for *expected_name}"
        )

    row* = []

    for tr in table.select(*tbody tr"):
        cells = [clean(td.get_text()) for td in tr.find_a*l("td")]

        if not cells:
  *         continue

        values * dict(zip(headers, cells))

      * raw_date = values.get("Date", "")*        opponent = values.get("Opp*nent", "")

        if not raw_dat* or not opponent:
            cont*nue

        win_loss = clean(valu*s.get("Win/Loss", ""))
        if *in_loss == "-":
            win_lo*s = ""

        score = clean(valu*s.get("Score", ""))
        if not*score or score == "-":
           *score = "-"

        record = clea*(values.get("Record", ""))
       *division = clean(values.get("Div",*""))
        points = clean(values*get("Points", ""))

        row = *
            "Date": convert_date(*aw_date, SEASON_YEAR),
           *"Opponent": opponent,
            *Class": clean(values.get("Class", *lass_code)),
            "W-L": re*ord or "-",
            "Div": div*sion or "-",
            "W/L": wi*_loss,
            "Score": score,*            "Points": points or "-*,
            "_team": team,
     *      "_team_display": team_displa* or team,
            "_class": cl*ss_code,
        }

        rows.a*pend(row)

    return norm(team), *ows


def main():
    by_team = {}*    seen_school_ids = set()

    f*r class_code in CLASS_CODES:
     *  schools = get_school_options(cla*s_code)

        print(
          * f"Class {class_code}: found {len(*chools)} schools"
        )

     *  for school in schools:
         *  school_id = school["sid"]
      *     expected_name = school["name"]

            if school_id in seen*school_ids:
                contin*e

            page = request_page*{
                "year": str(SEAS*N_YEAR),
                "class": *lass_code,
                "sid": *chool_id,
            })

        *   key, rows = parse_school_page(
*               page,
             *  class_code,
                expe*ted_name,
            )

         *  if rows:
                by_team*key] = rows
                seen_s*hool_ids.add(school_id)
          *     print(
                    f"* {expected_name}: {len(rows)} game*"
                )
            el*e:
                print(
        *           f"  WARNING: {expected_*ame} returned no games"
          *     )

            time.sleep(0.1*)

    game_count = sum(len(rows) *or rows in by_team.values())

    *f not by_team:
        raise Runti*eError(
            "Scrape return*d zero teams. Existing data was no* replaced."
        )

    payload*= {
        "updated": int(time.ti*e()),
        "season": SEASON_YEA*,
        "source": BASE_URL,
    *   "team_count": len(by_team),
   *    "game_count": game_count,
    *   "by_team": by_team,
    }

    *emporary_path = OUT_PATH.with_suff*x(".json.tmp")

    temporary_path*write_text(
        json.dumps(
  *         payload,
            ensu*e_ascii=False,
            separat*rs=(",", ":"),
        ),
        *ncoding="utf-8",
    )

    tempor*ry_path.replace(OUT_PATH)

    pri*t(
        f"Wrote {OUT_PATH}: "
 *      f"{len(by_team)} teams, {gam*_count} games"
    )


if __name__*== "__main__":
    main()
