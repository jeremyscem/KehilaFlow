import type { Campaign, CampaignCreate, Donor, DonorCreate, DonorSummary } from "./types";

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
