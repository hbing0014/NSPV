from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan_type: Mapped[str] = mapped_column(String(50), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    projects: Mapped[list["Project"]] = relationship(back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    project_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    budget_rmb: Mapped[float] = mapped_column(Float)
    marketplace: Mapped[str] = mapped_column(String(20), default="US")
    target_price_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_price_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    user: Mapped[User | None] = relationship(back_populates="projects")
    keywords: Mapped[list["Keyword"]] = relationship(back_populates="project")
    reports: Mapped[list["SelectionReport"]] = relationship(back_populates="project")


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    marketplace: Mapped[str] = mapped_column(String(20), default="US")
    category: Mapped[str] = mapped_column(String(100))
    monthly_search_volume: Mapped[int] = mapped_column(Integer, default=0)
    avg_price: Mapped[float] = mapped_column(Float, default=0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0)
    avg_reviews_top10: Mapped[float] = mapped_column(Float, default=0)
    avg_reviews_top3: Mapped[float] = mapped_column(Float, default=0)
    min_reviews_top10: Mapped[int] = mapped_column(Integer, default=0)
    sponsored_density: Mapped[float] = mapped_column(Float, default=0)
    amazon_basics_present: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    project: Mapped[Project] = relationship(back_populates="keywords")
    snapshots: Mapped[list["KeywordProductSnapshot"]] = relationship(back_populates="keyword")
    reports: Mapped[list["SelectionReport"]] = relationship(back_populates="keyword")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asin: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    marketplace: Mapped[str] = mapped_column(String(20), default="US")
    title: Mapped[str] = mapped_column(Text)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_sales_est: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_revenue_est: Mapped[float | None] = mapped_column(Float, nullable=True)
    bsr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_sponsored: Mapped[bool] = mapped_column(Boolean, default=False)
    seller_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    snapshots: Mapped[list["KeywordProductSnapshot"]] = relationship(back_populates="product")


class KeywordProductSnapshot(Base):
    __tablename__ = "keyword_product_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    asin: Mapped[str] = mapped_column(String(20), index=True)
    organic_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sponsored_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_no: Mapped[int] = mapped_column(Integer, default=1)
    is_sponsored: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    keyword: Mapped[Keyword] = relationship(back_populates="snapshots")
    product: Mapped[Product] = relationship(back_populates="snapshots")


class ScraperRun(Base):
    __tablename__ = "scraper_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    marketplace: Mapped[str] = mapped_column(String(20), default="US")
    provider: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    product_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reports: Mapped[list["SelectionReport"]] = relationship(back_populates="scraper_run")


class SelectionReport(Base):
    __tablename__ = "selection_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), index=True)
    scraper_run_id: Mapped[int | None] = mapped_column(ForeignKey("scraper_runs.id"), index=True, nullable=True)
    nsfs_score: Mapped[float] = mapped_column(Float)
    demand_score: Mapped[float] = mapped_column(Float)
    competition_score: Mapped[float] = mapped_column(Float)
    profit_score: Mapped[float] = mapped_column(Float)
    opportunity_score: Mapped[float] = mapped_column(Float)
    recommendation: Mapped[str] = mapped_column(String(100))
    risk_level: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(Text)
    key_risks: Mapped[list[str]] = mapped_column(JSON, default=list)
    key_opportunities: Mapped[list[str]] = mapped_column(JSON, default=list)
    action_suggestions: Mapped[list[str]] = mapped_column(JSON, default=list)
    products_snapshot: Mapped[list[dict]] = mapped_column(JSON, default=list)
    score_details: Mapped[dict] = mapped_column(JSON, default=dict)
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    scoring_version: Mapped[str] = mapped_column(String(50), default="v1.0.0", index=True)
    analysis_status: Mapped[str] = mapped_column(String(50), default="completed", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, index=True)

    project: Mapped[Project] = relationship(back_populates="reports")
    keyword: Mapped[Keyword] = relationship(back_populates="reports")
    scraper_run: Mapped[ScraperRun | None] = relationship(back_populates="reports")
