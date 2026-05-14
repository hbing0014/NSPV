from app.services.discovery.keyword_clusters import (
    build_primary_keyword,
    build_secondary_keywords,
    generate_keyword_cluster,
)
from app.services.discovery.seed_products import SeedProduct, load_seed_products


def make_product(product_name: str, category: str = "Kitchen & Dining", brand: str | None = None) -> SeedProduct:
    return SeedProduct(
        asin="NSPVTEST01",
        category=category,
        product_name=product_name,
        brand=brand,
        avg_price=29.99,
        avg_rating=4.4,
        avg_reviews_top10=420,
        min_reviews_top10=88,
        sponsored_density=0.24,
        weight_kg=0.48,
        estimated_monthly_sales=900,
        estimated_monthly_revenue=26991,
        sample_type="test",
    )


def test_under_sink_organizer_generates_expected_cluster() -> None:
    cluster = generate_keyword_cluster(make_product("Under Sink Organizer"))

    assert cluster.primary_keyword == "under sink organizer"
    assert "sink organizer" in cluster.secondary_keywords
    assert "under sink storage" in cluster.secondary_keywords
    assert any("kitchen" in keyword for keyword in cluster.long_tail_keywords)
    assert any("cabinet" in keyword for keyword in cluster.long_tail_keywords)


def test_primary_keyword_removes_brand_terms() -> None:
    primary = build_primary_keyword("SeedHome Under Sink Organizer", brand="SeedHome")

    assert primary == "under sink organizer"


def test_primary_keyword_removes_size_and_marketing_terms() -> None:
    primary = build_primary_keyword("Premium Large 12 Inch Cabinet Door Spice Rack Set")

    assert primary == "cabinet door spice rack"


def test_secondary_keywords_are_stable_and_deduped() -> None:
    secondary = build_secondary_keywords("water bottle storage rack")

    assert secondary == [
        "storage rack",
        "water bottle",
        "water bottle storage organizer",
    ]


def test_storage_category_generates_storage_semantic_long_tails() -> None:
    cluster = generate_keyword_cluster(
        make_product(
            "Acrylic Drawer Dividers",
            category="Storage & Organization",
            brand="StoreSeed",
        )
    )

    assert cluster.primary_keyword == "acrylic drawer dividers"
    assert any("storage" in keyword for keyword in cluster.long_tail_keywords)
    assert any("closet" in keyword for keyword in cluster.long_tail_keywords)
    assert any("home organization" in keyword for keyword in cluster.long_tail_keywords)


def test_all_seed_products_generate_non_empty_keyword_clusters() -> None:
    clusters = [generate_keyword_cluster(product) for product in load_seed_products()]

    assert len(clusters) == 30
    assert all(cluster.primary_keyword for cluster in clusters)
    assert all(cluster.secondary_keywords for cluster in clusters)
    assert all(cluster.long_tail_keywords for cluster in clusters)


def test_keyword_generation_is_deterministic_for_seed_products() -> None:
    first = [generate_keyword_cluster(product) for product in load_seed_products()]
    second = [generate_keyword_cluster(product) for product in load_seed_products()]

    assert first == second
