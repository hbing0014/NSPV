from app.schemas.analysis import ProductOut
from app.services import mock_crawler


class MockSearchScraper:
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        return mock_crawler.fetch_top20_products(keyword, marketplace)

