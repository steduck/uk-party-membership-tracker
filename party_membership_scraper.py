import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re  # moved to the top for clarity

WIKI_URL = "https://en.wikipedia.org/wiki/Political_party_membership_in_the_United_Kingdom"
HTML_FILE = "index.html"

def get_table_rows():
    response = requests.get(WIKI_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    print("✅ Downloaded Wikipedia page.")
    
    headings = soup.find_all(["h2", "h3"])
    print(f"✅ Found {len(headings)} headings.")

    for heading in headings:
        heading_text = heading.get_text()
        print(f"🔎 Checking heading: {heading_text}")
        if "Current membership" in heading.get_text():
            next_table = heading.find_next("table", class_="wikitable")
            if next_table:
                print("✅ Found the correct table!")
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
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>UK Political Party Membership Numbers</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; background: #fff; color: #222; }}
    table {{ width: 100%; border-collapse: collapse; max-width: 800px; margin: 0 auto; }}
    th, td {{ padding: 12px 16px; border-bottom: 1px solid #ccc; }}
    th {{ background: #f4f4f4; }}
    h1 {{ text-align: center; }}
    p {{ text-align: center; }}
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
                # Clean citation tags
                for sup in cells[0].find_all("sup"):
                    sup.decompose()
                for sup in cells[1].find_all("sup"):
                    sup.decompose()

                party = cells[0].get_text(strip=True)
                members_text = cells[1].get_text(strip=True)

                # Remove any lingering [1], [update], etc.
                members_text = re.sub(r"\[\d+\]", "", members_text)
                members_text = re.sub(r"\[update\]", "", members_text, flags=re.IGNORECASE)
                members_text = members_text.strip()

                # Example placeholder movement logic - always shows +0 for now
                movement_value = 0
                movement_sign = "+" if movement_value >= 0 else "-"
                movement_class = "style='color: green;'" if movement_value >= 0 else "style='color: red;'"
                html += f"<tr><td>{party}</td><td>{members_text}</td><td {movement_class}>{movement_sign}{abs(movement_value)}</td></tr>\n"

    html += """
        </tbody>
      </table>
      <p style='text-align: center; padding-top: 20px;'>
        Source: <a href='https://en.wikipedia.org/wiki/Political_party_membership_in_the_United_Kingdom' target='_blank'>Wikipedia</a>
      </p>
    </body>
    </html>

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    rows = get_table_rows()
    generate_html(rows)
    print(f"✅ index.html updated with {len(rows)} rows.")

if __name__ == "__main__":
    main()
