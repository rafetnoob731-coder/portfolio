/* Behavioral smoke test for the NEXUS portfolio.
   Loads index.html into jsdom, stubs browser APIs, executes main.js
   and asserts key behaviors: preloader, reveals, nav, form, error boundary.
   Usage: NODE_PATH=$HOME/.cache/npmtest/node_modules node test/smoke.js */
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const ROOT = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");
const script = fs.readFileSync(path.join(ROOT, "js", "main.js"), "utf8");

let failures = 0;
function check(name, cond, extra = "") {
  if (cond) console.log(`  ✓ ${name}`);
  else { failures++; console.log(`  ✗ ${name} ${extra}`); }
}

// ── virtual console: surface real page errors ──
const vc = new VirtualConsole();
const pageErrors = [];
vc.on("jsdomError", (e) => pageErrors.push(e.message));
vc.on("error", (...a) => pageErrors.push(a.join(" ")));

(async () => {
  const dom = new JSDOM(html, {
    url: "http://localhost:8899/index.html",
    pretendToBeVisual: true,
    virtualConsole: vc,
    runScripts: "outside-only",
  });
  const { window } = dom;
  const { document } = window;

  // ── API stubs ──
  window.matchMedia = () => ({ matches: false, addEventListener() {}, addListener() {}, removeListener() {} });
  window.scrollTo = () => {};
  window.scrollBy = () => {};
  window.open = () => null;
  class FakeIO {
    constructor(cb) { this.cb = cb; }
    observe(el) { queueMicrotask(() => this.cb([{ target: el, isIntersecting: true }])); }
    unobserve() {}
    disconnect() {}
  }
  window.IntersectionObserver = FakeIO;

  // service worker stub
  let swRegisteredUrl = null;
  const swListeners = {};
  Object.defineProperty(window.navigator, "serviceWorker", {
    configurable: true,
    value: {
      register: (url) => { swRegisteredUrl = url; return Promise.resolve({}); },
      addEventListener: (type, cb) => { swListeners[type] = cb; },
    },
  });

  console.log("— boot —");
  window.eval(script); // runs boot() (readyState likely loading → DOMContentLoaded)
  await new Promise((r) => setTimeout(r, 80));

  // ── preloader ──
  console.log("— preloader —");
  // wait (poll) for boot to run & the loading class to appear
  for (let i = 0; i < 40 && !document.body.classList.contains("is-loading"); i++) {
    await new Promise((r) => setTimeout(r, 25));
  }
  check("body starts with .is-loading", document.body.classList.contains("is-loading"));
  await new Promise((r) => setTimeout(r, 1400));
  check("preloader marked done", document.getElementById("preloader").classList.contains("is-done"));
  check("body gains .is-loaded", document.body.classList.contains("is-loaded"));

  // ── reveals ──
  console.log("— scroll reveals —");
  const revealed = [...document.querySelectorAll(".reveal")];
  check("all .reveal elements become visible", revealed.length > 0 && revealed.every((el) => el.classList.contains("is-visible")));

  // ── skill bars ──
  console.log("— skill bars —");
  const skills = [...document.querySelectorAll(".skill")];
  check("skill bars fill on view", skills.length === 6 && skills.every((s) => s.classList.contains("is-visible")));

  // ── mobile menu ──
  console.log("— mobile menu —");
  const toggle = document.getElementById("nav-toggle");
  toggle.click();
  check("menu opens", document.getElementById("mobile-menu").classList.contains("is-open"));
  check("aria-expanded=true", toggle.getAttribute("aria-expanded") === "true");
  toggle.click();
  check("menu closes", !document.getElementById("mobile-menu").classList.contains("is-open"));

  // ── smooth scroll ──
  console.log("— smooth scroll —");
  const hero = document.getElementById("hero");
  const spyActive = document.querySelector('.nav__link.is-active');
  check("scrollspy marks a section active", Boolean(spyActive));

  // ── form validation ──
  console.log("— form validation —");
  const form = document.getElementById("contact-form");
  const name = document.getElementById("f-name");
  const tg = document.getElementById("f-tg");
  const msg = document.getElementById("f-msg");
  name.value = "A";            // too short
  msg.value = "hi";            // too short
  form.dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  check("invalid name shows error", document.getElementById("f-name-error").textContent.length > 0);
  check("invalid name marked", name.closest(".field").classList.contains("is-invalid"));
  check("invalid msg shows error", document.getElementById("f-msg-error").textContent.length > 0);
  check("form NOT hidden on error", !form.hidden);

  name.value = "Nexus";
  tg.value = "@nexus_pro_dev";
  msg.value = "Salaam! I would love to collaborate on an automation project with you.";
  form.dispatchEvent(new window.Event("submit", { bubbles: true, cancelable: true }));
  await new Promise((r) => setTimeout(r, 800));
  check("valid form hides", form.hidden === true);
  check("success panel shows", document.getElementById("form-success").hidden === false);
  const link = document.getElementById("form-success-link").href;
  check("telegram deep-link built", link.startsWith("https://t.me/nexus_pro_dev?text="));

  // ── error boundary ──
  console.log("— error boundary —");
  window.dispatchEvent(new window.Event("error", { message: "Test crash" }));
  const fatal = document.getElementById("fatal-error");
  check("fatal overlay appears", fatal.hidden === false);
  check("fatal overlay labelled", fatal.getAttribute("aria-hidden") === "false");
  document.getElementById("fatal-reload").click();

  // ── image fallback ──
  console.log("— image fallback —");
  const img = document.querySelector(".about__avatar");
  img.dispatchEvent(new window.Event("error"));
  check("broken image replaced by data-URI", img.src.startsWith("data:image/svg+xml"));

  console.log("— service worker —");
  // SW registration happens on window load
  window.dispatchEvent(new window.Event("load"));
  await new Promise((r) => setTimeout(r, 30));
  check("registers ./sw.js", swRegisteredUrl === "./sw.js");
  // simulate SW → page message: offline-ready toast
  if (swListeners.message) {
    swListeners.message({ data: { type: "NX_OFFLINE_READY", version: "nexus-v1" } });
    check("offline-ready toast shown", document.getElementById("offline-banner").hidden === false);
    check("toast text updated", document.getElementById("offline-banner-text").textContent.includes("Offline mode ready"));
  }

  console.log("— page console errors —");
  // "Uncaught error:" is the error boundary logging our own synthetic crash test
  const real = pageErrors.filter((m) => !/not implemented/i.test(m) && !/Uncaught error/i.test(m));
  check("no uncaught page errors", real.length === 0, real.join(" | "));

  console.log(failures === 0 ? "\nALL TESTS PASSED ✅" : `\n${failures} FAILURES ❌`);
  process.exit(failures === 0 ? 0 : 1);
})().catch((e) => { console.error("Harness crashed:", e); process.exit(2); });
