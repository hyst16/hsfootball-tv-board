Office Teams (How to choose what each TV shows)

This site lets you show different schools on different TVs by passing an office key in the URL:

https://<your-username>.github.io/hsfootball-tv-board/?office=<office-key>


You control which schools appear for each office by editing one file: teams.json.

1) Edit teams.json

Open your repo on GitHub.

Click teams.json → click the ✏️ pencil to edit.

The file is a simple map from office key → list of team names:

{
  "mead-office": ["Wahoo", "Wahoo Neumann", "Yutan-Mead"],
  "bellwood-office": ["David City", "Aquinas Catholic"],
  "lincoln-office": ["Lincoln Southeast", "Lincoln Southwest", "Lincoln East"]
}


The left side ("mead-office", "bellwood-office", etc.) can be any short key you want.

The right side is a list of team names exactly how NSAA captions them (see Step 2 below).

Click Commit changes.

2) Use the exact team name NSAA uses

On the NSAA class pages, the team name is in the table caption and often includes a record, e.g.:

<b>Wahoo (0-0)</b>
<b>Wahoo Neumann (0-0)</b>
<b>Yutan-Mead (0-0)</b>


For teams.json, use the name part only (don’t include the record):

✅ Wahoo

✅ Wahoo Neumann

✅ Yutan-Mead

❌ Wahoo (0-0) (don’t include the record)

Tip: Some schools are listed differently than you might say them:

“Bishop Neumann” is typically listed as “Wahoo Neumann”.

“Mead” appears in a co-op as “Yutan-Mead”.

Easiest way to find the correct names

Open the helper page (already in the repo):

https://<your-username>.github.io/hsfootball-tv-board/debug.html


Type part of a name (e.g., wahoo, neumann, mead) in the filter box.

The table shows Team text (from NSAA) — copy that text (without the (0-0) part) into teams.json.

3) Put each TV on the right URL

Once teams.json is saved, point each TV to:

https://<your-username>.github.io/hsfootball-tv-board/?office=<office-key>


Examples:

Mead TV:
...?office=mead-office

Bellwood TV:
...?office=bellwood-office

The page auto-refreshes every 10 minutes.

4) How/when does data update?

A GitHub Action scrapes NSAA once a day and writes data/football.json.

You can run it anytime: Actions → “Scrape NSAA -> Build JSON” → Run workflow.

The updated time shows in the page footer.

Don’t edit data/football.json by hand—each run overwrites it.

5) Troubleshooting

The card says “No match found yet.”

The name in teams.json doesn’t match NSAA’s caption.

Open debug.html, search for the school, and copy the Team text (without the record) into teams.json.

Footer says “(no data yet)”.

The daily scraper hasn’t run or failed.

Go to Actions → Run workflow. After it finishes, refresh the page.

I want to add/remove teams later.

Edit teams.json anytime. Changes show immediately (no scraper run needed).

FAQ

Do capitalization, spaces, or dashes matter?
No—matching is case-insensitive and ignores punctuation. But the words must match NSAA’s naming (e.g., use “Wahoo Neumann”, not “Bishop Neumann”).

Can I have many offices?
Yes. Add more keys to teams.json, then use ?office=<that-key> in the URL.

Can I rotate pages (e.g., 6 teams split across 2 screens)?
Easiest is to make two office keys (mead-1, mead-2) with different team lists and put each URL on a separate TV. If you’d like auto-rotation on a single screen, we can add that—just ask.
