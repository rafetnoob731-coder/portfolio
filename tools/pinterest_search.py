#!/usr/bin/env python3
"""
Pinterest Search — CLI scraper for pinterest.com (search & ideas pages)
=====================================================================
Extracts real pins (title/description, image URLs, pin links, source
links) from the embedded page data. Works without login from mobile UA.

  python3 pinterest_search.py "gaming dashboard dark" --count 8
  python3 pinterest_search.py "free fire ui" --json
"""
import argparse
import html as html_mod
import json
import re
import sys
import urllib.parse
import urllib.request

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
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def fetch(url, timeout):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        print(c(f"✗ HTTP {e.code}", "91"), file=sys.stderr); sys.exit(1)
    except urllib.error.URLError as e:
        print(c(f"✗ Network: {e.reason}", "91"), file=sys.stderr); sys.exit(1)

def biggest_image(pin):
    """pick the largest image url from a pin's images dict."""
    best, bs = None, 0
    for variant in (pin.get("images") or {}).values():
        url = (variant or {}).get("url")
        if not url:
            continue
        size = (variant.get("width") or 0) * (variant.get("height") or 0)
        if size > bs:
            bs, best = size, url
    return best

def parse_pws(html_text):
    """parse pins from Pinterest's embedded __PWS_DATA__ JSON blob."""
    m = re.search(r'<script id="__PWS_DATA__"[^>]*>(.*?)</script>', html_text, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except Exception:
        return []
    pins = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "pin" and node.get("id"):
                desc = node.get("description") or node.get("title") or ""
                src = node.get("link") or ""
                if src.startswith("/"):
                    src = "https://www.pinterest.com" + src
                img = biggest_image(node)
                pins.append({
                    "id": node["id"],
                    "description": clean(desc),
                    "image": img,
                    "source": src,
                    "pin_url": f"https://www.pinterest.com/pin/{node['id']}/",
                })
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for key in ("resource_data_cache", "initial_pin_data", "resources", "data"):
        if key in data:
            walk(data[key])
            if pins:
                break
    return pins

def parse_loose(html_text):
    """fallback: regex extraction (alt texts + image urls + pin ids)."""
    ids = re.findall(r'href="/pin/(\d{10,20})/"', html_text)
    imgs = re.findall(r'(https://i\.pinimg\.com/(?:originals|474x)/[^"\s\)\}]+)', html_text)
    alts = re.findall(r'alt="([^"]{8,200})"', html_text)
    pins, seen = [], set()
    for i, pid in enumerate(ids):
        if pid in seen:
            continue
        seen.add(pid)
        desc = clean(alts[i]) if i < len(alts) else ""
        pins.append({
            "id": pid,
            "description": desc,
            "image": imgs[i] if i < len(imgs) else None,
            "source": "",
            "pin_url": f"https://www.pinterest.com/pin/{pid}/",
        })
    return pins

def search(query, count, timeout):
    url = "https://www.pinterest.com/search/pins/?" + urllib.parse.urlencode({"q": query})
    html_text = fetch(url, timeout)
    pins = parse_pws(html_text) or parse_loose(html_text)
    return pins[:count]

def main():
    p = argparse.ArgumentParser(description="Pinterest pin scraper CLI")
    p.add_argument("query", help="search query (quoted)")
    p.add_argument("--count", type=int, default=8, help="max pins (default 8)")
    p.add_argument("--json", action="store_true", help="print raw JSON")
    p.add_argument("--timeout", type=int, default=25)
    args = p.parse_args()

    pins = search(args.query, args.count, args.timeout)
    if args.json:
        print(json.dumps({"query": args.query, "engine": "pinterest", "results": pins},
                         indent=2, ensure_ascii=False))
        return

    if not pins:
        print(c("✗ No pins parsed.", "91"), file=sys.stderr)
        sys.exit(1)

    print(c(f"  PINTEREST  ·  “{args.query}”  ·  {len(pins)} pins", "36"))
    print(c("  " + "─" * 64, "90"))
    for i, pin in enumerate(pins, 1):
        print(f"{c(str(i).rjust(3), '33')}  {c(pin['description'][:90] or '(no description)', '1;97')}")
        if pin["image"]:
            print(f"      img {c(pin['image'][:90], '34')}")
        print(f"      pin {c(pin['pin_url'], '34')}")
        if pin["source"]:
            print(f"      src {c(pin['source'][:90], '36')}")
        print()

if __name__ == "__main__":
    main()
