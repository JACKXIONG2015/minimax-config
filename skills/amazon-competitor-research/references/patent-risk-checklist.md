# 专利风险检查表（Patent Risk Checklist）

> 选品调研**必做**的一步。漏了这条，上线后被冻结账户、库存压死的案例太多了。

---

## 第一步：识别"专利维权重灾区"类目

以下类目在中国对美诉讼中**特别活跃**，新卖家**必须**先查专利：

| 类目 | 代表案号 | 风险等级 |
|---|---|---|
| **红光理疗腰带/垫** | 22-cv-5301（Yihong Lighting）| 🔴 高 |
| **筋膜枪 / 按摩仪** | 多个 22-cv / 23-cv 系列 | 🔴 高 |
| **手机壳 / 手机支架** | 多个 22-cv / 23-cv | 🔴 高 |
| **筋膜球 / 花生球** | 多个 | 🟡 中 |
| **瑜伽 / 健身小件** | 多个 | 🟡 中 |
| **电动牙刷 / 冲牙器** | 多个 | 🟡 中 |
| **宠物用品** | 多个 | 🟡 中 |
| **LED 灯 / 灯带** | 多个 | 🟡 中 |
| **儿童玩具** | 多个 | 🔴 高 |
| **厨房小家电** | 多个 | 🟡 中 |

**判断方法**：
- 1688 同款越多 → 维权越活跃
- Amazon 上中国卖家越多 → 维权越活跃
- 售价 < $50 → 维权多（金额低，受理率高）

---

## 第二步：USPTO / Google Patents 检索

### 必查关键词模板

```
{品名} + wearable
{品名} + belt / pad / wrap
{品名} + LED + 660nm
{品名} + infrared + flexible
{品名} + photobiomodulation
{品名} + therapeutic + garment
```

**例**（红光理疗腰带）：
- `red light therapy belt wearable`
- `photobiomodulation garment`
- `LED therapy flexible pad 660 850`

### 检索工具

1. **Google Patents**（推荐）— https://patents.google.com
   - 免费、支持语义搜索
   - 看 cited patents 找核心专利
   
2. **USPTO 官方**— https://www.uspto.gov/patents/search
   - 完整数据库
   - 查 Patent Trial and Appeal Board (PTAB)

3. **FreePatentsOnline**— https://www.freepatentsonline.com
   - 简单易用

4. **PatSnap / Orbit**（付费）— 深度分析
   - $3,000-30,000/年
   - 出 FTO 报告必备

### 看什么

| 字段 | 关注点 |
|---|---|
| **Patent type** | Utility（实用）/ Design（外观）/ Plant |
| **Assignee** | 谁是专利权人（公司 or 个人）|
| **Filing date** | 申请时间（早 = 强）|
| **Expiration** | 过期时间（一般 20 年）|
| **Claims** | 权利要求（最关键） |
| **Cited by** | 被谁引用（说明被广泛使用）|
| **Family** | 同族专利（CN / US / EU 都要查）|

---

## 第三步：查诉讼案件

### 必查渠道

1. **PACER**（美国法院系统）— https://www.pacer.uscourts.gov
   - 注册账号 $30
   - 查 22-cv-XXXX 系列
   - 看案件文档、判决书、原告专利

2. **ITC**（国际贸易委员会）— https://www.usitc.gov
   - 337 调查（专利侵权）
   - 一般调查周期 12-18 个月

3. **Justia**（免费）— https://law.justia.com/cases/federal
   - 看部分公开案件
   - 看律所是谁

4. **RPX**（付费）— https://www.rpxcorp.com
   - 实时监控专利诉讼

### 关键搜索词

```
"{品名}" AND "22-cv"
"{品名}" AND "patent infringement"
"{品名}" AND "Amazon" AND "lawsuit"
{主要中国品牌} AND "patent" AND "Amazon"
```

**关注律所**：
- NI, WANG & MASSAND, PLLC（伊利诺伊，专注中国卖家）
- GBC (Greer Burns & Crain)
- EPS (Ellis and Winters)
- Keener (Keith Vogt)
- Artegis Law
- Jiang IPLLC

---

## 第四步：识别 4 类"易侵权"设计元素

不管类目，专利侵权通常围绕这 4 个维度：

| 元素 | 描述 | 规避方案 |
|---|---|---|
| **整体外形** | 矩形 / 圆形 / 异形 | 改用差异化形状 |
| **关键结构** | 控制器位置 / 接口类型 / 折叠方式 | 重新设计结构 |
| **LED / 芯片排布** | 等距 / 矩阵 / 蜂窝 | 改变排布规律 |
| **材料 / 工艺** | 织物 / 硅胶 / 塑料 | 换材料或工艺 |

### 通用规避原则

1. **整体改 ≥ 30%** — 不能只换个 logo
2. **关键结构改变** — 至少 1 个核心结构不同
3. **新增加分项** — 多一个功能（如脉动 + 振动）
4. **申请自有外观专利** — $2,000-4,000/个，1 个就够

---

## 第五步：风险评估矩阵

| 风险等级 | 触发条件 | 动作 |
|---|---|---|
| 🔴 **极高** | 有活跃诉讼 + 类目与涉案产品高度相似 | **不进入** 或改品类 |
| 🟡 **高** | 有 1-2 项专利 + 头部品牌有备案 | FTO 检索 + 改设计 |
| 🟢 **中** | 1 项专利可规避 | FTO 检索 + 简单改设计 |
| 🟢 **低** | 类目无明显专利 + 中国卖家分散 | 正常推进 |

---

## 第六步：3 个立刻能用的"避雷"动作

### 动作 1：上 PACER 查案件

```
1. 注册 PACER 账号 ($30)
2. 搜 22-cv-XXXX + {类目关键词}
3. 看案件文档：原告专利 + 法院禁令 + 被告名单
4. 时间投入：30 分钟
5. 价值：避免一个雷
```

### 动作 2：1688 询价时直接问

在标准询价话术里加上：

```
6. 贵公司是否收到过美国市场的专利诉讼或律师函？
   特别是 22-cv-XXXX 系列案件？能否提供清单？
```

很多 OEM 已经因为 Yihong / GBC 等律所的诉讼被冻结账户，**他们会主动告诉你**。

### 动作 3：FTO 检索

| 预算 | 方案 |
|---|---|
| < $500 | 自己 Google Patents 检索 + 1688 询价时问 |
| $500-2,000 | 找中国知识产权律师做初步检索 |
| **$1,500-3,000** | **美国专利律师做标准 FTO 检索**（推荐）|
| $5,000+ | PatSnap / Orbit 深度分析 + 律师 |

---

## 第七步：进入后持续监控

### 监控指标

1. **Amazon Account Health** — 每天检查，看有没有 "Intellectual Property Complaint"
2. **Brand Registry 后台** — 看有没有 "Report Infringement" 通知
3. **PACER 新案件** — 类目关键词 + 原告律所名
4. **同行动态** — Top 3 ASIN 是否有 listing 变更

### 应急响应

| 情况 | 动作 |
|---|---|
| 收到 GBC / NI, WANG 律师函 | 24 小时内联系美国律师 |
| Amazon 暂停 listing | 提交 POA（Plan of Action）|
| 收到 TRO（临时禁令）| 48 小时内应诉 |
| 银行账户被冻结 | 立即找美国律师，5 天内出方案 |

---

## 常见误区

1. ❌ "我换了 logo 就不是侵权" — 不对，整体外形相似就构成
2. ❌ "1688 同款多就说明没专利" — 不对，1688 不查专利
3. ❌ "我没在被告名单上就安全" — 不对，下一批可能就是你
4. ❌ "国内专利不查" — 不对，CN 专利权人也可能申请 US 同族
5. ❌ "Buy Box 消失只是技术问题" — 多数情况是被冻结

---

## 工具 / 资源

- **Google Patents**：https://patents.google.com
- **USPTO**：https://www.uspto.gov
- **PACER**：https://www.pacer.uscourts.gov
- **Justia**：https://law.justia.com/cases/federal
- **USPTO PAIR**：查申请进度
- **WIPO PATENTSCOPE**：国际专利
- **IPlytics**：专利分析
- **PatSnap / Orbit / Innography**：商业专利分析

---

## 关键提醒

> 选品时发现雷区**不要硬上**。改一个产品形态、加 1 个新功能、换 1 种材料，都能低成本绕开大部分专利。
>
> **FTO 检索不要省**。$1,500-3,000 一次的检索，能避免 10 万+ 的损失。
>
> **如果一个类目 5 个 ASIN 全是 Buy Box 异常 / 全部被告过的 listing** — 这是品类被维权的明确信号，**直接换品类**比硬上聪明。
