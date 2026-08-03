---
name: competitor-due-diligence
displayNames:
  zh-Hans: 竞品背调
  en: Competitor Due Diligence
description: |
  Conduct structured competitor background research covering 12 dimensions (basic info,
  financials, supply chain, product & pricing, channels, brand & marketing, customers,
  technology & IP, business trends, sales platforms & social, compliance, strategic moves).
  Use when the user asks for competitor analysis, rival profiling, competitive
  intelligence, market research on competitors, or "due diligence on a competitor".

  Use this skill when the user says things like (Chinese):
  竞品背调, 竞对分析, 竞对调研, 同行调研, 竞品分析, 竞争对手调查,
  调研一下某公司, 看看某家竞品, 分析一下对手, 帮我做一份竞品报告.

  Use this skill when the user says things like (English):
  competitor analysis, competitor research, competitive intelligence, rival profiling,
  due diligence on a competitor, competitive landscape analysis.

  Do NOT use this skill for:
  - General market sizing without a specific competitor (use deep-research instead)
  - Customer / supplier due diligence on a partner company (no competitor framing)
  - Internal company self-assessment (use a different framework)
version: 1.0
author: MiniMax-jack
---

# Competitor Due Diligence (竞品背调)

Structured 12-dimension framework for competitor background research. Use this to
produce a consistent, comparable profile for any rival — from quick scans to deep dives.

## When to load (hard rules)

- The user names a specific competitor or a list of competitors → load.
- The user wants a side-by-side comparison of multiple rivals → load.
- The user asks "how should I research a competitor" / "what dimensions matter" → load.

Skip this skill if the user just wants a market size report with no competitor
named, or wants partner / customer due diligence.

## Procedure

### Step 1 — Clarify scope (always, even if brief)

Ask only what truly changes the output. Default to quick mode if user is in a hurry.

| Question | Why it matters | Default if user doesn't answer |
|---|---|---|
| Which competitor(s)? | Scope | Single named competitor |
| Industry / segment? | Which dimensions to prioritize | Cross-border e-commerce |
| Depth: quick / full? | How many dimensions to actually fill | Quick (high-priority dims only) |
| Output format? | Markdown report / spreadsheet / slides | Markdown report |
| Time horizon? | Years of history to cover | Last 3–5 years |

If depth is `quick`, only do the 4 high-priority dimensions for the industry.
If `full`, do all 12.

### Step 2 — Apply the 12-dimension framework

Walk through each dimension per `references/dimensions.md`. For each dimension:

1. Sub-items list (in `dimensions.md`)
2. Pick data sources from `references/data-sources.md` (primary + secondary)
3. Execute the research method (in `dimensions.md`)
4. Capture findings + source URL + confidence level (high / medium / low)
5. Flag data gaps explicitly — do NOT invent data

Use the prioritized dimension matrix in `references/industry-prioritization.md` to
decide which dimensions deserve deep treatment for the target industry.

### Step 3 — Synthesize

Read `references/output-template.md` and produce the report in the agreed format.
Always include the SWOT block and the "Strategic Recommendations" section —
those are what the user actually buys the skill for.

### Step 4 — Deliver

Save the report under the agreed location. Default: a new folder named
`competitor-<short-name>-<YYYYMMDD>/` under the current workspace. Include the
raw source list as a separate `sources.md` so the user can verify.

### Step 5 — Render the visual PDF (always, unless user opts out)

After writing `report.md`, also produce a visual PDF. The PDF is a
**浓缩配套** — same data, but with cover + 7 charts + 9 sections for
shareable distribution. The agent does this by:

1. Writing a `config.json` next to `report.md` that follows the schema in
   `scripts/pdf-build/examples/`. (Map the markdown content into the
   structured config keys.)
2. Running the build script:

```bash
python scripts/pdf-build/build_pdf.py --config config.json \
    --output <ShortName>-竞品背调-可视化版.pdf
```

3. Delivering the PDF alongside `report.md`.

The script is self-contained: auto-detects CJK font (SimHei / PingFang /
Noto), generates 7 matplotlib charts, renders HTML, outputs PDF via
xhtml2pdf. No external services, ~2 seconds per build.

If the user explicitly says they only want Markdown (e.g., "不要 PDF"),
skip this step.

## Output contract

A correct run produces:

- `report.md` — Executive Summary + Company Profile + 12-dimension findings + SWOT + Strategic Recommendations + Sources & Confidence.
- `sources.md` — flat list of every URL / tool / database queried, with dimension tag.
- `config.json` — structured data feeding the PDF build (see `scripts/pdf-build/examples/`).
- `<ShortName>-竞品背调-可视化版.pdf` — visual PDF with cover + 7 charts + 9 sections.
- If `quick` mode: only the 4 high-priority dimensions filled, others marked "not pursued (quick mode)".
- Every numeric or factual claim cites a source; low-confidence claims are explicitly tagged `[low-confidence]`.
- Output language matches the user's prompt language (Chinese input → Chinese report, English input → English report).

If a sub-item cannot be researched (paid tool, no public data), mark it
`[data gap]` and move on. Never fabricate.

## Failure handling

- **No named competitor**: ask once. If user only says "the SaaS market", refuse with a redirect to market sizing.
- **No public data at all**: produce a partial report with `[data gap]` markers and a "next steps / data needed" section.
- **Conflict between sources**: present both, note the conflict, mark lower confidence.
- **Tool fails (e.g., SimilarWeb 403)**: retry once, then fall back to free alternatives listed in `data-sources.md`.
- **Out-of-scope request** (e.g., user asks for hacking / illegal data): refuse and explain.

## Windows (win32) platform notes

This skill is mostly research-driven (web tools + read/write), not shell-heavy.
But some operational notes:

- When running Python scripts to crawl / scrape, use `python` (Windows launcher). Avoid `python3` which often doesn't exist on Windows.
- For pip installs, prefer `py -m pip install ...` to avoid PATH issues.
- Path separators: use `\` in scripts; `os.path.join` / `pathlib.Path` handle this.
- For any CLI tool (e.g., `gh`, `jq`), check for `.cmd` / `.ps1` wrappers before declaring "not found".
- All `web_search` / `web_fetch` / `images_search_and_download` tool calls work the same on Windows; no adaptation needed.
- If the user wants the report as a Word file, hand off to the `docx` skill; for slides, hand off to `pptx`.

## References

- `references/dimensions.md` — full breakdown of all 12 dimensions (sub-items, data sources, research method)
- `references/data-sources.md` — master list of data sources and tools, with selection matrix
- `references/industry-prioritization.md` — which dimensions to prioritize per industry type
- `references/output-template.md` — report structure, SWOT template, confidence-level rubric
- `references/pdf-build.md` — how to fill `config.json` and run the PDF build
- `scripts/pdf-build/build_pdf.py` — the PDF builder (CLI: `--config` / `--output`)
- `scripts/pdf-build/examples/shining-lighting.json` — full example config
- `scripts/pdf-build/README.md` — install / run / schema reference
