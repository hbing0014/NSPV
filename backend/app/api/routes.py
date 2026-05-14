from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.core.config import get_settings
from app.core.errors import ApiError
from app.db.session import get_db
from app.models.tables import (
    Category,
    DiscoveryReport,
    Keyword,
    KeywordProductSnapshot,
    Product,
    ProductOpportunity,
    Project,
    ScraperRun,
    SelectionReport,
    User,
)
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, ProductOut, ReportListItem
from app.schemas.discovery import (
    DiscoverProductOut,
    DiscoverProductsResponse,
    DiscoveryRequest,
    RadarProductOut,
    RadarProductsResponse,
)
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.discovery.discovery_service import DiscoveredProduct, discover_products
from app.services.scoring import analyze_products
from app.services.scrapers import get_search_scraper
from app.services.scrapers.base import ScraperError

router = APIRouter(prefix="/api")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_project_or_404(project_id: int, db: Session, current_user: User | None = None) -> Project:
    project = db.get(Project, project_id)
    if project is None or not can_access_project(project, current_user):
        raise ApiError(
            code="PROJECT_NOT_FOUND",
            message="Project not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"project_id": project_id},
        )
    return project


@router.post("/projects", response_model=ProjectOut)
def create_project(
    request: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> ProjectOut:
    project = Project(**request.model_dump(), status="active", user_id=current_user.id if current_user else None)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project_to_response(project)


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> list[ProjectOut]:
    projects = db.scalars(
        select(Project)
        .where(project_owner_filter(current_user))
        .order_by(Project.created_at.desc())
        .limit(100)
    ).all()
    return [project_to_response(project) for project in projects]


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> ProjectOut:
    return project_to_response(get_project_or_404(project_id, db, current_user))


@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    request: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> ProjectOut:
    project = get_project_or_404(project_id, db, current_user)
    updates = request.model_dump(exclude_unset=True)
    next_target_price_min = updates.get("target_price_min", project.target_price_min)
    next_target_price_max = updates.get("target_price_max", project.target_price_max)
    if next_target_price_min is not None and next_target_price_max is not None and next_target_price_min > next_target_price_max:
        raise ApiError(
            code="VALIDATION_ERROR",
            message="target_price_min cannot exceed target_price_max",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "field": "target_price_min",
                "target_price_min": next_target_price_min,
                "target_price_max": next_target_price_max,
            },
        )

    for field, value in updates.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project_to_response(project)


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, bool]:
    project = get_project_or_404(project_id, db, current_user)
    db.delete(project)
    db.commit()
    return {"deleted": True}


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> AnalyzeResponse:
    if request.target_price_min > request.target_price_max:
        raise ApiError(
            code="VALIDATION_ERROR",
            message="target_price_min cannot exceed target_price_max",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "field": "target_price_min",
                "target_price_min": request.target_price_min,
                "target_price_max": request.target_price_max,
            },
        )

    scraper_run = ScraperRun(
        keyword=request.keyword,
        marketplace=request.marketplace,
        provider=get_settings().scraper_provider.lower(),
        status="running",
        product_count=0,
        started_at=now_utc(),
    )
    db.add(scraper_run)
    db.flush()

    try:
        products = get_search_scraper().fetch_top20_products(request.keyword, request.marketplace)
    except ScraperError as exc:
        finish_scraper_run(db, scraper_run, "failed", 0, str(exc))
        raise ApiError(
            code="SCRAPER_FAILED",
            message=str(exc),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"keyword": request.keyword, "marketplace": request.marketplace},
        ) from exc
    except NotImplementedError as exc:
        finish_scraper_run(db, scraper_run, "failed", 0, str(exc))
        raise ApiError(
            code="SCRAPER_FAILED",
            message=str(exc),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"keyword": request.keyword, "marketplace": request.marketplace},
        ) from exc
    except ValueError as exc:
        finish_scraper_run(db, scraper_run, "failed", 0, str(exc))
        raise ApiError(
            code="SCRAPER_PROVIDER_INVALID",
            message=str(exc),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"provider_error": str(exc)},
        ) from exc

    if not products:
        finish_scraper_run(db, scraper_run, "empty", 0, "Amazon search returned no products.")
        raise ApiError(
            code="SCRAPER_EMPTY_RESULT",
            message="Amazon search returned no products.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"keyword": request.keyword, "marketplace": request.marketplace},
        )

    finish_scraper_run(db, scraper_run, "completed", len(products), None)
    score = analyze_products(
        keyword=request.keyword,
        products=products,
        budget_rmb=request.budget_rmb,
        target_price_min=request.target_price_min,
        target_price_max=request.target_price_max,
        locale=request.locale,
    )

    if request.project_id is not None:
        project = get_project_or_404(request.project_id, db, current_user)
    else:
        project = Project(
            user_id=current_user.id if current_user else None,
            project_name=f"{request.keyword} analysis",
            category=request.category,
            budget_rmb=request.budget_rmb,
            marketplace=request.marketplace,
            target_price_min=request.target_price_min,
            target_price_max=request.target_price_max,
            status="active",
        )
        db.add(project)
        db.flush()

    if request.product_opportunity_id is not None and db.get(ProductOpportunity, request.product_opportunity_id) is None:
        raise ApiError(
            code="PRODUCT_OPPORTUNITY_NOT_FOUND",
            message="Product opportunity not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"product_opportunity_id": request.product_opportunity_id},
        )

    details = score["score_details"]
    keyword = Keyword(
        project_id=project.id,
        keyword=request.keyword,
        marketplace=request.marketplace,
        category=request.category,
        monthly_search_volume=details.monthly_search_volume,
        avg_price=details.avg_price,
        avg_rating=details.avg_rating,
        avg_reviews_top10=details.avg_reviews_top10,
        avg_reviews_top3=details.avg_reviews_top3,
        min_reviews_top10=details.min_reviews_top10,
        sponsored_density=details.sponsored_density,
        amazon_basics_present=details.amazon_basics_present,
    )
    db.add(keyword)
    db.flush()

    saved_products: list[ProductOut] = []
    for rank, item in enumerate(products, start=1):
        product = db.scalar(select(Product).where(Product.asin == item.asin))
        if product is None:
            product = Product(
                asin=item.asin,
                marketplace=request.marketplace,
                title=item.title,
                brand=item.brand,
                price=item.price,
                rating=item.rating,
                review_count=item.review_count,
                monthly_sales_est=item.monthly_sales_est,
                monthly_revenue_est=item.monthly_revenue_est,
                bsr=item.bsr,
                is_sponsored=item.is_sponsored,
                seller_type=item.seller_type,
                image_url=item.image_url,
                product_url=item.product_url,
            )
            db.add(product)
            db.flush()

        snapshot = KeywordProductSnapshot(
            keyword_id=keyword.id,
            product_id=product.id,
            asin=item.asin,
            organic_rank=None if item.is_sponsored else rank,
            sponsored_rank=rank if item.is_sponsored else None,
            page_no=1,
            is_sponsored=item.is_sponsored,
            price=item.price,
            rating=item.rating,
            review_count=item.review_count,
        )
        db.add(snapshot)
        saved_products.append(
            item.model_copy(update={"organic_rank": snapshot.organic_rank, "sponsored_rank": snapshot.sponsored_rank})
        )

    report = SelectionReport(
        project_id=project.id,
        keyword_id=keyword.id,
        scraper_run_id=scraper_run.id,
        product_opportunity_id=request.product_opportunity_id,
        nsfs_score=score["nsfs_score"],
        demand_score=score["demand_score"],
        competition_score=score["competition_score"],
        profit_score=score["profit_score"],
        opportunity_score=score["opportunity_score"],
        recommendation=score["recommendation"],
        risk_level=score["risk_level"],
        summary=score["summary"],
        key_risks=score["warnings"],
        key_opportunities=score["opportunities"],
        action_suggestions=score["suggestions"],
        products_snapshot=[product.model_dump() for product in saved_products],
        score_details=details.model_dump(),
        input_payload=request.model_dump(mode="json"),
        scoring_version=score["scoring_version"],
        analysis_status="completed",
        error_message=None,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report_to_response(report, request.keyword)


@router.post("/discover/products", response_model=DiscoverProductsResponse)
def discover_product_opportunities(
    request: DiscoveryRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> DiscoverProductsResponse:
    if request.project_id is not None:
        project = get_project_or_404(request.project_id, db, current_user)
    else:
        project = Project(
            user_id=current_user.id if current_user else None,
            project_name=f"{request.category} discovery",
            category=request.category,
            budget_rmb=request.budget_rmb,
            marketplace=request.marketplace,
            target_price_min=request.price_min,
            target_price_max=request.price_max,
            status="active",
        )
        db.add(project)
        db.flush()

    result = discover_products(request)
    category = get_or_create_category(db, request.category, request.marketplace)
    saved_products: list[tuple[DiscoveredProduct, ProductOpportunity]] = []
    for item in result.products:
        opportunity = ProductOpportunity(
            category_id=category.id,
            asin=item.source.asin,
            product_name=item.source.product_name,
            brand=item.source.brand,
            primary_keyword=item.keyword_cluster.primary_keyword,
            keyword_cluster_id=None,
            avg_price=item.source.avg_price,
            avg_rating=item.source.avg_rating,
            avg_reviews_top10=item.source.avg_reviews_top10,
            min_reviews_top10=item.source.min_reviews_top10,
            monthly_search_volume=int(item.source.estimated_monthly_sales * 20),
            estimated_monthly_sales=item.source.estimated_monthly_sales,
            estimated_monthly_revenue=item.source.estimated_monthly_revenue,
            demand_score=item.demand_score,
            competition_score=item.competition_score,
            profit_score=item.profit_score,
            opportunity_score=item.opportunity_score,
            launch_score=item.launch_score,
            supplier_score=item.supplier_score,
            npfs_score=item.npfs_score,
            estimated_budget_rmb=item.estimated_budget_rmb,
            estimated_moq=item.estimated_moq,
            estimated_first_order_qty=item.estimated_moq,
            estimated_launch_days=item.estimated_launch_days,
            risk_level=item.risk_level,
            recommendation=item.recommendation,
            is_red_ocean="RED_OCEAN" in item.tags,
            is_amazon_basics=item.source.amazon_basics_present,
            is_fragile=item.source.is_fragile,
            is_seasonal=item.source.seasonality_score > 0.7,
            is_heavy=item.source.weight_kg is not None and item.source.weight_kg > 1,
            is_patent_risk=item.source.patent_risk_level == "high",
            differentiation_paths=item.key_opportunities,
            key_risks=item.warnings,
            key_opportunities=item.key_opportunities,
        )
        db.add(opportunity)
        db.flush()
        saved_products.append((item, opportunity))

    report = DiscoveryReport(
        project_id=project.id,
        user_id=current_user.id if current_user else None,
        input_category=request.category,
        input_budget_rmb=request.budget_rmb,
        input_risk_preference=request.risk_preference,
        input_price_min=request.price_min,
        input_price_max=request.price_max,
        input_weight_limit=request.weight_limit_kg,
        exclude_red_ocean=request.exclude_red_ocean,
        exclude_amazon_basics=request.exclude_amazon_basics,
        total_products_scanned=result.total_products_scanned,
        total_products_filtered=result.total_products_filtered,
        total_recommendations=len(saved_products),
        recommended_products=[opportunity.id for _, opportunity in saved_products],
        summary=f"Found {len(saved_products)} product opportunities for {request.category}.",
        strategy_advice="Validate the primary keyword before sourcing and avoid high-risk products.",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return DiscoverProductsResponse(
        discovery_report_id=report.id,
        project_id=project.id,
        total_products_scanned=result.total_products_scanned,
        total_products_filtered=result.total_products_filtered,
        total_recommendations=len(saved_products),
        products=[discovered_product_to_response(item, opportunity) for item, opportunity in saved_products],
    )


@router.get("/radar/products", response_model=RadarProductsResponse)
def list_radar_products(
    category: str | None = None,
    risk_level: str | None = None,
    budget_max: float | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    sort: str = "highest_npfs",
    limit: int = 50,
    db: Session = Depends(get_db),
) -> RadarProductsResponse:
    limit = max(1, min(limit, 100))
    query = select(ProductOpportunity).outerjoin(Category)

    if category:
        query = query.where(Category.category_name == category)
    if risk_level:
        query = query.where(ProductOpportunity.risk_level == risk_level)
    if budget_max is not None:
        query = query.where(ProductOpportunity.estimated_budget_rmb <= budget_max)
    if price_min is not None:
        query = query.where(ProductOpportunity.avg_price >= price_min)
    if price_max is not None:
        query = query.where(ProductOpportunity.avg_price <= price_max)

    query = query.order_by(*radar_sort_order(sort)).limit(limit)
    products = db.scalars(query).all()
    return RadarProductsResponse(
        total=len(products),
        products=[radar_product_to_response(product) for product in products],
    )


@router.get("/radar/products/{opportunity_id}", response_model=RadarProductOut)
def get_radar_product(opportunity_id: int, db: Session = Depends(get_db)) -> RadarProductOut:
    opportunity = db.get(ProductOpportunity, opportunity_id)
    if opportunity is None:
        raise ApiError(
            code="PRODUCT_OPPORTUNITY_NOT_FOUND",
            message="Product opportunity not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"opportunity_id": opportunity_id},
        )
    return radar_product_to_response(opportunity)


@router.get("/reports/{report_id}", response_model=AnalyzeResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> AnalyzeResponse:
    report = db.get(SelectionReport, report_id)
    if report is None or not can_access_project(report.project, current_user):
        raise ApiError(
            code="REPORT_NOT_FOUND",
            message="Report not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"report_id": report_id},
        )
    return report_to_response(report, report.keyword.keyword)


@router.get("/projects/{project_id}/reports", response_model=list[ReportListItem])
def get_project_reports(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> list[ReportListItem]:
    get_project_or_404(project_id, db, current_user)
    reports = db.scalars(
        select(SelectionReport)
        .where(SelectionReport.project_id == project_id)
        .order_by(SelectionReport.created_at.desc())
    ).all()
    return [report_to_list_item(report) for report in reports]


@router.get("/reports", response_model=list[ReportListItem])
def get_all_reports(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> list[ReportListItem]:
    reports = db.scalars(
        select(SelectionReport)
        .join(Project)
        .where(project_owner_filter(current_user))
        .order_by(SelectionReport.created_at.desc())
        .limit(50)
    ).all()
    return [report_to_list_item(report) for report in reports]


def report_to_response(report: SelectionReport, keyword_text: str) -> AnalyzeResponse:
    return AnalyzeResponse(
        report_id=report.id,
        project_id=report.project_id,
        keyword_id=report.keyword_id,
        scraper_run_id=report.scraper_run_id,
        keyword=keyword_text,
        nsfs_score=report.nsfs_score,
        recommendation=report.recommendation,
        risk_level=report.risk_level,
        demand_score=report.demand_score,
        competition_score=report.competition_score,
        profit_score=report.profit_score,
        opportunity_score=report.opportunity_score,
        summary=report.summary,
        warnings=report.key_risks or [],
        suggestions=report.action_suggestions or [],
        opportunities=report.key_opportunities or [],
        score_details=report.score_details,
        products=[ProductOut(**product) for product in (report.products_snapshot or [])],
        input_payload=report.input_payload or {},
        scoring_version=report.scoring_version,
        analysis_status=report.analysis_status,
        error_message=report.error_message,
        created_at=report.created_at,
    )


def discovered_product_to_response(item: DiscoveredProduct, opportunity: ProductOpportunity) -> DiscoverProductOut:
    return DiscoverProductOut(
        product_opportunity_id=opportunity.id,
        asin=item.source.asin,
        product_name=item.source.product_name,
        category=item.source.category,
        primary_keyword=item.keyword_cluster.primary_keyword,
        secondary_keywords=item.keyword_cluster.secondary_keywords,
        long_tail_keywords=item.keyword_cluster.long_tail_keywords,
        avg_price=item.source.avg_price,
        avg_rating=item.source.avg_rating,
        avg_reviews_top10=item.source.avg_reviews_top10,
        min_reviews_top10=item.source.min_reviews_top10,
        sponsored_density=item.source.sponsored_density,
        npfs_score=item.npfs_score,
        demand_score=item.demand_score,
        competition_score=item.competition_score,
        profit_score=item.profit_score,
        opportunity_score=item.opportunity_score,
        launch_score=item.launch_score,
        supplier_score=item.supplier_score,
        estimated_budget_rmb=item.estimated_budget_rmb,
        estimated_moq=item.estimated_moq,
        estimated_launch_days=item.estimated_launch_days,
        risk_level=item.risk_level,
        recommendation=item.recommendation,
        tags=item.tags,
        warnings=item.warnings,
        key_opportunities=item.key_opportunities,
    )


def radar_sort_order(sort: str):
    if sort == "lowest_risk":
        risk_order = case(
            (ProductOpportunity.risk_level == "low", 1),
            (ProductOpportunity.risk_level == "medium", 2),
            (ProductOpportunity.risk_level == "high", 3),
            else_=4,
        )
        return (
            risk_order.asc(),
            ProductOpportunity.npfs_score.desc(),
        )
    if sort == "lowest_budget":
        return (
            ProductOpportunity.estimated_budget_rmb.asc(),
            ProductOpportunity.npfs_score.desc(),
        )
    if sort == "highest_profit":
        return (
            ProductOpportunity.profit_score.desc(),
            ProductOpportunity.npfs_score.desc(),
        )
    if sort == "easiest_launch":
        return (
            ProductOpportunity.launch_score.desc(),
            ProductOpportunity.npfs_score.desc(),
        )
    return (ProductOpportunity.npfs_score.desc(),)


def radar_product_to_response(opportunity: ProductOpportunity) -> RadarProductOut:
    return RadarProductOut(
        product_opportunity_id=opportunity.id,
        asin=opportunity.asin,
        product_name=opportunity.product_name,
        category=opportunity.category.category_name if opportunity.category else None,
        primary_keyword=opportunity.primary_keyword,
        avg_price=opportunity.avg_price,
        avg_rating=opportunity.avg_rating,
        avg_reviews_top10=opportunity.avg_reviews_top10,
        min_reviews_top10=opportunity.min_reviews_top10,
        npfs_score=opportunity.npfs_score,
        demand_score=opportunity.demand_score,
        competition_score=opportunity.competition_score,
        profit_score=opportunity.profit_score,
        opportunity_score=opportunity.opportunity_score,
        launch_score=opportunity.launch_score,
        supplier_score=opportunity.supplier_score,
        estimated_budget_rmb=opportunity.estimated_budget_rmb,
        estimated_moq=opportunity.estimated_moq,
        estimated_launch_days=opportunity.estimated_launch_days,
        risk_level=opportunity.risk_level,
        recommendation=opportunity.recommendation,
        is_red_ocean=opportunity.is_red_ocean,
        is_amazon_basics=opportunity.is_amazon_basics,
        is_fragile=opportunity.is_fragile,
        is_seasonal=opportunity.is_seasonal,
        is_heavy=opportunity.is_heavy,
        is_patent_risk=opportunity.is_patent_risk,
        differentiation_paths=opportunity.differentiation_paths or [],
        key_risks=opportunity.key_risks or [],
        key_opportunities=opportunity.key_opportunities or [],
        created_at=opportunity.created_at,
        updated_at=opportunity.updated_at,
    )


def report_to_list_item(report: SelectionReport) -> ReportListItem:
    return ReportListItem(
        report_id=report.id,
        project_id=report.project_id,
        scraper_run_id=report.scraper_run_id,
        keyword=report.keyword.keyword,
        nsfs_score=report.nsfs_score,
        recommendation=report.recommendation,
        risk_level=report.risk_level,
        analysis_status=report.analysis_status,
        created_at=report.created_at,
    )


def finish_scraper_run(
    db: Session,
    scraper_run: ScraperRun,
    status_value: str,
    product_count: int,
    error_message: str | None,
) -> None:
    scraper_run.status = status_value
    scraper_run.product_count = product_count
    scraper_run.error_message = error_message
    scraper_run.finished_at = now_utc()
    db.commit()


def can_access_project(project: Project, current_user: User | None) -> bool:
    expected_user_id = current_user.id if current_user else None
    return project.user_id == expected_user_id


def project_owner_filter(current_user: User | None):
    return Project.user_id == (current_user.id if current_user else None)


def project_to_response(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        project_name=project.project_name,
        category=project.category,
        budget_rmb=project.budget_rmb,
        marketplace=project.marketplace,
        target_price_min=project.target_price_min,
        target_price_max=project.target_price_max,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def get_or_create_category(db: Session, category_name: str, marketplace: str) -> Category:
    category = db.scalar(
        select(Category).where(
            Category.category_name == category_name,
            Category.marketplace == marketplace,
        )
    )
    if category is not None:
        return category

    category = Category(
        category_name=category_name,
        parent_category=None,
        amazon_category_id=None,
        marketplace=marketplace,
        is_active=True,
        priority_level="high",
    )
    db.add(category)
    db.flush()
    return category
