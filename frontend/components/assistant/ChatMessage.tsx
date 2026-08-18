"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  hasPendingAction?: boolean;
  onConfirm?: () => void;
  onCancel?: () => void;
  isConfirmLoading?: boolean;
}

export function ChatMessage({
  role,
  content,
  hasPendingAction = false,
  onConfirm,
  onCancel,
  isConfirmLoading = false,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className="flex gap-4 max-w-4xl">
      {/* Avatar */}
      <div className="flex-shrink-0 pt-1">
        {isUser ? (
          <div
            className="flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold"
            style={{
              background: "var(--accent)",
              color: "#0f1117",
            }}
          >
            A
          </div>
        ) : (
          <div
            className="flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold"
            style={{
              background: "var(--accent-muted)",
              color: "var(--accent)",
            }}
          >
            K
          </div>
        )}
      </div>

      {/* Message */}
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>
          {isUser ? "Admin" : "KehilaFlow AI"}
        </div>
        <div
          className="prose max-w-none text-sm leading-relaxed"
          style={{ color: "var(--text-primary)" }}
        >
          {content.split("\n").map((line, i) => (
            <div key={i}>
              {line === "" ? <div className="h-2" /> : line}
            </div>
          ))}
        </div>

        {/* Confirm/Cancel buttons for pending actions */}
        {hasPendingAction && !isUser && (
          <div className="flex gap-2 mt-4">
            <button
              onClick={onConfirm}
              disabled={isConfirmLoading}
              className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
              style={{
                background: "var(--accent)",
                color: "#0f1117",
              }}
              onMouseEnter={(e) => {
                if (!isConfirmLoading) {
                  e.currentTarget.style.background = "var(--accent-hover)";
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "var(--accent)";
              }}
            >
              {isConfirmLoading ? "Confirming..." : "Confirm"}
            </button>
            <button
              onClick={onCancel}
              disabled={isConfirmLoading}
              className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
              style={{
                background: "var(--bg)",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
              }}
              onMouseEnter={(e) => {
                if (!isConfirmLoading) {
                  e.currentTarget.style.background = "var(--surface)";
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "var(--bg)";
              }}
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
