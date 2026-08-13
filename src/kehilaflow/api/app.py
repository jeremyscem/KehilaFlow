from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from kehilaflow.api.schemas.campaign import CampaignCreate
from kehilaflow.api.schemas.donation import DonationCreate
from kehilaflow.api.schemas.donor import DonorCreate
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
from kehilaflow.services.donation_service import DonationService
from kehilaflow.services.donor_service import DonorService
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


SessionDep = Annotated[Session, Depends(get_session)]


def build_donor_service(session: Session) -> DonorService:
    return DonorService(
        donor_repository=DonorRepository(session),
        donation_repository=DonationRepository(session),
        pledge_repository=PledgeRepository(session),
    )


@app.get("/")
def root():
    return {"message": "KehilaFlow API is running"}


@app.get("/donors")
def get_donors(
    session: SessionDep,
):
    service = build_donor_service(session)

    return service.get_all()


@app.post("/donors", status_code=201)
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
        )

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
        )

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


@app.get("/donors/{donor_id}/summary")
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
        )


@app.get("/campaigns")
def get_campaigns(session: SessionDep):
    service = CampaignService(CampaignRepository(session))

    return service.get_all()


@app.post("/campaigns", status_code=201)
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
