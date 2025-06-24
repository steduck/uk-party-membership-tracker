import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

WIKI_URL = "https://en.wikipedia.org/wiki/Political_party_membership_in_the_United_Kingdom"
HTML_FILE = "index.html"
DATA_FILE = "data.json"
HISTORY_FILE = "history.json"

def get_table_rows():
    response = requests.get(WIKI_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    print("\u2705 Downloaded Wikipedia page.")

    headings = soup.find_all(["h2", "h3"])
    print(f"\u2705 Found {len(headings)} headings.")

    for heading in headings:
        heading_text = heading.get_text()
        print(f"🔎 Checking heading: {heading_text}")
        if "Current membership" in heading_text:
            next_table = heading.find_next("table", class_="wikitable")
            if next_table:
                print("\u2705 Found the correct table!")
                rows = next_table.find_all("tr")[1:]  # skip header row
                print(f"\u2705 Found {len(rows)} rows.")
                return rows
            else:
                print("\u274c Heading found but no table found after it.")
    print("\u274c Could not find the correct heading or table.")
    return []

def load_json(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_html(rows, previous_data):
    today = datetime.now().strftime("%d %B %Y")
    current_data = {}

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>UK Political Party Membership Numbers</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; background: #fff; color: #222; }}
    table {{ width: 100%; border-collapse: collapse; max-width: 800px; margin: 0 auto; }}
    th, td {{ padding: 12px 16px; border-bottom: 1px solid #ccc; }}
    th {{ background: #f4f4f4; }}
    h1, p {{ text-align: center; }}
  </style>
</head>
<body>
  <h1>UK Political Party Membership Numbers</h1>
  <p>Last updated: {today}</p>
  <table>
    <thead>
      <tr><th>Party</th><th>Members</th><th>Movement</th></tr>
    </thead>
    <tbody>
"""

    if not rows:
        html += "<tr><td colspan='3'>No data found.</td></tr>\n"
    else:
        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                party = cells[0].get_text(strip=True)
                # Remove citation numbers
                for sup in cells[1].find_all("sup"):
                    sup.decompose()
                members_text = cells[1].get_text(strip=True).replace(",", "")

                try:
                    members = int(members_text)
                except ValueError:
                    print(f"⚠️ Could not convert member count for {party}: {members_text}")
                    continue

                current_data[party] = members
                prev_members = previous_data.get(party)

                # Calculate movement
                if prev_members is None:
                    movement = "New"
                    colour = "black"
                else:
                    diff = members - prev_members
                    if diff > 0:
                        movement = f"+{diff}"
                        colour = "green"
                    elif diff < 0:
                        movement = f"{diff}"
                        colour = "red"
                    else:
                        movement = "0"
                        colour = "black"

                html += f"<tr><td>{party}</td><td>{members}</td><td style='color: {colour};'>{movement}</td></tr>\n"

    html += f"""
    </tbody>
  </table>
  <p style='text-align: center; padding-top: 20px;'>
    Source: <a href='{WIKI_URL}' target='_blank'>Wikipedia</a>
  </p>
</body>
</html>
"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    return current_data

def save_history(today, current_data):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

    today_record = {"date": today}
    today_record.update(current_data)
    history.append(today_record)

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def main():
    previous_data = load_json(DATA_FILE)
    rows = get_table_rows()
    current_data = generate_html(rows, previous_data)
    save_json(DATA_FILE, current_data)
    today = datetime.now().strftime("%d %B %Y")
    save_history(today, current_data)
    print(f"\u2705 index.html updated with {len(current_data)} rows.")

if __name__ == "__main__":
    main()
