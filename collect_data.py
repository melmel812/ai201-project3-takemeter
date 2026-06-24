"""
collect_data.py — collect r/TrueFilm posts via Arctic Shift (no API key needed)
https://arctic-shift.photon-reddit.com

Setup:   pip install requests pandas
Outputs: truefilm_raw.csv  — unlabeled posts ready for prelabel.py
"""

import time
import requests
import pandas as pd

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "TakeMeter-AI201-project/1.0"}

rows = []
seen_ids = set()


def add(text, url):
    text = text.strip()
    if len(text) < 200 or url in seen_ids:
        return False
    seen_ids.add(url)
    rows.append({"text": text[:1500], "label": "", "source_url": url, "annotation_notes": ""})
    return True


def fetch(endpoint, params):
    try:
        r = requests.get(f"{BASE}/{endpoint}", headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("data") or []
    except Exception as e:
        print(f"  request error: {e}")
        return []


def scrape_posts(after_ts, before_ts, min_score=5):
    """Collect self-posts in a time window, paginating until window is exhausted."""
    cursor = after_ts
    batch_count = 0
    while cursor < before_ts:
        data = fetch("posts/search", {
            "subreddit": "TrueFilm",
            "after": int(cursor),
            "before": int(before_ts),
            "sort": "asc",
            "limit": 100,
        })
        if not data:
            break
        for p in data:
            if not p.get("is_self") or not p.get("selftext"):
                continue
            if (p.get("score") or 0) < min_score:
                continue
            text = p["title"] + "\n\n" + p["selftext"]
            add(text, "https://reddit.com" + p["permalink"])
        cursor = data[-1].get("created_utc") or data[-1].get("created") or before_ts
        batch_count += 1
        if batch_count >= 4:   # max 400 posts per window to stay polite
            break
        time.sleep(0.8)


def scrape_comments(after_ts, before_ts, min_score=3):
    """Collect comments — richer source of reaction and short opinion posts."""
    cursor = after_ts
    batch_count = 0
    while cursor < before_ts:
        data = fetch("comments/search", {
            "subreddit": "TrueFilm",
            "after": int(cursor),
            "before": int(before_ts),
            "sort": "asc",
            "limit": 100,
        })
        if not data:
            break
        for c in data:
            body = (c.get("body") or "").strip()
            if (c.get("score") or 0) < min_score:
                continue
            permalink = "https://reddit.com" + c.get("permalink", "")
            add(body, permalink)
        cursor = data[-1].get("created_utc") or data[-1].get("created") or before_ts
        batch_count += 1
        if batch_count >= 3:
            break
        time.sleep(0.8)


# ── Time windows (Unix timestamps) ────────────────────────────────────────────
# Six yearly windows gives variety in films discussed and writing styles.
WINDOWS = [
    (1514764800, 1546300800),   # 2018
    (1546300800, 1577836800),   # 2019
    (1577836800, 1609459200),   # 2020
    (1609459200, 1640995200),   # 2021
    (1640995200, 1672531200),   # 2022
    (1672531200, 1704067200),   # 2023
    (1704067200, 1735689600),   # 2024
]

print("Collecting self-posts (min score 5)...")
for after, before in WINDOWS:
    before_count = len(rows)
    scrape_posts(after, before, min_score=5)
    print(f"  {after//31557600 + 1970 - 1}: +{len(rows) - before_count} posts  (total {len(rows)})")

print("\nCollecting comments (min score 3) — good source of reaction posts...")
for after, before in WINDOWS[2:]:   # 2020-onward; older comments are sparser
    before_count = len(rows)
    scrape_comments(after, before, min_score=3)
    print(f"  {after//31557600 + 1970 - 1}: +{len(rows) - before_count} comments  (total {len(rows)})")

# ── Save ───────────────────────────────────────────────────────────────────────
df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv("truefilm_raw.csv", index=False)
print(f"\nSaved {len(df)} examples to truefilm_raw.csv")
print("Run: python prelabel.py")
