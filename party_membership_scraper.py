import requests
from bs4 import BeautifulSoup
from datetime import datetime

WIKI_URL = "https://en.wikipedia.org/wiki/Political_party_membership_in_the_United_Kingdom"
HTML_FILE = "index.html"

def get_table_rows():
    response = requests.get(WIKI_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the first table after a heading that says "Membership of UK political parties"
    headings = soup.find_all(["h2", "h3"])
    for heading in headings:
        if "Membership of UK political parties" in heading.get_text():
            next_table = heading.find_next("table", class_="wikitable")
            if next_table:
                return next_table.find_all("tr")[1:]  # skip header row
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
      <tr><th>Party</th><th>Members</th><th>Source</th></tr>
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
                members = cells[1].get_text(strip=True)
                html += f"<tr><td>{party}</td><td>{members}</td><td><a href='{WIKI_URL}'>Wikipedia</a></td></tr>\n"

    html += """</tbody></table></body></html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    rows = get_table_rows()
    generate_html(rows)
    print("✅ index.html updated.")

if __name__ == "__main__":
    main()
