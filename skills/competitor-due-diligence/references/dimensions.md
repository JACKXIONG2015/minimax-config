# Competitor Due Diligence - Dimension Details

Detailed breakdown of each of the 12 dimensions, including sub-items, data sources, and research methods.

---

## Dimension 1: Basic Company Info (基础信息)

### Sub-items
- Company founding date and registration history
- Registered capital and paid-in capital
- Company legal form (LLC, corporation, sole proprietorship, etc.)
- Business scope (registered vs. actual)
- Company scale: annual revenue, employee count, office/factory locations
- Main controllers: equity structure, ultimate beneficial owner (UBO), actual controller
- Key personnel: founders, executives, board members, their backgrounds
- Organizational structure: department setup, reporting lines

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| 企查查 / 天眼查 / 启信宝 | Chinese companies | Paid API/web |
| Companies House (UK) | UK companies | Free |
| SEC EDGAR | US public companies | Free |
| OpenCorporates | Global registry | Free/paid |
| LinkedIn | Employee count, org structure | Free/paid |
| Crunchbase | Startup info, founders | Free/paid |
| Company official website | Basic info, team page | Free |

### Research Method
1. Search company registry to get registration data
2. Trace equity structure to identify UBO
3. Cross-reference LinkedIn for employee count and org structure
4. Check company website for official team bios and office locations

---

## Dimension 2: Financial & Capital (财务资本)

### Sub-items
- Revenue scale and year-over-year growth rate (3-5 years)
- Gross margin, net margin, EBITDA
- Funding history: rounds, amounts, investors, valuation
- Asset-liability ratio, current ratio, cash flow from operations
- Key financial risks (high debt, declining margins, cash burn)

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Annual reports / 10-K / 20-F | Public companies | Free |
| Crunchbase / PitchBook | Funding history | Paid |
| Wind / Capital IQ / Bloomberg | Financial data | Paid |
| 企查查 financial module | Chinese private companies | Paid |
| SEC EDGAR | US filings | Free |
| HKEX / SSE / SZSE | HK/China listed | Free |

### Research Method
1. For public companies: pull annual reports for 3-5 year financials
2. For private companies: check registry filings for reported financials (may be incomplete)
3. Search Crunchbase/PitchBook for funding rounds and valuations
4. Calculate growth rates and margin trends
5. Compare with industry benchmarks

---

## Dimension 3: Supply Chain (供应链)

### Sub-items
- Main suppliers (reverse-lookup via import bills of lading)
- Supplier concentration and dependency
- Production bases: locations, capacity, ownership vs. outsourced
- Warehouse and fulfillment network (especially for e-commerce)
- Raw material sources and dependency
- Supply chain stability indicators (disruptions, delays, quality issues)

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| ImportGenius / Panjiva / PIERS | US import bills of lading | Paid |
| 52wmb.com (外贸邦) | China customs data | Paid |
| Datamyne | Global trade data | Paid |
| Company filings (supply chain risk sections) | Public companies | Free |
| News / industry reports | Supply chain disruptions | Free/paid |
| Google Maps / satellite imagery | Factory/warehouse locations | Free |

### Research Method
1. Search customs/shipping databases by company name to find suppliers
2. Cross-reference supplier names with the target company's filings
3. Use satellite imagery to verify factory/warehouse locations
4. Monitor news for supply chain disruption events
5. Compare supplier overlap with your own supply chain

---

## Dimension 4: Product & Pricing (产品定价)

### Sub-items
- Product line portfolio: breadth (categories) and depth (SKUs per category)
- Pricing strategy: price ranges, tier structure, premium vs. value positioning
- Promotion cadence: discount frequency, depth, seasonal patterns
- Core differentiation: patents, exclusive technology, brand moat, unique design
- New product launch rhythm and category expansion direction
- Product quality signals: ratings, reviews, return rates, warranty policies

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Competitor website / online store | Product catalog, pricing | Free |
| Amazon / eBay / Alibaba listings | Pricing, reviews, ratings | Free/paid |
| Helium 10 / Jungle Scout | Amazon product data | Paid |
| Google Shopping | Price comparison | Free |
| Patent databases (Google Patents, 智慧芽) | Technology differentiation | Free/paid |
| Industry analyst reports | Product benchmarking | Paid |

### Research Method
1. Crawl competitor website for full product catalog and pricing
2. Scrape e-commerce listings for pricing, reviews, and ratings
3. Track price changes over time using price monitoring tools
4. Search patent databases for proprietary technology
5. Analyze review patterns for quality and satisfaction signals

---

## Dimension 5: Channels & Markets (渠道市场)

### Sub-items
- Market share in target market segments
- Regional layout: which countries/regions are primary, secondary, emerging
- Channel strategy: direct sales vs. distributor vs. agent; online vs. offline ratio
- Distributor/agent network: key partners, exclusivity agreements
- Geographic expansion plans and recent market entries
- Channel conflict or channel partner churn

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Euromonitor / Statista | Market share data | Paid |
| SimilarWeb | Website traffic by country | Free/paid |
| Customs data | Export destinations | Paid |
| Industry association reports | Market size and share | Paid |
| Company filings (segment reporting) | Public companies | Free |
| Trade show attendee lists | Distributor identification | Free |

### Research Method
1. Use SimilarWeb to analyze website traffic by geography
2. Cross-reference customs data for export destination analysis
3. Check industry reports for market share estimates
4. Identify distributors via trade show lists, partner pages, B2B directories
5. Map channel coverage and identify gaps

---

## Dimension 6: Brand & Marketing (品牌营销)

### Sub-items
- Brand positioning and value proposition (how they tell their story)
- Advertising spend and strategy: Google Ads, Facebook Ads, TikTok Ads
- SEO/SEM performance: keyword rankings, organic vs. paid traffic
- Content marketing: blog, video, podcast output and quality
- KOL/influencer partnerships: who promotes them, engagement levels
- PR and media coverage: tone, frequency, key messages
- Brand sentiment: social listening, review aggregation

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Semrush / Ahrefs | SEO/SEM, keyword data | Paid |
| SimilarWeb | Traffic sources, engagement | Free/paid |
| Facebook Ad Library | Active ad creatives | Free |
| Google Ads Transparency Center | Google ad history | Free |
| Brand24 / Mention | Social listening | Paid |
| TikTok Creative Center | TikTok ad trends | Free |

### Research Method
1. Use Semrush/Ahrefs to analyze organic and paid search strategy
2. Check Facebook Ad Library and Google Ads Transparency for active campaigns
3. Scan social media for KOL partnerships and branded content
4. Use social listening tools for brand sentiment analysis
5. Analyze content output frequency and quality across channels

---

## Dimension 7: Customer Relationships (客户关系)

### Sub-items
- Main customers (identified via customs data, bills of lading, shipping manifests)
- Customer concentration: top 5/10 customer revenue share
- Customer repeat purchase rate and retention metrics
- Customer reviews, testimonials, and word-of-mouth
- Customer churn signals and complaints
- Key account relationships (long-term contracts, exclusivity)

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| ImportGenius / Panjiva | Import/export customer identification | Paid |
| 52wmb.com (外贸邦) | China customs buyer/seller data | Paid |
| LinkedIn (customer company employees) | B2B customer identification | Free/paid |
| G2 / Capterra / Trustpilot | B2B/B2C reviews | Free |
| Amazon / app store reviews | Consumer reviews | Free |
| Company case studies / testimonials | Named customers | Free |

### Research Method
1. Search customs databases for the competitor's shipping records to identify buyers
2. Check company website case studies and testimonials for named customers
3. Scrape review platforms for customer satisfaction signals
4. Analyze review patterns for common complaints and praise themes
5. Estimate customer concentration from available data

---

## Dimension 8: Technology & IP (技术IP)

### Sub-items
- Patent portfolio: quantity, quality, technology fields, geographic coverage
- R&D investment ratio (R&D as % of revenue)
- Technology barriers / moat: trade secrets, proprietary algorithms, exclusive licenses
- Digitalization level: e-commerce maturity, ERP/CRM adoption, automation
- Open source contributions and developer community presence (for tech companies)
- Technical talent pool: key engineers, research team size

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Google Patents | Global patents | Free |
| 智慧芽 (Patsnap) | Patent analytics | Paid |
| WIPO Patentscope | International patents | Free |
| USPTO / EPO / CNIPA | Regional patent offices | Free |
| GitHub | Open source contributions | Free |
| Company filings (R&D expense) | Public companies | Free |

### Research Method
1. Search patent databases by assignee name to build patent portfolio map
2. Categorize patents by technology field and analyze filing trends
3. Check annual reports for R&D spending data
4. Evaluate digitalization through website tech stack (BuiltWith, Wappalyzer)
5. Search GitHub for open source repositories and developer activity

---

## Dimension 9: Business Trends (业务趋势)

### Sub-items
- Revenue and profit trend over 3-5 years
- Business model evolution (e.g., product to service, offline to online)
- Market position changes (gaining or losing share)
- Geographic expansion or contraction
- Product category expansion or pruning
- Recent strategic pivots, restructurings, or layoffs
- Key milestone events (funding, acquisitions, leadership changes)

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Annual reports / 10-K (multi-year) | Public companies | Free |
| Crunchbase (funding timeline) | Startups | Free/paid |
| News archives (Google News, Factiva) | Events and milestones | Free/paid |
| LinkedIn (employee count trend) | Growth/contraction signals | Free/paid |
| SimilarWeb (traffic trend) | Online growth signals | Free/paid |
| Wayback Machine | Website evolution | Free |

### Research Method
1. Pull 3-5 years of financial data for trend analysis
2. Use LinkedIn employee count as a proxy for growth/contraction
3. Search news archives for key events and strategic shifts
4. Use Wayback Machine to track website and positioning evolution
5. Synthesize into a timeline of major milestones

---

## Dimension 10: Sales Platforms & Social Media (销售平台与社媒)

### Sub-items
- E-commerce platforms: Amazon, eBay, Shopify, Alibaba, Walmart, Etsy, independent DTC sites
- App Store presence: iOS App Store, Google Play rankings and reviews
- Social media accounts: Facebook, Instagram, TikTok, LinkedIn, YouTube, Twitter/X, Pinterest
- Follower counts, engagement rates, posting frequency per platform
- Content strategy: themes, formats (video, image, live), tone of voice
- Paid social spending estimates
- Influencer/affiliate program structure

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Platform direct search | Account discovery | Free |
| Social Blade / HypeAuditor | Social media analytics | Free/paid |
| Sensor Tower / data.ai | App rankings and data | Paid |
| Helium 10 / Jungle Scout | Amazon seller data | Paid |
| BuiltWith | E-commerce tech stack | Free/paid |
| SimilarWeb | Platform traffic | Free/paid |

### Research Method
1. Search each major platform for the competitor's official accounts
2. Use Social Blade for follower growth trends and engagement metrics
3. Check app stores for mobile app presence and ratings
4. Identify all e-commerce storefronts (marketplace + DTC sites)
5. Analyze content themes and posting cadence across platforms
6. Estimate paid social spending from ad library data

---

## Dimension 11: Compliance & Risk (合规风险)

### Sub-items
- Legal proceedings: lawsuits filed and faced (IP, contract, employment, consumer)
- Regulatory penalties: fines, sanctions, compliance violations
- Product recalls and safety incidents
- Intellectual property disputes (infringement claims, ITC actions)
- Environmental, social, governance (ESG) risks
- Policy and regulatory exposure (trade tariffs, data privacy, industry-specific)
- Insurance and risk management practices

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Court records (US: PACER, PacerMonitor) | US litigation | Paid |
| 中国裁判文书网 / 企查查司法 | China litigation | Free/paid |
| CPSC recalls (US) | Product recalls | Free |
| EU RAPEX | EU product safety | Free |
| SEC enforcement actions | US securities | Free |
| News / legal databases (LexisNexis) | Comprehensive | Paid |
| ITC EDIS | US trade disputes | Free |

### Research Method
1. Search court databases by company name for litigation history
2. Check recall databases for product safety incidents
3. Search regulatory enforcement databases
4. Monitor news for compliance-related events
5. Assess regulatory exposure based on industry and geography

---

## Dimension 12: Strategic Moves (战略动向)

### Sub-items
- Recent M&A activity: acquisitions, divestitures, mergers
- Strategic partnerships and joint ventures
- New market entry signals (geographic, product category)
- Capital operations: IPO plans, delisting, restructuring, share buybacks
- Leadership changes (CEO, key executives, board members)
- Public strategic statements (earnings calls, press releases, investor day)
- Investment priorities and capital allocation direction

### Data Sources
| Source | Coverage | Access |
|---|---|---|
| Crunchbase / PitchBook | M&A and funding | Paid |
| Press releases (PR Newswire, Business Wire) | Official announcements | Free |
| Earnings call transcripts (Seeking Alpha) | Public companies | Free/paid |
| News (Google News, Reuters, Bloomberg) | Strategic moves | Free/paid |
| SEC 8-K filings | Material events | Free |
| LinkedIn (leadership changes) | Executive moves | Free/paid |

### Research Method
1. Search news and press releases for recent strategic announcements
2. Check Crunchbase for M&A and investment activity
3. Review earnings call transcripts for forward-looking statements
4. Monitor SEC filings for material events (8-K)
5. Track LinkedIn for leadership departures and arrivals
6. Synthesize into a strategic direction assessment
