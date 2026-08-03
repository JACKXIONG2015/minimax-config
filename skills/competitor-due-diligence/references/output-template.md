# Output Template

Use this structure for the final report. The user agreed on Markdown by default;
swap in spreadsheet or slides if asked.

## 1. Executive Summary

- 1–2 paragraphs: who the competitor is, why they matter to the user, top 3
  findings, overall threat level (low / medium / high).
- Include the "so what" — what the user should do as a result.

## 2. Company Profile

- Founding date, headquarters, business scope, scale (revenue / employees if
  public), key executives, ownership / UBO summary.
- 1–2 short paragraphs, not bullet soup.

## 3. Dimension-by-Dimension Analysis

For each of the 12 dimensions (or only the high-priority 4 in quick mode):

- **Finding**: 1–3 sentences, what the data shows.
- **Source**: URL / database / tool used.
- **Confidence**: high / medium / low with a one-line reason.

Format example:

> ### Dimension 1 — Basic Company Info
> - **Finding**: Founded 2014 in Shenzhen, 800+ employees, Series C in 2022
>   led by Sequoia China.
> - **Source**: [企查查](https://qcc.com/...), Crunchbase, LinkedIn.
> - **Confidence**: high — corroborated across registry, news, and LinkedIn.

If data is missing, use:

> ### Dimension 3 — Supply Chain
> - **Finding**: [data gap] — no public customs data for the past 12 months;
>   competitor uses opaque 3PL arrangement per industry rumor (single source,
>   unverified).
> - **Source**: ImportGenius returned 0 results; no filings.
> - **Confidence**: low — would need paid access or supplier-side intel.

## 4. SWOT Summary

Tabular format, 4 cells. Each cell: 3–5 bullets, each bullet ≤ 15 words.

```
| Strengths | Weaknesses |
|---|---|
| • ... | • ... |
| • ... | • ... |
| Opportunities | Threats |
| • ... | • ... |
| • ... | • ... |
```

## 5. Strategic Recommendations

Actionable items, not data dumps. Each recommendation has:
- **Action**: what to do.
- **Rationale**: which finding(s) it builds on.
- **Effort / Impact**: low / med / high on each axis.

Aim for 3–6 recommendations. Sort by impact.

## 6. Data Sources & Confidence

Flat list, one source per line, grouped by dimension. Include:
- Tool name + URL
- Query used (so it's reproducible)
- Date accessed
- Coverage / limitation notes

Example:

```
- 企查查 | https://qcc.com/xxx | searched "Anker Innovations" 2026-07-29
  | covers Chinese companies only
- Crunchbase | https://crunchbase.com/organization/anker-innovations
  | accessed 2026-07-29 | covers funding history since 2011
```

## Formatting conventions

- Use tables for side-by-side comparisons of multiple competitors.
- For 2+ competitors, add a "competitor scorecard" matrix at the top:
  rows = dimensions, columns = competitors, cells = 1–5 score.
- For visual strength comparison across dimensions, suggest a radar chart
  (describe it in text; rendering is the user's call).
- Always flag low-confidence findings explicitly with `[low-confidence]`.
- Use the same language as the user's prompt.

## Visual PDF (companion deliverable)

In addition to `report.md`, every run also produces a visual PDF — a
shareable version with cover + 7 charts + 9 sections. See
`references/pdf-build.md` for the full workflow. Quick summary:

1. Write `report.md` as usual.
2. Fill a `config.json` next to it (schema in `scripts/pdf-build/examples/`).
3. Run `python scripts/pdf-build/build_pdf.py --config config.json --output <ShortName>-竞品背调-可视化版.pdf`.
4. Deliver the PDF alongside the markdown.

The PDF is a **浓缩配套**, not a replacement — Markdown is the source of truth
(long-form, full citations), PDF is the shareable / archive version.
