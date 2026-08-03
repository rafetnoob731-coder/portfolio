#!/usr/bin/env python3
"""
Brave Search — CLI scraper for search.brave.com
===============================================
No API key needed. Uses the public search page with a mobile browser
header set (Brave blocks bare requests, so the full header set matters).

  python3 brave_search.py "free fire ob54 patch notes"
  python3 brave_search.py "python asyncio docs" --count 10
  python3 brave_search.py "any query" --json
"""
import argparse
import html as html_mod
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://search.brave.com/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "Upgrade-Insecure-Requests": "1",
}

try:
    _COLOR = sys.stdout.isatty()
except Exception:
    _COLOR = False

def c(text, code):
    return f"\033[{code}m{text}\033[0m" if _COLOR else text

def clean(s):
    s = html_mod.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def fetch(query, timeout):
    url = BASE + "?" + urllib.parse.urlencode({"q": query, "source": "android"})
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        print(c(f"✗ HTTP {e.code}", "91"), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(c(f"✗ Network error: {e.reason}", "91"), file=sys.stderr)
        sys.exit(1)

def parse(html_text):
    """Extract organic results from Brave's HTML."""
    results, seen = [], set()

    # split on result anchors
    parts = re.split(r'data-pos="\d+"', html_text)
    for part in parts[1:]:
        m_title = re.search(r'class="title search-snippet-title[^"]*"\s+title="([^"]+)"', part)
        m_url = re.search(r'<a href="(https?://[^"]+)"', part)
        if not m_title or not m_url:
            continue
        url = m_url.group(1)
        if url in seen or "brave.com" in url:
            continue
        seen.add(url)

        m_desc = re.search(r'generic-snippet[^>]*>(.*?)(?:<div class="snippet|$)', part, re.S)
        results.append({
            "position": len(results) + 1,
            "title": clean(m_title.group(1)),
            "url": url,
            "snippet": clean(m_desc.group(1)) if m_desc else "",
        })
        if len(results) >= 60:
            break
    return results

def main():
    p = argparse.ArgumentParser(description="Brave search scraper CLI")
    p.add_argument("query", help="search query (quoted)")
    p.add_argument("--count", type=int, default=10, help="max results (default 10)")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--timeout", type=int, default=25)
    args = p.parse_args()

    html_text = fetch(args.query, args.timeout)
    if len(html_text) < 2000:
        print(c("✗ Empty/blocked response — Brave may be rate-limiting. Try again shortly.", "91"), file=sys.stderr)
        sys.exit(1)

    results = parse(html_text)[:args.count]
    if args.json:
        print(json.dumps({"query": args.query, "engine": "brave", "results": results},
                         indent=2, ensure_ascii=False))
        return

    if not results:
        print(c("✗ No results parsed.", "91"), file=sys.stderr)
        sys.exit(1)

    print(c(f"  BRAVE  ·  “{args.query}”  ·  {len(results)} results", "36"))
    print(c("  " + "─" * 60, "90"))
    for r in results:
        print(f"{c(str(r['position']).rjust(3), '33')}  {c(r['title'], '1;97')}")
        print(f"      {c(r['url'], '34')}")
        if r["snippet"]:
            print(f"      {r['snippet'][:220]}{'…' if len(r['snippet']) > 220 else ''}")
        print()

if __name__ == "__main__":
    main()
