export const locales = ["zh-CN", "en"] as const;

export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "zh-CN";

export const dictionaries = {
  "zh-CN": {
    language: {
      label: "语言",
      chinese: "中文",
      english: "English"
    },
    nav: {
      analyze: "分析",
      reports: "历史报告"
    },
    home: {
      eyebrow: "New Seller Product Validator",
      title: "Amazon 新店选品风险判断",
      subtitle: "输入一个美国站关键词，系统会分析首页 Top20 商品结构，生成 NSFS 评分、红海预警和进入建议。",
      fields: {
        project: "项目",
        loadingProjects: "正在同步已有项目，不影响本次分析",
        createProject: "不选择项目，本次分析自动创建新项目",
        keyword: "关键词",
        marketplace: "Marketplace",
        category: "类目",
        budget: "预算 RMB",
        targetPriceMin: "目标售价下限",
        targetPriceMax: "目标售价上限",
        excludeRedOcean: "默认排除红海市场"
      },
      error: {
        projectLoad: "项目加载失败",
        connect: "无法连接 NSPV API，请检查后端服务后重试。",
        analyzeFailed: "分析失败，请重试。",
        title: "分析失败"
      },
      actions: {
        analyze: "开始分析",
        retry: "重试分析",
        loading: "正在分析 Amazon Top20..."
      },
      signals: {
        demand: ["需求", "搜索量和预估月销量"],
        competition: ["竞争", "Review结构、广告和品牌集中度"],
        profit: ["利润", "利润率、ROI 和 Break-even ACOS"],
        opportunity: ["机会", "评分缺口和产品升级潜力"]
      }
    },
    reports: {
      title: "历史报告",
      subtitle: "最近 50 次关键词分析。",
      newAnalysis: "新分析",
      empty: "暂无报告。",
      columns: {
        keyword: "关键词",
        nsfs: "NSFS",
        recommendation: "推荐等级",
        risk: "风险",
        created: "创建时间"
      }
    },
    report: {
      report: "报告",
      newAnalysis: "新分析",
      nsfsScore: "NSFS 评分",
      risk: "风险",
      keyword: "关键词",
      scoring: "评分版本",
      decisionSummary: "决策摘要",
      avgPrice: "平均价格",
      avgRating: "平均评分",
      sponsored: "广告占比",
      top10Reviews: "Top10 Review",
      scores: {
        demand: "需求分",
        competition: "竞争分",
        profit: "利润分",
        opportunity: "机会分"
      },
      panels: {
        reviewCompetition: "Review 竞争结构",
        redOceanWarnings: "红海预警",
        profitEstimate: "利润估算",
        opportunitySignals: "机会信号",
        actionSuggestions: "操作建议"
      },
      metrics: {
        top10AvgReviews: "Top10平均Review",
        top3AvgReviews: "Top3平均Review",
        top10MinReviews: "Top10最低Review",
        brandConcentration: "品牌集中度",
        netMargin: "净利率",
        roi: "ROI",
        breakEvenAcos: "Break-even ACOS",
        avgMonthlySales: "平均月销量",
        painPoints: "痛点数量",
        upgradePotential: "升级潜力",
        listingWeakness: "Listing弱点",
        homogenization: "同质化程度"
      },
      empty: {
        warnings: "暂无明显红海预警。",
        opportunities: "暂无机会信号。",
        suggestions: "暂无操作建议。"
      },
      products: {
        title: "Top20 商品",
        subtitle: "本报告使用的搜索结果快照。",
        count: "个商品",
        sponsored: "广告",
        organic: "自然",
        columns: {
          rank: "排名",
          product: "商品",
          brand: "品牌",
          price: "价格",
          rating: "评分",
          reviews: "Review",
          sales: "预估销量",
          type: "类型"
        }
      }
    },
    labels: {
      recommendations: {
        "Strongly Recommended": "强烈推荐",
        "Worth Research": "可重点研究",
        Caution: "谨慎",
        Avoid: "建议放弃"
      },
      risks: {
        Low: "低",
        Medium: "中",
        High: "高"
      }
    }
  },
  en: {
    language: {
      label: "Language",
      chinese: "中文",
      english: "English"
    },
    nav: {
      analyze: "Analyze",
      reports: "Reports"
    },
    home: {
      eyebrow: "New Seller Product Validator",
      title: "Amazon New Seller Product Validator",
      subtitle: "Enter a US Amazon keyword to analyze the Top20 product structure, NSFS score, red-ocean warnings, and entry recommendation.",
      fields: {
        project: "Project",
        loadingProjects: "Syncing existing projects. This will not block analysis.",
        createProject: "No project selected. Create one from this analysis",
        keyword: "Keyword",
        marketplace: "Marketplace",
        category: "Category",
        budget: "Budget RMB",
        targetPriceMin: "Target Price Min",
        targetPriceMax: "Target Price Max",
        excludeRedOcean: "Exclude red ocean by default"
      },
      error: {
        projectLoad: "Failed to load projects",
        connect: "Cannot connect to NSPV API. Check the backend server and try again.",
        analyzeFailed: "Analyze failed. Please try again.",
        title: "Analysis failed"
      },
      actions: {
        analyze: "Analyze",
        retry: "Retry Analyze",
        loading: "Analyzing Amazon Top20..."
      },
      signals: {
        demand: ["Demand", "Search volume and estimated monthly sales"],
        competition: ["Competition", "Review structure, ads, brand concentration"],
        profit: ["Profit", "Margin, ROI and break-even ACOS"],
        opportunity: ["Opportunity", "Rating gaps and upgrade potential"]
      }
    },
    reports: {
      title: "Historical Reports",
      subtitle: "Latest 50 keyword analyses.",
      newAnalysis: "New Analysis",
      empty: "No reports yet.",
      columns: {
        keyword: "Keyword",
        nsfs: "NSFS",
        recommendation: "Recommendation",
        risk: "Risk",
        created: "Created"
      }
    },
    report: {
      report: "Report",
      newAnalysis: "New Analysis",
      nsfsScore: "NSFS Score",
      risk: "Risk",
      keyword: "Keyword",
      scoring: "Scoring",
      decisionSummary: "Decision Summary",
      avgPrice: "Avg Price",
      avgRating: "Avg Rating",
      sponsored: "Sponsored",
      top10Reviews: "Top10 Reviews",
      scores: {
        demand: "Demand Score",
        competition: "Competition Score",
        profit: "Profit Score",
        opportunity: "Opportunity Score"
      },
      panels: {
        reviewCompetition: "Review Competition",
        redOceanWarnings: "Red Ocean Warnings",
        profitEstimate: "Profit Estimate",
        opportunitySignals: "Opportunity Signals",
        actionSuggestions: "Action Suggestions"
      },
      metrics: {
        top10AvgReviews: "Top10 Avg Reviews",
        top3AvgReviews: "Top3 Avg Reviews",
        top10MinReviews: "Top10 Min Reviews",
        brandConcentration: "Brand Concentration",
        netMargin: "Net Margin",
        roi: "ROI",
        breakEvenAcos: "Break-even ACOS",
        avgMonthlySales: "Avg Monthly Sales",
        painPoints: "Pain Points",
        upgradePotential: "Upgrade Potential",
        listingWeakness: "Listing Weakness",
        homogenization: "Homogenization"
      },
      empty: {
        warnings: "No major red ocean warning.",
        opportunities: "No opportunity signals yet.",
        suggestions: "No suggestions."
      },
      products: {
        title: "Top20 Products",
        subtitle: "Snapshot used for this report.",
        count: "products",
        sponsored: "Sponsored",
        organic: "Organic",
        columns: {
          rank: "Rank",
          product: "Product",
          brand: "Brand",
          price: "Price",
          rating: "Rating",
          reviews: "Reviews",
          sales: "Sales Est.",
          type: "Type"
        }
      }
    },
    labels: {
      recommendations: {
        "Strongly Recommended": "Strongly Recommended",
        "Worth Research": "Worth Research",
        Caution: "Caution",
        Avoid: "Avoid"
      },
      risks: {
        Low: "Low",
        Medium: "Medium",
        High: "High"
      }
    }
  }
} as const;

export type Dictionary = (typeof dictionaries)[Locale];

export function isLocale(value: string | undefined): value is Locale {
  return value === "zh-CN" || value === "en";
}

export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale];
}

export function translateRecommendation(locale: Locale, value: string) {
  const labels = dictionaries[locale].labels.recommendations as Record<string, string>;
  return labels[value] ?? value;
}

export function translateRisk(locale: Locale, value: string) {
  const labels = dictionaries[locale].labels.risks as Record<string, string>;
  return labels[value] ?? value;
}
