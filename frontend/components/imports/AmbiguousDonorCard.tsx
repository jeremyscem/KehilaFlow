"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import type {
  DonorImportMatch,
  DonorResolution,
  DonorMatchCandidate,
} from "@/lib/types";

interface AmbiguousDonorCardProps {
  donor: DonorImportMatch;
  onResolve: (resolution: DonorResolution) => void;
  isResolved: boolean;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 0,
  }).format(amount);
};

export function AmbiguousDonorCard({
  donor,
  onResolve,
  isResolved,
}: AmbiguousDonorCardProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [firstName, setFirstName] = useState(donor.first_name);
  const [lastName, setLastName] = useState(donor.last_name);

  const displayName =
    donor.first_name && donor.last_name
      ? `${donor.first_name} ${donor.last_name}`
      : donor.last_name || "(No name)";

  const handleSelectCandidate = (candidate: DonorMatchCandidate) => {
    const resolution: DonorResolution = {
      source_first_name: donor.first_name,
      source_last_name: donor.last_name,
      action: candidate.source === "database" ? "link_database" : "link_excel",
      donor_id: candidate.source === "database" ? candidate.donor_id || "" : undefined,
      target_first_name: candidate.first_name,
      target_last_name: candidate.last_name,
    };
    onResolve(resolution);
  };

  const handleCreateDonor = () => {
    if (!firstName.trim() || !lastName.trim()) {
      return;
    }

    const resolution: DonorResolution = {
      source_first_name: donor.first_name,
      source_last_name: donor.last_name,
      action: "create",
      target_first_name: firstName,
      target_last_name: lastName,
    };
    onResolve(resolution);
    setShowCreateForm(false);
  };

  const handleIgnore = () => {
    const resolution: DonorResolution = {
      source_first_name: donor.first_name,
      source_last_name: donor.last_name,
      action: "ignore",
    };
    onResolve(resolution);
  };

  if (isResolved) {
    return (
      <Card className="p-5 opacity-60">
        <div className="flex items-start justify-between">
          <div>
            <p
              className="font-semibold text-sm"
              style={{ color: "var(--text-primary)" }}
            >
              {displayName}
            </p>
            <p
              className="text-xs mt-1"
              style={{ color: "var(--text-muted)" }}
            >
              ✓ Resolved
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-5">
      <div className="space-y-4">
        {/* Header with donor info */}
        <div className="flex items-start justify-between">
          <div>
            <p
              className="font-semibold text-sm"
              style={{ color: "var(--text-primary)" }}
            >
              {displayName}
            </p>
            <div
              className="flex gap-3 mt-2 text-xs"
              style={{ color: "var(--text-muted)" }}
            >
              {donor.paid_amount > 0 && (
                <span>Paid: {formatCurrency(donor.paid_amount)}</span>
              )}
              {donor.pledged_amount > 0 && (
                <span>Pledged: {formatCurrency(donor.pledged_amount)}</span>
              )}
            </div>
          </div>
        </div>

        {/* Candidates or create form */}
        {!showCreateForm && (
          <div className="space-y-2">
            {donor.candidates.length > 0 && (
              <div>
                <p
                  className="text-xs font-medium mb-2"
                  style={{ color: "var(--text-muted)" }}
                >
                  Possible matches:
                </p>
                <div className="space-y-2">
                  {donor.candidates.map((candidate, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSelectCandidate(candidate)}
                      className="w-full flex items-start gap-3 p-3 rounded-lg text-left transition-colors"
                      style={{
                        background: "var(--surface-raised)",
                        border: "1px solid var(--border)",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = "var(--surface-hover)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = "var(--surface-raised)";
                      }}
                    >
                      <div
                        className="flex-shrink-0 w-4 h-4 mt-1 rounded border"
                        style={{
                          border: "2px solid var(--text-muted)",
                        }}
                      />
                      <div className="flex-1">
                        <p
                          className="text-sm font-medium"
                          style={{ color: "var(--text-primary)" }}
                        >
                          {candidate.first_name} {candidate.last_name}
                        </p>
                        <p
                          className="text-xs mt-0.5"
                          style={{ color: "var(--text-muted)" }}
                        >
                          From {candidate.source === "database" ? "database" : "Excel"}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col gap-2 pt-2 border-t" style={{ borderColor: "var(--border-subtle)" }}>
              <button
                onClick={() => setShowCreateForm(true)}
                className="w-full flex items-start gap-3 p-3 rounded-lg text-left transition-colors"
                style={{
                  background: "var(--surface-raised)",
                  border: "1px solid var(--border)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "var(--surface-hover)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "var(--surface-raised)";
                }}
              >
                <div
                  className="flex-shrink-0 w-4 h-4 mt-1 rounded border"
                  style={{
                    border: "2px solid var(--text-muted)",
                  }}
                />
                <div className="flex-1">
                  <p
                    className="text-sm font-medium"
                    style={{ color: "var(--text-primary)" }}
                  >
                    Create a new donor
                  </p>
                </div>
              </button>

              <button
                onClick={handleIgnore}
                className="w-full flex items-start gap-3 p-3 rounded-lg text-left transition-colors"
                style={{
                  background: "var(--surface-raised)",
                  border: "1px solid var(--border)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "var(--surface-hover)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "var(--surface-raised)";
                }}
              >
                <div
                  className="flex-shrink-0 w-4 h-4 mt-1 rounded border"
                  style={{
                    border: "2px solid var(--text-muted)",
                  }}
                />
                <div className="flex-1">
                  <p
                    className="text-sm font-medium"
                    style={{ color: "var(--text-primary)" }}
                  >
                    Ignore this entry
                  </p>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Create form */}
        {showCreateForm && (
          <div className="space-y-3 pt-2 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <div>
              <label
                className="block text-xs font-medium mb-1"
                style={{ color: "var(--text-muted)" }}
              >
                First name
              </label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg text-sm"
                style={{
                  background: "var(--surface-raised)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                }}
              />
            </div>

            <div>
              <label
                className="block text-xs font-medium mb-1"
                style={{ color: "var(--text-muted)" }}
              >
                Last name
              </label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg text-sm"
                style={{
                  background: "var(--surface-raised)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                }}
              />
            </div>

            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleCreateDonor}
                disabled={!firstName.trim() || !lastName.trim()}
              >
                Confirm
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
