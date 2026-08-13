export interface Donor {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  active: boolean;
}

export interface Campaign {
  id: string;
  name: string;
  description: string | null;
  target_amount: number;
  active: boolean;
}

export interface Pledge {
  id: string;
  donor_id: string;
  amount: number;
  pledge_date: string;
  campaign_id: string | null;
}

export interface Donation {
  id: string;
  donor_id: string;
  amount: number;
  donation_date: string;
  campaign_id: string | null;
}

export interface DonorSummary {
  donor: Donor;
  total_pledged: number;
  total_paid: number;
  remaining: number;
  pledges: Pledge[];
  donations: Donation[];
}

export interface DonorCreate {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

export interface CampaignCreate {
  name: string;
  description?: string;
  target_amount?: number;
}
