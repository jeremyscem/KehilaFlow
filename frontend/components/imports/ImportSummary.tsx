import { StatCard } from "@/components/ui/StatCard";
import type { ExcelMatchResponse } from "@/lib/types";

interface ImportSummaryProps {
  match: ExcelMatchResponse;
}

export function ImportSummary({ match }: ImportSummaryProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Total donors"
        value={String(match.total_donors)}
        accent="default"
      />
      <StatCard
        label="New donors"
        value={String(match.new_donors)}
        accent="green"
      />
      <StatCard
        label="Existing donors"
        value={String(match.existing_donors)}
        accent="default"
      />
      <StatCard
        label="Need validation"
        value={String(match.ambiguous_donors)}
        accent={match.ambiguous_donors > 0 ? "amber" : "default"}
      />
    </div>
  );
}
