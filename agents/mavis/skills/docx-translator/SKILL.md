---
name: docx-translator
description: |
  Translate a Chinese-language DOCX into an English DOCX while preserving the
  original document's paragraph structure, run formatting, and every embedded
  image. Use when the user asks to translate a Chinese spec, report, proposal
  or product requirement saved as a .docx into English, especially when the
  deliverable must keep its images, layout, headings, captions, and image
  positions intact.

  Triggers (zh / en): "翻译这个 docx", "把这份中文 docx 翻译成英文", "中译英",
  "translate this Chinese docx to English", "convert this Chinese spec into
  English", "make an English version of this Chinese product spec".

  Do NOT use for: plain-text translation with no DOCX file, PDF / PPTX
  translation (use the pdf or pptx skills), DOCX generation from scratch (use
  the docx skill's CREATE_DOCX route), or source languages other than Chinese.
---

# docx-translator

Translate a Chinese DOCX into an English DOCX by editing the source file
in-place: the same `<w:body>` and the same run/drawing nodes, only the
`<w:t>` text content is replaced. Images, layout, headings, captions, and
table positions are preserved 1:1.

## Inputs to collect

- **Source DOCX path** — absolute path to the Chinese file.
- **Output path** — defaults to `<source_dir>/<source_stem>_EN.docx`. If the
  user wants a different name or location, ask before saving.
- **Target register** — the document may be a customer-facing spec
  (formal), an internal product requirement (technical), or marketing copy
  (persuasive). The model should infer from the source but flag if ambiguous
  (e.g. mixed register in the source).

Skip these questions if the user already supplied them; do not ask twice.

## Procedure

1. **Inspect the document first** with `python scripts/read_docx.py <src>
   <dump.txt>`. This writes a UTF-8 text dump of every top-level paragraph in
   body order, with `[IMG]` markers for paragraphs that contain a drawing.
   The dump is the model's working view; the source file is not modified by
   this step. The script also prints total paragraph / image counts to stdout.
   Reason: a translation pass without first seeing paragraph order and image
   positions will lose or reorder figures.

2. **Generate the translation map**. For every non-empty paragraph in the
   dump (in order), produce the English equivalent and assemble them as a
   JSON object: source text -> English text. Rules:
   - Keep proper nouns, model codes (`GBK`, `VEG`, `GC-FOLD`), and product
     names (`PAD`, `Recipe`, `Spec.Mix`) as-is.
   - Keep electrical / mechanical signals and units (`0-10V`, `DIM+`,
     `Type-C`, `RJ45`, `12 V`, `28 degC`) verbatim.
   - Preserve the original punctuation style (full-width vs half-width
     brackets) when matching; the map is keyed by exact source text.
   - For paragraphs that contain both text and a drawing, the text is still
     keyed as a single string; the drawing is preserved by the apply step
     without needing any mapping entry.
   - Keep file URLs, IP addresses, model numbers, and CSV filename
     references literally.
   - If a paragraph has no translatable text (e.g. only a `取消：` short
     label, image caption), translate minimally but consistently.

3. **Write the map to disk** as `translation.json` next to the output path.
   Use `json.dump(..., ensure_ascii=False, indent=2)` so Chinese source
   strings remain readable in the JSON for later review.

4. **Apply the translation** with
   `python scripts/apply_translation.py <src> translation.json <out>`.
   The script:
   - loads the source DOCX,
   - for every top-level `<w:p>` whose joined `<w:t>` text matches a key in
     the map, places the English text in the first `<w:t>` and clears all
     other `<w:t>` text in that paragraph,
   - leaves every `<w:drawing>` node untouched (so embedded images stay in
     their original position),
   - switches any Chinese font hint in `<w:rFonts>` (`eastAsia`, `cs`,
     `ascii`, `hAnsi`) that targets `SimSun / 宋体 / 微软雅黑 / Noto / 等线`
     style fonts to `Calibri`,
   - applies a small set of structural exceptions (see references/map-format.md),
   - writes the output DOCX and prints a verification report.

5. **Verify by diffing counts**. The apply script already prints:
   - source vs output paragraph count
   - source vs output paragraph-with-image count
   - source vs output total `<w:drawing>` count
   - source vs output image relationship count

   If any of these differ, the apply failed and the model must read the
   report, fix the map (or the exception list), and re-run from step 4 —
   do not patch the output by hand. If the source itself had an image rel
   mismatch (one image referenced by two drawings), that is expected and
   the apply step will preserve it.

6. **Deliver** the output path with `<deliver-assets>` and a one-line
   summary noting the paragraph / image / drawing counts.

## Output contract

- A single `.docx` file at the chosen output path, written by
  `apply_translation.py` from the source DOCX.
- The output has the same paragraph order, same drawings, same image
  relationships, and runs with the same `rPr` as the source. Only `<w:t>`
  text content and the font hints described above are different.
- A short text summary line: `Translated N paragraphs, preserved M images
  in K drawings.`

## Failure handling

- **`python-docx` not installed**: tell the user to run
  `pip install python-docx` and stop. Do not silently fall back to a
  different translation path.
- **Unmapped paragraphs**: the apply step exits with a non-zero status and
  lists every non-empty paragraph whose source text was not in the map. Read
  the list, add the missing keys, re-run step 4.
- **Drawing / image count drift**: stop and inspect. The most common cause
  is a paragraph whose `<w:t>` text is split across runs that the dump did
  not surface as a single line; use the structural exceptions in
  references/map-format.md to handle those paragraphs.
- **Special characters in the map**: make sure JSON escaping is correct for
  embedded quotes, backslashes, and Chinese full-width punctuation
  (`（`, `）`, `：`, `，`).

## Examples

**Input**: a 211-paragraph Chinese product spec with 50 embedded UI
screenshots and connector diagrams. User says "翻译这个 docx" and provides
the path `C:/path/to/GBK需求功能设计需求20260324.docx`.

**Procedure**:
1. `python scripts/read_docx.py "C:/path/to/GBK需求功能设计需求20260324.docx" dump.txt`
   - prints `Total paragraphs: 211 / paragraphs with images: 50`
2. LLM reads `dump.txt`, produces a 119-key translation map (only the
   non-empty paragraphs need a key) covering General Requirements,
   Interface Description, UI Overview, Lamp Selection, Output, Light Cycle,
   Spec.Mix, Recipe, Auto Temp, Sensors, and System sections.
3. `python -c "import json,sys; json.dump(map, open('translation.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)"`
4. `python scripts/apply_translation.py "C:/path/to/GBK需求功能设计需求20260324.docx" translation.json "C:/out/GBK_Functional_Design_Requirements_20260324_EN.docx"`
   - prints `paragraphs: 211 -> 211 / drawings: 50 -> 50 / image rels: 49 -> 49`
5. Deliver the output path with `<deliver-assets>` and the summary line.
