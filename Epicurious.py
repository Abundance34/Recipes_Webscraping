import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
import os
import re
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode
from urllib.robotparser import RobotFileParser
from abc import ABC, abstractmethod

# ---------------------------
# Configuration
# ---------------------------

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; RecipeScraper/1.0; +https://yourdomain.com/bot)'
}
PAGES_PER_SITE = 10
DELAY_MIN, DELAY_MAX = 1, 3
OUTPUT_FILE = 'Epicurious_dataset.jsonl'  # ✅ Save in script's working directory

# ---------------------------
# Logging setup
# ---------------------------

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------
# Utility functions
# ---------------------------

def get_crawl_delay(base_url):
    """Fetch and parse robots.txt; return crawl-delay in seconds or None."""
    rp = RobotFileParser()
    robots_url = base_url.rstrip('/') + '/robots.txt'
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.crawl_delay('*')
    except Exception as e:
        logger.debug(f"Could not parse robots.txt at {robots_url}: {e}")
        return None

def canonicalize_url(raw_url):
    """
    Strip only tracking query params (utm_*, fbclid, etc.) and return a normalized URL.
    """
    parsed = urlparse(raw_url)
    qs = parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k,v) for k,v in qs if not re.match(r'^(utm_|fbclid)', k)]
    new_query = urlencode(filtered)
    return urlunparse(parsed._replace(query=new_query))

def fetch_soup(session, url, timeout=10):
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')

def find_recipes_in_jsonld(data):
    found = []
    if isinstance(data, dict):
        types = data.get('@type', [])
        if (isinstance(types, list) and 'Recipe' in types) or types == 'Recipe':
            found.append(data)
        for v in data.values():
            found += find_recipes_in_jsonld(v)
    elif isinstance(data, list):
        for item in data:
            found += find_recipes_in_jsonld(item)
    return found

def extract_jsonld_recipe(soup):
    for script in soup.find_all('script', type='application/ld+json'):
        raw = script.string or script.get_text()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        recipes = find_recipes_in_jsonld(data)
        if recipes:
            return recipes[0]
    return {}

def flatten_instructions(instr):
    """
    Given recipeInstructions (which can be str, dicts, lists, HowToSection, etc),
    return a flat list of text steps.
    """
    steps = []
    if isinstance(instr, str):
        steps.append(instr)
    elif isinstance(instr, dict):
        # If it's a HowToSection, it may have an "itemListElement"
        if 'itemListElement' in instr:
            steps += flatten_instructions(instr['itemListElement'])
        elif 'text' in instr:
            steps.append(instr['text'])
    elif isinstance(instr, list):
        for item in instr:
            steps += flatten_instructions(item)
    return steps

# ---------------------------
# Site abstraction
# ---------------------------

class SiteScraper(ABC):
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = get_crawl_delay(self.base_url) or DELAY_MIN

    @abstractmethod
    def collect_recipe_urls(self):
        """Return a set of canonical recipe URLs to scrape."""
        pass

    @abstractmethod
    def extract_comments(self, soup):
        """Return a list of {author, text} from the soup."""
        pass

    def scrape(self):
        logger.info(f"→ collecting URLs from {self.base_url}…")
        urls = self.collect_recipe_urls()
        logger.info(f"   found {len(urls)} recipes on {self.base_url}")
        for url in urls:
            try:
                soup = fetch_soup(self.session, url)
                data = extract_jsonld_recipe(soup)
                if not data:
                    logger.debug(f"[{self.base_url}] no JSON-LD recipe on {url}")
                    continue

                rec = {
                    'source':       self.base_url,
                    'url':          url,
                    'title':        data.get('name'),
                    'ingredients':  data.get('recipeIngredient', []),
                    'instructions': flatten_instructions(data.get('recipeInstructions', [])),
                    'comments':     self.extract_comments(soup)
                }
                yield rec

            except requests.RequestException as e:
                logger.warning(f"[{self.base_url}] network error fetching {url}: {e}")
            except Exception as e:
                logger.error(f"[{self.base_url}] unexpected error on {url}: {e}")
            time.sleep(random.uniform(self.delay, DELAY_MAX))


# ---------------------------
# Concrete site scrapers
# ---------------------------


class Epicurious(SiteScraper):
    def __init__(self):
        super().__init__('https://www.epicurious.com')

    def collect_recipe_urls(self):
        urls = set()
        for p in range(1, PAGES_PER_SITE+1):
            soup = fetch_soup(self.session, f'{self.base_url}/search?content=recipe&page={p}')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/recipes/') or '/recipes/' in href:
                    full = self.base_url + href.split('?')[0]
                    urls.add(canonicalize_url(full))
            time.sleep(random.uniform(self.delay, DELAY_MAX))
        return urls

    def extract_comments(self, soup):
        comments = []
        for div in soup.select('div.reviews__review'):
            author = div.select_one('a.reviews__reviewer')
            text   = div.select_one('p.reviews__review-text')
            if author and text:
                comments.append({
                    'author': author.get_text(strip=True),
                    'text':   text.get_text(strip=True)
                })
        return comments


# ---------------------------
# Main runner
# ---------------------------

if __name__ == '__main__':
    scrapers = [
        Epicurious(),

    ]

    logger.info(f"📁 Will save recipes to: {os.path.abspath(OUTPUT_FILE)}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        total = 0
        for scraper in scrapers:
            for record in scraper.scrape():
                fout.write(json.dumps(record, ensure_ascii=False) + '\n')
                total += 1
                # Optional: Flush buffer after each write for real-time inspection
                fout.flush()

logger.info(f"\n✅ Done! Saved {total} recipes to {OUTPUT_FILE}")
