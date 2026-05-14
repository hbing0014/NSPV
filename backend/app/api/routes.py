from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_optional_current_user
from app.core.config import get_settings
from app.core.errors import ApiError
from app.db.session import get_db
from app.models.tables import Keyword, KeywordProductSnapshot, Product, Project, ScraperRun, SelectionReport, User
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, ProductOut, ReportListItem
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
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
