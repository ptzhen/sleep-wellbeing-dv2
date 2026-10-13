# Sleep and Wellbeing in Australia

FIT3179 Data Visualisation 2. Live site: https://ptzhen.github.io/sleep-wellbeing-dv2/

- `index.html`, `css/style.css`, `js/main.js`: the page
- `js/specs/`: one Vega-Lite spec per chart (the chart's div id matches the file name)
- `data/`: cleaned CSVs, TopoJSON boundaries and derived tables
- `scripts/`: Python used to clean the source spreadsheets and derive tables
  - `extract_abs_tus.py`, `extract_phidu.py`: ABS Time Use and PHIDU spreadsheets to CSV
  - `phn_distress_counts.py`: estimated distressed adults per PHN, with a point inside each PHN
  - `sunrise_field.py`: sunrise clock time grid and 30-minute isolines (NOAA equations)
  - `derive_tables.py`: sleep by life circumstance, capital vs rest of state, city sunrise times
- `sketch/`: hand-drawn design sketch (added last)
