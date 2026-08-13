"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import type { Campaign } from "@/lib/types";

function today() {
  return new Date().toISOString().split("T")[0];
}

// ─── Shared modal primitives ──────────────────────────────────────

function ModalShell({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
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
            {title}
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
        {children}
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required,
  min,
}: {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  min?: string;
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

function CampaignSelect({
  campaigns,
  value,
  onChange,
}: {
  campaigns: Campaign[];
  value: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
}) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
        Campaign
      </label>
      <select
        value={value}
        onChange={onChange}
        className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-all appearance-none"
        style={{
          background: "var(--bg)",
          border: "1px solid var(--border)",
          color: value ? "var(--text-primary)" : "var(--text-muted)",
          caretColor: "var(--accent)",
        }}
        onFocus={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
        onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
      >
        <option value="">No campaign</option>
        {campaigns.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
    </div>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <p
      className="text-sm px-3 py-2 rounded-lg"
      style={{ background: "var(--danger-muted)", color: "var(--danger)" }}
    >
      {message}
    </p>
  );
}

// ─── Add Pledge ───────────────────────────────────────────────────

interface AddPledgeModalProps {
  donorId: string;
  campaigns: Campaign[];
  onClose: () => void;
  onSuccess: () => void;
}

function AddPledgeModal({ donorId, campaigns, onClose, onSuccess }: AddPledgeModalProps) {
  const [form, setForm] = useState({ amount: "", pledge_date: today(), campaign_id: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function setField(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.donors.createPledge(donorId, {
        amount: parseInt(form.amount, 10),
        pledge_date: form.pledge_date,
        campaign_id: form.campaign_id || null,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create pledge");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ModalShell title="Add Pledge" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field
          label="Amount (₪)"
          type="number"
          value={form.amount}
          onChange={setField("amount")}
          min="1"
          required
        />
        <Field
          label="Pledge Date"
          type="date"
          value={form.pledge_date}
          onChange={setField("pledge_date")}
          required
        />
        <CampaignSelect
          campaigns={campaigns}
          value={form.campaign_id}
          onChange={setField("campaign_id")}
        />
        {error && <ErrorBanner message={error} />}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="ghost" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Saving…" : "Add Pledge"}
          </Button>
        </div>
      </form>
    </ModalShell>
  );
}

export function AddPledgeButton({
  donorId,
  campaigns,
}: {
  donorId: string;
  campaigns: Campaign[];
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  function handleSuccess() {
    setOpen(false);
    router.refresh();
  }

  return (
    <>
      <Button size="sm" onClick={() => setOpen(true)}>
        <PlusIcon />
        Add Pledge
      </Button>
      {open && (
        <AddPledgeModal
          donorId={donorId}
          campaigns={campaigns}
          onClose={() => setOpen(false)}
          onSuccess={handleSuccess}
        />
      )}
    </>
  );
}

// ─── Add Donation ─────────────────────────────────────────────────

interface AddDonationModalProps {
  donorId: string;
  campaigns: Campaign[];
  onClose: () => void;
  onSuccess: () => void;
}

function AddDonationModal({ donorId, campaigns, onClose, onSuccess }: AddDonationModalProps) {
  const [form, setForm] = useState({ amount: "", donation_date: today(), campaign_id: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function setField(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.donors.createDonation(donorId, {
        amount: parseInt(form.amount, 10),
        donation_date: form.donation_date,
        campaign_id: form.campaign_id || null,
      });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to register donation");
    } finally {
      setLoading(false);
    }
  }

  return (
    <ModalShell title="Add Donation" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field
          label="Amount (₪)"
          type="number"
          value={form.amount}
          onChange={setField("amount")}
          min="1"
          required
        />
        <Field
          label="Donation Date"
          type="date"
          value={form.donation_date}
          onChange={setField("donation_date")}
          required
        />
        <CampaignSelect
          campaigns={campaigns}
          value={form.campaign_id}
          onChange={setField("campaign_id")}
        />
        {error && <ErrorBanner message={error} />}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="ghost" type="button" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Saving…" : "Add Donation"}
          </Button>
        </div>
      </form>
    </ModalShell>
  );
}

export function AddDonationButton({
  donorId,
  campaigns,
}: {
  donorId: string;
  campaigns: Campaign[];
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  function handleSuccess() {
    setOpen(false);
    router.refresh();
  }

  return (
    <>
      <Button size="sm" onClick={() => setOpen(true)}>
        <PlusIcon />
        Add Donation
      </Button>
      {open && (
        <AddDonationModal
          donorId={donorId}
          campaigns={campaigns}
          onClose={() => setOpen(false)}
          onSuccess={handleSuccess}
        />
      )}
    </>
  );
}

// ─── Icons ────────────────────────────────────────────────────────

function PlusIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
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
