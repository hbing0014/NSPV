"""add v2 discovery schema

Revision ID: 0002_v2_discovery_schema
Revises: 0001_initial_schema
Create Date: 2026-05-14 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_v2_discovery_schema"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("category_name", sa.String(length=255), nullable=False),
        sa.Column("parent_category", sa.String(length=255), nullable=True),
        sa.Column("amazon_category_id", sa.String(length=100), nullable=True),
        sa.Column("marketplace", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("priority_level", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index("ix_categories_category_name", "categories", ["category_name"], unique=False)
    op.create_index("ix_categories_amazon_category_id", "categories", ["amazon_category_id"], unique=False)
    op.create_index("ix_categories_marketplace", "categories", ["marketplace"], unique=False)
    op.create_index("ix_categories_is_active", "categories", ["is_active"], unique=False)
    op.create_index("ix_categories_priority_level", "categories", ["priority_level"], unique=False)

    op.create_table(
        "category_scan_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("marketplace", sa.String(length=20), nullable=False),
        sa.Column("scan_type", sa.String(length=50), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("total_products_found", sa.Integer(), nullable=False),
        sa.Column("total_products_filtered", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_category_scan_jobs_id"), "category_scan_jobs", ["id"], unique=False)
    op.create_index("ix_category_scan_jobs_category_id", "category_scan_jobs", ["category_id"], unique=False)
    op.create_index("ix_category_scan_jobs_marketplace", "category_scan_jobs", ["marketplace"], unique=False)
    op.create_index("ix_category_scan_jobs_scan_type", "category_scan_jobs", ["scan_type"], unique=False)
    op.create_index("ix_category_scan_jobs_source_type", "category_scan_jobs", ["source_type"], unique=False)
    op.create_index("ix_category_scan_jobs_status", "category_scan_jobs", ["status"], unique=False)

    op.create_table(
        "category_products",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("scan_job_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("bsr", sa.Integer(), nullable=True),
        sa.Column("is_sponsored", sa.Boolean(), nullable=False),
        sa.Column("seller_type", sa.String(length=100), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("dimensions", sa.JSON(), nullable=False),
        sa.Column("is_fragile", sa.Boolean(), nullable=False),
        sa.Column("estimated_monthly_sales", sa.Integer(), nullable=True),
        sa.Column("estimated_monthly_revenue", sa.Float(), nullable=True),
        sa.Column("amazon_basics_present", sa.Boolean(), nullable=False),
        sa.Column("seasonality_score", sa.Float(), nullable=True),
        sa.Column("patent_risk_level", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scan_job_id"], ["category_scan_jobs.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_category_products_id"), "category_products", ["id"], unique=False)
    op.create_index("ix_category_products_scan_job_id", "category_products", ["scan_job_id"], unique=False)
    op.create_index("ix_category_products_category_id", "category_products", ["category_id"], unique=False)
    op.create_index("ix_category_products_asin", "category_products", ["asin"], unique=False)
    op.create_index("ix_category_products_patent_risk_level", "category_products", ["patent_risk_level"], unique=False)

    op.create_table(
        "product_opportunities",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=True),
        sa.Column("primary_keyword", sa.String(length=255), nullable=False),
        sa.Column("keyword_cluster_id", sa.Integer(), nullable=True),
        sa.Column("avg_price", sa.Float(), nullable=False),
        sa.Column("avg_rating", sa.Float(), nullable=False),
        sa.Column("avg_reviews_top10", sa.Float(), nullable=False),
        sa.Column("min_reviews_top10", sa.Integer(), nullable=False),
        sa.Column("monthly_search_volume", sa.Integer(), nullable=False),
        sa.Column("estimated_monthly_sales", sa.Integer(), nullable=False),
        sa.Column("estimated_monthly_revenue", sa.Float(), nullable=False),
        sa.Column("demand_score", sa.Float(), nullable=False),
        sa.Column("competition_score", sa.Float(), nullable=False),
        sa.Column("profit_score", sa.Float(), nullable=False),
        sa.Column("opportunity_score", sa.Float(), nullable=False),
        sa.Column("launch_score", sa.Float(), nullable=False),
        sa.Column("supplier_score", sa.Float(), nullable=False),
        sa.Column("npfs_score", sa.Float(), nullable=False),
        sa.Column("estimated_budget_rmb", sa.Float(), nullable=False),
        sa.Column("estimated_moq", sa.Integer(), nullable=False),
        sa.Column("estimated_first_order_qty", sa.Integer(), nullable=False),
        sa.Column("estimated_launch_days", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=50), nullable=False),
        sa.Column("recommendation", sa.String(length=100), nullable=False),
        sa.Column("is_red_ocean", sa.Boolean(), nullable=False),
        sa.Column("is_amazon_basics", sa.Boolean(), nullable=False),
        sa.Column("is_fragile", sa.Boolean(), nullable=False),
        sa.Column("is_seasonal", sa.Boolean(), nullable=False),
        sa.Column("is_heavy", sa.Boolean(), nullable=False),
        sa.Column("is_patent_risk", sa.Boolean(), nullable=False),
        sa.Column("differentiation_paths", sa.JSON(), nullable=False),
        sa.Column("key_risks", sa.JSON(), nullable=False),
        sa.Column("key_opportunities", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_product_opportunities_id"), "product_opportunities", ["id"], unique=False)
    op.create_index("ix_product_opportunities_category_id", "product_opportunities", ["category_id"], unique=False)
    op.create_index("ix_product_opportunities_asin", "product_opportunities", ["asin"], unique=False)
    op.create_index("ix_product_opportunities_primary_keyword", "product_opportunities", ["primary_keyword"], unique=False)
    op.create_index("ix_product_opportunities_npfs_score", "product_opportunities", ["npfs_score"], unique=False)
    op.create_index("ix_product_opportunities_risk_level", "product_opportunities", ["risk_level"], unique=False)
    op.create_index("ix_product_opportunities_recommendation", "product_opportunities", ["recommendation"], unique=False)
    op.create_index("ix_product_opportunities_is_red_ocean", "product_opportunities", ["is_red_ocean"], unique=False)

    op.create_table(
        "launch_scores",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("product_opportunity_id", sa.Integer(), nullable=True),
        sa.Column("asin", sa.String(length=20), nullable=False),
        sa.Column("estimated_moq", sa.Integer(), nullable=True),
        sa.Column("estimated_unit_cost_rmb", sa.Float(), nullable=True),
        sa.Column("estimated_shipping_cost_rmb", sa.Float(), nullable=True),
        sa.Column("estimated_packaging_complexity", sa.String(length=50), nullable=True),
        sa.Column("estimated_ppc_launch_cost", sa.Float(), nullable=True),
        sa.Column("estimated_review_difficulty", sa.Float(), nullable=True),
        sa.Column("estimated_inventory_cycle_days", sa.Integer(), nullable=True),
        sa.Column("estimated_total_launch_budget", sa.Float(), nullable=True),
        sa.Column("launch_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_opportunity_id"], ["product_opportunities.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_launch_scores_id"), "launch_scores", ["id"], unique=False)
    op.create_index("ix_launch_scores_product_opportunity_id", "launch_scores", ["product_opportunity_id"], unique=False)
    op.create_index("ix_launch_scores_asin", "launch_scores", ["asin"], unique=False)
    op.create_index("ix_launch_scores_launch_score", "launch_scores", ["launch_score"], unique=False)

    op.create_table(
        "discovery_reports",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("input_category", sa.String(length=100), nullable=False),
        sa.Column("input_budget_rmb", sa.Float(), nullable=False),
        sa.Column("input_risk_preference", sa.String(length=50), nullable=False),
        sa.Column("input_price_min", sa.Float(), nullable=True),
        sa.Column("input_price_max", sa.Float(), nullable=True),
        sa.Column("input_weight_limit", sa.Float(), nullable=True),
        sa.Column("exclude_red_ocean", sa.Boolean(), nullable=False),
        sa.Column("exclude_amazon_basics", sa.Boolean(), nullable=False),
        sa.Column("total_products_scanned", sa.Integer(), nullable=False),
        sa.Column("total_products_filtered", sa.Integer(), nullable=False),
        sa.Column("total_recommendations", sa.Integer(), nullable=False),
        sa.Column("recommended_products", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strategy_advice", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_discovery_reports_id"), "discovery_reports", ["id"], unique=False)
    op.create_index("ix_discovery_reports_project_id", "discovery_reports", ["project_id"], unique=False)
    op.create_index("ix_discovery_reports_user_id", "discovery_reports", ["user_id"], unique=False)

    with op.batch_alter_table("selection_reports") as batch_op:
        batch_op.add_column(sa.Column("product_opportunity_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_selection_reports_product_opportunity_id", ["product_opportunity_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_selection_reports_product_opportunity_id",
            "product_opportunities",
            ["product_opportunity_id"],
            ["id"],
            ondelete="SET NULL",
        )

    enable_row_level_security()


def downgrade() -> None:
    with op.batch_alter_table("selection_reports") as batch_op:
        batch_op.drop_constraint(
            "fk_selection_reports_product_opportunity_id",
            type_="foreignkey",
        )
        batch_op.drop_index("ix_selection_reports_product_opportunity_id")
        batch_op.drop_column("product_opportunity_id")

    op.drop_index("ix_discovery_reports_user_id", table_name="discovery_reports")
    op.drop_index("ix_discovery_reports_project_id", table_name="discovery_reports")
    op.drop_index(op.f("ix_discovery_reports_id"), table_name="discovery_reports")
    op.drop_table("discovery_reports")

    op.drop_index("ix_launch_scores_launch_score", table_name="launch_scores")
    op.drop_index("ix_launch_scores_asin", table_name="launch_scores")
    op.drop_index("ix_launch_scores_product_opportunity_id", table_name="launch_scores")
    op.drop_index(op.f("ix_launch_scores_id"), table_name="launch_scores")
    op.drop_table("launch_scores")

    op.drop_index("ix_product_opportunities_is_red_ocean", table_name="product_opportunities")
    op.drop_index("ix_product_opportunities_recommendation", table_name="product_opportunities")
    op.drop_index("ix_product_opportunities_risk_level", table_name="product_opportunities")
    op.drop_index("ix_product_opportunities_npfs_score", table_name="product_opportunities")
    op.drop_index("ix_product_opportunities_primary_keyword", table_name="product_opportunities")
    op.drop_index("ix_product_opportunities_asin", table_name="product_opportunities")
    op.drop_index("ix_product_opportunities_category_id", table_name="product_opportunities")
    op.drop_index(op.f("ix_product_opportunities_id"), table_name="product_opportunities")
    op.drop_table("product_opportunities")

    op.drop_index("ix_category_products_patent_risk_level", table_name="category_products")
    op.drop_index("ix_category_products_asin", table_name="category_products")
    op.drop_index("ix_category_products_category_id", table_name="category_products")
    op.drop_index("ix_category_products_scan_job_id", table_name="category_products")
    op.drop_index(op.f("ix_category_products_id"), table_name="category_products")
    op.drop_table("category_products")

    op.drop_index("ix_category_scan_jobs_status", table_name="category_scan_jobs")
    op.drop_index("ix_category_scan_jobs_source_type", table_name="category_scan_jobs")
    op.drop_index("ix_category_scan_jobs_scan_type", table_name="category_scan_jobs")
    op.drop_index("ix_category_scan_jobs_marketplace", table_name="category_scan_jobs")
    op.drop_index("ix_category_scan_jobs_category_id", table_name="category_scan_jobs")
    op.drop_index(op.f("ix_category_scan_jobs_id"), table_name="category_scan_jobs")
    op.drop_table("category_scan_jobs")

    op.drop_index("ix_categories_priority_level", table_name="categories")
    op.drop_index("ix_categories_is_active", table_name="categories")
    op.drop_index("ix_categories_marketplace", table_name="categories")
    op.drop_index("ix_categories_amazon_category_id", table_name="categories")
    op.drop_index("ix_categories_category_name", table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")


def enable_row_level_security() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for table_name in [
        "categories",
        "category_scan_jobs",
        "category_products",
        "product_opportunities",
        "launch_scores",
        "discovery_reports",
    ]:
        op.execute(f"alter table {table_name} enable row level security")
