
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from tqdm import tqdm
import time

BASE = "https://www.imsasrl.it"
OUTFILE = "pages.json"
VISITED = set()

def clean_text(soup):

for tag in soup(["script","style","noscript","footer","header","nav"]):
    tag.decompose()
text = soup.get_text(separator="\n")
lines = [l.strip() for l in text.splitlines()]
lines = [l for l in lines if l]
return "\n".join(lines)
def crawl(start=BASE, max_pages=500, delay=0.2):

to_visit = {start}
pages = []
while to_visit and len(pages) < max_pages:
    url = to_visit.pop()
    if url in VISITED: continue
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"IMSA-Chatbot-Bot/1.0"})
        if r.status_code != 200:
            print("skipping", url, "status", r.status_code)
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        text = clean_text(soup)
        pages.append({"url": url, "title": title, "text": text})
        VISITED.add(url)
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            parsed = urlparse(href)
            if parsed.netloc == urlparse(BASE).netloc:
                if parsed.scheme in ["http","https"]:
                    to_visit.add(href.split("#")[0])
        time.sleep(delay)
    except Exception as e:
        print("err", url, e)
with open(OUTFILE, "w", encoding="utf-8") as f:
    json.dump(pages, f, ensure_ascii=False, indent=2)
print(f"Saved {len(pages)} pages to {OUTFILE}")
if name == "main":

crawl()
