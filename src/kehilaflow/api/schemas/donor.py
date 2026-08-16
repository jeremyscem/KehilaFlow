from pydantic import BaseModel


class DonorCreate(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
