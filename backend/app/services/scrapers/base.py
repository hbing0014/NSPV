from typing import Protocol

from app.schemas.analysis import ProductOut


class SearchScraper(Protocol):
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        ...

