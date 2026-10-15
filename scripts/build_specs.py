"""Generates every Vega-Lite spec in js/specs/ (pretty-printed). Usage: python3 build_specs.py js/specs"""
import json, sys
OUT = sys.argv[1]
S = "https://vega.github.io/schema/vega-lite/v5.json"
INK, MUTED, GRID = "#23263a", "#5d6077", "#e6e3dc"
WEEKDAY, WEEKEND = "#3b5ba5", "#d08a1e"
MEN, WOMEN = "#2a7fbf", "#c4527a"
ACCENT = "#d08a1e"
PURPLES = ["#e6e1f2", "#bdb0dd", "#8e7cc3", "#5e4a9e", "#2f2366"]
CONFIG = {
    "background": "transparent",
    "font": "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif",
    "view": {"stroke": None},
    "title": {"font": "Fraunces, Georgia, serif", "fontSize": 18, "fontWeight": 600, "color": INK, "anchor": "start",
              "subtitleFont": "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif", "subtitleFontSize": 13, "subtitleFontWeight": 400, "subtitleColor": MUTED, "offset": 12},
    "axis": {"labelFontSize": 12, "titleFontSize": 12, "titleColor": MUTED, "labelColor": MUTED,
             "gridColor": GRID, "labelLimit": 320, "domainColor": "#c9c5bb", "tickColor": "#c9c5bb", "titleFontWeight": 400},
    "legend": {"labelLimit": 260, "titleLimit": 300, "labelFontSize": 12, "titleFontSize": 12, "titleColor": MUTED, "labelColor": INK, "titleFontWeight": 400},
    "header": {"labelFontSize": 13, "labelColor": INK, "titleFontSize": 13},
    "text": {"font": "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif", "color": INK},
}
AUS_PROJ = {"type": "conicEqualArea", "parallels": [-18, -36], "rotate": [-134, 0]}
specs = {}
def spec(name, title, subtitle, body):
    # titles live in the HTML (see index.html) so they wrap with the page
    s = {"$schema": S}
    s.update(body)
    if isinstance(body.get("height"), dict): s["autosize"] = {"type": "fit-x", "contains": "padding"}
    s["config"] = CONFIG; specs[name] = s

# 1. Waffle: 1 in 3 sleep under 7 hours (SHF 2025)
spec("waffle_short_sleep", "1 in 3 Australian adults sleep less than 7 hours",
     ["Each square is 1 in 100 adults, by usual sleep a night", "Sleep Health Foundation, Aussie Sleep Snapshot", "2025 (n = 1,012)"], {
    "width": 300, "height": 300,
    "data": {"sequence": {"start": 0, "stop": 100, "as": "i"}},
    "transform": [
        {"calculate": "datum.i % 10", "as": "col"},
        {"calculate": "floor(datum.i / 10)", "as": "row"},
        {"calculate": "datum.i < 33 ? 'Less than 7 hours' : '7 hours or more'", "as": "group"}],
    "mark": {"type": "square", "size": 520, "cornerRadius": 3},
    "encoding": {
        "x": {"field": "col", "type": "ordinal", "axis": None},
        "y": {"field": "row", "type": "ordinal", "axis": None},
        "color": {"field": "group", "type": "nominal", "title": None,
                  "scale": {"domain": ["Less than 7 hours", "7 hours or more"], "range": [ACCENT, "#cdd3e6"]},
                  "legend": {"orient": "bottom", "direction": "horizontal"}},
        "tooltip": [{"field": "group", "title": "Usual sleep"}]}})

# 2. World choropleth (OECD time use)
spec("map_world_sleep", "Australians sleep about as long as people in most surveyed countries",
     ["Average minutes of sleep per day, adults, latest OECD time-use survey", "Survey years vary (1999–2019); hover for each country's year. Grey: no survey"], {
    "width": "container", "height": 420,
    "projection": {"type": "equalEarth"},
    "data": {"url": "data/world_countries.topojson", "format": {"type": "topojson", "feature": "countries"}},
    "transform": [{"filter": "datum.properties.CONTINENT != 'Antarctica'"}],
    "layer": [
        {"mark": {"type": "geoshape", "fill": "#ecebe6", "stroke": "#ffffff", "strokeWidth": 0.4},
         "encoding": {"tooltip": [{"field": "properties.NAME", "title": "Country"}]}},
        {"transform": [
            {"lookup": "properties.ADM0_A3", "from": {"data": {"url": "data/oecd_sleep_by_country.csv"}, "key": "iso3",
                                                    "fields": ["sleep_min_total", "survey_year", "age_group", "country"]}},
            {"filter": "isValid(datum.sleep_min_total)"},
            {"calculate": "floor(datum.sleep_min_total/60) + 'h ' + round(datum.sleep_min_total % 60) + 'm'", "as": "hm"}],
         "params": [{"name": "hoverCountry", "select": {"type": "point", "on": "pointerover", "clear": "pointerout"}}],
         "mark": {"type": "geoshape", "stroke": "#ffffff", "strokeWidth": 0.4},
         "encoding": {
             "color": {"field": "sleep_min_total", "type": "quantitative", "title": "Minutes of sleep a day",
                       "scale": {"type": "threshold", "domain": [480, 500, 510, 520, 530],
                                 "range": ["#cfd9f0", "#a9bce4", "#7f9bd2", "#5679bd", "#3b5ba5", "#1e2f63"]},
                       "legend": {"orient": "bottom-left", "direction": "horizontal", "gradientLength": 320, "labelOverlap": False}},
             "stroke": {"condition": {"param": "hoverCountry", "empty": False, "value": INK}, "value": "#ffffff"},
             "strokeWidth": {"condition": {"param": "hoverCountry", "empty": False, "value": 1.5}, "value": 0.4},
             "tooltip": [{"field": "country", "title": "Country"},
                         {"field": "hm", "title": "Sleep per day"},
                         {"field": "survey_year", "title": "Survey year"},
                         {"field": "age_group", "title": "Ages covered"}]}},
        {"transform": [{"filter": "datum.properties.ADM0_A3 == 'AUS'"}],
         "mark": {"type": "geoshape", "fill": None, "stroke": ACCENT, "strokeWidth": 2}}]})

# 3. Dumbbell: men vs women by country
spec("dumbbell_country_sex", "Women out-sleep men in most countries",
     ["Minutes of sleep per day for women and men, latest survey per country", "Australia's OECD figure is from 2006 and covers ages 15+. OECD Time Use Database"], {
    "width": "container", "height": {"step": 15},
    "data": {"url": "data/oecd_sleep_by_country.csv"},
    "transform": [
        {"fold": ["sleep_min_men", "sleep_min_women"], "as": ["sexkey", "minutes"]},
        {"calculate": "datum.sexkey == 'sleep_min_men' ? 'Men' : 'Women'", "as": "sex"},
        {"calculate": "datum.country == 'Australia' ? 'Australia ★' : datum.country", "as": "label"}],
    "encoding": {
        "y": {"field": "label", "type": "nominal", "title": None,
              "sort": {"field": "sleep_min_total", "op": "mean", "order": "descending"},
              "axis": {"labelColor": {"condition": {"test": "datum.value == 'Australia ★'", "value": ACCENT}, "value": INK},
                       "labelFontWeight": {"condition": {"test": "datum.value == 'Australia ★'", "value": 700}, "value": 400},
                       "domain": False, "ticks": False}},
        "x": {"field": "minutes", "type": "quantitative", "title": "Minutes of sleep per day",
              "scale": {"domain": [430, 560]}, "axis": {"grid": True, "orient": "top", "values": [440, 460, 480, 500, 520, 540, 560]}}},
    "layer": [
        {"mark": {"type": "rule", "color": "#c9c5bb", "strokeWidth": 2}, "encoding": {"x": {"aggregate": "min", "field": "minutes"}, "x2": {"aggregate": "max", "field": "minutes"}}},
        {"mark": {"type": "circle", "size": 70, "opacity": 1, "stroke": "#fbfaf7", "strokeWidth": 1},
         "encoding": {"color": {"field": "sex", "type": "nominal", "title": None,
                                "scale": {"domain": ["Women", "Men"], "range": [WOMEN, MEN]},
                                "legend": {"orient": "top", "direction": "horizontal"}},
                      "tooltip": [{"field": "country", "title": "Country"}, {"field": "sex", "title": "Sex"},
                                  {"field": "minutes", "title": "Minutes a day", "format": ".0f"},
                                  {"field": "survey_year", "title": "Survey year"}]}}]})

# 4. Radial clock: % asleep by hour, weekday vs weekend
clock_layer = lambda day: {
    "transform": [{"filter": f"datum.day_type == '{day}'"}],
    "title": {"text": day + "s", "fontSize": 14, "anchor": "middle", "font": "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif", "fontWeight": 600},
    "width": 260, "height": 260,
    "layer": [
        {"mark": {"type": "arc", "stroke": "#fbfaf7", "strokeWidth": 1, "innerRadius": 18, "cornerRadius": 2},
         "encoding": {
             "theta": {"field": "hour_start", "type": "quantitative", "scale": {"domain": [0, 24]}},
             "theta2": {"field": "hour_end"},
             "radius": {"field": "pct", "type": "quantitative", "scale": {"type": "sqrt", "zero": True, "domain": [0, 100], "range": [18, 125]}},
             "color": {"value": WEEKDAY if day == "Weekday" else WEEKEND},
             "opacity": {"condition": {"param": "hourHover", "empty": True, "value": 1}, "value": 0.35},
             "tooltip": [{"field": "time_label", "title": "Time"}, {"field": "pct", "title": "% asleep", "format": ".1f"}]},
         "params": [{"name": "hourHover", "select": {"type": "point", "fields": ["hour_start"], "on": "pointerover", "clear": "pointerout"}}]},
        {"data": {"values": [{"r": 50}]},
         "mark": {"type": "arc", "filled": False, "stroke": "#ffffff", "strokeWidth": 1, "strokeDash": [3, 3]},
         "encoding": {"theta": {"datum": 0, "type": "quantitative", "scale": {"domain": [0, 24]}}, "theta2": {"datum": 24},
                      "radius": {"field": "r", "type": "quantitative"}}},
        {"mark": {"type": "text", "radius": 140, "fontSize": 11, "color": MUTED},
         "encoding": {"theta": {"field": "hour_start", "type": "quantitative", "scale": {"domain": [0, 24]}},
                      "text": {"field": "hourlabel"}}}]}
spec("radial_clock", "Weekday alarms get most of us up by 8 am; at the weekend 6 in 10 are still asleep at 7",
     ["% of people aged 15+ asleep in each hour (midnight at the top, clockwise)", "ABS, How Australians Use Their Time 2020–21, Tables 13–17"], {
    "data": {"url": "data/tus_activity_by_hour.csv", "format": {"type": "csv", "parse": {"hour_start": "number", "pct": "number"}}},
    "params": [{"name": "sexSel", "value": "Persons",
                "bind": {"input": "radio", "options": ["Persons", "Females", "Males"], "labels": ["Everyone", "Women", "Men"], "name": "Show: "}}],
    "transform": [
        {"filter": "datum.activity == 'Sleep' && datum.sex == sexSel && datum.day_type != 'All days'"},
        {"calculate": "datum.hour_start + 1", "as": "hour_end"},
                {"calculate": "datum.hour_start % 3 != 0 ? '' : datum.hour_start == 0 ? '12 am' : datum.hour_start == 12 ? '12 pm' : datum.hour_start < 12 ? datum.hour_start + ' am' : (datum.hour_start - 12) + ' pm'", "as": "hourlabel"}],
    "hconcat": [clock_layer("Weekday"), clock_layer("Weekend")],
    "resolve": {"scale": {"color": "independent"}}})

# 5. Slope weekday vs weekend (ABS 2024)
spec("slope_weekend", "Weekends buy back about 44 extra minutes of sleep",
     ["Average minutes asleep a day, people aged 15+", "ABS, How Australians Use Their Time 2024, Table 4.1"], {
    "width": "container", "height": 260,
    "data": {"url": "data/tus2024_sleep_summary.csv"},
    "transform": [{"filter": "datum.day_type != 'All days'"},
                  {"calculate": "datum.sex == 'All' ? 'Everyone' : datum.sex", "as": "who"},
                  {"calculate": "floor(datum.sleep_min/60) + 'h ' + (datum.sleep_min % 60) + 'm'", "as": "hm"},
                  {"calculate": "datum.who == 'Men' ? -9 : datum.who == 'Women' ? 9 : 0", "as": "nudge"}],
    "encoding": {
        "x": {"field": "day_type", "type": "ordinal", "title": None, "scale": {"padding": 0.5},
              "axis": {"labelAngle": 0, "labelFontSize": 13, "domain": False, "ticks": False, "orient": "top"}},
        "y": {"field": "sleep_min", "type": "quantitative", "title": "Minutes asleep", "scale": {"domain": [500, 570]},
              "axis": {"grid": True, "values": [500, 510, 520, 530, 540, 550, 560, 570]}},
        "color": {"field": "who", "type": "nominal", "title": None,
                  "scale": {"domain": ["Women", "Men", "Everyone"], "range": [WOMEN, MEN, INK]}, "legend": None}},
    "layer": [
        {"mark": {"type": "line", "strokeWidth": 2}, "encoding": {"detail": {"field": "who"}}},
        {"mark": {"type": "circle", "size": 70, "opacity": 1},
         "encoding": {"tooltip": [{"field": "who", "title": "Who"}, {"field": "day_type", "title": "Day"}, {"field": "hm", "title": "Sleep"}]}},
        {"transform": [{"filter": "datum.day_type == 'Weekend'"}],
         "mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 12, "dy": {"expr": "datum.nudge"}},
         "encoding": {"text": {"field": "who"}}},
        {"transform": [{"filter": "datum.day_type == 'Weekday' && datum.who == 'Everyone'"}],
         "mark": {"type": "text", "align": "right", "dx": -12, "fontSize": 12},
         "encoding": {"text": {"field": "hm"}}},
        {"transform": [{"filter": "datum.day_type == 'Weekend' && datum.who == 'Everyone'"}],
         "mark": {"type": "text", "align": "left", "dx": 70, "fontSize": 12, "fontWeight": 700},
         "encoding": {"text": {"value": "+44 min"}, "color": {"value": WEEKEND}}}]})

# 6. Sleep by age (SHF 2016): the young paradox
spec("line_age_quality", "Young adults sleep the longest but feel the worst",
     ["% of adults who usually get enough sleep, and % who often wake up unrefreshed, by age",
      "Sleep Health Foundation, Sleep Health Survey of Australian Adults 2016, Table 1"], {
    "width": "container", "height": 300,
    "data": {"url": "data/shf2016_by_age.csv"},
    "transform": [{"filter": "datum.age_group != 'All' && (datum.measure == 'adequate_sleep' || datum.measure == 'wake_unrefreshed')"},
                  {"calculate": "datum.measure == 'adequate_sleep' ? 'Get enough sleep' : 'Wake up unrefreshed'", "as": "label"}],
    "encoding": {
        "x": {"field": "age_group", "type": "ordinal", "title": "Age group", "sort": ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
              "axis": {"labelAngle": 0}},
        "y": {"field": "pct", "type": "quantitative", "title": "% of adults", "scale": {"domain": [0, 80]}},
        "color": {"field": "label", "type": "nominal", "title": None,
                  "scale": {"domain": ["Get enough sleep", "Wake up unrefreshed"], "range": [WEEKDAY, WEEKEND]},
                  "legend": {"orient": "top", "direction": "horizontal"}}},
    "layer": [
        {"mark": {"type": "line", "strokeWidth": 2.5, "point": {"size": 60, "filled": True}},
         "encoding": {"tooltip": [{"field": "label", "title": "Measure"}, {"field": "age_group", "title": "Age"},
                                  {"field": "pct", "title": "% of adults", "format": ".1f"}]}},
        {"transform": [{"filter": "datum.age_group == '18-24' || datum.age_group == '65+'"}],
         "mark": {"type": "text", "dy": -12, "fontSize": 12, "fontWeight": 600},
         "encoding": {"text": {"field": "pct", "type": "quantitative", "format": ".0f"}}}]})

# 7. Life circumstances diverging bar (ABS 2024)
CIRC_ORDER = ["Parent, youngest child under 1", "Parent, youngest child aged 1", "Parent, youngest child 2–4",
              "Parent, youngest child 5–11", "Parent, youngest child 12–14", "No child under 15 at home",
              "Carer", "Not a carer", "Volunteer", "Not a volunteer", "Has a disability", "No disability"]
spec("bar_circumstance", "A baby at home costs about half an hour of sleep a night",
     ["Minutes asleep a day compared with the average adult (528 minutes), people aged 15+",
      "ABS, How Australians Use Their Time 2024, Tables 5, 11, 12 and 13"], {
    "width": "container", "height": {"step": 28},
    "data": {"url": "data/sleep_by_circumstance.csv"},
    "params": [{"name": "circSex", "value": "All",
                "bind": {"input": "radio", "options": ["All", "Women", "Men"], "labels": ["Everyone", "Women", "Men"], "name": "Show: "}}],
    "transform": [{"filter": "datum.sex == circSex"},
                  {"calculate": "datum.sleep_min - 528", "as": "diff"},
                  {"calculate": "datum.diff >= 0 ? 'More than average' : 'Less than average'", "as": "dir"},
                  {"calculate": "(datum.diff > 0 ? '+' : '') + datum.diff + ' min'", "as": "difflabel"},
                  {"calculate": "floor(datum.sleep_min/60) + 'h ' + (datum.sleep_min % 60) + 'm'", "as": "hm"}],
    "encoding": {
        "y": {"field": "group", "type": "nominal", "title": None, "sort": CIRC_ORDER,
              "axis": {"domain": False, "ticks": False, "labelLimit": 320}},
        "x": {"field": "diff", "type": "quantitative", "title": "Minutes compared with the average adult",
              "scale": {"domain": [-40, 20]}, "axis": {"grid": True, "values": [-40, -30, -20, -10, 0, 10, 20]}}},
    "layer": [
        {"mark": {"type": "bar", "height": 16, "cornerRadius": 3},
         "encoding": {"color": {"field": "dir", "type": "nominal", "title": None,
                                "scale": {"domain": ["Less than average", "More than average"], "range": [WEEKEND, WEEKDAY]},
                                "legend": {"orient": "top", "direction": "horizontal"}},
                      "tooltip": [{"field": "group", "title": "Group"}, {"field": "hm", "title": "Sleep a day"},
                                  {"field": "difflabel", "title": "Compared with average"}]}},
        {"mark": {"type": "rule", "color": INK}, "encoding": {"x": {"datum": 0}, "y": None}},
        {"mark": {"type": "text", "fontSize": 12, "dx": {"expr": "datum.diff >= 0 ? 6 : -6"},
                  "align": {"expr": "datum.diff >= 0 ? 'left' : 'right'"}},
         "encoding": {"text": {"field": "difflabel"}}}]})

# 8. Lifestyle dumbbell (SHF 2016 Table 9)
spec("dumbbell_lifestyle", "Late-night screens, work and caffeine go with poorer sleep",
     ["% of adults with two or more sleep problems, healthier vs riskier habit",
      "Sleep Health Foundation, Survey of Australian Adults 2016, Table 9"], {
    "width": "container", "height": {"step": 46},
    "data": {"values": [
        {"habit": "Work in the hour before bed", "level": "Never", "kind": "Healthier habit", "pct": 36.5},
        {"habit": "Work in the hour before bed", "level": "Nightly", "kind": "Riskier habit", "pct": 71.4},
        {"habit": "Sleep before work days", "level": "5.5 to 9 hours", "kind": "Healthier habit", "pct": 43.6},
        {"habit": "Sleep before work days", "level": "Under 5.5 hours", "kind": "Riskier habit", "pct": 75.7},
        {"habit": "Caffeinated drinks a day", "level": "None", "kind": "Healthier habit", "pct": 40.5},
        {"habit": "Caffeinated drinks a day", "level": "6 or more", "kind": "Riskier habit", "pct": 60.6},
        {"habit": "Internet in the hour before bed", "level": "Never", "kind": "Healthier habit", "pct": 38.8},
        {"habit": "Internet in the hour before bed", "level": "Nightly", "kind": "Riskier habit", "pct": 58.5}]},
    "encoding": {
        "y": {"field": "habit", "type": "nominal", "title": None, "sort": {"field": "pct", "op": "max", "order": "descending"},
              "axis": {"domain": False, "ticks": False, "labelLimit": 320}},
        "x": {"field": "pct", "type": "quantitative", "title": "% with two or more sleep problems",
              "scale": {"domain": [0, 100]}, "axis": {"grid": True}}},
    "layer": [
        {"mark": {"type": "rule", "strokeWidth": 3, "color": "#c9c5bb"}, "encoding": {"x": {"aggregate": "min", "field": "pct"}, "x2": {"aggregate": "max", "field": "pct"}}},
        {"mark": {"type": "circle", "size": 140, "opacity": 1, "stroke": "#fbfaf7", "strokeWidth": 1.5},
         "encoding": {"color": {"field": "kind", "type": "nominal", "title": None,
                                "scale": {"domain": ["Healthier habit", "Riskier habit"], "range": [WEEKDAY, WEEKEND]},
                                "legend": {"orient": "top", "direction": "horizontal"}},
                      "tooltip": [{"field": "habit", "title": "Habit"}, {"field": "level", "title": "Level"},
                                  {"field": "pct", "title": "% with 2+ problems", "format": ".1f"}]}},
        {"mark": {"type": "text", "dy": -14, "fontSize": 11, "color": MUTED}, "encoding": {"text": {"field": "level"}}}]})

# 9. Work and driving impacts: two bases, shown as two panels
spec("bar_work_impacts", "Sleepiness follows people to work and onto the road",
     ["% because of sleepiness or a sleep problem; work questions were answered by people in work",
      "Sleep Health Foundation, Sleep Health Survey of Australian Adults 2016, Table 7"], {
    "data": {"values": [
        {"base": "Among people in work", "impact": "Made errors at work (past 3 months)", "pct": 29.0, "note": "45.8% of 18–24 and 39.2% of 25–34 year olds"},
        {"base": "Among people in work", "impact": "Fell or nearly fell asleep on the job (past month)", "pct": 17.1, "note": "27.1% of 18–24 year olds"},
        {"base": "Among people in work", "impact": "Missed a day of work (past 4 weeks)", "pct": 17.0, "note": "30.4% of 25–34 year olds"},
        {"base": "Among all adults", "impact": "Ever nodded off while driving", "pct": 19.9, "note": "22.3% of men, 17.2% of women"},
        {"base": "Among all adults", "impact": "Drove drowsy every week (past year)", "pct": 16.0, "note": "30.1% of 25–34 year olds"},
        {"base": "Among all adults", "impact": "Crashed after dozing off (past year)", "pct": 5.5, "note": "10.1% of 25–34 year olds"}]},
    "width": "container", "height": {"step": 32},
    "encoding": {
        "y": {"field": "impact", "type": "nominal", "title": None,
              "sort": ["Made errors at work (past 3 months)", "Fell or nearly fell asleep on the job (past month)",
                       "Missed a day of work (past 4 weeks)", "Ever nodded off while driving",
                       "Drove drowsy every week (past year)", "Crashed after dozing off (past year)"],
              "axis": {"domain": False, "ticks": False, "labelLimit": 320}},
        "x": {"field": "pct", "type": "quantitative", "title": "% of the group", "scale": {"domain": [0, 35]}, "axis": {"grid": True}},
        "color": {"field": "base", "type": "nominal", "title": None,
                  "scale": {"domain": ["Among people in work", "Among all adults"], "range": [WEEKDAY, "#8fa6d6"]},
                  "legend": {"orient": "top", "direction": "horizontal"}}},
    "layer": [
        {"mark": {"type": "bar", "height": 18, "cornerRadiusEnd": 3},
         "encoding": {"tooltip": [{"field": "impact", "title": "Impact"}, {"field": "base", "title": "Out of"},
                                  {"field": "pct", "title": "%", "format": ".1f"}, {"field": "note", "title": "Highest group"}]}},
        {"mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 12},
         "encoding": {"text": {"field": "pct", "type": "quantitative", "format": ".0f"}, "color": {"value": INK}}}]})

# 10. Wellbeing heatmap (SHF 2025)
spec("heatmap_wellbeing", "People with back pain and mental health conditions sleep worst on every measure",
     ["Sleep measures by health condition. Colour: how many times worse than adults with neither", "Sleep Health Foundation, Aussie Sleep Snapshot 2025 (n = 1,012)"], {
    "width": "container", "height": {"step": 48},
    "data": {"url": "data/shf2025_by_group.csv"},
    "transform": [
        {"filter": "datum.group_type == 'health'"},
        {"fold": ["sleep_hours", "poor_nights_per_week", "productivity_days_lost", "pct_consistent_pattern", "pct_insomnia", "pct_sleep_apnoea"],
         "as": ["metric", "value"]},
        {"calculate": "toNumber(datum.value)", "as": "value"},
        {"joinaggregate": [{"op": "max", "field": "value", "as": "dummy"}]},
        {"window": [{"op": "first_value", "field": "value", "as": "neither"}], "groupby": ["metric"],
         "sort": [{"field": "is_neither", "order": "descending"}]},
        {"lookup": "metric", "from": {"data": {"values": [
            {"metric": "sleep_hours", "label": "Sleep (hours)", "better": "higher", "fmt": "h", "ord": 1},
            {"metric": "poor_nights_per_week", "label": "Poor nights/week", "better": "lower", "fmt": "n", "ord": 2},
            {"metric": "productivity_days_lost", "label": "Work days hit/week", "better": "lower", "fmt": "n", "ord": 3},
            {"metric": "pct_consistent_pattern", "label": "Regular routine", "better": "higher", "fmt": "%", "ord": 4},
            {"metric": "pct_insomnia", "label": "Insomnia", "better": "lower", "fmt": "%", "ord": 5},
            {"metric": "pct_sleep_apnoea", "label": "Sleep apnoea", "better": "lower", "fmt": "%", "ord": 6}]},
            "key": "metric", "fields": ["label", "better", "fmt", "ord"]}}],
    "mark": "rect"})
# heatmap needs the 'Neither' reference: compute with joinaggregate on a flag instead of the window trick
hm = specs["heatmap_wellbeing"]
hm["transform"] = hm["transform"][:3] + [
    {"calculate": "datum.group == 'Neither' ? datum.value : null", "as": "ref"},
    {"joinaggregate": [{"op": "max", "field": "ref", "as": "neither"}], "groupby": ["metric"]},
    hm["transform"][-1],
    {"calculate": "datum.better == 'lower' ? datum.value / datum.neither : datum.neither / datum.value", "as": "times_worse"},
    {"calculate": "datum.fmt == '%' ? format(datum.value, '.0f') + '%' : format(datum.value, '.1f')", "as": "valuelabel"},
    {"calculate": "datum.group == 'Neither' ? 'Neither condition' : datum.group", "as": "grouplabel"}]
del hm["mark"]
hm["encoding"] = {
    "x": {"field": "label", "type": "nominal", "title": None, "sort": {"field": "ord"},
          "axis": {"orient": "top", "labelAngle": 0, "labelLimit": 200, "domain": False, "ticks": False,
                   "labelExpr": "split(datum.label, ' a ')[0] == datum.label ? datum.label : datum.label"}},
    "y": {"field": "grouplabel", "type": "nominal", "title": None,
          "sort": ["Neither condition", "Back pain only", "Mental health only", "Both"],
          "axis": {"domain": False, "ticks": False}}}
hm["layer"] = [
    {"mark": {"type": "rect", "stroke": "#fbfaf7", "strokeWidth": 2, "cornerRadius": 3},
     "encoding": {"color": {"field": "times_worse", "type": "quantitative", "title": "Times worse than neither",
                            "scale": {"type": "threshold", "domain": [1.1, 1.5, 2, 3], "range": ["#f1efe9", "#f6dcb5", "#e9b46a", "#d08a1e", "#8f5a0c"]},
                            "legend": {"orient": "bottom", "direction": "horizontal", "titleLimit": 300, "labelExpr": "isFinite(datum.value) ? datum.value + '×' : ''"}},
                  "tooltip": [{"field": "grouplabel", "title": "Group"}, {"field": "label", "title": "Measure"},
                              {"field": "valuelabel", "title": "Value"},
                              {"field": "times_worse", "title": "Times worse than neither", "format": ".1f"}]}},
    {"mark": {"type": "text", "fontSize": 13},
     "encoding": {"text": {"field": "valuelabel"},
                  "color": {"condition": {"test": "datum.times_worse >= 2", "value": "#ffffff"}, "value": INK}}}]
hm["width"] = "container"

# 11. PHN choropleth (existing, restyled here)
def phn_choro(field, title_suffix=""):
    return {
        "projection": AUS_PROJ,
        "layer": [
            {"transform": [{"calculate": "'No data (suppressed)'", "as": "status"}],
             "mark": {"type": "geoshape", "fill": "#e4e4ea", "stroke": "#ffffff", "strokeWidth": 0.5},
             "encoding": {"tooltip": [{"field": "properties.PHN_NAME", "title": "PHN"}, {"field": "status", "title": "Distress"}]}},
            {"transform": [
                {"lookup": "properties.PHN_CODE", "from": {"data": {"url": "data/phidu_phn_2022.csv"}, "key": "code",
                                                         "fields": ["k10_high_persons", "k10_high_female", "k10_high_male"]}},
                {"filter": "isValid(datum.k10_high_persons)"}],
             "mark": {"type": "geoshape", "stroke": "#ffffff", "strokeWidth": 0.5},
             "encoding": {
                 "color": {"field": field, "type": "quantitative",
                           "scale": {"type": "threshold", "domain": [11, 13, 15, 17], "range": PURPLES},
                           "legend": {"orient": "top-left", "title": "% adults in high distress"}},
                 "tooltip": [{"field": "properties.PHN_NAME", "title": "PHN"}, {"field": "properties.STATE_NAME", "title": "State"},
                             {"field": "k10_high_persons", "type": "quantitative", "title": "All adults (%)", "format": ".1f"},
                             {"field": "k10_high_female", "type": "quantitative", "title": "Women (%)", "format": ".1f"},
                             {"field": "k10_high_male", "type": "quantitative", "title": "Men (%)", "format": ".1f"}]}}]}
spec("map_distress_phn", "Distress is worst in regional Queensland, NSW and Tasmania",
     ["% of adults with high or very high distress (K10), age-standardised, by PHN, 2022", "Grey: Western Queensland, estimate suppressed. PHIDU Social Health Atlas"], {
    "width": "container", "height": 460,
    "data": {"url": "data/phn.topojson", "format": {"type": "topojson", "feature": "phn"}}, **phn_choro("k10_high_persons")})

# 12. Small multiples: women vs men
sm = {"data": {"url": "data/phn.topojson", "format": {"type": "topojson", "feature": "phn"}}, "hconcat": []}
for f, lab in [("k10_high_female", "Women"), ("k10_high_male", "Men")]:
    v = phn_choro(f); v["width"] = 470; v["height"] = 380
    v["layer"][1]["encoding"]["color"]["legend"] = {"orient": "bottom-left", "title": "% in high distress", "direction": "horizontal"} if lab == "Women" else None
    v["title"] = {"text": lab, "fontSize": 14, "font": "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif", "fontWeight": 600}
    sm["hconcat"].append(v)
sm["resolve"] = {"scale": {"color": "shared"}}
spec("map_distress_sex", "Women report more distress than men in every region",
     ["% of women and of men with high or very high psychological distress, by PHN, 2022", "PHIDU Social Health Atlas of Australia"], sm)

# 13. Proportional symbol: number of distressed adults
spec("map_distress_count", "", [], {
    "hconcat": [
        {"name": "symmap", "width": 520, "height": 440, "projection": AUS_PROJ,
         "layer": [
            {"data": {"url": "data/aus_states.topojson", "format": {"type": "topojson", "feature": "aus_states"}},
             "mark": {"type": "geoshape", "fill": "#ece9e2", "stroke": "#ffffff", "strokeWidth": 1}},
            {"data": {"url": "data/phn_distress_counts.csv"},
             "transform": [{"filter": "isValid(datum.distressed_adults) && datum.distressed_adults > 0"}],
             "params": [{"name": "hoverMap", "select": {"type": "point", "fields": ["code"], "on": "pointerover", "clear": "pointerout"}}],
             "mark": {"type": "circle", "stroke": "#ffffff", "strokeWidth": 1},
             "encoding": {
                 "longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"},
                 "size": {"field": "distressed_adults", "type": "quantitative", "title": "Distressed adults",
                          "scale": {"type": "linear", "domain": [0, 210000], "range": [0, 1500]},
                          "legend": {"orient": "top-left", "values": [25000, 100000, 200000], "format": ",.0f",
                                     "symbolFillColor": "#5e4a9e", "symbolOpacity": 0.6, "symbolStrokeColor": "#ffffff"}},
                 "color": {"condition": {"test": {"or": [{"param": "hoverMap", "empty": False}, {"param": "hoverBar", "empty": False}]}, "value": ACCENT}, "value": "#5e4a9e"},
                 "opacity": {"condition": {"test": {"or": [{"param": "hoverMap", "empty": False}, {"param": "hoverBar", "empty": False}]}, "value": 0.95}, "value": 0.6},
                 "order": {"field": "distressed_adults", "sort": "descending"},
                 "tooltip": [{"field": "name", "title": "PHN"}, {"field": "state", "title": "State"},
                             {"field": "distressed_adults", "title": "Distressed adults (est.)", "format": ",.0f"}]}}]},
        {"name": "symbars", "width": 200, "height": {"step": 14},
         "data": {"url": "data/phn_distress_counts.csv"},
         "transform": [{"filter": "isValid(datum.distressed_adults) && datum.distressed_adults > 0"}],
         "params": [{"name": "hoverBar", "select": {"type": "point", "fields": ["code"], "on": "pointerover", "clear": "pointerout"}}],
         "mark": {"type": "bar", "height": 10, "cornerRadiusEnd": 2},
         "encoding": {
             "y": {"field": "name", "type": "nominal", "title": None, "sort": "-x",
                   "axis": {"domain": False, "ticks": False, "labelFontSize": 11, "labelLimit": 220}},
             "x": {"field": "distressed_adults", "type": "quantitative", "title": "Distressed adults",
                   "axis": {"format": "~s", "grid": True, "tickCount": 4}},
             "color": {"condition": {"test": {"or": [{"param": "hoverMap", "empty": False}, {"param": "hoverBar", "empty": False}]}, "value": ACCENT}, "value": "#5e4a9e"},
             "tooltip": [{"field": "name", "title": "PHN"}, {"field": "distressed_adults", "title": "Distressed adults (est.)", "format": ",.0f"}]}}],
    "spacing": 40})

# 15. Sunrise scalar field
SUN_LABELS = ["before 4:30 am", "4:30–5:00 am", "5:00–5:30 am", "5:30–6:00 am", "6:00–6:30 am", "6:30–7:00 am", "7:00–7:30 am", "after 7:30 am"]
SUN = ["#fff4c8", "#fde2a0", "#f6c27a", "#e79a5c", "#c96f4f", "#96505a", "#5e3a5e", "#2b2a55"]
spec("map_sunrise", "In summer the sun rises before 5 am in Brisbane, almost an hour before Sydney",
     ["Clock time of sunrise on the longest and shortest days, white lines every 30 minutes", "Qld, WA and the NT have no daylight saving. Calculated with NOAA solar equations"], {
    "width": "container", "height": 440, "projection": AUS_PROJ,
    "params": [{"name": "season", "value": "Summer (21 December)",
                "bind": {"input": "radio", "options": ["Summer (21 December)", "Winter (21 June)"], "labels": ["Summer (21 December)", "Winter (21 June)"], "name": "Day: "}}],
    "layer": [
        {"data": {"url": "data/sunrise_bands.topojson", "format": {"type": "topojson", "feature": "bands"}},
         "transform": [{"filter": "datum.properties.season == season"}],
         "mark": {"type": "geoshape", "stroke": "#ffffff", "strokeWidth": 0.6},
         "encoding": {
             "color": {"field": "properties.label", "type": "ordinal", "title": "Sunrise (clock time)",
                       "scale": {"domain": SUN_LABELS, "range": SUN},
                       "legend": {"orient": "bottom", "direction": "horizontal", "columns": 4, "symbolType": "square",
                                  "symbolSize": 160, "labelFontSize": 12, "columnPadding": 16, "rowPadding": 6}},
             "tooltip": [{"field": "properties.state", "title": "State"}, {"field": "properties.label", "title": "Sunrise"}]}},
        {"data": {"url": "data/aus_states.topojson", "format": {"type": "topojson", "feature": "aus_states"}},
         "mark": {"type": "geoshape", "filled": False, "stroke": INK, "strokeWidth": 0.8}},
        {"data": {"url": "data/sunrise_cities.csv"},
         "transform": [{"filter": "datum.season == season"}, {"calculate": "datum.city + ' ' + datum.sunrise_label", "as": "lab"}],
         "encoding": {"longitude": {"field": "lon", "type": "quantitative"}, "latitude": {"field": "lat", "type": "quantitative"}},
         "layer": [
             {"mark": {"type": "circle", "size": 34, "color": INK, "stroke": "#ffffff", "strokeWidth": 1, "opacity": 1},
              "encoding": {"tooltip": [{"field": "city", "title": "City"}, {"field": "sunrise_label", "title": "Sunrise"}]}},
             {"mark": {"type": "text", "fontSize": 11, "fontWeight": 600, "color": INK,
                       "dx": {"expr": "datum.city == 'Adelaide' || datum.city == 'Melbourne' ? -6 : 6"},
                       "align": {"expr": "datum.city == 'Adelaide' || datum.city == 'Melbourne' ? 'right' : 'left'"},
                       "dy": {"expr": "datum.city == 'Canberra' ? 8 : datum.city == 'Sydney' ? -4 : 0"}},
              "encoding": {"text": {"field": "lab"}}}]}]})

for k, v in specs.items():
    with open(f"{OUT}/{k}.vg.json", "w") as f:
        json.dump(v, f, indent=2, ensure_ascii=False); f.write("\n")
print(list(specs))
