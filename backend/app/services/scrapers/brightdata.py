from app.schemas.analysis import ProductOut


class BrightDataSearchScraper:
    def fetch_top20_products(self, keyword: str, marketplace: str) -> list[ProductOut]:
        raise NotImplementedError("BrightData scraper is not implemented yet.")

