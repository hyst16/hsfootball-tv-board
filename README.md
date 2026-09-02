# HS Football TV — Office URL Guide

This repository powers the HS Football TV boards. Use the Office URL feature to show a curated list of teams on each TV by visiting a GitHub Pages URL that includes an office key.

Quick start

- Debug / Teams Builder (pick teams, preview JSON):
  https://hyst16.github.io/hsfootball-tv-board/debug.html

Full URL format (use your org or username in place of `hyst16`):

https://hyst16.github.io/hsfootball-tv-board/?office=<office-key>

Example (clickable):

- [Mead TV — mead-office](https://hyst16.github.io/hsfootball-tv-board/?office=mead-office)

Office URL mappings and teams

Below is the current list of office keys and the teams they contain. These are updated from `teams.json`.

<!-- offices-start -->

## Office URL mappings

Use the links to open each office directly:

- [mead-office](https://hyst16.github.io/hsfootball-tv-board/?office=mead-office)
  - Wahoo
  - Bishop Neumann
  - Mead
  - Yutan

- [northbend-office](https://hyst16.github.io/hsfootball-tv-board/?office=northbend-office)
  - North Bend Central
  - Arlington
  - Logan View/Scribner-Snyder (LVSS)
  - Schuyler

- [tarnov-office](https://hyst16.github.io/hsfootball-tv-board/?office=tarnov-office)
  - Columbus
  - Columbus Lakeview
  - Scotus Central Catholic
  - Humphrey-Lindsay
  - Archangels Catholic
  - Twin River

- [yanka-office](https://hyst16.github.io/hsfootball-tv-board/?office=yanka-office)
  - Aquinas Catholic
  - David City
  - East Butler

<!-- offices-end -->

How to edit teams (simple)

1) Use the Debug / Teams Builder page to select teams and build a `teams.json` snippet.
2) Click "Copy JSON" and then click the **Edit on GitHub** link to open `teams.json` in the web editor.
3) Paste the updated JSON and commit the change to the `main` branch.

Notes

- Matching is case-insensitive and ignores punctuation; use the NSAA team text (no record) when possible.
- The site refreshes teams automatically when `teams.json` changes.
- If you accidentally create an office key, use the Debug page's **Delete selected office** button and then paste/commit the updated JSON to GitHub.

Troubleshooting

- 404 for debug page: wait a minute and hard refresh (Ctrl+F5). Ensure the site is published from the `main` branch.
- If a team shows as "Missing" in the Debug UI, use the suggested replacement or pick the correct team from the list and update `teams.json`.

