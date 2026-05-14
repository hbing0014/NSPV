from pathlib import Path

from app.services.discovery.seed_products import (
    SeedProduct,
    group_seed_products_by_category,
    load_seed_products,
    seed_categories,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "v2_seed_products.json"


def test_seed_products_load_deterministically() -> None:
    first = load_seed_products(FIXTURE_PATH)
    second = load_seed_products(FIXTURE_PATH)

    assert [product.asin for product in first] == [product.asin for product in second]
    assert [product.product_name for product in first] == [product.product_name for product in second]


def test_seed_products_cover_required_categories() -> None:
    products = load_seed_products(FIXTURE_PATH)

    assert len(products) >= 30
    assert seed_categories(products) == [
        "Home & Kitchen",
        "Kitchen & Dining",
        "Storage & Organization",
    ]


def test_seed_products_have_unique_asins_and_valid_models() -> None:
    products = load_seed_products(FIXTURE_PATH)
    asins = [product.asin for product in products]

    assert len(asins) == len(set(asins))
    assert all(isinstance(product, SeedProduct) for product in products)


def test_seed_products_do_not_include_fake_links_or_images() -> None:
    raw_text = FIXTURE_PATH.read_text(encoding="utf-8")

    assert "product_url" not in raw_text
    assert "image_url" not in raw_text
    assert "amazon.com" not in raw_text


def test_seed_products_cover_rule_fixture_cases() -> None:
    products = load_seed_products(FIXTURE_PATH)

    assert any(product.sample_type == "low_risk" for product in products)
    assert any(product.sample_type == "medium_risk" for product in products)
    assert any(product.avg_reviews_top10 > 1500 for product in products)
    assert any(product.amazon_basics_present for product in products)
    assert any(product.weight_kg and product.weight_kg > 1 for product in products)
    assert any(product.is_fragile for product in products)
    assert any(product.avg_price < 15 for product in products)
    assert any(product.seasonality_score > 0.8 for product in products)


def test_group_seed_products_by_category_is_stable() -> None:
    grouped = group_seed_products_by_category(load_seed_products(FIXTURE_PATH))

    assert list(grouped) == [
        "Home & Kitchen",
        "Kitchen & Dining",
        "Storage & Organization",
    ]
    assert all(len(products) == 10 for products in grouped.values())
    assert grouped["Kitchen & Dining"][0].asin == "NSPVK00001"
