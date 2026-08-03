/* ════════════════════════════════════════════════════════════════════════════
   NEXUS — Portfolio Interactions
   Zero dependencies · ES6+
   Modules: preloader · particles · cursor · nav · reveals · tilt · magnetic ·
            smooth scroll · scrollspy · form · error boundary · offline
   ════════════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* ────────────────────────────── HELPERS ────────────────────────────── */
  const $  = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const canHover = window.matchMedia("(pointer: fine)").matches;
  const isMobile = () => window.innerWidth < 768;

  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp = (v, min, max) => Math.min(max, Math.max(min, v));
  const expoOut = (t) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  /* ────────────────────────────── 1. PRELOADER ───────────────────────── */
  const preloader = $("#preloader");
  const pctEl = $("#preloader-pct");
  const fillEl = $("#preloader-fill");

  function runPreloader() {
    document.body.classList.add("is-loading");

    if (prefersReducedMotion.matches) {
      finishPreloader();
      return;
    }

    let progress = 0;
    const total = 1100; // ms
    const start = performance.now();

    (function tick(now) {
      const t = Math.min(1, (now - start) / total);
      const eased = expoOut(t);
      progress = Math.round(eased * 100);
      if (pctEl) pctEl.textContent = progress + "%";
      if (fillEl) fillEl.style.width = progress + "%";
      if (t < 1) requestAnimationFrame(tick);
      else finishPreloader();
    })(start);
  }

  function finishPreloader() {
    if (!preloader) return;
    preloader.classList.add("is-done");
    document.body.classList.remove("is-loading");
    document.body.classList.add("is-loaded"); // releases hero entrance animations
    window.setTimeout(() => preloader.setAttribute("aria-hidden", "true"), 700);
  }

  /* ────────────────────────────── 2. PARTICLE CANVAS ─────────────────── */
  const canvas = $("#particle-canvas");
  let pCtx = null, particles = [], rafId = null, pointer = { x: -9999, y: -9999 };

  function initParticles() {
    if (!canvas || !canvas.getContext) return;
    pCtx = canvas.getContext("2d");
    if (!pCtx) return; // canvas unavailable (very old browsers / test env)
    buildParticles();

    window.addEventListener("resize", debounce(buildParticles, 200));
    window.addEventListener("mousemove", (e) => {
      pointer.x = e.clientX;
      pointer.y = e.clientY;
    });
    window.addEventListener("mouseout", () => { pointer.x = -9999; pointer.y = -9999; });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stopParticles(); else startParticles();
    });

    if (prefersReducedMotion.matches) {
      drawParticlesFrame(); // single static frame
    } else {
      startParticles();
    }
  }

  function buildParticles() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + "px";
    canvas.style.height = window.innerHeight + "px";
    pCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const count = Math.min(Math.floor((window.innerWidth * window.innerHeight) / 18000), 80);
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: (Math.random() - 0.5) * 0.22,
      vy: (Math.random() - 0.5) * 0.22,
      r: Math.random() * 1.8 + 0.4,
      a: Math.random() * 0.35 + 0.08,
      hue: Math.random() < 0.78 ? "94, 143, 255" : "56, 214, 255",
      tw: Math.random() * Math.PI * 2,
    }));
  }

  function drawParticlesFrame() {
    if (!pCtx) return;
    pCtx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    for (const p of particles) {
      pCtx.beginPath();
      pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      pCtx.fillStyle = `rgba(${p.hue}, ${p.a})`;
      pCtx.fill();
    }
  }

  function startParticles() {
    if (rafId) return;
    const step = () => {
      rafId = requestAnimationFrame(step);
      if (!pCtx) return;
      pCtx.clearRect(0, 0, window.innerWidth, window.innerHeight);

      const mouseR = 150;
      for (const p of particles) {
        // gentle repulsion from cursor
        const dx = p.x - pointer.x;
        const dy = p.y - pointer.y;
        const dist = Math.hypot(dx, dy);
        if (dist < mouseR && dist > 0.01) {
          const force = (1 - dist / mouseR) * 0.6;
          p.vx += (dx / dist) * force * 0.18;
          p.vy += (dy / dist) * force * 0.18;
        }
        // damp & drift
        p.vx *= 0.985;
        p.vy *= 0.985;
        p.x += p.vx;
        p.y += p.vy;

        // wrap around edges
        if (p.x < -10) p.x = window.innerWidth + 10;
        if (p.x > window.innerWidth + 10) p.x = -10;
        if (p.y < -10) p.y = window.innerHeight + 10;
        if (p.y > window.innerHeight + 10) p.y = -10;

        p.tw += 0.02;
        const twinkle = 0.7 + 0.3 * Math.sin(p.tw);

        pCtx.beginPath();
        pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        pCtx.fillStyle = `rgba(${p.hue}, ${(p.a * twinkle).toFixed(3)})`;
        pCtx.fill();
      }

      // connective lines on large screens
      if (window.innerWidth >= 1024 && !prefersReducedMotion.matches) {
        for (let i = 0; i < particles.length; i++) {
          for (let j = i + 1; j < particles.length; j++) {
            const a = particles[i], b = particles[j];
            const d = Math.hypot(a.x - b.x, a.y - b.y);
            if (d < 110) {
              pCtx.beginPath();
              pCtx.moveTo(a.x, a.y);
              pCtx.lineTo(b.x, b.y);
              pCtx.strokeStyle = `rgba(94, 143, 255, ${(0.10 * (1 - d / 110)).toFixed(3)})`;
              pCtx.lineWidth = 0.6;
              pCtx.stroke();
            }
          }
        }
      }
    };
    step();
  }

  function stopParticles() {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
  }

  /* ────────────────────────────── 3. CUSTOM CURSOR ───────────────────── */
  const dot = $("#cursor-dot");
  const ring = $("#cursor-ring");

  function initCursor() {
    if (!canHover || !dot || !ring || prefersReducedMotion.matches) return;

    let mx = -100, my = -100, dx = -100, dy = -100, rx = -100, ry = -100;

    window.addEventListener("mousemove", (e) => {
      mx = e.clientX; my = e.clientY;
    });

    (function loop() {
      dx = lerp(dx, mx, 0.42);
      dy = lerp(dy, my, 0.42);
      rx = lerp(rx, mx, 0.16);
      ry = lerp(ry, my, 0.16);
      dot.style.transform = `translate(${dx - 3}px, ${dy - 3}px)`;
      ring.style.transform = `translate(${rx - 18}px, ${ry - 18}px)`;
      requestAnimationFrame(loop);
    })();

    const hoverables = "a, button, input, textarea, .project, .chip-list li, .about__highlights li";
    document.addEventListener("mouseover", (e) => {
      if (e.target.closest(hoverables)) ring.classList.add("is-hover");
    });
    document.addEventListener("mouseout", (e) => {
      if (e.target.closest(hoverables)) ring.classList.remove("is-hover");
    });
    window.addEventListener("mousedown", () => ring.classList.add("is-down"));
    window.addEventListener("mouseup", () => ring.classList.remove("is-down"));
    document.documentElement.addEventListener("mouseleave", () => {
      dot.style.opacity = "0"; ring.style.opacity = "0";
    });
    document.documentElement.addEventListener("mouseenter", () => {
      dot.style.opacity = "1"; ring.style.opacity = "1";
    });
  }

  /* ────────────────────────────── 4. NAVIGATION ──────────────────────── */
  const nav = $("#site-nav");
  const navToggle = $("#nav-toggle");
  const mobileMenu = $("#mobile-menu");

  function initNav() {
    let lastY = 0;

    window.addEventListener("scroll", () => {
      const y = window.scrollY;
      if (y > 40) nav.classList.add("is-scrolled");
      else nav.classList.remove("is-scrolled");

      // hide on scroll down, reveal on scroll up (desktop)
      if (y > 180 && y > lastY && !isMobile()) nav.classList.add("is-hidden");
      else nav.classList.remove("is-hidden");
      lastY = y;
    }, { passive: true });

    if (navToggle && mobileMenu) {
      navToggle.addEventListener("click", () => {
        const open = mobileMenu.classList.toggle("is-open");
        navToggle.classList.toggle("is-open", open);
        navToggle.setAttribute("aria-expanded", String(open));
        mobileMenu.setAttribute("aria-hidden", String(!open));
        document.body.style.overflow = open ? "hidden" : "";
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && mobileMenu.classList.contains("is-open")) {
          navToggle.click();
        }
      });
      window.addEventListener("resize", debounce(() => {
        if (!isMobile() && mobileMenu.classList.contains("is-open")) navToggle.click();
      }, 150));
    }

    // close mobile menu when a nav link is tapped (handled in scroll handler too)
    $$(".mobile-menu a[data-nav]").forEach((a) =>
      a.addEventListener("click", () => {
        if (mobileMenu.classList.contains("is-open")) navToggle.click();
      })
    );

    // scrollspy — highlight the section currently in view
    const sections = ["hero", "about", "skills", "projects", "contact"]
      .map((id) => document.getElementById(id))
      .filter(Boolean);
    const links = $$(".nav__link[data-nav]");

    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          links.forEach((l) =>
            l.classList.toggle("is-active", l.getAttribute("href") === "#" + entry.target.id)
          );
        }
      });
    }, { rootMargin: "-42% 0px -52% 0px" });
    sections.forEach((s) => spy.observe(s));
  }

  /* ────────────────────────────── 5. SMOOTH ANCHOR SCROLL ────────────── */
  function initSmoothScroll() {
    document.addEventListener("click", (e) => {
      const link = e.target.closest('a[href^="#"]');
      if (!link) return;
      const targetId = link.getAttribute("href");
      if (targetId === "#") return;

      const target = targetId === "#top" ? document.body : $(targetId);
      if (!target) return;
      e.preventDefault();

      const navH = nav ? nav.offsetHeight + 4 : 0;
      const dest = target === document.body ? 0 : target.getBoundingClientRect().top + window.scrollY - navH;
      const startY = window.scrollY;
      const delta = dest - startY;
      const duration = Math.min(1100, Math.max(500, Math.abs(delta) * 0.6));
      const start = performance.now();

      function step(now) {
        const t = clamp((now - start) / duration, 0, 1);
        window.scrollTo(0, startY + delta * expoOut(t));
        if (t < 1) requestAnimationFrame(step);
        else {
          try { history.replaceState(null, "", targetId); } catch (_) { /* file:// safe */ }
        }
      }
      requestAnimationFrame(step);
    });
  }

  /* ────────────────────────────── 6. SCROLL PROGRESS ─────────────────── */
  const progressBar = $("#scroll-progress-bar");

  function initProgress() {
    if (!progressBar) return;
    const update = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      progressBar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  /* ────────────────────────────── 7. REVEAL OBSERVER ─────────────────── */
  function initReveals() {
    const items = $$(".reveal");
    if (!("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const d = entry.target.dataset.delay || 0;
          entry.target.style.setProperty("--d", d);
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);

          // Once the reveal settles, drop the transform transition on tilt cards
          // so 3D tilt follows the cursor instantly (no laggy easing).
          if (entry.target.classList.contains("tilt")) {
            const delay = (parseFloat(d) || 0) * 120;
            window.setTimeout(() => {
              entry.target.style.transition =
                "border-color .4s cubic-bezier(.25,1,.5,1), box-shadow .5s cubic-bezier(.16,1,.3,1)";
            }, delay + 950);
          }
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    items.forEach((el) => io.observe(el));

    // skill bars fill when the section scrolls into view
    const skills = $("#skills");
    if (skills && "IntersectionObserver" in window) {
      const so = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            $$(".skill", skills).forEach((s, i) => {
              window.setTimeout(() => s.classList.add("is-visible"), i * 90);
            });
            so.disconnect();
          }
        });
      }, { threshold: 0.25 });
      so.observe(skills);
    }
  }

  /* ────────────────────────────── 8. 3D TILT CARDS ───────────────────── */
  function initTilt() {
    if (prefersReducedMotion.matches || !canHover) return;
    $$(".tilt").forEach((card) => {
      let raf = null;

      card.addEventListener("mousemove", (e) => {
        if (raf) return;
        raf = requestAnimationFrame(() => {
          const rect = card.getBoundingClientRect();
          const px = (e.clientX - rect.left) / rect.width - 0.5;
          const py = (e.clientY - rect.top) / rect.height - 0.5;
          card.style.setProperty("--rx", (-py * 7).toFixed(2) + "deg");
          card.style.setProperty("--ry", (px * 9).toFixed(2) + "deg");
          card.style.transform =
            `perspective(900px) rotateX(${(-py * 7).toFixed(2)}deg) rotateY(${(px * 9).toFixed(2)}deg) translateY(-4px)`;
          raf = null;
        });
      });

      card.addEventListener("mouseleave", () => {
        card.style.transform = "";
        card.style.setProperty("--rx", "0deg");
        card.style.setProperty("--ry", "0deg");
      });
    });
  }

  /* ────────────────────────────── 9. MAGNETIC BUTTONS ────────────────── */
  function initMagnetic() {
    if (prefersReducedMotion.matches || !canHover) return;
    $$("[data-magnetic]").forEach((el) => {
      el.addEventListener("mousemove", (e) => {
        const rect = el.getBoundingClientRect();
        const mx = e.clientX - rect.left - rect.width / 2;
        const my = e.clientY - rect.top - rect.height / 2;
        el.style.setProperty("--mx", (mx * 0.28).toFixed(1) + "px");
        el.style.setProperty("--my", (my * 0.28).toFixed(1) + "px");
      });
      el.addEventListener("mouseleave", () => {
        el.style.setProperty("--mx", "0px");
        el.style.setProperty("--my", "0px");
      });
    });
  }

  /* ────────────────────────────── 10. BACK TO TOP ────────────────────── */
  function initToTop() {
    const btn = $("#to-top-btn");
    if (!btn) return;
    window.addEventListener("scroll", () => {
      btn.classList.toggle("is-visible", window.scrollY > 640);
    }, { passive: true });
    btn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: prefersReducedMotion.matches ? "auto" : "smooth" });
    });
  }

  /* ────────────────────────────── 11. IMAGES: BLUR-UP + FALLBACK ─────── */
  const FALLBACK_IMG =
    "data:image/svg+xml," + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500">' +
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0" stop-color="#0b0e18"/><stop offset="1" stop-color="#12172a"/></linearGradient></defs>' +
      '<rect width="800" height="500" fill="url(#g)"/>' +
      '<text x="400" y="262" font-family="monospace" font-size="22" fill="#5e8fff" text-anchor="middle" letter-spacing="6">NEXUS</text></svg>'
    );

  function initImages() {
    $$("img").forEach((img) => {
      // blur-up shimmer placeholder for lazy images
      if (img.loading === "lazy" && !img.classList.contains("blur-up")) {
        img.classList.add("blur-up");
      }
      img.addEventListener("load", () => img.classList.add("is-loaded"), { once: true });
      if (img.complete && img.naturalWidth > 0) img.classList.add("is-loaded");

      // graceful fallback if the file is missing
      img.addEventListener("error", function handleErr() {
        if (img.dataset.fallbackApplied) return;
        img.dataset.fallbackApplied = "1";
        img.src = FALLBACK_IMG;
        img.classList.add("is-loaded");
      });
    });
  }

  /* ────────────────────────────── 12. CONTACT FORM ───────────────────── */
  function initForm() {
    const form = $("#contact-form");
    if (!form) return;

    const name = $("#f-name");
    const tg = $("#f-tg");
    const msg = $("#f-msg");
    const submit = $("#form-submit");
    const success = $("#form-success");
    const successLink = $("#form-success-link");

    const fields = [
      {
        el: name, err: $("#f-name-error"),
        test: (v) => v.trim().length >= 2,
        bad: "Please enter at least 2 characters.",
      },
      {
        el: tg, err: $("#f-tg-error"),
        test: (v) => v.trim() === "" || /^@?[A-Za-z0-9_]{3,32}$/.test(v.trim()),
        bad: "Handles look like @username (3–32 chars).",
      },
      {
        el: msg, err: $("#f-msg-error"),
        test: (v) => v.trim().length >= 10,
        bad: "Tell me a bit more — at least 10 characters.",
      },
    ];

    function setError(f, message) {
      f.el.closest(".field").classList.toggle("is-invalid", Boolean(message));
      f.err.textContent = message || "";
    }

    function validateField(f) {
      const ok = f.test(f.el.value);
      setError(f, ok ? "" : f.bad);
      return ok;
    }

    // live re-validation while typing
    fields.forEach((f) => {
      f.el.addEventListener("input", () => {
        if (f.el.closest(".field").classList.contains("is-invalid")) validateField(f);
      });
      f.el.addEventListener("blur", () => validateField(f));
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const results = fields.map(validateField);
      const firstBad = fields.find((_, i) => !results[i]);
      if (firstBad) {
        firstBad.el.focus();
        return;
      }

      // short "sending" state → then hand off to Telegram
      submit.classList.add("is-loading");
      submit.disabled = true;
      await sleep(650);
      submit.classList.remove("is-loading");
      submit.disabled = false;

      const handle = tg.value.trim();
      const from = name.value.trim() + (handle ? ` (@${handle.replace(/^@/, "")})` : "");
      const body =
        `Salaam Nexus 👋\n\n` +
        `From: ${from}\n` +
        `Message:\n${msg.value.trim()}`;

      const url = "https://t.me/nexus_pro_dev?text=" + encodeURIComponent(body);

      form.hidden = true;
      success.hidden = false;
      if (successLink) successLink.href = url;
      window.open(url, "_blank", "noopener");

      form.reset();
    });
  }

  /* ────────────────────────────── 13. GLOBAL ERROR BOUNDARY ──────────── */
  function initErrorBoundary() {
    const overlay = $("#fatal-error");
    const msgEl = $("#fatal-msg");
    let shown = false;

    function showFatal(message) {
      if (shown || !overlay) return;
      shown = true;
      if (msgEl && message) msgEl.textContent = message;
      overlay.hidden = false;
      overlay.setAttribute("aria-hidden", "false");
    }

    window.addEventListener("error", (e) => {
      // ignore benign ResizeObserver noise
      if (e.message && /ResizeObserver/i.test(e.message)) return;
      console.error("Uncaught error:", e.error || e.message);
      showFatal(e.message || "An unexpected error occurred.");
    });

    window.addEventListener("unhandledrejection", (e) => {
      console.error("Unhandled rejection:", e.reason);
      showFatal("A background task failed. Please reload to continue.");
    });

    const reload = $("#fatal-reload");
    if (reload) reload.addEventListener("click", () => window.location.reload());
  }

  /* ────────────────────────────── 14. OFFLINE TOAST ───────────────────── */
  function initConnectivity() {
    const banner = $("#offline-banner");
    if (!banner) return;
    const closeBtn = $("#offline-banner-close");
    const textEl = $("#offline-banner-text");
    const iconEl = $("#offline-banner-icon");
    let hideTimer = null;

    /** Shared toast: shows the banner with a message, auto-hides. */
    function showToast(message, icon) {
      if (textEl) textEl.textContent = message;
      if (iconEl) iconEl.textContent = icon || "📡";
      banner.hidden = false;
      clearTimeout(hideTimer);
      hideTimer = window.setTimeout(() => { banner.hidden = true; }, 7000);
    }

    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        banner.hidden = true;
        clearTimeout(hideTimer);
      });
    }
    window.addEventListener("offline", () => showToast("You're offline — the site runs fully from local files, so everything still works. Reconnect to load web fonts."));
    window.addEventListener("online", () => { banner.hidden = true; clearTimeout(hideTimer); });

    // show immediately if the browser already considers us offline
    if (navigator.onLine === false) {
      showToast("You're offline — the site runs fully from local files, so everything still works. Reconnect to load web fonts.");
    }
  }

  /* ────────────────────────────── 15. SERVICE WORKER ──────────────────── */
  function initServiceWorker() {
    // SWs need a secure context (https or localhost) — skip file:// and jsdom
    if (!("serviceWorker" in navigator)) return;
    if (location.protocol !== "http:" && location.protocol !== "https:") return;

    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("./sw.js", { scope: "./", updateViaCache: "none" })
        .then(() => console.info("[NEXUS] Service worker registered"))
        .catch((err) => console.warn("[NEXUS] SW registration skipped:", err.message));
    });

    // SW → page message: offline cache is ready
    navigator.serviceWorker.addEventListener("message", (event) => {
      if (!event.data || event.data.type !== "NX_OFFLINE_READY") return;
      if (localStorage.getItem("nx_offline_notified") === event.data.version) return;
      localStorage.setItem("nx_offline_notified", event.data.version);

      const banner = $("#offline-banner");
      if (!banner) return;
      const textEl = $("#offline-banner-text");
      const iconEl = $("#offline-banner-icon");
      if (textEl) textEl.textContent = "Offline mode ready — this site now works even without internet.";
      if (iconEl) iconEl.textContent = "⚡";
      banner.hidden = false;
      window.setTimeout(() => { banner.hidden = true; }, 6000);
    });
  }

  /* ────────────────────────────── 15. MISC ───────────────────────────── */
  function initMisc() {
    const yearEl = $("#year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());
  }

  /* ────────────────────────────── BOOT ───────────────────────────────── */
  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }

  function boot() {
    initErrorBoundary();
    initParticles();
    initCursor();
    initNav();
    initSmoothScroll();
    initProgress();
    initReveals();
    initTilt();
    initMagnetic();
    initToTop();
    initImages();
    initForm();
    initConnectivity();
    initServiceWorker();
    initMisc();

    // ensure images already cached don't stay in blur state
    window.addEventListener("load", () => {
      $$("img").forEach((img) => { if (img.complete && img.naturalWidth > 0) img.classList.add("is-loaded"); });
    });

    // start page immediately (hero entrance waits for .is-loaded)
    window.setTimeout(runPreloader, 60);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
