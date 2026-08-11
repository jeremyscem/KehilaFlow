from uuid import UUID

from fastapi import FastAPI, HTTPException

from kehilaflow.api.schemas.donation import DonationCreate
from kehilaflow.api.schemas.donor import DonorCreate
from kehilaflow.api.schemas.pledge import PledgeCreate
from kehilaflow.database.connection import create_tables, get_connection
from kehilaflow.exceptions.donor_exceptions import (
    DonorAlreadyExistsError,
    DonorNotFoundError,
)
from kehilaflow.models.donation import Donation
from kehilaflow.models.donor import Donor
from kehilaflow.models.pledge import Pledge
from kehilaflow.repositories.donation_repository import DonationRepository
from kehilaflow.repositories.donor_repository import DonorRepository
from kehilaflow.repositories.pledge_repository import PledgeRepository
from kehilaflow.services.donation_service import DonationService
from kehilaflow.services.donor_service import DonorService
from kehilaflow.services.pledge_service import PledgeService

app = FastAPI(
    title="KehilaFlow API",
    version="0.1.0",
)

connection = get_connection()
create_tables(connection)

donor_repository = DonorRepository(connection)
donation_repository = DonationRepository(connection)
pledge_repository = PledgeRepository(connection)

donor_service = DonorService(
    donor_repository=donor_repository,
    donation_repository=donation_repository,
    pledge_repository=pledge_repository,
)

donation_service = DonationService(
    donation_repository=donation_repository,
    donor_repository=donor_repository,
)

pledge_service = PledgeService(
    pledge_repository=pledge_repository,
)


@app.get("/")
def root():
    return {"message": "KehilaFlow API is running"}


@app.get("/donors")
def get_donors():
    return donor_service.get_all()


@app.post("/donors", status_code=201)
def create_donor(data: DonorCreate):
    donor = Donor(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
    )

    try:
        donor_service.create(donor)
    except DonorAlreadyExistsError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )

    return donor


@app.post("/donors/{donor_id}/pledges", status_code=201)
def create_pledge(
    donor_id: UUID,
    data: PledgeCreate,
):
    pledge = Pledge(
        donor_id=donor_id,
        amount=data.amount,
        pledge_date=data.pledge_date,
        campaign=data.campaign,
    )

    pledge_service.create(pledge)

    return pledge


@app.post("/donors/{donor_id}/donations", status_code=201)
def create_donation(
    donor_id: UUID,
    data: DonationCreate,
):
    donation = Donation(
        donor_id=donor_id,
        amount=data.amount,
        donation_date=data.donation_date,
        campaign=data.campaign,
    )

    try:
        donation_service.create(donation)
    except DonorNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    return donation


@app.get("/donors/{donor_id}/summary")
def get_donor_summary(donor_id: UUID):
    try:
        return donor_service.get_summary(donor_id)
    except DonorNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
