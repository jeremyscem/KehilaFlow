from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ExcelValue = str | int | float | bool | None


ExcelTarget = Literal[
    "first_name",
    "last_name",
    "email",
    "phone",
    "date",
    "campaign_name",
    "pledged_amount",
    "paid_amount",
    "ignore",
]


DonorMatchStatus = Literal[
    "existing",
    "new",
    "ambiguous",
]


DonorMatchSource = Literal[
    "database",
    "excel",
]


class ExcelPreviewResponse(BaseModel):
    file_name: str
    sheet_name: str
    columns: list[str]
    rows: list[dict[str, ExcelValue]]
    total_rows: int


class ExcelColumnMapping(BaseModel):
    source: str
    target: ExcelTarget
    confidence: float
    reason: str


class ExcelAnalysisResponse(BaseModel):
    mappings: list[ExcelColumnMapping]


class PreparedDonor(BaseModel):
    first_name: str
    last_name: str
    pledged_amount: float
    paid_amount: float
    remaining: float


class ExcelPrepareResponse(BaseModel):
    total_rows: int
    total_donors: int
    total_pledged: float
    total_paid: float
    total_remaining: float
    donors: list[PreparedDonor]
    mappings: list[ExcelColumnMapping]


class DonorMatchCandidate(BaseModel):
    donor_id: UUID | None = None
    first_name: str
    last_name: str
    source: DonorMatchSource


class DonorImportMatch(BaseModel):
    first_name: str
    last_name: str
    pledged_amount: float
    paid_amount: float
    remaining: float

    status: DonorMatchStatus
    donor_id: UUID | None = None
    candidates: list[DonorMatchCandidate] = Field(default_factory=list)


class ExcelMatchResponse(BaseModel):
    total_donors: int
    existing_donors: int
    new_donors: int
    ambiguous_donors: int
    donors: list[DonorImportMatch]


class ExcelImportResponse(BaseModel):
    file_name: str
    created_donors: int
    existing_donors: int
    created_campaigns: int
    created_pledges: int
    created_donations: int
    total_pledged: float
    total_paid: float


ResolutionAction = Literal[
    "link_database",
    "link_excel",
    "create",
    "ignore",
]


class DonorResolution(BaseModel):
    source_first_name: str
    source_last_name: str
    action: ResolutionAction

    donor_id: UUID | None = None

    target_first_name: str | None = None
    target_last_name: str | None = None
