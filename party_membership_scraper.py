import requests
from bs4 import BeautifulSoup
from datetime import datetime

WIKI_URL = "https://en.wikipedia.org/wiki/Political_party_membership_in_the_United_Kingdom"
HTML_FILE = "index.html"

HEADER_HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
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

    tables = soup.find_all("table", {"class": "wikitable"})
    if not tables:
        raise Exception("No tables found on Wikipedia page")

    party_data = []
    table = tables[0]  # First table is usually the current one
    for row in table.find_all("tr")[1:]:
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            party = cells[0].get_text(strip=True)
            members = cells[1].get_text(strip=True)
            party_data.append((party, members, "<a href='{}'>Wikipedia</a>".format(WIKI_URL)))

    return party_data

def generate_html(data):
    today = datetime.now().strftime("%d %B %Y")
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER_HTML.format(today))
        for party, members, source in data:
            f.write(f"      <tr><td>{party}</td><td>{members}</td><td>{source}</td></tr>\n")
        f.write(FOOTER_HTML)

def main():
    try:
        data = scrape_membership_table()
        generate_html(data)
        print("HTML updated successfully.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
