"use client";

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const SUGGESTIONS = [
  "Who owes us the most money?",
  "What are our total pledged and collected amounts?",
  "Show our active campaigns",
  "Find a donor",
];

export function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {SUGGESTIONS.map((question) => (
        <button
          key={question}
          onClick={() => onSelect(question)}
          className="p-4 rounded-lg text-left text-sm font-medium transition-all duration-150 cursor-pointer"
          style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            color: "var(--text-primary)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--surface-raised)";
            e.currentTarget.style.borderColor = "var(--accent)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "var(--surface)";
            e.currentTarget.style.borderColor = "var(--border)";
          }}
        >
          {question}
        </button>
      ))}
    </div>
  );
}
