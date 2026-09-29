from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, EmailStr, Field, model_validator

class DemandCreate(BaseModel):
    title: str = Field(min_length=5, max_length=240)
    unit: str = Field(min_length=3, max_length=160)
    justification: str = Field(min_length=10, max_length=5000)
    quantity: Decimal = Field(gt=0, le=1_000_000_000, decimal_places=4)
    unit_measure: str = Field(min_length=1, max_length=80)
    unit_value: Decimal = Field(gt=0, le=10_000_000_000, decimal_places=4)
    priority: str = Field(pattern="^(low|medium|high)$")
    dependency_description: str | None = Field(None, max_length=2000)
    requester_name: str = Field(min_length=3, max_length=160)
    requester_email: EmailStr | None = None
    desired_start_date: date | None = None
    renewal_contract: bool = False
    category: str = Field(pattern="^(goods|services|works|it)$")
    desired_date: date
    original_value: Decimal = Field(gt=0, le=10_000_000_000, decimal_places=2)
    pncp_item_code: str | None = Field(None, max_length=80)
    pncp_catalog_code: int | None = Field(None, gt=0)
    pncp_classification: int | None = Field(None, ge=1, le=2)
    pncp_superior_code: str | None = Field(None, max_length=100)
    pncp_superior_name: str | None = Field(None, max_length=255)
    extraordinary: bool = False
    extraordinary_justification: str | None = Field(None, max_length=3000)

    @model_validator(mode="after")
    def validate_totals_and_dates(self):
        expected = (self.quantity * self.unit_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if expected != self.original_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
            raise ValueError("Valor total deve corresponder à quantidade multiplicada pelo valor unitário")
        if self.desired_start_date and self.desired_start_date > self.desired_date:
            raise ValueError("Data inicial não pode ser posterior à data pretendida de conclusão")
        if self.extraordinary and not self.extraordinary_justification:
            raise ValueError("Inclusão extraordinária exige justificativa específica")
        return self

class DemandUpdate(BaseModel):
    title: str = Field(min_length=5, max_length=240)
    unit: str = Field(min_length=3, max_length=160)
    justification: str = Field(min_length=10, max_length=5000)
    quantity: Decimal = Field(gt=0, le=1_000_000_000, decimal_places=4)
    unit_measure: str = Field(min_length=1, max_length=80)
    unit_value: Decimal = Field(gt=0, le=10_000_000_000, decimal_places=4)
    priority: str = Field(pattern="^(low|medium|high)$")
    dependency_description: str | None = Field(None, max_length=2000)
    requester_name: str = Field(min_length=3, max_length=160)
    requester_email: EmailStr | None = None
    desired_start_date: date | None = None
    renewal_contract: bool = False
    category: str = Field(pattern="^(goods|services|works|it)$")
    desired_date: date
    original_value: Decimal = Field(gt=0, le=10_000_000_000, decimal_places=2)
    pncp_item_code: str | None = Field(None, max_length=80)
    pncp_catalog_code: int | None = Field(None, gt=0)
    pncp_classification: int | None = Field(None, ge=1, le=2)
    pncp_superior_code: str | None = Field(None, max_length=100)
    pncp_superior_name: str | None = Field(None, max_length=255)
    change_justification: str = Field(min_length=10, max_length=3000)

    @model_validator(mode="after")
    def validate_totals_and_dates(self):
        expected = (self.quantity * self.unit_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if expected != self.original_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
            raise ValueError("Valor total deve corresponder à quantidade multiplicada pelo valor unitário")
        if self.desired_start_date and self.desired_start_date > self.desired_date:
            raise ValueError("Data inicial não pode ser posterior à data pretendida de conclusão")
        return self

class DemandDelete(BaseModel):
    justification: str = Field(min_length=10, max_length=3000)

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

class ApprovalStart(BaseModel):
    flow_id: int = Field(gt=0)

class ApprovalDecisionCreate(BaseModel):
    decision: str = Field(pattern="^(approve|reject)$")
    actor_role: str = Field(min_length=3, max_length=80)
    justification: str | None = Field(None, max_length=3000)
