import json
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.orm import Session

from kehilaflow.ai.assistant import ask_claude
from kehilaflow.api.schemas.ai import AIChatRequest, AIChatResponse
from kehilaflow.api.schemas.campaign import CampaignCreate
from kehilaflow.api.schemas.dashboard import (
    DashboardStatsResponse,
)
from kehilaflow.api.schemas.donation import DonationCreate
from kehilaflow.api.schemas.donor import DonorCreate, DonorSummaryResponse
from kehilaflow.api.schemas.imports import (
    DonorResolution,
    ExcelAnalysisResponse,
    ExcelImportResponse,
    ExcelMatchResponse,
    ExcelPrepareResponse,
    ExcelPreviewResponse,
)
from kehilaflow.api.schemas.pledge import PledgeCreate
from kehilaflow.database.orm import get_session
from kehilaflow.exceptions.donor_exceptions import (
    DonorAlreadyExistsError,
    DonorNotFoundError,
)
from kehilaflow.models.campaign import Campaign
from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge
from kehilaflow.repositories.campaign_repository import CampaignRepository
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.repositories.pledge_repository import PledgeRepository
from kehilaflow.services.campaign_service import CampaignService
from kehilaflow.services.dashboard_service import (
    get_dashboard_stats,
)
from kehilaflow.services.donation_service import DonationService
from kehilaflow.services.donor_service import DonorService
from kehilaflow.services.excel_ai_service import (
    analyze_excel_columns,
)
from kehilaflow.services.excel_confirm_service import (
    ExcelAlreadyImportedError,
    ExcelAmbiguousDonorsError,
    confirm_excel_import,
)
from kehilaflow.services.excel_import_service import (
    preview_excel,
)
from kehilaflow.services.excel_match_service import (
    match_excel_donors,
)
from kehilaflow.services.excel_prepare_service import (
    prepare_excel_import,
)
from kehilaflow.services.pledge_service import PledgeService

app = FastAPI(
    title="KehilaFlow API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


SessionDep = Annotated[
    Session,
    Depends(get_session),
]


def build_donor_service(
    session: Session,
) -> DonorService:
    return DonorService(
        donor_repository=DonorRepository(session),
        donation_repository=DonationRepository(session),
        pledge_repository=PledgeRepository(session),
    )


@app.get("/")
def root():
    return {"message": "KehilaFlow API is running"}


# ==========================================
# DONORS
# ==========================================


@app.get("/donors")
def get_donors(
    session: SessionDep,
):
    service = build_donor_service(session)

    return service.get_all()


@app.post(
    "/donors",
    status_code=201,
)
def create_donor(
    data: DonorCreate,
    session: SessionDep,
):
    service = build_donor_service(session)

    donor = Donor(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
    )

    try:
        service.create(donor)

    except DonorAlreadyExistsError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return donor


@app.post(
    "/donors/{donor_id}/donations",
    status_code=201,
)
def create_donation(
    donor_id: UUID,
    data: DonationCreate,
    session: SessionDep,
):
    service = DonationService(
        donation_repository=DonationRepository(session),
        donor_repository=DonorRepository(session),
    )

    donation = Donation(
        donor_id=donor_id,
        amount=data.amount,
        donation_date=data.donation_date,
        campaign_id=data.campaign_id,
    )

    try:
        service.create(donation)

    except DonorNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return donation


@app.post(
    "/donors/{donor_id}/pledges",
    status_code=201,
)
def create_pledge(
    donor_id: UUID,
    data: PledgeCreate,
    session: SessionDep,
):
    service = PledgeService(
        pledge_repository=PledgeRepository(session),
    )

    pledge = Pledge(
        donor_id=donor_id,
        amount=data.amount,
        pledge_date=data.pledge_date,
        campaign_id=data.campaign_id,
    )

    service.create(pledge)

    return pledge


@app.get("/donors/{donor_id}/summary", response_model=DonorSummaryResponse)
def get_donor_summary(
    donor_id: UUID,
    session: SessionDep,
):
    service = build_donor_service(session)

    try:
        return service.get_summary(donor_id)

    except DonorNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


# ==========================================
# CAMPAIGNS
# ==========================================


@app.get("/campaigns")
def get_campaigns(
    session: SessionDep,
):
    service = CampaignService(CampaignRepository(session))

    return service.get_all()


@app.post(
    "/campaigns",
    status_code=201,
)
def create_campaign(
    data: CampaignCreate,
    session: SessionDep,
):
    service = CampaignService(CampaignRepository(session))

    campaign = Campaign(
        name=data.name,
        description=data.description,
        target_amount=data.target_amount,
    )

    service.create(campaign)

    return campaign


# ==========================================
# AI ASSISTANT
# ==========================================


@app.post(
    "/ai/chat",
    response_model=AIChatResponse,
)
def ai_chat(
    data: AIChatRequest,
    session: SessionDep,
) -> AIChatResponse:
    result = ask_claude(
        message=data.message,
        history=data.history,
        pending_action_token=(data.pending_action_token),
        session=session,
        allow_writes=True,
    )

    return AIChatResponse(
        answer=result.answer,
        pending_action_token=(result.pending_action_token),
    )


# ==========================================
# EXCEL PREVIEW
# ==========================================


@app.post(
    "/imports/excel/preview",
    response_model=ExcelPreviewResponse,
)
async def preview_excel_file(
    file: Annotated[
        UploadFile,
        File(),
    ],
) -> ExcelPreviewResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing file name.",
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported.",
        )

    file_bytes = await file.read()

    return preview_excel(
        file_bytes=file_bytes,
        file_name=file.filename,
    )


# ==========================================
# EXCEL ANALYZE
# ==========================================


@app.post(
    "/imports/excel/analyze",
    response_model=ExcelAnalysisResponse,
)
async def analyze_excel_file(
    file: Annotated[
        UploadFile,
        File(),
    ],
) -> ExcelAnalysisResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing file name.",
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported.",
        )

    file_bytes = await file.read()

    preview = preview_excel(
        file_bytes=file_bytes,
        file_name=file.filename,
    )

    return analyze_excel_columns(
        preview=preview,
        file_bytes=file_bytes,
    )


# ==========================================
# EXCEL PREPARE
# ==========================================


@app.post(
    "/imports/excel/prepare",
    response_model=ExcelPrepareResponse,
)
async def prepare_excel_file(
    file: Annotated[
        UploadFile,
        File(),
    ],
) -> ExcelPrepareResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing file name.",
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported.",
        )

    file_bytes = await file.read()

    preview = preview_excel(
        file_bytes=file_bytes,
        file_name=file.filename,
    )

    analysis = analyze_excel_columns(
        preview=preview,
        file_bytes=file_bytes,
    )

    return prepare_excel_import(
        file_bytes=file_bytes,
        analysis=analysis,
    )


# ==========================================
# EXCEL MATCH
# ==========================================


@app.post(
    "/imports/excel/match",
    response_model=ExcelMatchResponse,
)
async def match_excel_file(
    file: Annotated[
        UploadFile,
        File(),
    ],
    session: SessionDep,
) -> ExcelMatchResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing file name.",
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported.",
        )

    file_bytes = await file.read()

    preview = preview_excel(
        file_bytes=file_bytes,
        file_name=file.filename,
    )

    analysis = analyze_excel_columns(
        preview=preview,
        file_bytes=file_bytes,
    )

    prepared = prepare_excel_import(
        file_bytes=file_bytes,
        analysis=analysis,
    )

    return match_excel_donors(
        prepared=prepared,
        session=session,
    )


# ==========================================
# EXCEL CONFIRM
# ==========================================


@app.post(
    "/imports/excel/confirm",
    response_model=ExcelImportResponse,
)
async def confirm_excel_file(
    session: SessionDep,
    file: Annotated[
        UploadFile,
        File(),
    ],
    resolutions: Annotated[
        str,
        Form(),
    ] = "[]",
) -> ExcelImportResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing file name.",
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported.",
        )

    # --------------------------------------
    # Parse admin donor resolutions
    # --------------------------------------

    try:
        raw_resolutions = json.loads(resolutions)

        if not isinstance(
            raw_resolutions,
            list,
        ):
            raise HTTPException(
                status_code=422,
                detail=("Resolutions must be a JSON array."),
            )

        parsed_resolutions = [
            DonorResolution.model_validate(resolution) for resolution in raw_resolutions
        ]

    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=422,
            detail="Invalid resolutions JSON.",
        ) from error

    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail="Invalid donor resolution.",
        ) from error

    # --------------------------------------
    # Read original Excel
    # --------------------------------------

    file_bytes = await file.read()

    preview = preview_excel(
        file_bytes=file_bytes,
        file_name=file.filename,
    )

    analysis = analyze_excel_columns(
        preview=preview,
        file_bytes=file_bytes,
    )

    # --------------------------------------
    # Confirm import
    # --------------------------------------

    try:
        return confirm_excel_import(
            file_bytes=file_bytes,
            file_name=file.filename,
            analysis=analysis,
            resolutions=parsed_resolutions,
            session=session,
        )

    except ExcelAlreadyImportedError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except ExcelAmbiguousDonorsError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error


@app.get(
    "/dashboard/stats",
    response_model=DashboardStatsResponse,
)
def dashboard_stats(
    session: SessionDep,
) -> DashboardStatsResponse:
    stats = get_dashboard_stats(session)

    return DashboardStatsResponse(**stats)
