import re
from dataclasses import dataclass, field

from app.services.discovery.seed_products import SeedProduct


SIZE_PATTERN = re.compile(
    r"\b(\d+(\.\d+)?\s?(inch|inches|in|cm|mm|oz|ounce|ounces|lb|lbs|kg|g|pack|pcs|piece|pieces|set|sets)|x[- ]?large|large|small|medium)\b",
    re.IGNORECASE,
)
TOKEN_PATTERN = re.compile(r"[^a-z0-9\s&-]")

MARKETING_TERMS = {
    "best",
    "premium",
    "upgraded",
    "new",
    "improved",
    "heavy duty",
    "durable",
    "modern",
    "large",
    "small",
    "medium",
    "set",
    "pack",
}

BRAND_SUFFIXES = {
    "seed",
    "seedhome",
    "gripseed",
    "cookseed",
    "boardseed",
    "freshseed",
    "measureseed",
    "bakeseed",
    "rackseed",
    "washseed",
    "livingseed",
    "closetseed",
    "linenseed",
    "bathseed",
    "sleepseed",
    "cleanseed",
    "comfortseed",
    "deskseed",
    "storeseed",
    "labelseed",
    "vanityseed",
    "hookseed",
}

CATEGORY_CONTEXT = {
    "Kitchen & Dining": ["kitchen", "cabinet", "countertop"],
    "Home & Kitchen": ["home", "bedroom", "laundry"],
    "Storage & Organization": ["storage", "closet", "home organization"],
    "Cleaning Tools": ["cleaning", "household"],
    "Household Supplies": ["household", "home"],
}


@dataclass(frozen=True)
class KeywordCluster:
    product_name: str
    category: str
    primary_keyword: str
    secondary_keywords: list[str] = field(default_factory=list)
    long_tail_keywords: list[str] = field(default_factory=list)


def generate_keyword_cluster(product: SeedProduct) -> KeywordCluster:
    primary_keyword = build_primary_keyword(product.product_name, brand=product.brand)
    secondary_keywords = build_secondary_keywords(primary_keyword)
    long_tail_keywords = build_long_tail_keywords(primary_keyword, product.category)
    return KeywordCluster(
        product_name=product.product_name,
        category=product.category,
        primary_keyword=primary_keyword,
        secondary_keywords=secondary_keywords,
        long_tail_keywords=long_tail_keywords,
    )


def build_primary_keyword(product_name: str, brand: str | None = None) -> str:
    normalized = normalize_text(product_name)
    normalized = remove_brand_terms(normalized, brand)
    normalized = SIZE_PATTERN.sub(" ", normalized)
    normalized = remove_marketing_terms(normalized)
    return compact_spaces(normalized)


def build_secondary_keywords(primary_keyword: str) -> list[str]:
    words = primary_keyword.split()
    candidates: list[str] = []

    if len(words) >= 3:
        candidates.append(" ".join(words[-2:]))
        candidates.append(" ".join(words[:2]))
    if "under sink" in primary_keyword and primary_keyword != "sink organizer":
        candidates.append("sink organizer")
    if primary_keyword.endswith("organizer"):
        root = primary_keyword.removesuffix(" organizer").strip()
        if root:
            candidates.append(f"{root} storage")
    if primary_keyword.endswith("rack"):
        root = primary_keyword.removesuffix(" rack").strip()
        if root:
            candidates.append(f"{root} organizer")
    if primary_keyword.endswith("holder"):
        root = primary_keyword.removesuffix(" holder").strip()
        if root:
            candidates.append(f"{root} organizer")
    if len(words) == 2:
        candidates.append(f"{primary_keyword} for home")

    return dedupe_keywords([candidate for candidate in candidates if candidate and candidate != primary_keyword])


def build_long_tail_keywords(primary_keyword: str, category: str) -> list[str]:
    contexts = CATEGORY_CONTEXT.get(category, ["home"])
    templates = [
        "{keyword} for {context}",
        "best {keyword} for {context}",
        "{context} {keyword} for small spaces",
    ]
    long_tail: list[str] = []
    for context in contexts[:3]:
        for template in templates:
            long_tail.append(template.format(keyword=primary_keyword, context=context))
    return dedupe_keywords(long_tail)


def normalize_text(value: str) -> str:
    normalized = value.lower().replace("&", " and ")
    normalized = TOKEN_PATTERN.sub(" ", normalized)
    return compact_spaces(normalized)


def remove_brand_terms(value: str, brand: str | None = None) -> str:
    terms = set(BRAND_SUFFIXES)
    if brand:
        terms.add(normalize_text(brand).replace(" ", ""))
        terms.update(normalize_text(brand).split())

    words = value.split()
    filtered = [word for word in words if word not in terms]
    return " ".join(filtered)


def remove_marketing_terms(value: str) -> str:
    cleaned = value
    for term in sorted(MARKETING_TERMS, key=len, reverse=True):
        cleaned = re.sub(rf"\b{re.escape(term)}\b", " ", cleaned)
    return compact_spaces(cleaned)


def compact_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def dedupe_keywords(keywords: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for keyword in keywords:
        normalized = compact_spaces(keyword)
        if normalized and normalized not in seen:
            deduped.append(normalized)
            seen.add(normalized)
    return deduped
