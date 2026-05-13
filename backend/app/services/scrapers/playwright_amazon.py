from app.schemas.analysis import ProductOut


class PlaywrightAmazonSearchScraper:
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        raise NotImplementedError("Playwright Amazon scraper is not implemented yet.")

