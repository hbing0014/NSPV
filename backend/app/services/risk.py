from app.schemas.analysis import ScoreDetails

WARNING_MESSAGES = {
    "top10_reviews_high": {
        "zh-CN": "Top10平均Review过高，新店进入难度大",
        "en": "Top10 average reviews are too high for a new seller",
    },
    "sponsored_density_high": {
        "zh-CN": "广告竞争激烈，PPC成本风险高",
        "en": "Sponsored density is high, which raises PPC cost risk",
    },
    "amazon_basics_present": {
        "zh-CN": "存在Amazon自营品牌竞争风险",
        "en": "Amazon private-label competition risk is present",
    },
    "avg_price_low": {
        "zh-CN": "客单价偏低，广告和利润空间不足",
        "en": "Average price is too low for healthy ad and profit room",
    },
    "mature_market": {
        "zh-CN": "产品成熟度高，差异化难度大",
        "en": "Product maturity is high, making differentiation difficult",
    },
    "price_outside_target": {
        "zh-CN": "首页均价与目标售价区间不匹配",
        "en": "Page-one average price does not match the target price range",
    },
}


def warning_text(code: str, locale: str) -> str:
    messages = WARNING_MESSAGES[code]
    return messages.get(locale, messages["zh-CN"])


def generate_risk_warnings(
    details: ScoreDetails,
    target_price_min: float,
    target_price_max: float,
    locale: str = "zh-CN",
) -> list[str]:
    warnings: list[str] = []

    if details.avg_reviews_top10 > 2500:
        warnings.append(warning_text("top10_reviews_high", locale))
    if details.sponsored_density > 0.50:
        warnings.append(warning_text("sponsored_density_high", locale))
    if details.amazon_basics_present:
        warnings.append(warning_text("amazon_basics_present", locale))
    if details.avg_price < 15:
        warnings.append(warning_text("avg_price_low", locale))
    if details.avg_rating > 4.8 and details.avg_reviews_top10 > 2000:
        warnings.append(warning_text("mature_market", locale))
    if details.avg_price < target_price_min or details.avg_price > target_price_max:
        warnings.append(warning_text("price_outside_target", locale))

    return warnings
