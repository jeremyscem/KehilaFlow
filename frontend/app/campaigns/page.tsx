import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Campaign } from "@/lib/types";

function fmt(amount: number) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

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
      <div className="space-y-6 max-w-6xl">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
            Campaigns
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-muted)" }}>
            {campaigns.length} campaign{campaigns.length !== 1 ? "s" : ""}
          </p>
        </div>

        {campaigns.length === 0 ? (
          <Card className="p-12 text-center">
            <p className="text-sm" style={{ color: "var(--text-muted)" }}>
              No campaigns yet.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {campaigns.map((campaign) => (
              <Card key={campaign.id} className="p-5 space-y-3">
                <div className="flex items-start justify-between">
                  <h2 className="font-semibold text-sm" style={{ color: "var(--text-primary)" }}>
                    {campaign.name}
                  </h2>
                  <span
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      background: campaign.active ? "var(--success-muted)" : "var(--danger-muted)",
                      color: campaign.active ? "var(--success)" : "var(--danger)",
                    }}
                  >
                    {campaign.active ? "Active" : "Archived"}
                  </span>
                </div>

                {campaign.description && (
                  <p className="text-xs leading-relaxed" style={{ color: "var(--text-muted)" }}>
                    {campaign.description}
                  </p>
                )}

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                      Target
                    </span>
                    <span className="text-xs font-semibold" style={{ color: "var(--accent)" }}>
                      {fmt(campaign.target_amount)}
                    </span>
                  </div>
                  <div
                    className="h-1.5 rounded-full overflow-hidden"
                    style={{ background: "var(--border)" }}
                  >
                    <div className="h-full rounded-full w-0" style={{ background: "var(--accent)" }} />
                  </div>
                  <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    0% collected
                  </p>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
