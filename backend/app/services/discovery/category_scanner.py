from dataclasses import dataclass, field

from app.services.discovery.rules import ProductLayer, ProductTag, RuleEvaluation, ScannerRuleConfig, evaluate_product
from app.services.discovery.seed_products import SeedProduct, load_seed_products


@dataclass(frozen=True)
class ScannedProduct:
    product: SeedProduct
    evaluation: RuleEvaluation

    @property
    def asin(self) -> str:
        return self.product.asin

    @property
    def layer(self) -> ProductLayer:
        return self.evaluation.layer

    @property
    def tags(self) -> list[ProductTag]:
        return self.evaluation.tags


@dataclass(frozen=True)
class CategoryScanResult:
    products: list[ScannedProduct] = field(default_factory=list)

    @property
    def total_products_scanned(self) -> int:
        return len(self.products)

    @property
    def rejected(self) -> list[ScannedProduct]:
        return [product for product in self.products if product.layer == ProductLayer.REJECTED]

    @property
    def research(self) -> list[ScannedProduct]:
        return [product for product in self.products if product.layer == ProductLayer.RESEARCH]

    @property
    def opportunities(self) -> list[ScannedProduct]:
        return [product for product in self.products if product.layer == ProductLayer.OPPORTUNITY]

    @property
    def total_products_filtered(self) -> int:
        return len(self.rejected)


def scan_products(
    products: list[SeedProduct] | None = None,
    config: ScannerRuleConfig | None = None,
    category: str | None = None,
) -> CategoryScanResult:
    source_products = products or load_seed_products()
    if category is not None:
        source_products = [product for product in source_products if product.category == category]

    scanned = [
        ScannedProduct(product=product, evaluation=evaluate_product(product, config=config))
        for product in sorted(source_products, key=lambda item: item.asin)
    ]
    return CategoryScanResult(products=scanned)


def opportunity_products(
    products: list[SeedProduct] | None = None,
    config: ScannerRuleConfig | None = None,
    category: str | None = None,
) -> list[ScannedProduct]:
    return scan_products(products=products, config=config, category=category).opportunities
