import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { api } from "@/lib/api";
import { AddDonationButton, AddPledgeButton } from "./DonorActions";
import Link from "next/link";
import type { Campaign } from "@/lib/types";

function fmt(amount: number) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default async function DonorProfilePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let summary;
  try {
    summary = await api.donors.summary(id);
  } catch {
    return (
      <AppShell>
        <div className="space-y-4">
          <Link href="/donors" className="text-sm" style={{ color: "var(--text-muted)" }}>
            ← Back to Donors
          </Link>
          <p style={{ color: "var(--danger)" }}>Donor not found.</p>
        </div>
      </AppShell>
    );
  }

  const campaigns: Campaign[] = await api.campaigns.list().catch(() => []);
  const { donor, total_pledged, total_paid, remaining, pledges, donations } = summary;

  return (
    <AppShell>
      <div className="space-y-8 max-w-5xl">
        {/* Breadcrumb */}
        <Link
          href="/donors"
          className="inline-flex items-center gap-1.5 text-sm transition-colors"
          style={{ color: "var(--text-muted)" }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-primary)")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
        >
          <ChevronLeftIcon /> Donors
        </Link>

        {/* Header */}
        <div className="flex items-center gap-4">
          <div
            className="flex items-center justify-center w-14 h-14 rounded-2xl text-xl font-bold"
            style={{ background: "var(--accent-muted)", color: "var(--accent)" }}
          >
            {donor.first_name[0]}{donor.last_name[0]}
          </div>
          <div>
            <h1 className="text-2xl font-bold" style={{ color: "var(--text-primary)" }}>
              {donor.first_name} {donor.last_name}
            </h1>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-sm" style={{ color: "var(--text-muted)" }}>{donor.email}</span>
              {donor.phone && (
                <span className="text-sm" style={{ color: "var(--text-muted)" }}>· {donor.phone}</span>
              )}
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
          </div>
        </div>

        {/* Financial summary */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard label="Total Pledged" value={fmt(total_pledged)} accent="default" />
          <StatCard label="Total Paid" value={fmt(total_paid)} accent="green" />
          <StatCard
            label="Remaining"
            value={fmt(remaining)}
            accent={remaining > 0 ? "amber" : "default"}
          />
        </div>

        {/* Pledges & Donations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pledges */}
          <Card>
            <div
              className="flex items-center justify-between px-5 py-4"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                Pledges{" "}
                <span className="ml-1 text-xs font-normal" style={{ color: "var(--text-muted)" }}>
                  ({pledges.length})
                </span>
              </h2>
              <AddPledgeButton donorId={id} campaigns={campaigns} />
            </div>
            <div className="divide-y" style={{ borderColor: "var(--border-subtle)" }}>
              {pledges.length === 0 ? (
                <p className="px-5 py-8 text-sm text-center" style={{ color: "var(--text-muted)" }}>
                  No pledges yet.
                </p>
              ) : (
                pledges.map((p) => (
                  <div key={p.id} className="flex items-center justify-between px-5 py-3">
                    <div>
                      <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                        {fmt(p.amount)}
                      </p>
                      <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                        {p.pledge_date}
                      </p>
                    </div>
                    <span className="text-xs" style={{ color: "var(--accent)" }}>
                      Pledge
                    </span>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Donations */}
          <Card>
            <div
              className="flex items-center justify-between px-5 py-4"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                Donations{" "}
                <span className="ml-1 text-xs font-normal" style={{ color: "var(--text-muted)" }}>
                  ({donations.length})
                </span>
              </h2>
              <AddDonationButton donorId={id} campaigns={campaigns} />
            </div>
            <div className="divide-y" style={{ borderColor: "var(--border-subtle)" }}>
              {donations.length === 0 ? (
                <p className="px-5 py-8 text-sm text-center" style={{ color: "var(--text-muted)" }}>
                  No donations yet.
                </p>
              ) : (
                donations.map((d) => (
                  <div key={d.id} className="flex items-center justify-between px-5 py-3">
                    <div>
                      <p className="text-sm font-medium" style={{ color: "var(--success)" }}>
                        {fmt(d.amount)}
                      </p>
                      <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                        {d.donation_date}
                      </p>
                    </div>
                    <span className="text-xs" style={{ color: "var(--success)" }}>
                      Paid
                    </span>
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

function ChevronLeftIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}
