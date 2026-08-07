"""Read a DOCX and dump every top-level paragraph in body order.

Usage:
    python read_docx.py <input.docx> <output.txt>

Output format (UTF-8, one line per item):
    [P style=...]   <text>          # text paragraph (style name if present)
    [TBL_START]                     # table begins
      [TR]  cell1 || cell2 || ...   # one row, cells joined by ' || '
    [TBL_END]                       # table ends

Drawings are noted inline: a paragraph that contains a <w:drawing> is marked
with a leading [IMG] tag in the dump so the model can keep picture positions
in mind when generating the translation map.

The script also prints to stdout:
    TOTAL_PARAGRAPHS=<n>
    PARAGRAPHS_WITH_IMAGES=<n>
    TOTAL_DRAWINGS=<n>
    TOTAL_IMAGES=<n>   # unique image relationships
"""
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python read_docx.py <input.docx> <output.txt>", file=sys.stderr)
        return 2

    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    if not src.is_file():
        print(f"input not found: {src}", file=sys.stderr)
        return 2

    doc = Document(str(src))
    body = doc.element.body

    top_paras = [ch for ch in body.iterchildren() if ch.tag == qn("w:p")]

    # Pre-compute stats before writing dump
    paragraphs_with_images = sum(1 for p in top_paras if p.findall(".//" + qn("w:drawing")))
    total_drawings = sum(len(p.findall(".//" + qn("w:drawing"))) for p in top_paras)
    image_rels = sum(1 for r in doc.part.rels.values() if "image" in r.reltype)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for child in body.iterchildren():
            tag = child.tag.split("}")[-1]
            if tag == "p":
                text = "".join(t.text or "" for t in child.iter(qn("w:t")))
                style = ""
                pPr = child.find(qn("w:pPr"))
                if pPr is not None:
                    ps = pPr.find(qn("w:pStyle"))
                    if ps is not None:
                        style = ps.get(qn("w:val")) or ""
                has_img = bool(child.findall(".//" + qn("w:drawing")))
                marker = "[IMG] " if has_img else ""
                f.write(f"{marker}[P style={style}] {text}\n")
            elif tag == "tbl":
                f.write("[TBL_START]\n")
                for row in child.iter(qn("w:tr")):
                    cells = []
                    for cell in row.findall(qn("w:tc")):
                        cell_paras = []
                        for p in cell.findall(qn("w:p")):
                            pt = "".join(t.text or "" for t in p.iter(qn("w:t")))
                            cell_paras.append(pt)
                        cells.append("\n".join(cell_paras).strip())
                    f.write(f"  [TR] {' || '.join(cells)}\n")
                f.write("[TBL_END]\n")

    print(f"TOTAL_PARAGRAPHS={len(top_paras)}")
    print(f"PARAGRAPHS_WITH_IMAGES={paragraphs_with_images}")
    print(f"TOTAL_DRAWINGS={total_drawings}")
    print(f"TOTAL_IMAGES={image_rels}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
