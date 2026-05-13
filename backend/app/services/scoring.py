from collections import Counter

from app.schemas.analysis import ProductOut, ScoreDetails
from app.services.mock_crawler import estimate_search_volume


USD_TO_RMB = 7.2
SCORING_VERSION = "v1.0.0"


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def demand_score(search_volume: int) -> float:
    if search_volume > 50000:
        return 95
    if search_volume >= 20000:
        return 85
    if search_volume >= 10000:
        return 75
    if search_volume >= 5000:
        return 60
    return 40


def review_competition_score(avg_reviews_top10: float) -> float:
    if avg_reviews_top10 < 100:
        return 95
    if avg_reviews_top10 < 300:
        return 85
    if avg_reviews_top10 < 800:
        return 65
    if avg_reviews_top10 < 2000:
        return 40
    return 15


def sponsored_score(sponsored_density: float) -> float:
    if sponsored_density < 0.15:
        return 90
    if sponsored_density < 0.30:
        return 70
    if sponsored_density < 0.50:
        return 45
    return 20


def profit_score(net_margin: float) -> float:
    if net_margin > 0.35:
        return 95
    if net_margin >= 0.25:
        return 80
    if net_margin >= 0.15:
        return 60
    return 30


def recommendation(nsfs: float) -> str:
    if nsfs >= 85:
        return "Strongly Recommended"
    if nsfs >= 70:
        return "Worth Research"
    if nsfs >= 50:
        return "Caution"
    return "Avoid"


def risk_level(nsfs: float, warnings: list[str]) -> str:
    severe = len(warnings) >= 3
    if nsfs < 50 or severe:
        return "High"
    if nsfs < 70 or warnings:
        return "Medium"
    return "Low"


def analyze_products(
    keyword: str,
    products: list[ProductOut],
    budget_rmb: float,
    target_price_min: float,
    target_price_max: float,
) -> dict:
    top10 = products[:10]
    top3 = products[:3]
    prices = [p.price or 0 for p in products if p.price]
    ratings = [p.rating or 0 for p in products if p.rating]
    reviews_top10 = [p.review_count or 0 for p in top10]
    reviews_top3 = [p.review_count or 0 for p in top3]
    monthly_sales = [p.monthly_sales_est or 0 for p in products]
    brands = [p.brand or "Unknown" for p in top10]

    avg_price = sum(prices) / max(len(prices), 1)
    avg_rating = sum(ratings) / max(len(ratings), 1)
    avg_reviews_top10 = sum(reviews_top10) / max(len(reviews_top10), 1)
    avg_reviews_top3 = sum(reviews_top3) / max(len(reviews_top3), 1)
    min_reviews_top10 = min(reviews_top10) if reviews_top10 else 0
    sponsored_density = len([p for p in products if p.is_sponsored]) / max(len(products), 1)
    brand_counts = Counter(brands)
    brand_concentration = brand_counts.most_common(1)[0][1] / max(len(top10), 1)
    amazon_basics_present = any((p.brand or "").lower() == "amazon basics" for p in products)
    monthly_search_volume = estimate_search_volume(keyword)
    avg_monthly_sales = sum(monthly_sales) / max(len(monthly_sales), 1)

    purchase_cost_rmb = avg_price * USD_TO_RMB * 0.28
    shipping_cost_rmb = avg_price * USD_TO_RMB * 0.08
    fba_fee_usd = max(3.8, avg_price * 0.16)
    referral_fee_usd = avg_price * 0.15
    estimated_ad_cost_usd = avg_price * 0.12
    total_cost_usd = purchase_cost_rmb / USD_TO_RMB + shipping_cost_rmb / USD_TO_RMB + fba_fee_usd + referral_fee_usd + estimated_ad_cost_usd
    net_profit_usd = avg_price - total_cost_usd
    net_margin = net_profit_usd / avg_price if avg_price else 0
    roi = net_profit_usd / (purchase_cost_rmb / USD_TO_RMB + shipping_cost_rmb / USD_TO_RMB) if purchase_cost_rmb else 0
    break_even_acos = max(0, net_margin + 0.12)

    review_score = review_competition_score(avg_reviews_top10)
    ad_score = sponsored_score(sponsored_density)
    comp_score = review_score * 0.7 + ad_score * 0.3
    if amazon_basics_present:
        comp_score -= 15
    if brand_concentration > 0.4:
        comp_score -= 8
    comp_score = clamp(comp_score)

    negative_review_density = clamp((4.7 - avg_rating) / 1.2, 0, 1)
    pain_points_count = int(negative_review_density * 8) + (1 if min_reviews_top10 < 100 else 0)
    listing_quality_weakness = clamp((4.6 - avg_rating) * 30 + (1 - min(avg_reviews_top10 / 2000, 1)) * 30, 0, 100)
    homogenization_level = clamp(brand_concentration * 100 + (avg_rating - 4.3) * 30, 0, 100)
    upgrade_potential = clamp(negative_review_density * 55 + listing_quality_weakness * 0.45, 0, 100)

    if 4.2 <= avg_rating <= 4.5 and avg_reviews_top10 < 800:
        opp_score = 86
    elif avg_rating > 4.8 and avg_reviews_top10 > 2000:
        opp_score = 35
    else:
        opp_score = clamp(55 + upgrade_potential * 0.45 - homogenization_level * 0.2)

    dem_score = demand_score(monthly_search_volume)
    prof_score = profit_score(net_margin)
    nsfs = dem_score * 0.25 + comp_score * 0.30 + prof_score * 0.25 + opp_score * 0.20

    warnings: list[str] = []
    if avg_reviews_top10 > 2500:
        warnings.append("Top10平均Review过高，新店进入难度大")
    if sponsored_density > 0.50:
        warnings.append("广告竞争激烈，PPC成本风险高")
    if amazon_basics_present:
        warnings.append("存在Amazon自营品牌竞争风险")
    if avg_price < 15:
        warnings.append("客单价偏低，广告和利润空间不足")
    if avg_rating > 4.8 and avg_reviews_top10 > 2000:
        warnings.append("产品成熟度高，差异化难度大")
    if avg_price < target_price_min or avg_price > target_price_max:
        warnings.append("首页均价与目标售价区间不匹配")

    suggestions = [
        "Avoid competing on main keyword only",
        "Focus on long-tail keywords",
        "Recommended first order quantity: 300-500 units" if budget_rmb >= 80000 else "Recommended first order quantity: 150-300 units",
    ]
    opportunities = [
        "Review数量较低的Listing可作为差异化切入口",
        "优先验证可升级的功能点和包装组合",
    ]
    summary = build_summary(nsfs, warnings, avg_reviews_top10, sponsored_density)

    details = ScoreDetails(
        monthly_search_volume=monthly_search_volume,
        avg_monthly_sales=round(avg_monthly_sales, 2),
        search_trend="stable",
        seasonality_score=70,
        avg_price=round(avg_price, 2),
        avg_rating=round(avg_rating, 2),
        avg_reviews_top10=round(avg_reviews_top10, 2),
        avg_reviews_top3=round(avg_reviews_top3, 2),
        min_reviews_top10=min_reviews_top10,
        sponsored_density=round(sponsored_density, 2),
        brand_concentration=round(brand_concentration, 2),
        amazon_basics_present=amazon_basics_present,
        net_margin=round(net_margin, 2),
        roi=round(roi, 2),
        break_even_acos=round(break_even_acos, 2),
        negative_review_density=round(negative_review_density, 2),
        pain_points_count=pain_points_count,
        listing_quality_weakness=round(listing_quality_weakness, 2),
        homogenization_level=round(homogenization_level, 2),
        upgrade_potential=round(upgrade_potential, 2),
    )

    return {
        "nsfs_score": round(nsfs, 1),
        "demand_score": round(dem_score, 1),
        "competition_score": round(comp_score, 1),
        "profit_score": round(prof_score, 1),
        "opportunity_score": round(opp_score, 1),
        "recommendation": recommendation(nsfs),
        "risk_level": risk_level(nsfs, warnings),
        "summary": summary,
        "warnings": warnings,
        "suggestions": suggestions,
        "opportunities": opportunities,
        "score_details": details,
    }


def build_summary(nsfs: float, warnings: list[str], avg_reviews_top10: float, sponsored_density: float) -> str:
    if nsfs >= 70:
        base = "需求和利润空间具备继续研究价值"
    elif nsfs >= 50:
        base = "存在一定机会，但新店进入需要谨慎验证"
    else:
        base = "当前关键词对新店不够友好"

    review_text = "首页Review压力较高" if avg_reviews_top10 > 800 else "Review门槛相对可控"
    ad_text = "广告竞争偏强" if sponsored_density > 0.3 else "广告密度尚可"
    risk_text = f"，主要风险：{warnings[0]}" if warnings else ""
    return f"{base}，{review_text}，{ad_text}{risk_text}。"
