#!/usr/bin/env python3
"""
NEXUS Portfolio — Image Generator
=================================
Generates all site imagery (avatar, hero background, OG cover,
project covers, favicon) with Pillow: dark luxury aesthetic,
neon blue accents, soft glows, dot grids and particles.

Output: ../assets/img/ (WebP primary + JPEG fallback where needed)

Usage:  python3 generate_images.py
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

# ──────────────────────────────────────────────────────────────────────────
# PATHS & FONTS
# ──────────────────────────────────────────────────────────────────────────
HERE   = os.path.dirname(os.path.abspath(__file__))
OUT    = os.path.join(HERE, "..", "assets", "img")
os.makedirs(OUT, exist_ok=True)

F_BOLD = "/system/fonts/DroidSans-Bold.ttf"
F_SEMI = "/system/fonts/SourceSansPro-SemiBold.ttf"
F_REG  = "/system/fonts/SourceSansPro-Regular.ttf"
F_MONO = "/system/fonts/CutiveMono.ttf"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# ──────────────────────────────────────────────────────────────────────────
# PALETTE
# ──────────────────────────────────────────────────────────────────────────
BG_TOP    = (7, 8, 14)      # #07080e
BG_BOT    = (4, 5, 9)       # #040509
NEON      = (94, 143, 255)  # #5e8fff  electric blue
NEON_SOFT = (120, 164, 255)
CYAN      = (56, 214, 255)  # #38d6ff
VIOLET    = (138, 92, 246)
TEAL      = (45, 212, 191)
INK       = (240, 246, 255) # near-white text

# ──────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────
def base(w, h):
    """Vertical gradient canvas."""
    img = Image.new("RGB", (w, h))
    px  = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img.convert("RGBA")

def radial_glow(img, cx, cy, radius, color, alpha=1.0):
    """Soft radial glow blob (proper radial-gradient + blur + composite)."""
    r = int(radius)
    size = r * 2
    # 1) radial alpha gradient (bright core, smooth falloff)
    grad = Image.new("L", (size, size), 0)
    gd = ImageDraw.Draw(grad)
    for i in range(r, 0, -4):
        a = int(255 * (1 - i / r) ** 1.5)
        gd.ellipse([r - i, r - i, r + i, r + i], fill=a)
    grad = grad.filter(ImageFilter.GaussianBlur(max(6, r * 0.16)))
    # 2) place on a full-canvas alpha mask
    alpha_canvas = Image.new("L", img.size, 0)
    alpha_canvas.paste(grad, (int(cx - r), int(cy - r)))
    alpha_canvas = alpha_canvas.point(lambda v: int(v * alpha))
    # 3) tint + composite
    layer = Image.new("RGBA", img.size, color + (0,))
    layer.putalpha(alpha_canvas)
    img.alpha_composite(layer)

def grid(img, spacing=44, color=(120, 150, 220), alpha=0.05):
    """Faint dot grid."""
    d = ImageDraw.Draw(img)
    w, h = img.size
    for x in range(0, w, spacing):
        for y in range(0, h, spacing):
            if random.random() < 0.55:
                d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=color + (int(alpha * 255),))

def particles(img, n, colors, size_range=(1, 3), alpha_range=(0.08, 0.5), seed=None):
    """Random particles with glow for the brighter ones."""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        s = rnd.uniform(*size_range)
        c = rnd.choice(colors)
        a = int(rnd.uniform(*alpha_range) * 255)
        d.ellipse([x - s, y - s, x + s, y + s], fill=c + (a,))
        if s > 2.2 and rnd.random() < 0.5:
            d.ellipse([x - s * 2.4, y - s * 2.4, x + s * 2.4, y + s * 2.4], fill=c + (a // 6,))

def vignette(img, strength=110, spread=0.62):
    """Darken edges with a soft radial mask (transparent centre)."""
    w, h = img.size
    cx, cy = w / 2, h / 2
    inner = math.hypot(cx, cy) * spread
    mask = Image.new("L", (w, h), 255)
    dm = ImageDraw.Draw(mask)
    dm.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(inner * 0.35))
    mask = mask.point(lambda v: int(v * strength / 255))  # max darkness = strength
    black = Image.new("RGB", img.size, (0, 0, 0))
    out = img.copy()
    out.paste(black, (0, 0), mask)
    return out

def text_ls(d, xy, s, fnt, fill, tracking=0, anchor="la"):
    """Draw text with manual letter-spacing (tracking in px)."""
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=fnt, fill=fill, anchor=anchor)
        x += d.textlength(ch, font=fnt) + tracking

def text_width(d, s, fnt, tracking=0):
    return sum(d.textlength(ch, font=fnt) for ch in s) + tracking * max(0, len(s) - 1)

def centered_ls(d, cx, y, s, fnt, fill, tracking=0):
    w = text_width(d, s, fnt, tracking)
    text_ls(d, (cx - w / 2, y), s, fnt, fill, tracking)

def save(img, name, webp_quality=82, jpg=False, jpg_quality=84):
    img = img.convert("RGB")
    img.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=webp_quality, method=6)
    if jpg:
        img.save(os.path.join(OUT, name + ".jpg"), "JPEG", quality=jpg_quality, optimize=True)
    print(f"  ✓ {name}.webp" + (" + .jpg" if jpg else ""))

# ──────────────────────────────────────────────────────────────────────────
# 1. AVATAR  (512×512)
# ──────────────────────────────────────────────────────────────────────────
def make_avatar():
    S = 512
    img = base(S, S)
    radial_glow(img, S * 0.5, S * 0.42, S * 0.5, NEON, 0.35)
    radial_glow(img, S * 0.82, S * 0.2, S * 0.24, CYAN, 0.20)
    grid(img, 34, (130, 160, 230), 0.05)
    particles(img, 46, [NEON, CYAN, (200, 214, 255)], (1, 2.6), (0.1, 0.5), seed=7)
    vignette(img, 90)

    d = ImageDraw.Draw(img)
    cx = cy = S / 2
    # outer glass ring (double stroke + glow)
    for r, wdt, col, al in [(168, 14, NEON, 60), (162, 4, (150, 180, 255), 200), (150, 2, NEON, 255)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col + (al,), width=wdt)
    # inner faint fill
    d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(13, 17, 30, 120))
    # N monogram with glow
    f_big = font(F_BOLD, 210)
    f_sm  = font(F_MONO, 26)
    n_txt = "N"
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow_layer)
    dg.text((cx, cy), n_txt, font=f_big, fill=NEON + (255,), anchor="mm")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(glow_layer)
    d.text((cx, cy), n_txt, font=f_big, fill=(236, 244, 255), anchor="mm")
    # underline tick
    d.line([cx - 62, cy + 128, cx + 62, cy + 128], fill=NEON + (255,), width=3)
    d.line([cx - 62, cy + 134, cx - 20, cy + 134], fill=CYAN + (255,), width=3)
    text_ls(d, (cx, cy + 168), "NEXUS", f_sm, (170, 190, 230, 230), tracking=8, anchor="mm")
    save(img, "avatar", jpg=True)

# ──────────────────────────────────────────────────────────────────────────
# 2. HERO BACKGROUND  (1920×1080)
# ──────────────────────────────────────────────────────────────────────────
def make_hero():
    W, H = 1920, 1080
    img = base(W, H)
    radial_glow(img, W * 0.18, H * 0.22, H * 0.55, NEON, 0.45)
    radial_glow(img, W * 0.86, H * 0.75, H * 0.62, CYAN, 0.26)
    radial_glow(img, W * 0.55, H * 0.1, H * 0.35, VIOLET, 0.20)
    grid(img, 52, (130, 160, 230), 0.045)
    particles(img, 130, [NEON, CYAN, (210, 225, 255)], (1, 3), (0.08, 0.45), seed=21)
    # faint horizon line
    d = ImageDraw.Draw(img)
    d.line([(0, H * 0.94), (W, H * 0.94)], fill=(140, 170, 255, 28), width=2)
    img = vignette(img, 120)
    save(img, "hero-bg", jpg=True)

# ──────────────────────────────────────────────────────────────────────────
# 3. OG COVER  (1200×630)
# ──────────────────────────────────────────────────────────────────────────
def make_og():
    W, H = 1200, 630
    img = base(W, H)
    radial_glow(img, W * 0.22, H * 0.28, H * 0.7, NEON, 0.48)
    radial_glow(img, W * 0.84, H * 0.72, H * 0.66, CYAN, 0.26)
    grid(img, 48, (130, 160, 230), 0.05)
    particles(img, 90, [NEON, CYAN, (210, 225, 255)], (1, 2.6), (0.1, 0.5), seed=5)
    img = vignette(img, 100)

    d = ImageDraw.Draw(img)
    f_ov = font(F_MONO, 30)
    f_h1 = font(F_BOLD, 148)
    f_sub = font(F_SEMI, 34)
    f_tag = font(F_REG, 26)

    text_ls(d, (W/2, 168), "//  DEVELOPER  ·  CREATOR  ·  INNOVATOR", f_ov, (130, 165, 235, 255), tracking=6, anchor="mm")
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow_layer)
    dg.text((W/2, 316), "NEXUS", font=f_h1, fill=NEON + (255,), anchor="mm")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(glow_layer)
    d.text((W/2, 316), "NEXUS", font=f_h1, fill=(240, 246, 255), anchor="mm")
    d.line([W/2 - 260, 402, W/2 + 260, 402], fill=NEON + (255,), width=3)
    d.line([W/2 - 260, 410, W/2 - 160, 410], fill=CYAN + (255,), width=3)

    text_ls(d, (W/2, 462), "PORTFOLIO  ·  BANGLADESH  🇧🇩", f_sub, (176, 194, 232, 255), tracking=5, anchor="mm")
    text_ls(d, (W/2, 512), "@nexus_pro_dev", f_tag, (120, 140, 185, 255), tracking=3, anchor="mm")
    save(img, "og-cover")

# ──────────────────────────────────────────────────────────────────────────
# 4. PROJECT COVERS  (800×500)
# ──────────────────────────────────────────────────────────────────────────
PROJECTS = [
    dict(file="project-1", name="NEXUS BOT SUITE", cat="TELEGRAM PLATFORM", num="01",
         hue=NEON, hue2=CYAN,
         art="nodes"),     # hexagonal node network
    dict(file="project-2", name="GUILD GLORY ENGINE", cat="AUTOMATION CORE", num="02",
         hue=(138, 92, 246), hue2=(94, 143, 255),
         art="crown"),     # crown + rising bars
    dict(file="project-3", name="NEXUS SPAM ROOM", cat="REAL-TIME ROOM OPS", num="03",
         hue=CYAN, hue2=(94, 143, 255),
         art="radar"),     # radar rings + pulse
    dict(file="project-4", name="WEB SCRAPER SUITE", cat="DATA INFRASTRUCTURE", num="04",
         hue=(45, 212, 191), hue2=(94, 143, 255),
         art="globe"),     # globe arcs + nodes
    dict(file="project-5", name="ENCRYPTION TOOLKIT", cat="PROTOBUF · AES", num="05",
         hue=(255, 122, 89), hue2=(94, 143, 255),
         art="lock"),      # padlock + key line
    dict(file="project-6", name="UPTIME MONITOR", cat="24/7 OBSERVABILITY", num="06",
         hue=(120, 164, 255), hue2=CYAN,
         art="pulse"),     # heartbeat line
]

def draw_art(img, art, cx, cy, hue, hue2):
    d = ImageDraw.Draw(img)
    if art == "nodes":
        pts = [(cx, cy - 70), (cx + 60, cy - 35), (cx + 60, cy + 35), (cx, cy + 70),
               (cx - 60, cy + 35), (cx - 60, cy - 35)]
        d.polygon(pts, outline=hue + (255,), width=3)
        for i in range(6):
            a = math.radians(i * 60 + 30)
            x, y = cx + 105 * math.cos(a), cy + 105 * math.sin(a)
            d.line([pts[i], (x, y)], fill=hue + (120,), width=2)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=hue2 + (255,))
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(240, 246, 255, 255))
    elif art == "crown":
        d.polygon([(cx - 80, cy + 45), (cx - 80, cy - 35), (cx - 40, cy + 5), (cx, cy - 55),
                   (cx + 40, cy + 5), (cx + 80, cy - 35), (cx + 80, cy + 45)], fill=hue + (70,), outline=hue + (255,), width=3)
        for i, h in enumerate([70, 110, 150, 110, 70]):
            x0 = cx - 96 + i * 48
            d.rectangle([x0, cy + 58 - h, x0 + 40, cy + 58], outline=hue2 + (255,), width=3)
    elif art == "radar":
        for r in (40, 80, 120, 155):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=hue + (120,), width=2)
        d.line([(cx - 155, cy), (cx + 155, cy)], fill=hue + (90,), width=1)
        d.line([(cx, cy - 155), (cx, cy + 155)], fill=hue + (90,), width=1)
        for a in (35, 145, 250):
            x, y = cx + 150 * math.cos(math.radians(a)), cy + 150 * math.sin(math.radians(a))
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=hue2 + (255,))
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=hue2 + (255,))
    elif art == "globe":
        for r, aa in ((75, 0.85), (110, 0.5)):
            for off in (-34, 0, 34):
                d.ellipse([cx - r, cy - r + off, cx + r, cy + r + off], outline=hue + (int(200 * aa),), width=2)
        d.line([(cx - 110, cy), (cx + 110, cy)], fill=hue + (140,), width=1)
        for a in (20, 80, 160, 240, 300):
            x, y = cx + 130 * math.cos(math.radians(a)), cy + 130 * math.sin(math.radians(a))
            d.ellipse([x - 3.5, y - 3.5, x + 3.5, y + 3.5], fill=hue2 + (255,))
    elif art == "lock":
        d.rounded_rectangle([cx - 62, cy - 18, cx + 62, cy + 62], radius=16, fill=hue + (60,), outline=hue + (255,), width=3)
        d.arc([cx - 42, cy - 92, cx + 42, cy - 8], 180, 360, fill=hue + (255,), width=6)
        d.ellipse([cx - 7, cy + 10, cx + 7, cy + 24], fill=(240, 246, 255, 255))
        for y in (40, 66):
            d.line([(cx - 30, y), (cx + 30, y)], fill=(240, 246, 255, 110), width=2)
    elif art == "pulse":
        pts = []
        for i in range(120):
            t = i / 119
            x = cx - 150 + t * 300
            y = cy - 46 + 46 * math.sin(t * math.pi * 5) * math.exp(-abs(t - 0.5) * 3)
            if 0.42 < t < 0.58:
                y = cy - 52 + (abs(t - 0.5) / 0.08) * 70
            pts.append((x, y))
        d.line(pts, fill=hue + (255,), width=4)
        d.line([(cx + 150, cy + 8), (cx + 176, cy + 8)], fill=hue2 + (255,), width=4)
        d.text((cx + 186, cy - 2), "99.98%", font=font(F_MONO, 24), fill=hue2 + (255,), anchor="lm")

def make_projects():
    for p in PROJECTS:
        W, H = 800, 500
        img = base(W, H)
        radial_glow(img, W * 0.78, H * 0.22, H * 0.55, p["hue"], 0.28)
        radial_glow(img, W * 0.16, H * 0.85, H * 0.5, p["hue2"], 0.16)
        grid(img, 40, (130, 160, 230), 0.05)
        particles(img, 40, [p["hue"], p["hue2"], (210, 225, 255)], (1, 2.2), (0.1, 0.45), seed=hash(p["file"]) % 999)
        img = vignette(img, 90)
        d = ImageDraw.Draw(img)

        draw_art(img, p["art"], W * 0.74, H * 0.46, p["hue"], p["hue2"])

        f_num = font(F_BOLD, 130)
        f_nm  = font(F_BOLD, 42)
        f_cat = font(F_MONO, 22)
        f_wm  = font(F_MONO, 18)

        d.text((W - 54, 46), p["num"], font=f_num, fill=(255, 255, 255, 26), anchor="ra")
        d.line([(54, H - 118), (300, H - 118)], fill=p["hue"] + (255,), width=4)
        d.line([(54, H - 110), (140, H - 110)], fill=p["hue2"] + (255,), width=4)
        d.text((54, H - 96), p["name"], font=f_nm, fill=(236, 244, 255, 255), anchor="lm")
        d.text((56, H - 46), p["cat"], font=f_cat, fill=(150, 175, 225, 255), anchor="lm")
        d.text((W - 40, H - 36), "NEXUS//PROJECT", font=f_wm, fill=(130, 155, 210, 120), anchor="rm")
        save(img, p["file"], jpg=True)

# ──────────────────────────────────────────────────────────────────────────
# 5. FAVICON (256 PNG + SVG)
# ──────────────────────────────────────────────────────────────────────────
def make_favicon():
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([8, 8, S - 8, S - 8], radius=52, fill=(7, 8, 14, 255))
    glow_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow_layer)
    f = font(F_BOLD, 148)
    dg.text((S/2, S/2 + 6), "N", font=f, fill=NEON + (255,), anchor="mm")
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(glow_layer)
    d.text((S/2, S/2 + 6), "N", font=f, fill=(238, 245, 255, 255), anchor="mm")
    d.ellipse([S - 64, 40, S - 40, 64], fill=CYAN + (255,))
    img.save(os.path.join(OUT, "favicon.png"))
    print("  ✓ favicon.png")
    with open(os.path.join(OUT, "favicon.svg"), "w") as fh:
        fh.write(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<rect x="2" y="2" width="60" height="60" rx="13" fill="#07080e"/>'
            '<text x="32" y="45" font-family="Arial, sans-serif" font-size="40" font-weight="700" '
            'fill="#eef5ff" text-anchor="middle">N</text>'
            '<circle cx="54" cy="14" r="5" fill="#38d6ff"/></svg>'
        )
    print("  ✓ favicon.svg")

# ──────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("NEXUS Portfolio — generating imagery…")
    make_avatar()
    make_hero()
    make_og()
    make_projects()
    make_favicon()
    print("Done →", os.path.abspath(OUT))
