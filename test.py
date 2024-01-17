import requests
from bs4 import BeautifulSoup

url = "https://www.sec.gov/Archives/edgar/data/1608638/000119312519039441/d689911ddefm14a.htm"
anchor = "toc689911_37"

# Fetch the HTML content
with requests.Session() as session:
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.93 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8',
        'referer': 'https://www.sec.gov/edgar/search/',
        'Accept-Language': 'en-US,en;q=0.5'
    })
    response = session.get(url)
    response.raise_for_status()


# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the anchor and the first table after the anchor
anchor_tag = soup.find(id=anchor)
first_table = anchor_tag.find_next('table')


