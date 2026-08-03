#!/usr/bin/env python3
"""
DuckDuckGo Search — CLI scraper for html.duckduckgo.com
=======================================================
Free + unlimited. DDG's JS page redirects bot-ish clients to the
"non-JavaScript site", so we hit the lite endpoint directly
(html.duckduckgo.com/html/), which serves classic parseable HTML.

  python3 ddg_search.py "best portfolio design trends 2026"
  python3 ddg_search.py "css scroll animations examples" --count 8
  python3 ddg_search.py "any query" --json
"""
import argparse
import html as html_mod
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://html.duckduckgo.com/html/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
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

def decode_href(raw):
    """DDG wraps URLs in /l/?uddg=<encoded> — extract the real destination."""
    if "uddg=" in raw:
        return urllib.parse.unquote(raw.split("uddg=")[1].split("&")[0])
    return raw

def fetch(query, timeout):
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode({"q": query}),
                                 headers=HEADERS)
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
    """Extract organic results from DDG lite HTML."""
    results, seen = [], set()
    # each result: <div class="result ..."> ... <a class="result__a" href="...">TITLE</a> ...
    blocks = re.split(r'<div class="result\b', html_text)[1:]
    for block in blocks:
        m_a = re.search(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        m_s = re.search(r'class="result__snippet"[^>]*>(.*?)</(?:a|div|td)>', block, re.S)
        if not m_a:
            continue
        url = decode_href(html_mod.unescape(m_a.group(1)))
        if url in seen or "duckduckgo.com" in url:
            continue
        seen.add(url)
        results.append({
            "position": len(results) + 1,
            "title": clean(m_a.group(2)),
            "url": url,
            "snippet": clean(m_s.group(1)) if m_s else "",
        })
        if len(results) >= 30:
            break
    return results

def main():
    p = argparse.ArgumentParser(description="DuckDuckGo search scraper CLI")
    p.add_argument("query", help="search query (quoted)")
    p.add_argument("--count", type=int, default=10, help="max results (default 10)")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--timeout", type=int, default=25)
    args = p.parse_args()

    html_text = fetch(args.query, args.timeout)
    if len(html_text) < 2000:
        print(c("✗ Empty/blocked response — try again shortly.", "91"), file=sys.stderr)
        sys.exit(1)

    results = parse(html_text)[:args.count]
    if args.json:
        print(json.dumps({"query": args.query, "engine": "duckduckgo",
                          "results": results}, indent=2, ensure_ascii=False))
        return

    if not results:
        print(c("✗ No results parsed.", "91"), file=sys.stderr)
        sys.exit(1)

    print(c(f"  DUCKDUCKGO  ·  “{args.query}”  ·  {len(results)} results", "36"))
    print(c("  " + "─" * 60, "90"))
    for r in results:
        print(f"{c(str(r['position']).rjust(3), '33')}  {c(r['title'], '1;97')}")
        print(f"      {c(r['url'], '34')}")
        if r["snippet"]:
            print(f"      {r['snippet'][:220]}{'…' if len(r['snippet']) > 220 else ''}")
        print()

if __name__ == "__main__":
    main()
