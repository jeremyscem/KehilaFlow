import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import type { ExcelImportResponse } from "@/lib/types";

interface ImportSuccessProps {
  result: ExcelImportResponse;
  onImportAnother: () => void;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 0,
  }).format(amount);
};

export function ImportSuccess({ result, onImportAnother }: ImportSuccessProps) {
  return (
    <div className="space-y-6">
      {/* Success header */}
      <Card className="p-8 text-center">
        <div
          className="inline-flex items-center justify-center w-12 h-12 rounded-full mb-4"
          style={{
            background: "color-mix(in srgb, var(--success) 12%, transparent)",
            color: "var(--success)",
          }}
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h2
          className="text-2xl font-bold mb-2"
          style={{ color: "var(--text-primary)" }}
        >
          Import completed
        </h2>
        <p style={{ color: "var(--text-muted)" }}>
          {result.file_name} has been successfully imported
        </p>
      </Card>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p
            className="text-xs font-medium mb-2 uppercase tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Donors created
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--success)" }}
          >
            {result.created_donors}
          </p>
        </div>

        <div>
          <p
            className="text-xs font-medium mb-2 uppercase tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Existing donors matched
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--text-primary)" }}
          >
            {result.existing_donors}
          </p>
        </div>

        <div>
          <p
            className="text-xs font-medium mb-2 uppercase tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Campaigns created
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--text-primary)" }}
          >
            {result.created_campaigns}
          </p>
        </div>

        <div>
          <p
            className="text-xs font-medium mb-2 uppercase tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Pledges imported
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--text-primary)" }}
          >
            {result.created_pledges}
          </p>
        </div>

        <div>
          <p
            className="text-xs font-medium mb-2 uppercase tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Payments imported
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--text-primary)" }}
          >
            {result.created_donations}
          </p>
        </div>

        <div>
          <p
            className="text-xs font-medium mb-2 uppercase tracking-wider"
            style={{ color: "var(--text-muted)" }}
          >
            Total amount
          </p>
          <p
            className="text-2xl font-bold"
            style={{ color: "var(--text-primary)" }}
          >
            {formatCurrency(result.total_paid + result.total_pledged)}
          </p>
        </div>
      </div>

      {/* Details card */}
      <Card className="p-5">
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b" style={{ borderColor: "var(--border-subtle)" }}>
            <p style={{ color: "var(--text-muted)" }}>Total pledged</p>
            <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
              {formatCurrency(result.total_pledged)}
            </p>
          </div>
          <div className="flex justify-between items-center py-2">
            <p style={{ color: "var(--text-muted)" }}>Total paid</p>
            <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
              {formatCurrency(result.total_paid)}
            </p>
          </div>
        </div>
      </Card>

      {/* Action button */}
      <Button
        className="w-full"
        onClick={onImportAnother}
      >
        Import another file
      </Button>
    </div>
  );
}
