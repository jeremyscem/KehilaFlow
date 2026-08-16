"use client";

import { useState, useRef, useEffect } from "react";

interface ChatComposerProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatComposer({ onSend, disabled = false }: ChatComposerProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  // Auto-resize textarea as content grows
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  }, [message]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (message.trim() && !disabled) {
        onSend(message.trim());
        setMessage("");
      }
    }
  };

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
    }
  };

  return (
    <div
      className="flex gap-3 p-4 rounded-xl border"
      style={{
        background: "var(--surface)",
        borderColor: "var(--border)",
      }}
    >
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Ask about KehilaFlow…"
        className="flex-1 resize-none outline-none text-sm p-2 rounded-lg transition-all"
        style={{
          background: "var(--bg)",
          border: "1px solid var(--border)",
          color: "var(--text-primary)",
          caretColor: "var(--accent)",
          minHeight: "40px",
          maxHeight: "120px",
        }}
        onFocus={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
        onBlur={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
        rows={1}
      />

      <button
        onClick={handleSend}
        disabled={!message.trim() || disabled}
        className="flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-all duration-150 flex-shrink-0 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
        style={{
          background: "var(--accent)",
          color: "#0f1117",
          height: "fit-content",
          marginTop: "auto",
          marginBottom: "auto",
        }}
        onMouseEnter={(e) => {
          if (!disabled && message.trim()) {
            e.currentTarget.style.background = "var(--accent-hover)";
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "var(--accent)";
        }}
      >
        <SendIcon />
      </button>
    </div>
  );
}

function SendIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}
