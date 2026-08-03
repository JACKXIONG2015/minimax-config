# PDF Build — How to Render the Visual Report

The skill ships with a self-contained PDF builder. After writing `report.md`,
the agent also produces a `config.json` and runs the builder to get a
shareable PDF.

## Why a separate config?

The markdown is for humans (long-form, flexible). The PDF needs **structured
data** so the template can place the right chart at the right slot, color the
right KPI, fill the right table cell. The config is that structured form.

You can think of the workflow as:

```
report.md   ←  what you write, narrative form
   ↓
config.json ←  what the PDF needs, structured form
   ↓
build_pdf.py ← renders charts + HTML → PDF
```

## Build command

```bash
python scripts/pdf-build/build_pdf.py \
    --config config.json \
    --output <ShortName>-竞品背调-可视化版.pdf
```

The script:
- Auto-detects a CJK font (SimHei on Windows, PingFang on macOS, Noto on Linux)
- Generates 7 matplotlib charts (PNG, base64-embedded)
- Renders an HTML template
- Outputs PDF via xhtml2pdf
- Also writes a sibling `.html` for layout debugging

Takes ~2 seconds. No external services.

## Config schema — top-level keys

| Key | Type | Required | Notes |
|---|---|---|---|
| `company` | object | yes | name_en, name_zh, short_name, city_zh, website, tagline |
| `report` | object | yes | date, version |
| `stats_banner` | array[4] | yes | top banner (num + lbl) |
| `kpis` | array[4] | yes | KPI cards (label, value, unit, color, desc) |
| `lead_text` | string | yes | exec summary lead |
| `insight_text` | string | yes | "核心判断" callout |
| `basics_rows` | array | yes | company info table rows |
| `basics_insight` | string | yes | callout below basics |
| `products.lines` | array[5] | yes | product line table |
| `products.efficiency_benchmark` | array | optional | if present, chart 1 renders |
| `products.power_range` | object | optional | if present, chart 2 renders |
| `threats` | object | yes | level_distribution, dimensions, conclusion |
| `confidence.dims` | array[12] | yes | confidence scores per dim |
| `swot` | object | yes | S/W/O/T arrays + insights |
| `digital` | object | yes | channels + channels_table |
| `recs` | object | yes | scatter, top3, backup |
| `gaps` | object | yes | free_sources, paid_sources |
| `footer_note` | string | optional | bottom-of-page note |

**Optional chart-data omission:** if you leave out `products.efficiency_benchmark`
or `products.power_range`, the corresponding chart section is hidden entirely
(no empty placeholder). Use this when the data isn't relevant for the
competitor (e.g., a SaaS company has no μmol/J).

## Color / class codes

KPI `color`: `blue`, `green`, `orange`, `amber`, `red`, `teal`, `purple`

Pill `*_class`: `ok` (green), `warn` (amber), `bad` (red), `good` (blue), `best` (purple)

## Full example

See `scripts/pdf-build/examples/shining-lighting.json` for a complete,
copy-paste-ready config that covers all 7 charts and 9 sections.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Chinese renders as boxes | No CJK font found | Install SimHei / Noto Sans CJK |
| `ModuleNotFoundError: matplotlib` | Deps not installed | `pip install -r scripts/pdf-build/requirements.txt` |
| Charts are too small | width=500 default | The `width` attribute is fixed (xhtml2pdf can't compute %); edit template if you need bigger |
| Table cell content gets cut | A column has too much text | Shorten the text in the config; xhtml2pdf can't auto-shrink |
| Page break in the wrong place | `avoid-break` class missing | Add `avoid-break` to the `<div class="chart-card">` wrapper |

## Notes on xhtml2pdf

The PDF engine does **NOT** support:
- Flexbox / grid
- CSS gradients (use solid colors)
- `position: relative / absolute`
- CSS variables (`--accent`)
- `::before` / `::after` with `content`
- `@page :first` pseudo-class

If you ever need to extend the template, stick to:
- Tables for layout
- `background-color` (not `background: ...` shorthand)
- Inline `style=` on individual elements
- Bordered cells, simple spans
