import requests
from bs4 import BeautifulSoup
from datetime import datetime

WIKI_URL = "https://en.wikipedia.org/wiki/Political_party_membership_in_the_United_Kingdom"
HTML_FILE = "index.html"

HEADER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>UK Political Party Membership Numbers</title>
  <style>
    body { font-family: Arial, sans-serif; background-color: #ffffff; color: #222; margin: 0; padding: 20px; }
    h1 { text-align: center; margin-bottom: 30px; }
    table { width: 100%; border-collapse: collapse; margin: 0 auto; max-width: 800px; }
    th, td { text-align: left; padding: 12px 16px; border-bottom: 1px solid #ddd; }
    th { background-color: #f4f4f4; }
    a { color: #0056b3; text-decoration: none; }
  </style>
</head>
<body>
  <h1>UK Political Party Membership Numbers</h1>
  <p style='text-align:center'>Last updated: {}</p>
  <table>
    <thead>
      <tr>
        <th>Party</th>
        <th>Members</th>
        <th>Source</th>
      </tr>
    </thead>
    <tbody>
"""

FOOTER_HTML = """
    </tbody>
  </table>
</body>
</html>
"""

def scrape_membership_table():
    response = requests.get(WIKI_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    # Look for the first wikitable with at least 2 columns
    tables = soup.find_all("table", class_="wikitable")
    for table in tables:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if "Party" in headers[0] and "Members" in headers[1]:
            print("✅ Found membership table.")
            return table.find_all("tr")[1:]  # skip header row
    print("❌ Could not find membership table.")
    return []

def generate_html(rows):
    today = datetime.now().strftime("%d %B %Y")
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER_HTML.format(today))
        if not rows:
            f.write("<tr><td colspan='3'>No data could be loaded.</td></tr>\n")
        else:
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    party = cells[0].get_text(strip=True)
                    members = cells[1].get_text(strip=True)
                    source = f"<a href='{WIKI_URL}' target='_blank'>Wikipedia</a>"
                    f.write(f"<tr><td>{party}</td><td>{members}</td><td>{source}</td></tr>\n")
        f.write(FOOTER_HTML)

def main():
    try:
        rows = scrape_membership_table()
        generate_html(rows)
        print("✅ index.html generated successfully.")
    except Exception as e:
        print("❌ Script error:", e)

if __name__ == "__main__":
    main()
