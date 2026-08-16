"use client";

import { Card } from "@/components/ui/Card";

interface PreviewTableProps {
  columns: string[];
  rows: Record<string, string | number | boolean | null>[];
}

export function PreviewTable({ columns, rows }: PreviewTableProps) {
  return (
    <Card className="overflow-hidden">
      {/* Table with horizontal scroll */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-max">
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                  style={{ color: "var(--text-muted)", background: "var(--surface-raised)" }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                style={{
                  borderTop: rowIndex === 0 ? "none" : "1px solid var(--border-subtle)",
                }}
              >
                {columns.map((col) => {
                  const value = row[col];
                  const displayValue =
                    value === null || value === undefined ? "—" : String(value);

                  return (
                    <td
                      key={`${rowIndex}-${col}`}
                      className="px-4 py-3 text-sm"
                      style={{ color: "var(--text-primary)" }}
                    >
                      {displayValue}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
