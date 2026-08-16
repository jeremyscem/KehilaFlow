"use client";

import { useState, useRef } from "react";

interface FileUploadAreaProps {
  onFileSelect: (file: File) => void;
  loading?: boolean;
  selectedFileName?: string;
}

export function FileUploadArea({
  onFileSelect,
  loading = false,
  selectedFileName,
}: FileUploadAreaProps) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.name.endsWith(".xlsx")) {
        onFileSelect(file);
      } else {
        alert("Please select a .xlsx file");
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  return (
    <div
      className="rounded-xl border-2 border-dashed p-12 text-center transition-all cursor-pointer"
      style={{
        borderColor: dragActive ? "var(--accent)" : "var(--border)",
        background: dragActive ? "var(--accent-muted)" : "transparent",
      }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          handleClick();
        }
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx"
        onChange={handleChange}
        className="hidden"
        disabled={loading}
      />

      <div className="flex flex-col items-center gap-3">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{
            background: "var(--accent-muted)",
            color: "var(--accent)",
          }}
        >
          <UploadIcon />
        </div>

        {selectedFileName ? (
          <div>
            <p className="font-medium text-sm" style={{ color: "var(--text-primary)" }}>
              {selectedFileName}
            </p>
            <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
              {loading ? "Uploading..." : "Click to replace"}
            </p>
          </div>
        ) : (
          <div>
            <p className="font-medium text-sm" style={{ color: "var(--text-primary)" }}>
              Drag and drop your Excel file
            </p>
            <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
              or click to browse (.xlsx only)
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function UploadIcon() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}
