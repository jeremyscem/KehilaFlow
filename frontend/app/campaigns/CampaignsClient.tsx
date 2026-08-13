"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import type { Campaign } from "@/lib/types";

function fmt(amount: number) {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function CampaignsClient({ initialCampaigns }: { initialCampaigns: Campaign[] }) {
  const router = useRouter();
  const [campaigns, setCampaigns] = useState(initialCampaigns);
  const [showCreate, setShowCreate] = useState(false);

  async function handleCreate(data: { name: string; description: string; target_amount: string }) {
    const campaign = await api.campaigns.create({
      name: data.name,
      description: data.description || undefined,
      target_amount: data.target_amount ? parseInt(data.target_amount, 10) : undefined,
    });
    setCampaigns((prev) => [campaign, ...prev]);
    setShowCreate(false);
    router.refresh();
  }

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
            Campaigns
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-muted)" }}>
            {campaigns.length} campaign{campaigns.length !== 1 ? "s" : ""}
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <PlusIcon />
          Add Campaign
        </Button>
      </div>

      {/* Grid */}
      {campaigns.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-sm" style={{ color: "var(--text-muted)" }}>
            No campaigns yet. Create one to get started.
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
                  className="text-xs px-2 py-0.5 rounded-full shrink-0 ml-2"
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

      {showCreate && (
        <CreateCampaignModal
          onClose={() => setShowCreate(false)}
          onSubmit={handleCreate}
        />
      )}
    </div>
  );
}

// ─── Modal ────────────────────────────────────────────────────────

interface CreateCampaignModalProps {
  onClose: () => void;
  onSubmit: (data: { name: string; description: string; target_amount: string }) => Promise<void>;
}

function CreateCampaignModal({ onClose, onSubmit }: CreateCampaignModalProps) {
  const [form, setForm] = useState({ name: "", description: "", target_amount: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create campaign");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)" }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="w-full max-w-md rounded-xl p-6 shadow-2xl"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-base font-semibold" style={{ color: "var(--text-primary)" }}>
            Add Campaign
          </h2>
          <button
            onClick={onClose}
            className="flex items-center justify-center w-7 h-7 rounded-lg transition-colors"
            style={{ color: "var(--text-muted)" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--surface-raised)";
              e.currentTarget.style.color = "var(--text-primary)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "var(--text-muted)";
            }}
          >
            <CloseIcon />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Name" value={form.name} onChange={set("name")} required />

          {/* Description textarea */}
          <div className="space-y-1.5">
            <label className="block text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
              Description
            </label>
            <textarea
              value={form.description}
              onChange={set("description")}
              rows={3}
              placeholder="Optional"
              className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-all resize-none"
              style={{
                background: "var(--bg)",
                border: "1px solid var(--border)",
                color: "var(--text-primary)",
                caretColor: "var(--accent)",
              }}
              onFocus={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
              onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
            />
          </div>

          <Field
            label="Target Amount (₪)"
            type="number"
            value={form.target_amount}
            onChange={set("target_amount")}
            min="0"
            placeholder="Optional"
          />

          {error && (
            <p
              className="text-sm px-3 py-2 rounded-lg"
              style={{ background: "var(--danger-muted)", color: "var(--danger)" }}
            >
              {error}
            </p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating…" : "Create Campaign"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Shared field ─────────────────────────────────────────────────

function Field({
  label,
  value,
  onChange,
  type = "text",
  required,
  min,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  min?: string;
  placeholder?: string;
}) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
        {label}
        {required && <span style={{ color: "var(--accent)" }}> *</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        min={min}
        placeholder={placeholder}
        className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-all"
        style={{
          background: "var(--bg)",
          border: "1px solid var(--border)",
          color: "var(--text-primary)",
          caretColor: "var(--accent)",
        }}
        onFocus={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
        onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
      />
    </div>
  );
}

// ─── Icons ────────────────────────────────────────────────────────

function PlusIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}
