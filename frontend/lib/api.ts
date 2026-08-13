import type {
  Campaign,
  CampaignCreate,
  Donation,
  DonationCreate,
  Donor,
  DonorCreate,
  DonorSummary,
  Pledge,
  PledgeCreate,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Request failed");
  }

  return res.json() as Promise<T>;
}

export const api = {
  donors: {
    list: () => request<Donor[]>("/donors"),
    create: (data: DonorCreate) =>
      request<Donor>("/donors", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    summary: (id: string) => request<DonorSummary>(`/donors/${id}/summary`),
    createPledge: (donorId: string, data: PledgeCreate) =>
      request<Pledge>(`/donors/${donorId}/pledges`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    createDonation: (donorId: string, data: DonationCreate) =>
      request<Donation>(`/donors/${donorId}/donations`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  campaigns: {
    list: () => request<Campaign[]>("/campaigns"),
    create: (data: CampaignCreate) =>
      request<Campaign>("/campaigns", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
};
