from app.core.config import get_settings
from app.services.scrapers.base import SearchScraper
from app.services.scrapers.brightdata import BrightDataSearchScraper
from app.services.scrapers.mock import MockSearchScraper
from app.services.scrapers.playwright_amazon import PlaywrightAmazonSearchScraper


def get_search_scraper() -> SearchScraper:
    provider = get_settings().scraper_provider.lower()

    if provider == "mock":
        return MockSearchScraper()
    if provider == "playwright":
        return PlaywrightAmazonSearchScraper()
    if provider == "brightdata":
        return BrightDataSearchScraper()

    raise ValueError(f"Unsupported SCRAPER_PROVIDER: {provider}")

