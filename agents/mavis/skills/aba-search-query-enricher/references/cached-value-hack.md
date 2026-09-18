# openpyxl 写公式的 `<v></v>` 陷阱

## 问题

`openpyxl` 写公式时, 默认会在 cell 的 XML 里写一个**空**的 cached value:

```xml
<c r="B2"><f>IFERROR(AC2/K2,0)</f><v></v></c>
```

Excel 看到这个空 cached value 之后, **不会**自动重算公式, 直接显示空. 用户必须按
`Ctrl+Alt+F9` 强制重算才能看到数值. 第一次遇到这个问题的人会以为脚本写错了.

## 验证

```python
import zipfile, re
with zipfile.ZipFile('output.xlsx', 'r') as z:
    sheet_xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8')
m = re.search(r'<c r="B2"[^>]*>.*?</c>', sheet_xml, re.DOTALL)
print(m.group())
# 正确版本: <c r="B2" s="2"><f>IFERROR(AC2/K2,0)</f><v>0.0189</v></c>
# 错误版本: <c r="B2" s="2"><f>IFERROR(AC2/K2,0)</f><v></v></c>
```

## 解决方案: zipfile 改 XML 注入 cached value

```python
import zipfile, re

def inject_cached_values(path, formula_cells):
    """formula_cells: [(col_letter, row_idx, computed_value), ...]"""
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
        # 主模式: cell 已经有 <v></v> 占位, 替换
        pattern = rf'(<c r="{ref}"[^/>]*>)(<f>[^<]+</f>)<v></v>(</c>)'
        replacement = rf'\1\2<v>{val}</v>\3'
        new_xml, n = re.subn(pattern, replacement, sheet_xml)
        if n == 1:
            injected += 1
            sheet_xml = new_xml
            continue
        # 兜底: cell 没有 <v></v>, 直接在 </f> 后插入
        pattern2 = rf'(<c r="{ref}"[^/>]*>)(<f>[^<]+</f>)(</c>)'
        replacement2 = rf'\1\2<v>{val}</v>\3'
        new_xml2, n2 = re.subn(pattern2, replacement2, sheet_xml)
        if n2 == 1:
            injected += 1
            sheet_xml = new_xml2

    files[sheet_path] = sheet_xml.encode('utf-8')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)
    return injected
```

## 为什么不用纯静态值

| 方案 | 改原数据时 4 个指标 | Excel 打开就显示 | 适用场景 |
|---|---|---|---|
| 纯公式 (无 cached value) | 自动重算 | ❌ 显示空, 需 F9 | ❌ 不可用 |
| 纯公式 + cached value | 自动重算 | ✅ 显示 | ✅ **本 skill 采用** |
| 纯静态值 | ❌ 不跟随, 需重跑 | ✅ 显示 | 数据不再变化, 想简化 |

## 验证 cached value 注入成功

```python
# 跑完脚本后, 检查 XML
n_with_v_filled = len(re.findall(r'<f>[^<]+</f><v>[^<]+</v>', sheet_xml))
n_with_v_empty = len(re.findall(r'<f>[^<]+</f><v></v>', sheet_xml))
print(f'有 cached value 的公式 cell: {n_with_v_filled}')
print(f'空的 cached value (待修复): {n_with_v_empty}')
# 预期: 有 cached value 的数量 = 4 × 数据行数, 空的 = 0
```

## 数字格式与 cached value 关系

`number_format = '0.00%'` 让 Excel 把 0.0189 显示为 `1.89%`. cached value 仍存为
**小数** (`<v>0.0189</v>`), 不是字符串 `1.89%`. 数字格式是显示层的事, 不影响 cached
value 的存储.

如果 cached value 误存为字符串 (`<v>1.89%</v>`), Excel 会按文本处理, 后续 SUM/AVERAGE
会忽略它. 所以注入时**必须**用 Python 的 float, 用 `f'{val}'` 写小数.
