from app.schemas.analysis import ScoreDetails


def generate_risk_warnings(
    details: ScoreDetails,
    target_price_min: float,
    target_price_max: float,
) -> list[str]:
    warnings: list[str] = []

    if details.avg_reviews_top10 > 2500:
        warnings.append("Top10平均Review过高，新店进入难度大")
    if details.sponsored_density > 0.50:
        warnings.append("广告竞争激烈，PPC成本风险高")
    if details.amazon_basics_present:
        warnings.append("存在Amazon自营品牌竞争风险")
    if details.avg_price < 15:
        warnings.append("客单价偏低，广告和利润空间不足")
    if details.avg_rating > 4.8 and details.avg_reviews_top10 > 2000:
        warnings.append("产品成熟度高，差异化难度大")
    if details.avg_price < target_price_min or details.avg_price > target_price_max:
        warnings.append("首页均价与目标售价区间不匹配")

    return warnings
