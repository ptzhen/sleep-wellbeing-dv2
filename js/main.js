// Each chart div's id matches its spec file in js/specs/
const charts = [
  "waffle_short_sleep",
  "map_world_sleep", "dumbbell_country_sex",
  "radial_clock", "ridgeline_day", "slope_weekend", "map_sunrise",
  "line_age_quality", "bar_circumstance",
  "dumbbell_lifestyle", "bar_work_impacts",
  "heatmap_wellbeing",
  "map_distress_phn", "map_distress_sex", "map_distress_count", "tile_capital_rest"
];

const views = {};
charts.forEach(id => {
  vegaEmbed("#" + id, "js/specs/" + id + ".vg.json", {actions: false})
    .then(r => { views[id] = r.view; })
    .catch(console.error);
});

// "Play the night": steps the radial clock's own hour parameter from 10 pm to 10 am
const playBtn = document.getElementById("playNight");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
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
