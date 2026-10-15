// Each chart div's id matches its spec file in js/specs/
const charts = [
  "waffle_short_sleep",
  "map_world_sleep", "dumbbell_country_sex",
  "radial_clock", "slope_weekend", "map_sunrise",
  "line_age_quality", "bar_circumstance",
  "dumbbell_lifestyle", "bar_work_impacts",
  "heatmap_wellbeing",
  "map_distress_phn", "map_distress_sex", "map_distress_count"
];

charts.forEach(id => {
  vegaEmbed("#" + id, "js/specs/" + id + ".vg.json", {actions: false})
    .catch(console.error);
});
