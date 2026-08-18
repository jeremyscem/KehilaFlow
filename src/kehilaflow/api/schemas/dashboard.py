from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_donors: int
    active_campaigns: int
    total_pledged: int
    total_paid: int
    total_outstanding: int
    donors_with_balance: int
