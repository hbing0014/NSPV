from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ProjectBase(BaseModel):
    project_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    budget_rmb: float = Field(gt=0)
    marketplace: str = Field(default="US", max_length=20)
    target_price_min: float | None = Field(default=None, gt=0)
    target_price_max: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_price_range(self) -> "ProjectBase":
        if (
            self.target_price_min is not None
            and self.target_price_max is not None
            and self.target_price_min > self.target_price_max
        ):
            raise ValueError("target_price_min cannot exceed target_price_max")
        return self


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    budget_rmb: float | None = Field(default=None, gt=0)
    marketplace: str | None = Field(default=None, max_length=20)
    target_price_min: float | None = Field(default=None, gt=0)
    target_price_max: float | None = Field(default=None, gt=0)
    status: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_price_range(self) -> "ProjectUpdate":
        if (
            self.target_price_min is not None
            and self.target_price_max is not None
            and self.target_price_min > self.target_price_max
        ):
            raise ValueError("target_price_min cannot exceed target_price_max")
        return self


class ProjectOut(BaseModel):
    id: int
    project_name: str
    category: str
    budget_rmb: float
    marketplace: str
    target_price_min: float | None
    target_price_max: float | None
    status: str
    created_at: datetime
    updated_at: datetime

