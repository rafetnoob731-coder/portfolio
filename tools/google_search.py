#!/usr/bin/env python3
"""
Google Search — CLI scraper for google.com/search
=================================================
⚠️ IMPORTANT: Google's SERP is JS-gated. Plain HTTP clients get an
"enablejs" retry shell instead of results (this device included).
This tool detects that and reports it clearly.

It works where Google serves static HTML (some regions/networks) —
run it from a PC or different network to try. For reliable Google
results use the Custom Search JSON API (free: 100 queries/day).

  python3 google_search.py "your query"
  python3 google_search.py "query" --count 10 --json
"""
import argparse
import html as html_mod
import json
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://www.google.com/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "CONSENT=YES+cb.20240101-01-p0.en+FX+111; SOCS=CAISHAgBEhJnd3NfMjAyNDAxMDEtMF9SQzIaAmVuIAEaBgiA_LyaBg",
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

def fetch(query, count, timeout):
    params = {"q": query, "hl": "en", "gl": "us", "num": min(count, 100), "ie": "UTF-8"}
    req = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(params), headers=HEADERS)
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
    """Google serves an 'enablejs' shell to non-JS clients."""
    return ("enablejs" in html_text or "retry" in html_text) and "<h3" not in html_text

def parse(html_text):
    """Parse a static Google SERP (h3 titles + /url?q= destinations)."""
    results, seen = [], set()
    # result blocks: each h3 is inside an <a href="/url?q=...">
    blocks = re.split(r'<h3[^>]*>', html_text)[1:]
    for i, block in enumerate(blocks):
        m_url = re.search(r'href="(/url\?q=|https?://)([^"&]+)', block[:3000])
        if not m_url:
            continue
        url = m_url.group(2)
        if url.startswith("http"):
            pass
        else:
            continue
        if url in seen or "google." in url:
            continue
        seen.add(url)
        m_title = re.search(r'</?h3[^>]*>(.*?)</h3>', block, re.S) or re.match(r'(.*?)</h3>', block, re.S)
        m_snip = re.search(r'class="[^"]*(?:VwiC3b|IsZvec|yDYNvb)[^"]*"[^>]*>(.*?)</(?:div|span)>', block, re.S)
        results.append({
            "position": len(results) + 1,
            "title": clean(m_title.group(1) if m_title else ""),
            "url": urllib.parse.unquote(url),
            "snippet": clean(m_snip.group(1)) if m_snip else "",
        })
        if len(results) >= 30:
            break
    return results

def main():
    p = argparse.ArgumentParser(description="Google search scraper CLI (JS-gated on most networks)")
    p.add_argument("query", help="search query (quoted)")
    p.add_argument("--count", type=int, default=10, help="max results (default 10)")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--timeout", type=int, default=25)
    args = p.parse_args()

    html_text = fetch(args.query, args.count, args.timeout)

    if is_js_gated(html_text):
        print(c("✗ Google returned its JS-only shell (no HTML results).", "91"), file=sys.stderr)
        print(c("  Google blocks non-browser clients. Use tools/brave_search.py or", "93"), file=sys.stderr)
        print(c("  tools/ddg_search.py instead, or the Google Custom Search JSON API.", "93"), file=sys.stderr)
        sys.exit(3)

    results = parse(html_text)[:args.count]
    if args.json:
        print(json.dumps({"query": args.query, "engine": "google", "results": results},
                         indent=2, ensure_ascii=False))
        return

    if not results:
        print(c("✗ No results parsed.", "91"), file=sys.stderr)
        sys.exit(1)

    print(c(f"  GOOGLE  ·  “{args.query}”  ·  {len(results)} results", "36"))
    print(c("  " + "─" * 60, "90"))
    for r in results:
        print(f"{c(str(r['position']).rjust(3), '33')}  {c(r['title'], '1;97')}")
        print(f"      {c(r['url'], '34')}")
        if r["snippet"]:
            print(f"      {r['snippet'][:220]}{'…' if len(r['snippet']) > 220 else ''}")
        print()

if __name__ == "__main__":
    main()
