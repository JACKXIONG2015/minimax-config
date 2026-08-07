"""Apply a Chinese -> English translation map to a DOCX in place.

Usage:
    python apply_translation.py <input.docx> <translation.json> <output.docx>

The translation JSON is a dict {source_text: english_text}. The script:

  - opens the source DOCX with python-docx
  - for each top-level <w:p>, tries two modes:
      1. JOINED mode: if the joined <w:t> text of the paragraph is a map key,
         place the value in the first <w:t> and clear all later <w:t>.
      2. PER-W_T mode: if the joined text is not a key, look up each non-empty
         <w:t> individually. This handles paragraphs whose original runs were
         split (e.g. heading + small caption, lead-in + URL).
  - leaves <w:drawing> runs untouched so embedded images stay in place
  - switches any Chinese font hint in <w:rFonts> (eastAsia, cs, ascii, hAnsi)
    that targets SimSun / 宋体 / 微软雅黑 / Noto / 等线 to Calibri
  - writes the output DOCX and prints a verification report

The script reports any <w:t> that could not be mapped and exits non-zero.
"""
import json
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


CN_FONT_KEYWORDS = (
    "simsun", "simhei", "simyou", "simkai", "simfang",
    "宋体", "黑体", "微软雅黑", "msyh", "fangsong", "kaiti",
    "noto", "wqy", "pingfang", "苹方", "heiti", "songti",
    "deng", "等线", "fzzheng", "fzshu", "fzshuti",
)

XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def switch_chinese_fonts(p_elem) -> None:
    for rfonts in p_elem.iter(qn("w:rFonts")):
        for attr in ("eastAsia", "cs", "ascii", "hAnsi"):
            v = rfonts.get(qn("w:" + attr))
            if v is None:
                continue
            if any(k in v.lower() for k in CN_FONT_KEYWORDS):
                rfonts.set(qn("w:" + attr), "Calibri")


def apply_joined(p_elem, joined: str, new_text: str) -> None:
    """Place new_text in t[0], clear t[1+]."""
    t_elems = p_elem.findall(".//" + qn("w:t"))
    if not t_elems:
        return
    t_elems[0].text = new_text
    t_elems[0].set(XML_SPACE, "preserve")
    for t in t_elems[1:]:
        t.text = ""


def apply_per_w_t(p_elem, tr_map: dict) -> list:
    """Try to translate each non-empty <w:t> using the map. Returns the list
    of <w:t> source strings that could not be translated."""
    t_elems = p_elem.findall(".//" + qn("w:t"))
    unmapped = []
    for t in t_elems:
        if not (t.text and t.text.strip()):
            continue
        if t.text in tr_map:
            t.text = tr_map[t.text]
            t.set(XML_SPACE, "preserve")
        else:
            unmapped.append(t.text)
    return unmapped


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "usage: python apply_translation.py <input.docx> <translation.json> <output.docx>",
            file=sys.stderr,
        )
        return 2

    src = Path(sys.argv[1])
    map_path = Path(sys.argv[2])
    out = Path(sys.argv[3])

    if not src.is_file():
        print(f"input not found: {src}", file=sys.stderr)
        return 2
    if not map_path.is_file():
        print(f"translation map not found: {map_path}", file=sys.stderr)
        return 2

    with map_path.open("r", encoding="utf-8") as f:
        tr_map = json.load(f)

    if not isinstance(tr_map, dict):
        print("translation map must be a JSON object {source: english}", file=sys.stderr)
        return 2

    doc = Document(str(src))
    body = doc.element.body
    top_paras = [ch for ch in body.iterchildren() if ch.tag == qn("w:p")]

    # Pre-translation counts
    src_total_paras = len(top_paras)
    src_paras_with_img = sum(1 for p in top_paras if p.findall(".//" + qn("w:drawing")))
    src_total_drawings = sum(len(p.findall(".//" + qn("w:drawing"))) for p in top_paras)
    src_image_rels = sum(1 for r in doc.part.rels.values() if "image" in r.reltype)

    unmapped_report = []  # list of (paragraph_index, source_text)
    for i, p in enumerate(top_paras):
        t_elems = p.findall(".//" + qn("w:t"))
        if not t_elems:
            continue
        joined = "".join(t.text or "" for t in t_elems)
        if not joined.strip():
            continue

        if joined in tr_map:
            apply_joined(p, joined, tr_map[joined])
            switch_chinese_fonts(p)
            continue

        # Fall back to per-w_t mode (handles split runs, lead-in + URL, etc.)
        unmapped = apply_per_w_t(p, tr_map)
        if unmapped:
            for src_text in unmapped:
                unmapped_report.append((i, src_text))
        switch_chinese_fonts(p)

    if unmapped_report:
        print(
            f"ERROR: {len(unmapped_report)} <w:t> element(s) had no translation entry:",
            file=sys.stderr,
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        for idx, src_text in unmapped_report:
            err_path = out.parent / f"_unmapped_p{idx:03d}_{abs(hash(src_text))}.txt"
            err_path.write_text(src_text, encoding="utf-8")
            print(f"  paragraph#{idx}  {src_text!r}  (saved to {err_path})", file=sys.stderr)
        return 3

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))

    # Post-write verification
    verify = Document(str(out))
    v_body = verify.element.body
    v_top = [ch for ch in v_body.iterchildren() if ch.tag == qn("w:p")]
    v_total_paras = len(v_top)
    v_paras_with_img = sum(1 for p in v_top if p.findall(".//" + qn("w:drawing")))
    v_total_drawings = sum(len(p.findall(".//" + qn("w:drawing"))) for p in v_top)
    v_image_rels = sum(1 for r in verify.part.rels.values() if "image" in r.reltype)

    print(f"paragraphs: {src_total_paras} -> {v_total_paras}")
    print(f"paragraphs_with_images: {src_paras_with_img} -> {v_paras_with_img}")
    print(f"drawings: {src_total_drawings} -> {v_total_drawings}")
    print(f"image_rels: {src_image_rels} -> {v_image_rels}")

    if (
        src_total_paras != v_total_paras
        or src_paras_with_img != v_paras_with_img
        or src_total_drawings != v_total_drawings
        or src_image_rels != v_image_rels
    ):
        print("WARN: counts drifted; inspect the output before delivering.", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
