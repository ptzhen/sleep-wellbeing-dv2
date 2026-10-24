// Each chart div's id matches its spec file in js/specs/
const charts = [
  "waffle_short_sleep",
  "map_world_sleep", "dumbbell_country_sex",
  "radial_clock", "ridgeline_day", "map_sunrise",
  "line_age_quality", "bar_circumstance",
  "dumbbell_lifestyle", "bar_work_impacts",
  "heatmap_wellbeing",
  "map_distress_phn", "map_distress_sex", "map_distress_count", "tile_capital_rest", "box_lga_state"
];

const views = {};
// Charts that build up once when first scrolled into view. Each spec has a
// "reveal" parameter (default 1 = the finished chart); here we run it from 0 to 1.
const REVEAL = {waffle_short_sleep: 1500, bar_circumstance: 1000, heatmap_wellbeing: 1200};
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// The multi-map figures have fixed sizes; on narrow screens stack them and shrink them to fit
const FIT = ["map_distress_phn", "map_distress_sex"];
function naturalWidth(s) {
  if (s.hconcat) return s.hconcat.reduce((a, c) => a + naturalWidth(c), 0) + (s.spacing ?? 20) * (s.hconcat.length - 1);
  if (s.vconcat) return Math.max(...s.vconcat.map(naturalWidth));
  return typeof s.width === "number" ? s.width : 0;
}
function stack(s, avail) {
  if (s.hconcat && s.hconcat.every(c => naturalWidth(c) >= 300) && naturalWidth(s) > avail) { s.vconcat = s.hconcat; delete s.hconcat; }
  (s.hconcat || s.vconcat || []).forEach(c => stack(c, avail));
}
function shrink(s, f) {
  (s.hconcat || s.vconcat || []).forEach(c => shrink(c, f));
  if (typeof s.width === "number") s.width = Math.round(s.width * f);
  if (typeof s.height === "number") s.height = Math.round(s.height * f);
  const p = s.projection;
  if (p && p.scale) { p.scale *= f; if (p.translate) p.translate = p.translate.map(t => t * f); }
}
// Map labels stay full size, so on a shrunk map they would spill over; the tooltips carry the values instead
function dropLabels(s) {
  (s.hconcat || s.vconcat || []).forEach(dropLabels);
  if (s.layer) s.layer = s.layer.filter(l => !(l.data && l.data.values && l.data.values.some(v => v.lab)));
  (s.layer || []).forEach(l => {
    const leg = l.encoding && l.encoding.color && l.encoding.color.legend;
    if (leg && leg.orient === "top-left") Object.assign(leg, {orient: "bottom", direction: "horizontal"});
  });
}
function fitSpec(spec, avail) {
  if (naturalWidth(spec) <= avail) return spec;
  stack(spec, avail);
  const f = avail / naturalWidth(spec);
  if (f < 1) shrink(spec, f);
  if (f < 0.75) dropLabels(spec);
  return spec;
}

charts.forEach(id => {
  const url = "js/specs/" + id + ".vg.json?v=7";
  const el = document.getElementById(id);
  const src = FIT.includes(id)
    ? fetch(url).then(r => r.json()).then(s => fitSpec(s, el.clientWidth - 24))
    : Promise.resolve(url);
  src.then(s => vegaEmbed("#" + id, s, {actions: false}))
    .then(r => {
      views[id] = r.view;
      if (REVEAL[id] && !reduceMotion) prepareReveal(id, r.view);
    })
    .catch(console.error);
});

function prepareReveal(id, view) {
  view.signal("reveal", 0).run();
  const el = document.getElementById(id);
  const obs = new IntersectionObserver(entries => {
    if (!entries.some(e => e.isIntersecting)) return;
    obs.disconnect();
    const start = performance.now() + 250, dur = REVEAL[id];
    const ease = t => 1 - Math.pow(1 - t, 3);
    const step = now => {
      const t = Math.min(1, Math.max(0, (now - start) / dur));
      view.signal("reveal", ease(t)).run();
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, {threshold: 0.45});
  obs.observe(el);
}

// "Play the night": steps the radial clock's own hour parameter from 10 pm to 10 am
const playBtn = document.getElementById("playNight");
let timer = null;
const NIGHT = [22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
function stopPlay() {
  clearInterval(timer); timer = null;
  playBtn.setAttribute("aria-pressed", "false");
  playBtn.querySelector(".ico").textContent = "▶";
  playBtn.querySelector(".lbl").textContent = "Play the night";
  if (views.radial_clock) views.radial_clock.signal("playing", false).run();
}
if (playBtn) playBtn.addEventListener("click", () => {
  const v = views.radial_clock;
  if (!v) return;
  if (timer) { stopPlay(); return; }
  let i = 0;
  v.signal("playing", true).signal("playHour", NIGHT[0]).run();
  if (reduceMotion) { v.signal("playHour", 7).run(); stopPlay(); return; }
  playBtn.setAttribute("aria-pressed", "true");
  playBtn.querySelector(".ico").textContent = "❚❚";
  playBtn.querySelector(".lbl").textContent = "Pause";
  timer = setInterval(() => {
    i += 1;
    if (i >= NIGHT.length) { stopPlay(); v.signal("playHour", 7).run(); return; }  // rest on the 7 am story moment
    v.signal("playHour", NIGHT[i]).run();
  }, 900);
});

// Page decoration only (no data): stars, chapter bar and gentle reveals
document.documentElement.classList.add("js");

// Stars in the hero sky
const stars = document.querySelector(".stars");
if (stars) {
  for (let i = 0; i < 140; i++) {
    const s = document.createElement("span");
    const size = Math.random() < 0.85 ? 1 + Math.random() * 1.5 : 2.5;
    s.className = "star";
    s.style.cssText = `left:${Math.random() * 100}%;top:${Math.random() * 100}%;width:${size}px;height:${size}px;` +
      `animation-delay:${(Math.random() * 5).toFixed(2)}s;animation-duration:${(3 + Math.random() * 4).toFixed(2)}s`;
    stars.appendChild(s);
  }
}

// Fade figures up as they scroll into view
const revealed = document.querySelectorAll(".card, .moment .wrap, .takeaways li");
revealed.forEach(el => el.classList.add("reveal"));
const io = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
}, {rootMargin: "0px 0px -8% 0px"});
revealed.forEach(el => io.observe(el));

// Progress line and current chapter in the sticky bar
const bar = document.querySelector(".progress span");
const links = [...document.querySelectorAll(".nightbar li a")];
const chapters = links.map(a => document.querySelector(a.getAttribute("href")));
function onScroll() {
  const h = document.documentElement;
  const p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight);
  if (bar) bar.style.width = (p * 100).toFixed(1) + "%";
  let cur = -1;
  chapters.forEach((c, i) => { if (c && c.getBoundingClientRect().top < 120) cur = i; });
  links.forEach((a, i) => a.classList.toggle("on", i === cur));
}
document.addEventListener("scroll", onScroll, {passive: true});
onScroll();

// Keep jargon definitions inside the screen on narrow layouts
document.querySelectorAll(".term").forEach(t => {
  const tip = t.querySelector(".tip");
  const place = () => {
    t.style.setProperty("--shift", "0px");
    const r = tip.getBoundingClientRect(), pad = 12;
    let shift = 0;
    if (r.left < pad) shift = pad - r.left;
    else if (r.right > window.innerWidth - pad) shift = window.innerWidth - pad - r.right;
    t.style.setProperty("--shift", shift + "px");
  };
  t.addEventListener("mouseenter", place);
  t.addEventListener("focus", place);
});
