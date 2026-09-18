# -*- coding: utf-8 -*-
"""
Enrich Amazon ABA Search Query Performance XLSX with 4 derived metric columns.

Usage:
    python enrich_aba.py <input.xlsx> <output.xlsx>

What it does:
  1. Reads the source ABA SQP export (default 34 cols, row 1 = filter row,
     row 2 = header, row 3+ = data).
  2. Drops the filter row.
  3. Builds a new workbook with 38 columns: A = 搜索查询, B-E = 4 new metrics,
     F-AH = original cols 2-34.
  4. Writes IFERROR formulas for the 4 new columns AND injects cached values
     via raw XML so Excel displays the result immediately on open (avoids the
     openpyxl-empty-<v> bug where formulas show as blank until F9).
"""
import os
import re
import sys
import zipfile

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment


# 0-based column indices in the source 34-col schema.
# 详细列名见 references/columns-map.md
COL_TOTAL_CLICKS = 6   # G  点击量：总次数
COL_BRAND_CLICKS = 8   # I  点击量：点击的品牌数
COL_TOTAL_CARTS  = 15  # P  购物车添加：总数
COL_BRAND_CARTS  = 17  # R  加入购物车：涉及品牌数
COL_TOTAL_ORDERS = 24  # Y  购买：下单总数
COL_BRAND_ORDERS = 26  # AA 购买次数：品牌数量

NEW_HEADERS = [
    '关键词类目平均转化率',  # B  购买下单总数 / 点击总量
    '关键词类目加购率',      # C  购物车添加总数 / 点击总量
    '品牌转化率',            # D  购买品牌数 / 点击品牌数
    '品牌加购率',            # E  加购品牌数 / 点击品牌数
]


def detect_filter_skip(rows):
    """源文件 row 1 通常是 `品牌=["..."] 报告范围=...` 这种筛选条件, 不是表头.
    启发式: row 0 至少 2 个值以 `品牌` / `报告范围` / `选择年份` / `选择月份` 开头
    则视为筛选行, 返回 1 表示跳过; 否则返回 0.
    """
    if not rows:
        return 0
    first = rows[0]
    markers = ('品牌', '报告范围', '选择年份', '选择月份')
    n = sum(1 for v in first if isinstance(v, str) and any(v.startswith(m) for m in markers))
    return 1 if n >= 2 else 0


def compute_metrics(row):
    K  = row[COL_TOTAL_CLICKS]  or 0
    M  = row[COL_BRAND_CLICKS]  or 0
    T  = row[COL_TOTAL_CARTS]   or 0
    V  = row[COL_BRAND_CARTS]   or 0
    AC = row[COL_TOTAL_ORDERS]  or 0
    AE = row[COL_BRAND_ORDERS]  or 0
    return (
        AC / K if K else 0,  # cvr        = 购买下单总数 / 点击总量
        T  / K if K else 0,  # cart_rate  = 购物车添加总数 / 点击总量
        AE / M if M else 0,  # brand_cvr  = 购买品牌数 / 点击品牌数
        V  / M if M else 0,  # brand_cart = 加购品牌数 / 点击品牌数
    )


def write_workbook(rows, header, dst):
    """写新表: 38 列, row 1 是表头, row 2+ 是数据. 返回 formula_cells 列表."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'ABA_搜索查询绩效_加4指标'

    # 表头: A1 = 搜索查询
    ws.cell(1, 1, value=header[0])
    # B1..E1 = 4 个新指标
    for i, h in enumerate(NEW_HEADERS, start=2):
        c = ws.cell(1, i, value=h)
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='305496')
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    # F1..AH1 = 原 col 2-34
    for i, val in enumerate(header[1:], start=6):
        ws.cell(1, i, value=val)

    # 数据 + 公式
    formula_cells = []
    pct_fmt = '0.00%'
    for r_idx, row in enumerate(rows, start=2):
        # A 列: 关键词
        ws.cell(r_idx, 1, value=row[0])
        # 4 个新指标: 写公式 + 记录 (letter, r_idx, computed_value)
        cvr, cart, brand_cvr, brand_cart = compute_metrics(row)
        for col_idx, letter, formula, val in [
            (2, 'B', f'=IFERROR(AC{r_idx}/K{r_idx},0)',  cvr),
            (3, 'C', f'=IFERROR(T{r_idx}/K{r_idx},0)',   cart),
            (4, 'D', f'=IFERROR(AE{r_idx}/M{r_idx},0)',  brand_cvr),
            (5, 'E', f'=IFERROR(V{r_idx}/M{r_idx},0)',   brand_cart),
        ]:
            c = ws.cell(r_idx, col_idx, value=formula)
            c.number_format = pct_fmt
            formula_cells.append((letter, r_idx, val))
        # F 列起: 原 col 2-34
        for i, val in enumerate(row[1:], start=6):
            ws.cell(r_idx, i, value=val)

    # 列宽 + 冻结
    ws.column_dimensions['A'].width = 30
    for letter, w in zip(['B', 'C', 'D', 'E'], [22, 20, 16, 16]):
        ws.column_dimensions[letter].width = w
    ws.freeze_panes = 'F2'
    ws.row_dimensions[1].height = 32

    wb.save(dst)
    return formula_cells


def inject_cached_values(path, formula_cells):
    """openpyxl 写公式时默认带 <v></v> 空 cached value, Excel 看到后不自动重算.
    用 zipfile 打开 xlsx, 改 sheet1.xml, 把每个公式 cell 的 <v></v> 替换成
    <v>0.0189</v> 之类的实际计算值.
    """
    with zipfile.ZipFile(path, 'r') as z:
        files = {n: z.read(n) for n in z.namelist()}

    sheet_path = next(
        n for n in files
        if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')
    )
    sheet_xml = files[sheet_path].decode('utf-8')

    injected = 0
    for letter, r_idx, val in formula_cells:
        ref = f'{letter}{r_idx}'
        # 模式: <c r="B2" ...><f>IFERROR(...)</f><v></v></c>
        # 兜底: <c r="B2" ...><f>IFERROR(...)</f></c>  (没有 <v> 时)
        pattern_with_empty = (
            rf'(<c r="{ref}"[^/>]*>)(<f>[^<]+</f>)<v></v>(</c>)'
        )
        replacement_with_empty = rf'\1\2<v>{val}</v>\3'
        new_xml, n = re.subn(pattern_with_empty, replacement_with_empty, sheet_xml)

        if n == 1:
            injected += 1
            sheet_xml = new_xml
        else:
            # 兜底: 没有 <v></v> 时直接插入
            pattern_no_v = rf'(<c r="{ref}"[^/>]*>)(<f>[^<]+</f>)(</c>)'
            replacement_no_v = rf'\1\2<v>{val}</v>\3'
            new_xml2, n2 = re.subn(pattern_no_v, replacement_no_v, sheet_xml)
            if n2 == 1:
                injected += 1
                sheet_xml = new_xml2
            else:
                print(f'WARN: {ref} not matched (n={n}, n2={n2})', file=sys.stderr)

    files[sheet_path] = sheet_xml.encode('utf-8')

    # 重新打包 (保留原 zip 顺序, 但实际上 zip 标准不要求固定顺序)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)

    return injected


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]
    if not os.path.exists(src):
        print(f'ERROR: {src} not found', file=sys.stderr)
        sys.exit(1)

    # 1. 读源数据
    wb_in = openpyxl.load_workbook(src, read_only=True, data_only=True)
    ws_in = wb_in.active
    data = list(ws_in.iter_rows(values_only=True))
    wb_in.close()

    # 2. 跳过筛选行
    skip = detect_filter_skip(data)
    header = data[skip]
    rows = data[skip + 1:]
    print(f'Read {len(rows)} data rows (skipped {skip} filter row(s))')

    # 3. 写新表
    formula_cells = write_workbook(rows, header, dst)
    print(f'Saved (formula version): {dst}  size={os.path.getsize(dst)} bytes')

    # 4. 注入 cached value
    injected = inject_cached_values(dst, formula_cells)
    print(f'Injected cached values: {injected} / {len(formula_cells)}')
    print(f'Final file: {dst}  size={os.path.getsize(dst)} bytes')


if __name__ == '__main__':
    main()
