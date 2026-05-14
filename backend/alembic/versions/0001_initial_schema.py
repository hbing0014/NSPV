"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-14 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("plan_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("budget_rmb", sa.Float(), nullable=False),
        sa.Column("marketplace", sa.String(length=20), nullable=False),
        sa.Column("target_price_min", sa.Float(), nullable=True),
        sa.Column("target_price_max", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index("ix_projects_user_id", "projects", ["user_id"], unique=False)
    op.create_index("ix_projects_status", "projects", ["status"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("marketplace", sa.String(length=20), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("monthly_sales_est", sa.Integer(), nullable=True),
        sa.Column("monthly_revenue_est", sa.Float(), nullable=True),
        sa.Column("bsr", sa.Integer(), nullable=True),
        sa.Column("is_sponsored", sa.Boolean(), nullable=False),
        sa.Column("seller_type", sa.String(length=100), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("product_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("asin"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index("ix_products_asin", "products", ["asin"], unique=True)

    op.create_table(
        "scraper_runs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("marketplace", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("product_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_scraper_runs_id"), "scraper_runs", ["id"], unique=False)
    op.create_index("ix_scraper_runs_keyword", "scraper_runs", ["keyword"], unique=False)
    op.create_index("ix_scraper_runs_provider", "scraper_runs", ["provider"], unique=False)
    op.create_index("ix_scraper_runs_status", "scraper_runs", ["status"], unique=False)

    op.create_table(
        "keywords",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("marketplace", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("monthly_search_volume", sa.Integer(), nullable=False),
        sa.Column("avg_price", sa.Float(), nullable=False),
        sa.Column("avg_rating", sa.Float(), nullable=False),
        sa.Column("avg_reviews_top10", sa.Float(), nullable=False),
        sa.Column("avg_reviews_top3", sa.Float(), nullable=False),
        sa.Column("min_reviews_top10", sa.Integer(), nullable=False),
        sa.Column("sponsored_density", sa.Float(), nullable=False),
        sa.Column("amazon_basics_present", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_keywords_id"), "keywords", ["id"], unique=False)
    op.create_index("ix_keywords_keyword", "keywords", ["keyword"], unique=False)
    op.create_index("ix_keywords_project_id", "keywords", ["project_id"], unique=False)

    op.create_table(
        "keyword_product_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("keyword_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("organic_rank", sa.Integer(), nullable=True),
        sa.Column("sponsored_rank", sa.Integer(), nullable=True),
        sa.Column("page_no", sa.Integer(), nullable=False),
        sa.Column("is_sponsored", sa.Boolean(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_keyword_product_snapshots_keyword_id",
        "keyword_product_snapshots",
        ["keyword_id"],
        unique=False,
    )
    op.create_index(
        "ix_keyword_product_snapshots_product_id",
        "keyword_product_snapshots",
        ["product_id"],
        unique=False,
    )
    op.create_index("ix_keyword_product_snapshots_asin", "keyword_product_snapshots", ["asin"], unique=False)
    op.create_index(op.f("ix_keyword_product_snapshots_id"), "keyword_product_snapshots", ["id"], unique=False)

    op.create_table(
        "selection_reports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("keyword_id", sa.Integer(), nullable=False),
        sa.Column("scraper_run_id", sa.Integer(), nullable=True),
        sa.Column("nsfs_score", sa.Float(), nullable=False),
        sa.Column("demand_score", sa.Float(), nullable=False),
        sa.Column("competition_score", sa.Float(), nullable=False),
        sa.Column("profit_score", sa.Float(), nullable=False),
        sa.Column("opportunity_score", sa.Float(), nullable=False),
        sa.Column("recommendation", sa.String(length=100), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("key_risks", sa.JSON(), nullable=False),
        sa.Column("key_opportunities", sa.JSON(), nullable=False),
        sa.Column("action_suggestions", sa.JSON(), nullable=False),
        sa.Column("products_snapshot", sa.JSON(), nullable=False),
        sa.Column("score_details", sa.JSON(), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("scoring_version", sa.String(length=50), nullable=False),
        sa.Column("analysis_status", sa.String(length=50), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scraper_run_id"], ["scraper_runs.id"]),
    )
    op.create_index(op.f("ix_selection_reports_id"), "selection_reports", ["id"], unique=False)
    op.create_index("ix_selection_reports_project_id", "selection_reports", ["project_id"], unique=False)
    op.create_index("ix_selection_reports_keyword_id", "selection_reports", ["keyword_id"], unique=False)
    op.create_index("ix_selection_reports_created_at", "selection_reports", ["created_at"], unique=False)
    op.create_index("ix_selection_reports_analysis_status", "selection_reports", ["analysis_status"], unique=False)
    op.create_index("ix_selection_reports_scoring_version", "selection_reports", ["scoring_version"], unique=False)
    op.create_index("ix_selection_reports_scraper_run_id", "selection_reports", ["scraper_run_id"], unique=False)

    enable_row_level_security()


def downgrade() -> None:
    op.drop_index("ix_selection_reports_scraper_run_id", table_name="selection_reports")
    op.drop_index("ix_selection_reports_scoring_version", table_name="selection_reports")
    op.drop_index("ix_selection_reports_analysis_status", table_name="selection_reports")
    op.drop_index("ix_selection_reports_created_at", table_name="selection_reports")
    op.drop_index("ix_selection_reports_keyword_id", table_name="selection_reports")
    op.drop_index("ix_selection_reports_project_id", table_name="selection_reports")
    op.drop_index(op.f("ix_selection_reports_id"), table_name="selection_reports")
    op.drop_table("selection_reports")

    op.drop_index(op.f("ix_keyword_product_snapshots_id"), table_name="keyword_product_snapshots")
    op.drop_index("ix_keyword_product_snapshots_asin", table_name="keyword_product_snapshots")
    op.drop_index("ix_keyword_product_snapshots_product_id", table_name="keyword_product_snapshots")
    op.drop_index("ix_keyword_product_snapshots_keyword_id", table_name="keyword_product_snapshots")
    op.drop_table("keyword_product_snapshots")

    op.drop_index("ix_keywords_project_id", table_name="keywords")
    op.drop_index("ix_keywords_keyword", table_name="keywords")
    op.drop_index(op.f("ix_keywords_id"), table_name="keywords")
    op.drop_table("keywords")

    op.drop_index("ix_scraper_runs_status", table_name="scraper_runs")
    op.drop_index("ix_scraper_runs_provider", table_name="scraper_runs")
    op.drop_index("ix_scraper_runs_keyword", table_name="scraper_runs")
    op.drop_index(op.f("ix_scraper_runs_id"), table_name="scraper_runs")
    op.drop_table("scraper_runs")

    op.drop_index("ix_products_asin", table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")

    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_table("projects")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")


def enable_row_level_security() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for table_name in [
        "users",
        "projects",
        "keywords",
        "products",
        "keyword_product_snapshots",
        "selection_reports",
        "scraper_runs",
    ]:
        op.execute(f"alter table {table_name} enable row level security")
