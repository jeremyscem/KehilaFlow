import { AppShell } from "@/components/layout/AppShell";
import { CampaignsClient } from "./CampaignsClient";
import { api } from "@/lib/api";
import type { Campaign } from "@/lib/types";

async function getCampaigns() {
  try {
    return await api.campaigns.list();
  } catch {
    return [] as Campaign[];
  }
}

export default async function CampaignsPage() {
  const campaigns = await getCampaigns();

  return (
    <AppShell>
      <CampaignsClient initialCampaigns={campaigns} />
    </AppShell>
  );
}
