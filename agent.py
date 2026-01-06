import cloudscraper
import time
from bs4 import BeautifulSoup
from sources import SOURCES
from filters import is_eligible
from datetime import datetime
import json

STORAGE_FILE = "storage.json"
REMINDER_DAYS = [14, 7, 3]


def load_storage():
    try:
        with open(STORAGE_FILE) as f:
            return json.load(f)
    except:
        return {}


def save_storage(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def scrape_text(url):
    # 1. Create a scraper that mimics a desktop Chrome browser
    # This automatically handles Cloudflare challenges that caused the 403 errors
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    try:
        # 2. Use the scraper with a 30s timeout (increased from 15s/20s)
        # We don't need to manually set User-Agent headers; cloudscraper does it.
        r = scraper.get(url, timeout=60)
        
        # Check for HTTP errors (403, 404, 500)
        if r.status_code != 200:
            print(f"Warning: Failed to fetch {url}. Status code: {r.status_code}")
            return ""
        
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator=" ").lower()
    
    except Exception as e:
        # Just print a one-line warning instead of the full error
        print(f"  [!] Skipped {url} (Connection error or timeout)")
        return ""# Return empty string so the agent keeps running


def days_to_deadline(deadline):
    # Added error handling in case date format is wrong in storage
    try:
        d = datetime.strptime(deadline, "%Y-%m-%d")
        return (d - datetime.today()).days
    except ValueError:
        return -1 # Return invalid day count if parsing fails


def load_applied():
    try:
        with open("applied.txt") as f:
            return set(line.strip() for line in f)
    except:
        return set()


def run_agent():
    storage = load_storage()
    applied = load_applied()

    new_items = []
    reminders = []

    for src in SOURCES:
        print(f"Checking {src['name']}...") # Progress log
        
        # 3. Add a polite delay (2 seconds) to avoid network congestion/timeouts
        time.sleep(2)
        
        text = scrape_text(src["url"])

        # If scraping failed (text is empty), skip to next source
        if not text:
            continue

        if not is_eligible(text):
            continue

        if src["url"] not in storage:
            storage[src["url"]] = {
                "name": src["name"],
                "deadline": "2026-12-31",  # default if not parsed
                "applied": False
            }
            new_items.append(src)

        else:
            item = storage[src["url"]]
            if not item["applied"]:
                days = days_to_deadline(item["deadline"])
                if days in REMINDER_DAYS:
                    reminders.append({
                        "name": item["name"],
                        "url": src["url"],
                        "days": days
                    })

        if src["url"] in applied:
            storage[src["url"]]["applied"] = True

    save_storage(storage)
    return new_items, reminders