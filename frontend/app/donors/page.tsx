import { AppShell } from "@/components/layout/AppShell";
import { DonorsClient } from "./DonorsClient";
import { api } from "@/lib/api";
import type { Donor } from "@/lib/types";

async function getDonors() {
  try {
    return await api.donors.list();
  } catch {
    return [] as Donor[];
  }
}

export default async function DonorsPage() {
  const donors = await getDonors();

  return (
    <AppShell>
      <DonorsClient initialDonors={donors} />
    </AppShell>
  );
}
