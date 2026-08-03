#!/usr/bin/env python3
"""
Serpent Search — CLI wrapper for the Serpent API
================================================
Endpoints:
  • Quick Search  → https://apiserpent.com/api/search/quick  (1–100 results)
  • Deep Search   → https://apiserpent.com/api/search        (10–100 results, deep=true)

Auth:  X-API-Key header  (or `api_key` query param)
Key:   read from SERPENT_API_KEY env var, or pass with --key
       (never hardcode the key in scripts/repos!)

Usage:
  python3 serpent_search.py "free fire ob54 patch notes"
  python3 serpent_search.py "python async scraping" --deep --count 10
  python3 serpent_search.py "docker basics" --engine bing --json
  SERPENT_API_KEY=sk_live_... python3 serpent_search.py "question"
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://apiserpent.com/api/search"
QUICK_URL = BASE + "/quick"

try:
    _COLOR = sys.stdout.isatty()
except Exception:
    _COLOR = False

def c(text, code):
    return f"\033[{code}m{text}\033[0m" if _COLOR else text

def api_call(url, key, params, timeout):
    url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-API-Key": key, "User-Agent": "serpent-search-cli/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body).get("message", body)
        except Exception:
            msg = body
        print(c(f"✗ HTTP {e.code}: {msg}", "91"), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(c(f"✗ Network error: {e.reason}", "91"), file=sys.stderr)
        sys.exit(1)

def main():
    p = argparse.ArgumentParser(description="Serpent search API CLI")
    p.add_argument("query", help="search query (quoted)")
    p.add_argument("--deep", action="store_true", help="deep search (more comprehensive)")
    p.add_argument("--count", type=int, default=None, help="number of results (quick: 1–100, deep: 10–100)")
    p.add_argument("--engine", choices=["google", "bing", "yahoo", "duckduckgo"], default="google",
                   help="search engine (default: google)")
    p.add_argument("--country", default=None, help="2-letter country code, e.g. us, bd")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--key", default=os.environ.get("SERPENT_API_KEY"),
                   help="API key (default: $SERPENT_API_KEY)")
    args = p.parse_args()

    if not args.key:
        print(c("✗ No API key. Set SERPENT_API_KEY or pass --key.", "91"), file=sys.stderr)
        sys.exit(2)

    params = {"q": args.query, "engine": args.engine}
    if args.count:
        params["count" if args.deep else "num"] = args.count
    if args.deep:
        params["deep"] = "true"
    if args.country:
        params["country"] = args.country

    url = BASE if args.deep else QUICK_URL
    data = api_call(url, args.key, params, args.timeout)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if not data.get("success"):
        print(c("✗ Search failed.", "91"), file=sys.stderr)
        sys.exit(1)

    organic = (data.get("results") or {}).get("organic", [])
    meta = data.get("results") or {}
    print(c(f"  {meta.get('engine', 'web').upper()}  ·  “{data.get('query')}”  ·  {len(organic)} results", "36"))
    print(c("  " + "─" * 60, "90"))
    for r in organic:
        print(f"{c(str(r.get('position', '?')).rjust(3), '33')}  {c(r.get('title', ''), '1;97')}")
        print(f"      {c(r.get('url', ''), '34')}")
        snip = (r.get("snippet") or "").strip()
        if snip:
            print(f"      {snip[:220]}{'…' if len(snip) > 220 else ''}")
        print()

if __name__ == "__main__":
    main()
