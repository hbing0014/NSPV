import re
from urllib.parse import quote_plus

from app.schemas.analysis import ProductOut
from app.services.scrapers.base import ScraperBlockedError, ScraperError


AMAZON_HOSTS = {
    "US": "https://www.amazon.com",
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
JPY_TO_USD = 0.0067


class PlaywrightAmazonSearchScraper:
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        host = AMAZON_HOSTS.get(marketplace.upper())
        if host is None:
            raise ValueError(f"Unsupported marketplace for Playwright scraper: {marketplace}")

        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except ModuleNotFoundError as exc:
            raise ScraperError("Playwright package is not installed.") from exc

        search_url = f"{host}/s?k={quote_plus(keyword)}"

        try:
            with sync_playwright() as playwright:
                browser = None
                browser = playwright.chromium.launch(headless=True)
                try:
                    context = browser.new_context(
                        user_agent=USER_AGENT,
                        locale="en-US",
                        viewport={"width": 1366, "height": 900},
                    )
                    page = context.new_page()
                    page.goto(search_url, wait_until="domcontentloaded", timeout=45000)
                    content = page.content().lower()
                    if "enter the characters you see below" in content or "captcha" in content:
                        raise ScraperBlockedError("Amazon presented a captcha or bot check.")

                    page.wait_for_selector("[data-component-type='s-search-result']", timeout=15000)
                    cards = page.locator("[data-component-type='s-search-result']")
                    products = self._parse_cards(cards, host)
                    return products[:20]
                finally:
                    if browser is not None:
                        browser.close()
        except ScraperError:
            raise
        except PlaywrightTimeoutError as exc:
            raise ScraperError("Amazon search page timed out while loading results.") from exc
        except Exception as exc:
            raise ScraperError(f"Amazon search page could not be parsed: {exc}") from exc

    def _parse_cards(self, cards, host: str) -> list[ProductOut]:
        products: list[ProductOut] = []
        seen_asins: set[str] = set()

        for index in range(cards.count()):
            if len(products) >= 20:
                break

            card = cards.nth(index)
            asin = card.get_attribute("data-asin") or ""
            asin = asin.strip()
            if not asin or asin in seen_asins:
                continue

            title = first_text(card, ["h2 span", "h2 a", "[data-cy='title-recipe'] span"])
            if not title:
                continue

            product_href = first_attribute(card, ["h2 a", "a.a-link-normal.s-no-outline"], "href")
            product_url = normalize_amazon_url(product_href, host, asin)
            price = parse_price(first_text(card, [".a-price .a-offscreen", ".a-price"]))
            rating = parse_rating(first_text(card, [".a-icon-alt"]))
            review_count = parse_int(first_text(card, ["a[href*='customerReviews'] span", ".a-size-base.s-underline-text"]))
            image_url = first_attribute(card, ["img.s-image"], "src")
            is_sponsored = bool(first_text(card, [".puis-sponsored-label-text", "[aria-label='Sponsored']"]))
            organic_rank = None if is_sponsored else len(products) + 1
            sponsored_rank = len(products) + 1 if is_sponsored else None

            products.append(
                ProductOut(
                    asin=asin,
                    title=title,
                    brand=None,
                    price=price,
                    rating=rating,
                    review_count=review_count,
                    is_sponsored=is_sponsored,
                    image_url=image_url,
                    product_url=product_url,
                    organic_rank=organic_rank,
                    sponsored_rank=sponsored_rank,
                )
            )
            seen_asins.add(asin)

        return products


def first_text(root, selectors: list[str]) -> str | None:
    for selector in selectors:
        locator = root.locator(selector)
        if locator.count() == 0:
            continue
        text = locator.first.text_content(timeout=1000)
        if text and text.strip():
            return " ".join(text.split())
    return None


def first_attribute(root, selectors: list[str], attribute: str) -> str | None:
    for selector in selectors:
        locator = root.locator(selector)
        if locator.count() == 0:
            continue
        value = locator.first.get_attribute(attribute, timeout=1000)
        if value:
            return value
    return None


def normalize_amazon_url(href: str | None, host: str, asin: str) -> str:
    if not href:
        return f"{host}/dp/{asin}"
    if "/sspa/click" in href:
        return f"{host}/dp/{asin}"
    if href.startswith("http"):
        return href
    return f"{host}{href}"


def parse_price(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:,\d{3})*(?:\.\d{1,2})?)", text.replace("$", ""))
    if not match:
        return None
    raw_value = match.group(1).replace(",", "")
    if "JPY" in text.upper() or "¥" in text:
        return round(float(raw_value) * JPY_TO_USD, 2)
    if "." not in raw_value and "," not in match.group(1) and 3 <= len(raw_value) <= 5:
        return round(int(raw_value) / 100, 2)
    return float(raw_value)


def parse_rating(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def parse_int(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"(\d[\d,]*)", text)
    return int(match.group(1).replace(",", "")) if match else None
