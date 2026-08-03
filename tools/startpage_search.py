#!/usr/bin/env python3
"""
Startpage Search — CLI scraper for startpage.com/sp/search
==========================================================
⚠️ IMPORTANT: Startpage serves a JS-gate ("jsgate") robot-wall to
non-browser clients (CSS shell + token, no results). This tool
detects that and reports it clearly.

Startpage requires its JavaScript app + anti-bot challenge, so real
scraping needs a browser engine (Playwright/Puppeteer). The privacy
result-set (Google-index) is otherwise reachable via tools/brave_search.py.

  python3 startpage_search.py "your query"
  python3 startpage_search.py "query" --json
"""
import argparse
import html as html_mod
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://www.startpage.com/sp/search"

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

def fetch(query, timeout):
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode({"query": query}),
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

def is_js_gated(html_text):
    return "jsgate" in html_text or ("feedback_form" in html_text and "w-gl__result" not in html_text)

def parse(html_text):
    """Parse static Startpage results (w-gl__result blocks) when served."""
    results, seen = [], set()
    blocks = re.split(r'<div class="w-gl__result', html_text)[1:]
    for block in blocks:
        m_url = re.search(r'href="(https?://[^"]+)"', block)
        m_title = re.search(r'class="w-gl__result-title[^"]*"[^>]*>(.*?)</a>', block, re.S)
        if not m_url:
            continue
        url = m_url.group(1)
        if url in seen or "startpage.com" in url:
            continue
        seen.add(url)
        m_snip = re.search(r'class="w-gl__description"[^>]*>(.*?)</p>', block, re.S)
        results.append({
            "position": len(results) + 1,
            "title": clean(m_title.group(1)) if m_title else "",
            "url": url,
            "snippet": clean(m_snip.group(1)) if m_snip else "",
        })
        if len(results) >= 30:
            break
    return results

def main():
    p = argparse.ArgumentParser(description="Startpage search scraper CLI (JS-gated on most networks)")
    p.add_argument("query", help="search query (quoted)")
    p.add_argument("--count", type=int, default=10, help="max results (default 10)")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--timeout", type=int, default=25)
    args = p.parse_args()

    html_text = fetch(args.query, args.timeout)

    if is_js_gated(html_text):
        print(c("✗ Startpage returned its JS-gate robot wall (no HTML results).", "91"), file=sys.stderr)
        print(c("  Startpage blocks non-browser clients. Use tools/brave_search.py or", "93"), file=sys.stderr)
        print(c("  tools/ddg_search.py instead (same Google-quality coverage).", "93"), file=sys.stderr)
        sys.exit(3)

    results = parse(html_text)[:args.count]
    if args.json:
        print(json.dumps({"query": args.query, "engine": "startpage", "results": results},
                         indent=2, ensure_ascii=False))
        return

    if not results:
        print(c("✗ No results parsed.", "91"), file=sys.stderr)
        sys.exit(1)

    print(c(f"  STARTPAGE  ·  “{args.query}”  ·  {len(results)} results", "36"))
    print(c("  " + "─" * 60, "90"))
    for r in results:
        print(f"{c(str(r['position']).rjust(3), '33')}  {c(r['title'], '1;97')}")
        print(f"      {c(r['url'], '34')}")
        if r["snippet"]:
            print(f"      {r['snippet'][:220]}{'…' if len(r['snippet']) > 220 else ''}")
        print()

if __name__ == "__main__":
    main()
