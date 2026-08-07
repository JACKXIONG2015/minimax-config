# Translation Map Format

The translation map is a JSON object. Each key is a Chinese source string from
the source DOCX, each value is the English replacement. Saved as
`translation.json` next to the output path with `ensure_ascii=False, indent=2`
so Chinese keys stay readable.

## Basic shape

```json
{
  "总体要求": "General Requirements",
  "Wifi/网口内嵌网页控制盒": "WiFi / Ethernet controller box"
}
```

The script does not care about the order of keys. Only the exact string
match between key and source text matters.

## Two matching modes

The apply step uses two modes in order, falling back from the first to the
second when a paragraph cannot be matched.

### Mode 1: joined-paragraph (default)

For a paragraph, the script joins all `<w:t>` text in document order. If that
joined string is a key in the map, the script places the English value in
the first `<w:t>` and clears all later `<w:t>` in the same paragraph.

This is the right mode for the vast majority of paragraphs because most
paragraphs have a single text run, or multiple runs that all carry the same
font / size / style.

### Mode 2: per-w_t (fallback)

If a paragraph's joined text is not in the map, the script tries each
non-empty `<w:t>` element individually as a key. This is the right mode for
paragraphs whose original runs were intentionally split, e.g.:

- **Lead-in + URL in a separate run** (common with hyperlinks). The URL
  `<w:t>` is usually not in the map (URLs are not translated) so the script
  warns about it. To work around this, supply per-w_t keys for the
  surrounding text and let the URL `<w:t>` fall through with its original
  content. (The apply step is currently strict — see "Per-w_t untranslatable
  content" below for the workaround.)

- **Heading + small caption in different sizes**. The heading `<w:t>` and
  caption `<w:t>` carry different style hints; supplying one per-w_t key for
  each gives a clean translation while preserving the visual structure.

## Per-w_t untranslatable content (e.g. URLs)

The current apply step lists any non-empty `<w:t>` that has no map entry as
an unmapped error. If a paragraph contains a URL or other token that should
not be translated, supply a map entry that maps the URL to itself:

```json
{
  "UI见链接：": "UI mockups: ",
  "https://js.design/f/PjZVYW?p=-9T9-6sTWP&mode=design": "https://js.design/f/PjZVYW?p=-9T9-6sTWP&mode=design"
}
```

The script will then leave the URL `<w:t>` untouched and translate the
lead-in. This keeps the original hyperlink styling on the URL run.

## What to keep verbatim

When generating the map, leave the following categories unchanged (or map
them to themselves):

- **Product / model codes**: `GBK`, `VEG`, `SOLO`, `GCx`, `GC-FOLD`, `GC-wifi`,
  `PAD`, `Recipe`, `Spec.Mix`, `Auto Temp`, `Light Cycle`, `Output`, etc.
- **Group labels**: `Group A`, `Group B`, `Room A`, `Room B`, `Sensor_A`.
- **Electrical signals and units**: `0-10V`, `DIM+`, `DIM-`, `VCC`, `Type-C`,
  `RJ12`, `RJ14_A`, `RJ45`, `M8`, `12 V`, `28 degC`.
- **File names, URLs, IP addresses, CSV filenames** referenced in the spec.
- **Mode names that are quoted as UI strings**: `Manual`, `Recipe`,
  `Always ON`, `Always OFF`, `Standard Timer`, `Asynchronous Timer`.
- **Channel counts**: `1CH`, `2CH`, `3CH`, `4CH`, `1-5 channels`.

## Punctuation discipline

The apply step keys are matched character-for-character. The dump from
`read_docx.py` shows the source text exactly as it appears in the DOCX
(including half-width vs full-width punctuation). When copying source text
into the JSON:

- Copy the full-width Chinese punctuation (`：`, `（`, `）`, `，`, `；`,
  `？`, `！`, `。`) exactly as it appears.
- Do not silently normalize half-width `()` to full-width `（）` or vice
  versa. A source that uses `（VEG,SOLO）` (full-width) and `(GCx)`
  (half-width) in the same paragraph is intentional; match each as written.
- Trim only leading and trailing whitespace. Internal whitespace matters.

## Common pitfalls

- **Unmapped paragraphs**: usually means a key in the map does not match
  the source text exactly. Re-read the dump and check for whitespace, full
  vs half-width punctuation, or a stray newline.
- **JSON escaping**: Chinese full-width characters are safe to embed with
  `ensure_ascii=False`. For straight quotes or backslashes inside values,
  use the standard JSON escape sequences. For embedded newlines, use
  `\\n` (the apply step writes them as soft line breaks in Word).
- **Empty paragraphs**: paragraphs whose joined text is empty are skipped;
  no map entry is required for them.
- **Image-only paragraphs**: paragraphs whose only content is a `<w:drawing>`
  are also skipped; no map entry is required.
- **Section headers vs body**: each top-level paragraph in the body is
  treated independently. Section properties (`<w:sectPr>`) are not in this
  loop and are not affected by the translation.

## Verification

After running `apply_translation.py`, the script prints:

```
paragraphs: <N> -> <N>
paragraphs_with_images: <M> -> <M>
drawings: <K> -> <K>
image_rels: <R> -> <R>
```

All four deltas must be zero. If they are not, the script exits with code 4
and warns that the output needs inspection. Common causes:

- The script accidentally added or removed a paragraph. This should never
  happen; if it does, the source DOCX is corrupted in a way the script
  cannot handle — fall back to a manual re-translation.
- A `image_rels` delta usually means the source itself had an image that
  was referenced by multiple drawings (this is a Word convention, not a
  bug). Compare the source's `image_rels` count to the source's `drawings`
  count; if the rels count is smaller, this is the expected case.
