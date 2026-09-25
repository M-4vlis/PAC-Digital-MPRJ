from datetime import date
from pydantic import BaseModel, Field

class DemandCreate(BaseModel):
    title: str = Field(min_length=5, max_length=240)
    unit: str = Field(min_length=3, max_length=160)
    category: str = Field(pattern="^(goods|services|works|it)$")
    desired_date: date
    original_value: float = Field(gt=0, le=10_000_000_000)
    pncp_item_code: str | None = Field(None, max_length=80)
    extraordinary: bool = False
    justification: str | None = Field(None, max_length=3000)

class TransitionRequest(BaseModel):
    target: str = Field(pattern="^(preparatory|contracting|contracted|reprogrammed|cancelled)$")
    justification: str | None = Field(None, max_length=3000)

class SeiLinkRequest(BaseModel):
    process_number: str = Field(min_length=5, max_length=40, pattern=r"^[0-9.\-/]+$")
    protocol_id: str | None = Field(None, max_length=80)

class ReviewCreate(BaseModel):
    proposed_title: str | None = Field(None, max_length=240)
    proposed_value: float | None = Field(None, gt=0)
    proposed_date: date | None = None
    justification: str = Field(min_length=10, max_length=3000)

class LoaAdjustment(BaseModel):
    revised_value: float = Field(gt=0)
    adjusted_value: float = Field(gt=0)
    justification: str = Field(min_length=10, max_length=3000)

class BackplanRequest(BaseModel):
    desired_date: date
    category: str = "services"
    parameters: dict[str, int] | None = None
