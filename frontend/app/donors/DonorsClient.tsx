"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";
import type { Donor } from "@/lib/types";

interface Props {
  initialDonors: Donor[];
}

export function DonorsClient({ initialDonors }: Props) {
  const router = useRouter();
  const [donors, setDonors] = useState(initialDonors);
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return donors;
    return donors.filter(
      (d) =>
        d.first_name.toLowerCase().includes(q) ||
        d.last_name.toLowerCase().includes(q) ||
        (d.email ? d.email.toLowerCase().includes(q) : false)
    );
  }, [donors, search]);

  async function handleCreate(data: { first_name: string; last_name: string; email: string; phone: string }) {
    const donor = await api.donors.create(data);
    setDonors((prev) => [donor, ...prev]);
    setShowCreate(false);
    router.refresh();
  }

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
            Donors
          </h1>
          <p className="mt-1 text-sm" style={{ color: "var(--text-muted)" }}>
            {donors.length} donor{donors.length !== 1 ? "s" : ""} registered
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <PlusIcon />
          Add Donor
        </Button>
      </div>

      {/* Search */}
      <div className="relative">
        <span
          className="absolute left-3 top-1/2 -translate-y-1/2"
          style={{ color: "var(--text-muted)" }}
        >
          <SearchIcon />
        </span>
        <input
          type="text"
          placeholder="Search donors by name or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 rounded-lg text-sm outline-none transition-all"
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)",
            caretColor: "var(--accent)",
          }}
          onFocus={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
          onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
        />
      </div>

      {/* Table */}
      <Card>
        <table className="w-full">
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              {["Donor", "Email", "Phone", "Status"].map((h) => (
                <th
                  key={h}
                  className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                  style={{ color: "var(--text-muted)" }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-5 py-12 text-center">
                  <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    {search ? "No donors match your search." : "No donors yet. Add one to get started."}
                  </p>
                </td>
              </tr>
            ) : (
              filtered.map((donor, i) => (
                <tr
                  key={donor.id}
                  className="cursor-pointer transition-colors"
                  style={{
                    borderTop: i === 0 ? "none" : `1px solid var(--border-subtle)`,
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface-raised)")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                  onClick={() => router.push(`/donors/${donor.id}`)}
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">
                      <Avatar name={`${donor.first_name} ${donor.last_name}`} />
                      <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                        {donor.first_name} {donor.last_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-sm" style={{ color: "var(--text-secondary)" }}>
                    {donor.email}
                  </td>
                  <td className="px-5 py-3 text-sm" style={{ color: "var(--text-secondary)" }}>
                    {donor.phone ?? <span style={{ color: "var(--text-muted)" }}>—</span>}
                  </td>
                  <td className="px-5 py-3">
                    <Badge variant={donor.active ? "success" : "danger"}>
                      {donor.active ? "Active" : "Inactive"}
                    </Badge>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </Card>

      {/* Create modal */}
      {showCreate && (
        <CreateDonorModal
          onClose={() => setShowCreate(false)}
          onSubmit={handleCreate}
        />
      )}
    </div>
  );
}

// ─── Sub-components ────────────────────────────────────────────────

function Avatar({ name }: { name: string }) {
  const initials = name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
  return (
    <div
      className="flex items-center justify-center w-8 h-8 rounded-full text-xs font-semibold shrink-0"
      style={{ background: "var(--accent-muted)", color: "var(--accent)" }}
    >
      {initials}
    </div>
  );
}

interface CreateModalProps {
  onClose: () => void;
  onSubmit: (data: { first_name: string; last_name: string; email: string; phone: string }) => Promise<void>;
}

function CreateDonorModal({ onClose, onSubmit }: CreateModalProps) {
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", phone: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create donor");
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
            Add Donor
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
          <div className="grid grid-cols-2 gap-4">
            <Field label="First Name" value={form.first_name} onChange={set("first_name")} required />
            <Field label="Last Name" value={form.last_name} onChange={set("last_name")} required />
          </div>
          <Field label="Email" type="email" value={form.email} onChange={set("email")} required />
          <Field label="Phone" type="tel" value={form.phone} onChange={set("phone")} placeholder="Optional" />

          {error && (
            <p className="text-sm px-3 py-2 rounded-lg" style={{ background: "var(--danger-muted)", color: "var(--danger)" }}>
              {error}
            </p>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="ghost" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Creating…" : "Create Donor"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  placeholder?: string;
}

function Field({ label, value, onChange, type = "text", required, placeholder }: FieldProps) {
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

function SearchIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
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
