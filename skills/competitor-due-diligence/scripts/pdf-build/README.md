# PDF Build for competitor-due-diligence

Generates a visual PDF report (cover + 9 sections + 7 charts) from a structured
config JSON. The same template renders any competitor — just fill the JSON.

## Quick start

```bash
# Install deps (one time)
pip install -r requirements.txt

# Build the example (Shining Lighting)
python build_pdf.py --config examples/shining-lighting.json --output report.pdf
```

## How to use it for a new competitor

After writing `report.md` (Markdown report), produce a `config.json` next to it
that follows the schema in `examples/shining-lighting.json`. Then:

```bash
python build_pdf.py --config config.json --output <ShortName>-竞品背调-可视化版.pdf
```

The script will:

1. Auto-detect a CJK font (SimHei on Windows, PingFang on macOS, Noto on Linux)
   and register it with ReportLab for proper Chinese rendering.
2. Generate 7 charts as base64-encoded PNGs (matplotlib).
3. Render the HTML template (xhtml2pdf-compatible: tables, no flexbox/grid).
4. Output a single PDF, ~700 KB, 14-15 pages.

## Config schema (top-level keys)

| Key | Required | Description |
|---|---|---|
| `company` | yes | name_en, name_zh, short_name, city_zh, website, tagline |
| `report` | yes | date, version |
| `stats_banner` | yes | 4 items for the top banner (num + lbl) |
| `kpis` | yes | 4 KPI cards (label, value, unit, color, desc) |
| `lead_text` | yes | executive summary lead paragraph |
| `insight_text` | yes | "核心判断" callout text |
| `basics_rows` | yes | company basic info table |
| `basics_insight` | yes | callout below basics table |
| `products.lines` | yes | product line table (5 rows) |
| `products.efficiency_benchmark` | optional | chart 1 data (omit to hide chart) |
| `products.power_range` | optional | chart 2 data |
| `threats` | yes | level_distribution, dimensions, conclusion |
| `confidence.dims` | yes | 12-dimension confidence scores |
| `swot` | yes | S/W/O/T arrays + insights |
| `digital` | yes | channels + channels_table |
| `recs` | yes | scatter, top3, backup |
| `gaps` | yes | free_sources, paid_sources |
| `footer_note` | optional | bottom-of-page note |

Optional `charts.*` overrides per-chart title/label without changing the script.

## Color codes for KPIs

`blue`, `green`, `orange`, `amber`, `red`, `teal`, `purple`

## Pill classes

`ok` (green), `warn` (amber), `bad` (red), `good` (blue), `best` (purple)

## Notes for the agent (skill runner)

- The script is self-contained. No external services called.
- It writes both the PDF and a sibling `.html` (for debugging layout).
- On font issues, the script falls back to STSong-Light (xhtml2pdf built-in)
  but Chinese may render as boxes if the system has no CJK font at all.
- xhtml2pdf does NOT support modern CSS (flexbox, grid, gradients,
  pseudo-elements). The template uses table-based layout + solid colors only.
