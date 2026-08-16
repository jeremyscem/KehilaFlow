"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
}

export function ChatMessage({ role, content }: ChatMessageProps) {
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
      </div>
    </div>
  );
}
