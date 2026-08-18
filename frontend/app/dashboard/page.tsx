import { AppShell } from "@/components/layout/AppShell";
import { StatCard } from "@/components/ui/StatCard";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import type { Donor, Campaign, DashboardStats } from "@/lib/types";

function fmt(amount: number) {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

async function getDashboardData() {
  try {
    const [stats, donors, campaigns] = await Promise.all([
      api.dashboard.stats(),
      api.donors.list(),
      api.campaigns.list(),
    ]);
    return {
      stats,
      donors,
      campaigns,
    };
  } catch {
    return {
      stats: null as DashboardStats | null,
      donors: [] as Donor[],
      campaigns: [] as Campaign[],
    };
  }
}

export default async function DashboardPage() {
  const { stats, donors, campaigns } = await getDashboardData();

  return (
    <AppShell>
      <div className="space-y-8 max-w-6xl">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
            Dashboard
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-muted)" }}>
            Overview of KehilaFlow activity
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard
            label="Total Donors"
            value={String(stats?.total_donors ?? 0)}
            sub={`${stats?.donors_with_balance ?? 0} with balance`}
            accent="amber"
            icon={<UsersIcon />}
          />
          <StatCard
            label="Active Campaigns"
            value={String(stats?.active_campaigns ?? 0)}
            accent="green"
            icon={<CampaignIcon />}
          />
          <StatCard
            label="Total Pledged"
            value={fmt(stats?.total_pledged ?? 0)}
            accent="default"
            icon={<TargetIcon />}
          />
          <StatCard
            label="Total Paid"
            value={fmt(stats?.total_paid ?? 0)}
            accent="default"
            icon={<WalletIcon />}
          />
          <StatCard
            label="Outstanding"
            value={fmt(stats?.total_outstanding ?? 0)}
            sub="to be collected"
            accent="amber"
            icon={<OutstandingIcon />}
          />
        </div>

        {/* Content grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent donors */}
          <Card>
            <div
              className="px-5 py-4"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                Recent Donors
              </h2>
            </div>
            <div className="divide-y" style={{ borderColor: "var(--border-subtle)" }}>
              {donors.length === 0 ? (
                <EmptyState label="No donors yet" />
              ) : (
                donors.slice(0, 6).map((donor) => (
                  <div key={donor.id} className="flex items-center justify-between px-5 py-3">
                    <div className="flex items-center gap-3">
                      <Avatar name={`${donor.first_name} ${donor.last_name}`} />
                      <div>
                        <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                          {donor.first_name} {donor.last_name}
                        </p>
                        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                          {donor.email}
                        </p>
                      </div>
                    </div>
                    <span
                      className="text-xs px-2 py-0.5 rounded-full"
                      style={{
                        background: donor.active ? "var(--success-muted)" : "var(--danger-muted)",
                        color: donor.active ? "var(--success)" : "var(--danger)",
                      }}
                    >
                      {donor.active ? "Active" : "Inactive"}
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Campaigns */}
          <Card>
            <div
              className="px-5 py-4"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                Campaigns
              </h2>
            </div>
            <div className="divide-y" style={{ borderColor: "var(--border-subtle)" }}>
              {campaigns.length === 0 ? (
                <EmptyState label="No campaigns yet" />
              ) : (
                campaigns.slice(0, 6).map((campaign) => (
                  <div key={campaign.id} className="px-5 py-3">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                        {campaign.name}
                      </p>
                      <span className="text-xs font-medium" style={{ color: "var(--accent)" }}>
                        {fmt(campaign.target_amount)}
                      </span>
                    </div>
                    {/* Progress bar placeholder */}
                    <div
                      className="h-1.5 rounded-full overflow-hidden"
                      style={{ background: "var(--border)" }}
                    >
                      <div
                        className="h-full rounded-full"
                        style={{ width: "0%", background: "var(--accent)" }}
                      />
                    </div>
                    <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                      0% collected
                    </p>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function Avatar({ name }: { name: string }) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div
      className="flex items-center justify-center w-8 h-8 rounded-full text-xs font-semibold shrink-0"
      style={{
        background: "var(--accent-muted)",
        color: "var(--accent)",
      }}
    >
      {initials}
    </div>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="px-5 py-8 text-center">
      <p className="text-sm" style={{ color: "var(--text-muted)" }}>
        {label}
      </p>
    </div>
  );
}

function UsersIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function CampaignIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </svg>
  );
}

function TargetIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  );
}

function WalletIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
      <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
      <path d="M18 12a2 2 0 0 0 0 4h4v-4Z" />
    </svg>
  );
}

function OutstandingIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
      <polyline points="13 2 13 9 20 9" />
      <line x1="12" y1="11" x2="12" y2="17" />
      <line x1="9" y1="14" x2="15" y2="14" />
    </svg>
  );
}
