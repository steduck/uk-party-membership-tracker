import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

WIKI_URL = "https://en.wikipedia.org/wiki/Membership_of_political_parties_in_the_United_Kingdom"
HTML_FILE = "index.html"
DATA_FILE = "data.json"

# Load previous data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        stored_data = json.load(f)
else:
    stored_data = {}

def get_table_rows():
    response = requests.get(WIKI_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    print("✅ Downloaded Wikipedia page.")

    headings = soup.find_all(["h2", "h3"])
    print(f"✅ Found {len(headings)} headings.")

    for heading in headings:
        heading_text = heading.get_text()
        print(f"🔎 Checking heading: {heading_text}")
        if "Current membership" in heading_text:
            next_table = heading.find_next("table", class_="wikitable")
            if next_table:
                print("✅ Found membership table.")
                rows = next_table.find_all("tr")[1:]  # skip header row
                print(f"✅ Found {len(rows)} rows.")
                return rows
            else:
                print("❌ Heading found but no table found after it.")

    print("❌ Could not find the correct heading or table.")
    return []

def generate_html(rows):
    today = datetime.now().strftime("%d %B %Y")
    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>UK Political Party Membership Numbers</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; background: #fff; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background: #f0f0f0; }}
    .increase {{ color: green; }}
    .decrease {{ color: red; }}
    .nochange {{ color: grey; }}
  </style>
</head>
<body>
<h1>UK Political Party Membership Numbers</h1>
<p>Last updated: {today}</p>
<table>
<thead>
<tr>
  <th>Party</th>
  <th>Members</th>
  <th>Change</th>
  <th>Last update</th>
  <th>Highest</th>
  <th>Lowest</th>
</tr>
</thead>
<tbody>
"""

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        party = cells[0].get_text(strip=True)

        # Clean citation tags
        for sup in cells[1].find_all("sup"):
            sup.decompose()
        members_text = cells[1].get_text(strip=True).replace(",", "")

        print(f"🔍 Raw party: {party}")
        print(f"🔍 Raw members text: '{members_text}'")

        try:
            members = int(members_text)
        except ValueError:
            print(f"⚠️ Could not convert member count for {party}: {members_text}")
            continue

        # Compare with stored data
        previous = stored_data.get(party, {}).get("current", members)
        highest = max(members, stored_data.get(party, {}).get("highest", members))
        lowest = min(members, stored_data.get(party, {}).get("lowest", members))
        last_updated = stored_data.get(party, {}).get("last_updated", today)

        if members != previous:
            last_updated = today

        change = members - previous
        if change > 0:
            change_html = f"<span class='increase'>+{change}</span>"
        elif change < 0:
            change_html = f"<span class='decrease'>{change}</span>"
        else:
            change_html = f"<span class='nochange'>0</span>"

        html += f"<tr><td>{party}</td><td>{members:,}</td><td>{change_html}</td><td>{last_updated}</td><td>{highest:,}</td><td>{lowest:,}</td></tr>\n"

        # Update stored data
        stored_data[party] = {
            "current": members,
            "previous": previous,
            "highest": highest,
            "lowest": lowest,
            "last_updated": last_updated
        }

    html += """</tbody></table></body></html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(stored_data, f, indent=2)

def main():
    rows = get_table_rows()
    generate_html(rows)
    print("✅ index.html updated.")

if __name__ == "__main__":
    main()
