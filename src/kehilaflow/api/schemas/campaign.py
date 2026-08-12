from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str
    description: str | None = None
    target_amount: int = 0
