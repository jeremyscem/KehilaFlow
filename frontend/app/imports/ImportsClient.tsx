"use client";

import { useState } from "react";
import { FileUploadArea } from "@/components/imports/FileUploadArea";
import { PreviewTable } from "@/components/imports/PreviewTable";
import { ImportSummary } from "@/components/imports/ImportSummary";
import { AmbiguousDonorCard } from "@/components/imports/AmbiguousDonorCard";
import { ImportSuccess } from "@/components/imports/ImportSuccess";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import type {
  ExcelPreviewResponse,
  ExcelMatchResponse,
  ExcelImportResponse,
  DonorResolution,
} from "@/lib/types";

type ImportStep = "upload" | "preview" | "match" | "confirm" | "success";

export function ImportsClient() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [step, setStep] = useState<ImportStep>("upload");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<ExcelPreviewResponse | null>(null);
  const [match, setMatch] = useState<ExcelMatchResponse | null>(null);
  const [resolutions, setResolutions] = useState<DonorResolution[]>([]);
  const [successResult, setSuccessResult] = useState<ExcelImportResponse | null>(null);

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setLoading(true);

    try {
      const response = await api.imports.previewExcel(file);
      setPreview(response);
      setStep("preview");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to preview Excel file";
      setError(errorMessage);
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  const handleProceedToMatch = async () => {
    if (!selectedFile) return;

    setError(null);
    setLoading(true);

    try {
      const response = await api.imports.matchExcel(selectedFile);
      setMatch(response);
      setResolutions([]);
      setStep("match");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to match donors";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleResolveAmbiguous = (resolution: DonorResolution) => {
    setResolutions((prev) => {
      const filtered = prev.filter(
        (r) =>
          !(
            r.source_first_name === resolution.source_first_name &&
            r.source_last_name === resolution.source_last_name
          )
      );
      return [...filtered, resolution];
    });
  };

  const handleConfirmImport = async () => {
    if (!selectedFile || !match) return;

    setError(null);
    setLoading(true);

    try {
      const response = await api.imports.confirmExcel(selectedFile, resolutions);
      setSuccessResult(response);
      setStep("success");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to confirm import";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setMatch(null);
    setResolutions([]);
    setSuccessResult(null);
    setError(null);
    setStep("upload");
  };

  const canConfirmImport =
    match &&
    match.ambiguous_donors === 0 ||
    (match &&
      resolutions.length === match.ambiguous_donors &&
      match.donors.every((d) =>
        d.status !== "ambiguous" ||
        resolutions.some(
          (r) =>
            r.source_first_name === d.first_name &&
            r.source_last_name === d.last_name
        )
      ));

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
          Excel Import
        </h1>
        <p className="mt-1 text-sm" style={{ color: "var(--text-muted)" }}>
          Import donors, pledges, and payments from an Excel file
        </p>
      </div>

      {/* Upload step */}
      {step === "upload" && (
        <div className="space-y-6">
          <FileUploadArea
            onFileSelect={handleFileSelect}
            loading={loading}
            selectedFileName={selectedFile?.name}
          />

          {error && (
            <div
              className="p-4 rounded-lg text-sm"
              style={{
                background: "var(--danger-muted)",
                color: "var(--danger)",
              }}
            >
              <p className="font-medium mb-1">Error</p>
              <p className="text-xs opacity-90 mb-3">{error}</p>
              <button
                onClick={handleReset}
                className="text-xs font-medium px-3 py-1.5 rounded transition-colors"
                style={{
                  background: "rgba(255, 255, 255, 0.1)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.2)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
                }}
              >
                Try another file
              </button>
            </div>
          )}

          {loading && (
            <div
              className="p-6 rounded-lg text-center"
              style={{
                background: "var(--surface-raised)",
                borderLeft: "4px solid var(--accent)",
              }}
            >
              <div className="flex items-center justify-center gap-2 mb-2">
                <div
                  className="w-2 h-2 rounded-full animate-pulse"
                  style={{ background: "var(--accent)" }}
                />
                <p className="font-medium text-sm" style={{ color: "var(--text-primary)" }}>
                  Analyzing your file...
                </p>
              </div>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                Please wait while we process your Excel file
              </p>
            </div>
          )}
        </div>
      )}

      {/* Preview step */}
      {step === "preview" && preview && (
        <div className="space-y-6">
          {/* Info cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <InfoCard label="File" value={preview.file_name} />
            <InfoCard label="Sheet" value={preview.sheet_name} />
            <InfoCard label="Columns" value={String(preview.columns.length)} />
            <InfoCard label="Rows" value={String(preview.total_rows)} />
          </div>

          {/* Columns detected */}
          <Card>
            <div
              className="px-5 py-4"
              style={{ borderBottom: "1px solid var(--border)" }}
            >
              <h3 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                Columns Detected
              </h3>
            </div>
            <div className="px-5 py-4 flex flex-wrap gap-2">
              {preview.columns.map((col) => (
                <span
                  key={col}
                  className="px-3 py-1.5 rounded-full text-xs font-medium"
                  style={{
                    background: "var(--accent-muted)",
                    color: "var(--accent)",
                  }}
                >
                  {col}
                </span>
              ))}
            </div>
          </Card>

          {/* Preview table */}
          <div>
            <h3 className="text-sm font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
              Data Preview
            </h3>
            <PreviewTable columns={preview.columns} rows={preview.rows} />
          </div>

          {error && (
            <div
              className="p-4 rounded-lg text-sm"
              style={{
                background: "var(--danger-muted)",
                color: "var(--danger)",
              }}
            >
              <p className="font-medium mb-1">Error</p>
              <p className="text-xs opacity-90">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <Button
              onClick={handleProceedToMatch}
              loading={loading}
            >
              {loading ? "Matching donors..." : "Match and Validate"}
            </Button>
            <Button variant="outline" onClick={handleReset} disabled={loading}>
              Change file
            </Button>
          </div>
        </div>
      )}

      {/* Match step */}
      {step === "match" && match && (
        <div className="space-y-6">
          {/* Summary */}
          <ImportSummary match={match} />

          {/* Ambiguous donors section */}
          {match.ambiguous_donors > 0 && (
            <div>
              <div className="mb-4">
                <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
                  Donors requiring validation
                </h2>
                <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
                  {resolutions.length} / {match.ambiguous_donors} resolved
                </p>
              </div>

              <div className="grid gap-4">
                {match.donors
                  .filter((d) => d.status === "ambiguous")
                  .map((donor, idx) => (
                    <AmbiguousDonorCard
                      key={idx}
                      donor={donor}
                      onResolve={handleResolveAmbiguous}
                      isResolved={resolutions.some(
                        (r) =>
                          r.source_first_name === donor.first_name &&
                          r.source_last_name === donor.last_name
                      )}
                    />
                  ))}
              </div>
            </div>
          )}

          {error && (
            <div
              className="p-4 rounded-lg text-sm"
              style={{
                background: "var(--danger-muted)",
                color: "var(--danger)",
              }}
            >
              <p className="font-medium mb-1">Error</p>
              <p className="text-xs opacity-90">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t" style={{ borderColor: "var(--border-subtle)" }}>
            <Button
              onClick={handleConfirmImport}
              disabled={loading || !canConfirmImport}
            >
              {loading ? "Confirming..." : "Confirm import"}
            </Button>
            <Button variant="outline" onClick={handleReset} disabled={loading}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Success step */}
      {step === "success" && successResult && (
        <ImportSuccess result={successResult} onImportAnother={handleReset} />
      )}
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <div className="px-4 py-4">
        <p className="text-xs font-medium mb-2" style={{ color: "var(--text-muted)" }}>
          {label}
        </p>
        <p className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          {value}
        </p>
      </div>
    </Card>
  );
}
