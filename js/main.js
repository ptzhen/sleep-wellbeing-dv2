// Each chart div's id matches its spec file in js/specs/
const charts = ["map_distress_phn"];

charts.forEach(id => {
  vegaEmbed("#" + id, "js/specs/" + id + ".vg.json", {actions: false})
    .catch(console.error);
});
