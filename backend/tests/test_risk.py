from app.schemas.analysis import ScoreDetails
from app.services.risk import generate_risk_warnings


def score_details(**overrides) -> ScoreDetails:
    base = {
        "monthly_search_volume": 20000,
        "avg_monthly_sales": 300,
        "search_trend": "stable",
        "seasonality_score": 70,
        "avg_price": 25,
        "avg_rating": 4.4,
        "avg_reviews_top10": 300,
        "avg_reviews_top3": 500,
        "min_reviews_top10": 20,
        "sponsored_density": 0.2,
        "brand_concentration": 0.2,
        "amazon_basics_present": False,
        "net_margin": 0.25,
        "roi": 0.6,
        "break_even_acos": 0.35,
        "negative_review_density": 0.2,
        "pain_points_count": 2,
        "listing_quality_weakness": 20,
        "homogenization_level": 30,
        "upgrade_potential": 40,
    }
    base.update(overrides)
    return ScoreDetails(**base)


def warnings_for(details: ScoreDetails, target_price_min: float = 20, target_price_max: float = 40) -> list[str]:
    return generate_risk_warnings(details, target_price_min, target_price_max)


def test_warns_when_top10_reviews_are_too_high() -> None:
    warnings = warnings_for(score_details(avg_reviews_top10=2501))

    assert "Top10平均Review过高，新店进入难度大" in warnings


def test_warns_when_sponsored_density_is_too_high() -> None:
    warnings = warnings_for(score_details(sponsored_density=0.51))

    assert "广告竞争激烈，PPC成本风险高" in warnings


def test_warns_when_amazon_basics_is_present() -> None:
    warnings = warnings_for(score_details(amazon_basics_present=True))

    assert "存在Amazon自营品牌竞争风险" in warnings


def test_warns_when_price_is_too_low() -> None:
    warnings = warnings_for(score_details(avg_price=14.99), target_price_min=10, target_price_max=40)

    assert "客单价偏低，广告和利润空间不足" in warnings


def test_warns_when_market_is_too_mature() -> None:
    warnings = warnings_for(score_details(avg_rating=4.9, avg_reviews_top10=2001))

    assert "产品成熟度高，差异化难度大" in warnings


def test_warns_when_price_is_outside_target_range() -> None:
    warnings = warnings_for(score_details(avg_price=45), target_price_min=20, target_price_max=40)

    assert "首页均价与目标售价区间不匹配" in warnings


def test_returns_no_warning_for_balanced_market() -> None:
    warnings = warnings_for(score_details())

    assert warnings == []
