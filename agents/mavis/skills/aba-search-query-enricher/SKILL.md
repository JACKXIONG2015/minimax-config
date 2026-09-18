---
name: aba-search-query-enricher
description: |
  Enrich Amazon Brand Analytics (ABA) 搜索查询绩效 (Search Query Performance) Excel
  exports with 4 derived metric columns: 关键词类目平均转化率, 关键词类目加购率,
  品牌转化率, 品牌加购率. Use when the user provides an ABA Search Query Performance
  (SQP) report from Amazon Seller Central Brand Analytics and asks to 加指标 /
  加转化率 / 加加购率 / 加列 / 算转化率 / 算加购率 / enrich / add metrics / compute CVR
  for the SQP report. Triggers on filenames matching `搜索查询绩效` /
  `Search_Query_Performance` / `search-query-performance` and on
  `品牌视图_综合` Brand Analytics exports. Do NOT use for: ABA 人口统计 / 商品对比 /
  购物篮 / 复购分析 (other ABA tables — different schemas), Amazon business reports
  (Sales / Advertising), Helium 10 / Sif keyword research exports (use
  `amazon-keyword-library-processing` instead), or non-Amazon data.
---

# ABA Search Query Enricher

## Inputs to collect
- 源文件路径 — Amazon Seller Central → Brand Analytics → 搜索查询绩效 导出的 XLSX
  (默认 34 列, row 1 是筛选条件行, row 2 是表头, row 3+ 是数据)
- (可选) 输出路径. 默认 `<源文件名>_加4指标.xlsx` 放在工作区根
- (可选) 品牌视图筛选条件. 默认沿用源文件 row 1 的内容, 不重写

如果用户只说"帮我处理一下这个 ABA 表"而没给路径, **先问路径**, 不要自己猜文件.

## Procedure

1. **验证源文件 schema** — 读 row 2 (真表头), 确认含这 6 个关键列名 (按顺序):
   `搜索查询` → `点击量：总次数` → `点击量：点击的品牌数` → `购物车添加：总数` →
   `加入购物车：涉及品牌数` → `购买：下单总数` → `购买次数：品牌数量`. 完整 34 列
   映射见 `references/columns-map.md`. 如果列名错位 / 缺失 → 报"源文件不是 ABA
   搜索查询绩效表", 让用户重新导出.
2. **检测并跳过筛选行** — 源文件 row 1 通常是 `品牌=["..."] 报告范围=["..."] 选择年份
   =["..."] 选择月份=["..."]`. 启发式: row 1 至少 2 个值以 `品牌` / `报告范围` /
   `选择年份` / `选择月份` 开头则视为筛选行, 跳过. 否则视为普通表头, 保留.
   原因: 否则新表 row 1 是筛选条件, A1 显示"品牌=..."而不是"搜索查询", 用户看到
   "第一列关键词不见了".
3. **建新工作簿, 在 col 2 前插入 4 列**:
   - B = 关键词类目平均转化率 = `=IFERROR(AC{n}/K{n},0)` (购买下单总数 ÷ 点击总量)
   - C = 关键词类目加购率 = `=IFERROR(T{n}/K{n},0)` (购物车添加总数 ÷ 点击总量)
   - D = 品牌转化率 = `=IFERROR(AE{n}/M{n},0)` (购买品牌数 ÷ 点击品牌数)
   - E = 品牌加购率 = `=IFERROR(V{n}/M{n},0)` (加购品牌数 ÷ 点击品牌数)
   数字格式 `0.00%`. 公式列字母依据 (插入 4 列后原列字母 +4): G→K, I→M, P→T, R→V, Y→AC, AA→AE.
4. **写公式 + 注入 cached value** — `scripts/enrich_aba.py` 已经封装好这两步. 直接
   `python scripts/enrich_aba.py <input> <output>` 跑. **不要**只用 openpyxl 写公式不
   注入 cached value, 否则 Excel 打开显示空. 原因见 `references/cached-value-hack.md`.
5. **验证输出**:
   - `max_row` = 1 (表头) + 数据行数; `max_col` = 38 (34 + 4)
   - A1 = "搜索查询"; B1..E1 是 4 个新指标名
   - 抽样 5 行 (row 2, 3, 4, 100, 500), 确认 cached value 与 Python 独立计算一致
   - 抽样 1 个公式 cell 的 XML, 确认 `<f>...</f><v>0.0189...</v>` (不是 `<v></v>`)
6. **交付** — 用 `<deliver-assets><media src="绝对路径" /></deliver-assets>` 附上
   绝对路径. 简短说明: 4 个新指标列的位置、公式含义、cached value 已注入所以不用
   F9. 提醒用户公式仍保留, 改原数据时自动重算.

## Output contract
- 一个 .xlsx, 38 列 × (1 + 数据行数) 行
- row 1 是表头 (A1=搜索查询, B1..E1=4 新指标, F1..AH1=原 33 列)
- 数据从 row 2 开始, A 列是搜索查询, B-E 是 4 个新指标, F-AH 是原 33 列
- 4 个新指标列数字格式 `0.00%`
- 公式 + cached value: Excel 打开即显示数值, 不需 F9; 改原数据时公式自动重算
- 不保留源文件的筛选条件行

## Failure handling
- **列结构不匹配** (不是 ABA 搜索查询绩效) → 不强行处理, 报"列名不符, 请确认源文件是
  Seller Central → Brand Analytics → 搜索查询绩效 → 综合 → 每月 的导出"
- **源数据某些行的"点击量：点击的品牌数"=0** → 公式 `=IFERROR(...,0)` 自动返回 0.
  这是**正确行为**, 不是 bug (该词下没有品牌带来点击, 品牌指标无意义)
- **cached value 注入失败** (正则不匹配) → 兜底为静态值 (无公式), 但保留原表头. 给用户
  一句说明: "由于技术限制, 这次是静态值版本, 改原数据需重新跑脚本"
- **源文件 row 1 不是筛选条件** (比如用户预先手动删了) → 启发式检测不到, 走默认路径,
  公式列字母仍按"插入 4 列后原 G/I/P/R/Y/AA → K/M/T/V/AC/AE"算, 不需要重新检测
- **输出文件已存在** → 覆盖前提示用户, 不静默替换

## Examples

**Input**: 用户说"把这份 ABA 表加 4 个指标列" + 文件 `8月US_搜索查询绩效_品牌视图_综合_Month_2026_08_31.xlsx` (FARMLITE 品牌, 1872 行, 34 列).

**Output**: `8月US_搜索查询绩效_FARMLITE_2026-08_加4指标.xlsx` (38 列, 1873 行, 4 个新指标列 B-E 含正确 cached value).

抽样验证: row 2 (源 "tent"): B=1.89% / C=13.62% / D=0% / E=0%; row 4 (源 "grow lights for indoor plants"): B=7.42% / C=28.50% / D=2.27% / E=6.82%.
