import hashlib
import random

from app.schemas.analysis import ProductOut


BRANDS = [
    "HomePeak",
    "KitchPro",
    "SimpleNest",
    "Amazon Basics",
    "ClearSpace",
    "DailyEase",
    "UrbanShelf",
    "BrightHome",
]


def stable_seed(keyword: str) -> int:
    digest = hashlib.sha256(keyword.lower().encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def estimate_search_volume(keyword: str) -> int:
    seed = stable_seed(keyword)
    base = 4000 + seed % 62000
    if any(term in keyword.lower() for term in ["organizer", "storage", "rack", "kitchen"]):
        base += 12000
    return min(base, 95000)


def fetch_top20_products(keyword: str, marketplace: str) -> list[ProductOut]:
    rng = random.Random(stable_seed(f"{marketplace}:{keyword}"))
    products: list[ProductOut] = []
    keyword_title = keyword.title()

    for index in range(1, 21):
        brand = rng.choice(BRANDS)
        is_sponsored = rng.random() < 0.32
        review_count = max(6, int(rng.lognormvariate(6.0, 1.0)))
        if index <= 3:
            review_count = int(review_count * rng.uniform(1.4, 2.6))
        price = round(rng.uniform(12.99, 49.99), 2)
        rating = round(min(4.9, max(3.8, rng.normalvariate(4.45, 0.25))), 1)
        monthly_sales = int(max(60, rng.lognormvariate(5.6, 0.55)))

        products.append(
            ProductOut(
                asin=f"B0{stable_seed(keyword + str(index)) % 10_000_000:07d}",
                title=f"{brand} {keyword_title} for Kitchen and Home, Size {index}",
                brand=brand,
                price=price,
                rating=rating,
                review_count=review_count,
                monthly_sales_est=monthly_sales,
                monthly_revenue_est=round(monthly_sales * price, 2),
                bsr=int(rng.uniform(500, 90000)),
                is_sponsored=is_sponsored,
                seller_type="FBA",
                image_url=None,
                product_url=None,
                organic_rank=None if is_sponsored else index,
                sponsored_rank=index if is_sponsored else None,
            )
        )

    return products
