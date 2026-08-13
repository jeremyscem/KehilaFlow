import { Card } from "./Card";

interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
  accent?: "amber" | "green" | "red" | "default";
  icon?: React.ReactNode;
}

const accentColors: Record<NonNullable<StatCardProps["accent"]>, string> = {
  amber: "var(--accent)",
  green: "var(--success)",
  red: "var(--danger)",
  default: "var(--text-secondary)",
};

export function StatCard({ label, value, sub, accent = "default", icon }: StatCardProps) {
  const color = accentColors[accent];

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            {label}
          </p>
          <p className="text-2xl font-bold tracking-tight" style={{ color }}>
            {value}
          </p>
          {sub && (
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {sub}
            </p>
          )}
        </div>
        {icon && (
          <div
            className="flex items-center justify-center w-10 h-10 rounded-lg"
            style={{ background: `color-mix(in srgb, ${color} 12%, transparent)`, color }}
          >
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}
