export interface Donor {
  id: string;
  first_name: string;
  last_name: string;
  email: string | null;
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

export interface PledgeCreate {
  amount: number;
  pledge_date: string;
  campaign_id: string | null;
}

export interface DonationCreate {
  amount: number;
  donation_date: string;
  campaign_id: string | null;
}

export interface CampaignCreate {
  name: string;
  description?: string;
  target_amount?: number;
}

export interface AIChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AIChatRequest {
  message: string;
  history?: AIChatMessage[];
  pending_action_token?: string | null;
}

export interface AIChatResponse {
  answer: string;
  pending_action_token?: string | null;
}

export interface ExcelPreviewResponse {
  file_name: string;
  sheet_name: string;
  columns: string[];
  rows: Record<string, string | number | boolean | null>[];
  total_rows: number;
}

export type DonorMatchStatus = "existing" | "new" | "ambiguous";

export type DonorMatchSource = "database" | "excel";

export interface DonorMatchCandidate {
  donor_id: string | null;
  first_name: string;
  last_name: string;
  source: DonorMatchSource;
}

export interface DonorImportMatch {
  first_name: string;
  last_name: string;
  pledged_amount: number;
  paid_amount: number;
  remaining: number;
  status: DonorMatchStatus;
  donor_id: string | null;
  candidates: DonorMatchCandidate[];
}

export interface ExcelMatchResponse {
  total_donors: number;
  existing_donors: number;
  new_donors: number;
  ambiguous_donors: number;
  donors: DonorImportMatch[];
}

export type ResolutionAction = "link_database" | "link_excel" | "create" | "ignore";

export interface DonorResolution {
  source_first_name: string;
  source_last_name: string;
  action: ResolutionAction;
  donor_id?: string;
  target_first_name?: string;
  target_last_name?: string;
}

export interface ExcelImportResponse {
  file_name: string;
  created_donors: number;
  existing_donors: number;
  created_campaigns: number;
  created_pledges: number;
  created_donations: number;
  total_pledged: number;
  total_paid: number;
}

export interface DashboardStats {
  total_donors: number;
  active_campaigns: number;
  total_pledged: number;
  total_paid: number;
  total_outstanding: number;
  donors_with_balance: number;
}
