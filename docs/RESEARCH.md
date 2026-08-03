# NEXUS — Design & Coding Research Collection

> Deep-research collection from live sources (searched & fetched, not memory).
> Compiled for future site/project inspiration. Not part of the live site.

---

## 1. Web Design Trends (2026) — *deep-read from Figma / Wix / Elementor*

| # | Trend | Notes | Source |
|---|-------|-------|--------|
| 1 | **3D & immersive elements** | Depth + interaction beyond static images; Nike/IKEA-style virtual try-ons; scroll-triggered 3D scenes | figma.com/resource-library/web-design-trends/ |
| 2 | **Experimental navigation** | Non-standard "Home/About/Contact" — exploration-style layouts, scroll-driven waypoints | same |
| 3 | **Dark mode, gradients, playful motion = baseline** | These are no longer "extras" — they're expected defaults | same |
| 4 | **Moody dark luxury portfolios** | Dark-first with one refined accent; editorial whitespace | envato.com/learn/portfolio-trends |
| 5 | **Gamified portfolios** | XP bars, achievements, level-up reveals, unlock-on-scroll | same |
| 6 | **AI-assisted site UX** | "Ask me" chat widgets; vibe-coded landing pages; AI workflows as a selling point | reallygooddesigns.com, figma.com |

## 2. Color Directions 2026–2027 — *deep-read from We Design Marbella*

**Two moods to pick one dominant + one accent:**

- **Calm, grounded neutrals** (trust/wellness): Cloud Dancer `#F0EEE9`, Mocha Mousse `#A47764`, Warm Beige `#E8DCC8`, Soft Grey `#D9D6D0`, Sand `#E3D5B8`
- **Neons on dark** (tech/gaming/AR/VR): Electric Blue `#00D4FF`, Vivid Purple `#8A2BE2`, Lime Green `#B4FF39` on Charcoal `#1A1A1D` — hero sections, buttons, gradients
- **2027 blue trend** + soft "neutral-plus-accent" for interfaces
- **Rules**: dark mode as a variation, restrained gradients, accessibility first

Source: wedesignmarbella.com/web-design-color-trends-for-2026-2027/

## 3. Animation Trends (2026) — *deep-read from Lummi (full article)*

1. **Stylized 2D animation is booming** — flat/stylized 2D stands out against AI hyperrealism & "animated slop"
2. **Intentional > simple** — subtle grain, motion with purpose, let the design breathe
3. **2D is iteration-friendly** — adjust colors/shapes without rebuilding 3D scenes (agile, social-first)
4. **Animated infographics** — data storytelling as motion
5. **Differentiation is the skill** — AI made animation cheap; taste is the filter

Source: lummi.ai/blog/animation-trends-2026

## 4. Micro-Interactions — *deep-read from vev.design + Awwwards + NN/G*

- Anatomy: **Trigger → Feedback → Loops & Modes** (user- or system-initiated)
- Rule: purpose over decoration — don't take over the design
- Cues: hover/click state changes, visual or audio feedback
- Good patterns: button feedback, load/progress states, success checkmarks, drag/swipe, form micro-cues

Sources: vev.design/blog/micro-interaction-examples/ · awwwards.com · nngroup.com

## 5. Coding Techniques & Libraries

| Idea | Where |
|------|-------|
| Native CSS scroll-driven animations (`animation-timeline: scroll()`) — no JS | freefrontend.com/css-scroll-driven/ |
| 30+ CSS scroll effects snippets | freefrontend.com/css-scroll-effects/ |
| Cinematic section transitions (fullPage-style) | alvarotrigo.com/fullPage/scroll-effects/ |
| WebGL/Three.js portfolio patterns (spatial depth, radial blur) | freefrontend.com/three-js/ (160+ examples) |
| Best Three.js portfolio breakdowns | creativedevjobs.com/blog/best-threejs-portfolio-examples-2025 |
| R3F (React Three Fiber) portfolio lessons | threejs-journey.com |
| UI animation & micro-interaction galleries | awwwards.com (UI Animation category) |

## 6. Image & Asset Sources (free)

- **Dark aesthetic photos**: pexels.com/search/dark-aesthetic/ · unsplash.com/s/photos/dark-aesthetic · pixabay.com (10k+)
- **3D embeds**: spline.design (free scene embeds) · market.pmnd.rs
- **Icons**: Iconify, Lucide, Tabler (tree-shakable, free)
- **Mockups**: Mockup World, ls.graphics, ui8.net freebies
- *(3D/icon/mockup sources from author knowledge — engines were CAPTCHA-blocked at fetch time)*

## 7. Search-Engine Learnings (operational)

- **Brave**: throttles at ~5 rapid queries (HTTP 429) → space 15–30s
- **DuckDuckGo**: escalates to image CAPTCHA after bursts → use lite endpoint, space queries
- **Serpent API**: free tier currently **exhausted** (HTTP 402) — reserved for critical lookups only

## 8. Idea Bank — quick wins for NEXUS site (future, not applied)

- 2D stylized SVG illustration layer on hero (grain + motion)
- Gamified "achievements" strip (XP-style reveals)
- Experimental nav (single-letter nav `N·E·X·U·S` or index number nav)
- Neon-on-dark accent pass using Electric Blue `#00D4FF` secondary accent
- Animated infographic for the stats section
- Native CSS scroll-driven reveals (drop JS dependency for reveal system)
- WebGL/Three.js aurora background toggleable behind particles
- AI "ask me" contact widget (links to Telegram)

## 9. ADVANCED — 3D Interfaces & WebGL (deep-read from live articles)

### The 2026 WebGL surge — creativedevjobs.com (full article read)
- **Big surge in WebGL/Three.js portfolios** — smooth animations, particle effects, interactive scenes, creative navigation patterns
- Studied examples emphasize **3D storytelling**, not just decoration

### 6 stunning WebGL portfolios — dev.to (full article read)
- **Robin Mastromarino** (Paris) — clean WebGL animations, interactive design
- **Keita Yamada** (Japan) — `100 Days of Poetry` gallery, 100 graphics, WebGL storytelling
- **Rocani Studio** (Berlin) — interactive stories for TikTok's Khaby Lame

### 160+ Three.js demos — freefrontend.com (read)
- 3D models, lighting experiments, **camera movement**, immersive scenes
- **GLSL shader demos**: chromatic-aberration sine wave (RGB channel separation via fragment shader), scroll-driven particle image matrix
- Advanced: scroll-driven WebGL image transitions (Three.js)

### Codrops / Smashing Magazine (RSS feeds — fresh articles)
- **Codrops**: "Building an Infinite GSAP Scroll Gallery with Parallax and Flip Transitions", "Engineering a Real-Time 3D Experience in Webflow", "The Story Is in the Interaction — luxury brand digital experiences"
- **Smashing**: "Thinking Outside The Box: Digital Design In The AI Era", "When It Makes Sense To 'Block' The Main Thread", "From Kickoff To First Concept — brand strategy to visual direction"

## 10. ENGINE REPORT — Google SERP scraping (honest verdict)

**Not feasible from this device.** Google serves a JS-only shell
(`/httpservice/retry/enablejs`) to all non-browser clients.
Tested: mobile UA, desktop UA, consent cookies, `gbv=1`, `udm=14` —
all return the same shell. Requires a real browser engine (Playwright/
Puppeteer) or the Google Custom Search JSON API (free 100 queries/day).
`tools/google_search.py` detects the shell and fails gracefully;
Brave + DDG tools cover the same search ground.

**Startpage — same verdict.** Serves a `jsgate` robot-wall (CSS shell +
token, `jsgate_feedback_form`) to non-browser clients; GET, POST and
cookie-jar retries all blocked. `tools/startpage_search.py` detects
and reports it. Requires a real browser engine too.

**Search engine throttle rules (recorded from real usage):**
- Brave: ~5 queries before HTTP 429 → space 15–30s
- DuckDuckGo: image-CAPTCHA after bursts → space queries, use lite endpoint
- Google: JS-gated entirely (no HTTP scraping)
- Startpage: JS-gate robot wall (no HTTP scraping)
- Serpent API: free tier exhausted (HTTP 402)
