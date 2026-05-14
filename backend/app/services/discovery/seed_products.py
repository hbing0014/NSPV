import json
from pathlib import Path

from pydantic import BaseModel, Field


DEFAULT_SEED_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "v2_seed_products.json"


class SeedProduct(BaseModel):
    asin: str = Field(min_length=10, max_length=20)
    category: str
    product_name: str
    brand: str | None = None
    avg_price: float = Field(gt=0)
    avg_rating: float = Field(ge=0, le=5)
    avg_reviews_top10: float = Field(ge=0)
    min_reviews_top10: int = Field(ge=0)
    sponsored_density: float = Field(ge=0, le=1)
    amazon_basics_present: bool = False
    weight_kg: float | None = Field(default=None, ge=0)
    is_fragile: bool = False
    seasonality_score: float = Field(default=0, ge=0, le=1)
    estimated_monthly_sales: int = Field(default=0, ge=0)
    estimated_monthly_revenue: float = Field(default=0, ge=0)
    patent_risk_level: str = "unknown"
    sample_type: str


def load_seed_products(path: Path | None = None) -> list[SeedProduct]:
    seed_path = path or DEFAULT_SEED_PATH
    records = json.loads(seed_path.read_text(encoding="utf-8"))
    products = [SeedProduct.model_validate(record) for record in records]
    return sorted(products, key=lambda product: product.asin)


def seed_categories(products: list[SeedProduct] | None = None) -> list[str]:
    seed_products = products or load_seed_products()
    return sorted({product.category for product in seed_products})


def group_seed_products_by_category(products: list[SeedProduct] | None = None) -> dict[str, list[SeedProduct]]:
    grouped: dict[str, list[SeedProduct]] = {}
    for product in products or load_seed_products():
        grouped.setdefault(product.category, []).append(product)
    return {category: sorted(items, key=lambda item: item.asin) for category, items in sorted(grouped.items())}
