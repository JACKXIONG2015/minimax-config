# 数据抓取字段定义（Data Fields）

> 5 个 ASIN 横向对比时，每个 ASIN 必抓的字段。所有字段从 Amazon 产品页直抓。

---

## 必抓字段（每 ASIN）

### 基础信息

| 字段 | 来源 | 用途 |
|---|---|---|
| **ASIN** | URL | 唯一标识 |
| **品牌** | 产品页 | 头部集中度分析 |
| **标题（完整）**| 产品页 | 关键词 + 产品形态分析 |
| **类别（大类）** | 产品页 | 市场容量 |
| **类别（细类）** | 产品页 | 子类目排名 |
| **上市日期** | Product Details | 新老程度 |
| **变体数** | 产品页 | SKU 矩阵分析 |

### 销售信号

| 字段 | 来源 | 用途 |
|---|---|---|
| **价格（USD）**| Buy Box | 定价对标 |
| **评分** | 产品页 | 信任度 |
| **评论数** | 产品页 | 销量估算锚点 |
| **BSR 排名** | Product Details | 类目内位置 |
| **过去 30 天评论增长** | 工具估算 | 趋势判断 |
| **月销量估算** | 工具 / 公式 | 容量判断 |

### 库存与渠道

| 字段 | 来源 | 用途 |
|---|---|---|
| **Buy Box 状态** | 产品页 | ⚠️ 异常标记 |
| **卖家数** | Buy Box 区域 | 渠道分散度 |
| **Amazon 自营?**| 卖家名 | 渠道类型 |
| **FBA / FBM** | 配送说明 | 物流方式 |
| **库存状态** | Buy Box | 是否断货 |

### Listing 质量

| 字段 | 来源 | 用途 |
|---|---|---|
| **Bullet points 数量** | 产品页 | listing 完整度 |
| **A+ Content 存在**| 产品页 | 品牌投入 |
| **视频数** | 产品页 | 投入度 |
| **图片数** | 产品页 | 投入度 |
| **Q&A 数量** | 产品页 | 互动度 |
| **FAQ 存在**| A+ | 信息完整度 |

### 信任信号

| 字段 | 来源 | 用途 |
|---|---|---|
| **Climate Pledge Friendly**| 产品页 | 平台认证 |
| **FSA / HSA Eligible**| 产品页 | 平台认证 |
| **Transparency** | 产品页 | 品牌保护 |
| **Brand Registry** | URL | 品牌注册 |

### 5 画像"未找到"统计

每个 ASIN 跑 5 个画像 × 3 个问题 = 15 个问题：

| 画像 | 必问 3 题 |
|---|---|
| 🅰️ 精打细算型 | 价格对比 / 保修 / FSA |
| 🅱️ 品质优先型 | 波长 / FDA / 临床数据 |
| 🅲️ 新手入门型 | 操作 / 安全 / 配件 |
| 🅳️ 比价犹豫型 | 竞品对比 / 差评 / 见效周期 |
| 🅴️ 快速决策型 | Buy Box / 配送 / 退换 |

详见 `consumer-personas.md`

---

## 选抓字段（高级分析）

### 细节信息

- **重量 / 尺寸** — 算 FBA 费用必备
- **包装类型** — 算头程必备
- **认证标识** — 看图片中是否有 FDA / CE / FCC / UL 标志
- **电源类型** — 电池 / 插电 / USB
- **保修详情** — "1 year manufacturer warranty" 之类

### 评论分析

- **5 星 / 4 星 / 3 星 / 差评 比例** — 用工具算
- **Top 10 差评关键词** — 提取改进点
- **带图评论数** — 看真实使用反馈
- **VP 评论数** — 看刷单痕迹

### 关键词

- **标题 / Bullet 中的高频词** — 看 SEO 思路
- **类目 Top 关键词** — 用 Helium 10 / Cerebro 查
- **Search Query 排名** — 用 Helium 10 查

---

## 数据源优先级

| 数据 | 优先级 | 工具 |
|---|---|---|
| 价格 / 评分 / 评论数 | 🟢 一手 | Amazon 产品页 |
| BSR | 🟢 一手 | Amazon Product Details |
| 月销量估算 | 🟡 工具 | Helium 10 / Jungle Scout |
| 采购成本 | 🟡 询价 | 1688 / Alibaba |
| 专利 | 🟡 检索 | Google Patents / USPTO |
| 30 天评论增长 | 🟡 工具 | Helium 10 / Cerebro |
| 关键词排名 | 🟡 工具 | Helium 10 |
| 评论情感分析 | 🟠 高级 | ReviewMeta / Helium 10 |

---

## 输出格式

每 ASIN 抓取后整理成结构化数据：

```json
{
  "asin": "B0XXXXXXX",
  "brand": "...",
  "title": "...",
  "category_l1": "Health & Household",
  "category_l2": "Light Therapy Products",
  "bsr_main": 7780,
  "bsr_sub": 4,
  "price_usd": 39.99,
  "rating": 4.5,
  "review_count": 1342,
  "listing_date": "2024-03-01",
  "variants": 2,
  "buy_box_status": "no_offers",  // ⚠️ 异常
  "fulfillment": "FBA",
  "is_amazon": false,
  "bullet_count": 5,
  "has_a_plus": true,
  "video_count": 6,
  "image_count": 7,
  "qna_count": 23,
  "certifications": [],
  "persona_gaps": {
    "budget": ["warranty", "fsa"],
    "quality": ["fda", "irradiance", "clinical_data"],
    "beginner": ["video_tutorial", "safety_distance"],
    "comparison": ["compare_table", "effect_timeline"],
    "quick": ["buy_box", "shipping"]
  }
}
```

5 个 ASIN 抓完后汇总，5 维度评分直接用结构化数据计算。

---

## 抓取注意事项

1. **改地址** — 默认地址可能是 Hong Kong / Taiwan，会触发 "cannot be shipped"，**改 US zip code 10001**
2. **重复抓取** — 同一个 ASIN 不同时间抓取可能数据有差（评论数、BSR），**用同一时点抓**
3. **缺数据不放弃** — Buy Box 空 / 价格空 都是重要信号，不是抓取失败
4. **保存原始 HTML** — 万一后面要回看证据，存到 workspace
5. **不依赖单一数据源** — 评论数 + BSR + 工具估算 = 三重验证
