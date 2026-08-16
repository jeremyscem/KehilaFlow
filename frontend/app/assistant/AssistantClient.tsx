"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/components/assistant/ChatMessage";
import { ChatComposer } from "@/components/assistant/ChatComposer";
import { SuggestedQuestions } from "@/components/assistant/SuggestedQuestions";
import { api } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function AssistantClient() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (text: string) => {
    // Add user message to chat
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const response = await api.ai.chat(text);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to get response from the assistant";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    handleSendMessage(question);
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full max-w-4xl">
      {/* Messages or welcome area */}
      {isEmpty ? (
        // Welcome state
        <div className="flex flex-col gap-6 items-center justify-center flex-1">
          <div className="text-center max-w-md">
            <h2 className="text-2xl font-bold mb-3" style={{ color: "var(--text-primary)" }}>
              KehilaFlow AI Assistant
            </h2>
            <p className="text-sm mb-2" style={{ color: "var(--text-secondary)" }}>
              Ask questions about your donors, pledges, payments and campaigns.
            </p>
            <div
              className="inline-block px-3 py-1.5 rounded-full text-xs font-medium mt-3"
              style={{
                background: "var(--accent-muted)",
                color: "var(--accent)",
              }}
            >
              Read-only
            </div>
          </div>

          {/* Suggested questions */}
          <div className="w-full">
            <SuggestedQuestions onSelect={handleSuggestedQuestion} />
          </div>
        </div>
      ) : (
        // Chat view
        <div className="flex-1 overflow-y-auto pr-2 space-y-6 min-w-0">
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
            />
          ))}

          {/* Loading state */}
          {loading && (
            <div className="flex gap-4 max-w-4xl">
              <div className="flex-shrink-0 pt-1">
                <div
                  className="flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold"
                  style={{
                    background: "var(--accent-muted)",
                    color: "var(--accent)",
                  }}
                >
                  K
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>
                  KehilaFlow AI
                </div>
                <div className="flex gap-1.5">
                  <div
                    className="w-2 h-2 rounded-full animate-pulse"
                    style={{ background: "var(--text-muted)" }}
                  />
                  <div
                    className="w-2 h-2 rounded-full animate-pulse"
                    style={{ background: "var(--text-muted)", animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 rounded-full animate-pulse"
                    style={{ background: "var(--text-muted)", animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div
              className="p-4 rounded-lg text-sm"
              style={{
                background: "var(--danger-muted)",
                color: "var(--danger)",
              }}
            >
              <p className="font-medium mb-1">The assistant couldn&apos;t complete this request</p>
              <p className="text-xs opacity-90">
                {error}
              </p>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-xs font-medium px-2 py-1 rounded transition-colors"
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
                Dismiss
              </button>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Composer at bottom (always visible) */}
      <div className="sticky bottom-0 pt-4 mt-6" style={{ backgroundImage: "linear-gradient(to top, var(--bg) 0%, transparent 100%)" }}>
        <ChatComposer onSend={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}
