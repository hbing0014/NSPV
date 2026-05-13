from typing import Protocol

from app.schemas.analysis import ProductOut


class ScraperError(Exception):
    pass


class ScraperBlockedError(ScraperError):
    pass


class SearchScraper(Protocol):
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        ...
