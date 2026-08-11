from pydantic import BaseModel


class DonorCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
