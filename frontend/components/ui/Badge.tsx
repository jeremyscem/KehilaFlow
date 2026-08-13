type BadgeVariant = "success" | "danger" | "warning" | "default";

const variants: Record<BadgeVariant, { bg: string; color: string }> = {
  success: { bg: "var(--success-muted)", color: "var(--success)" },
  danger: { bg: "var(--danger-muted)", color: "var(--danger)" },
  warning: { bg: "var(--accent-muted)", color: "var(--accent)" },
  default: { bg: "rgba(148,163,184,0.1)", color: "var(--text-secondary)" },
};

export function Badge({ children, variant = "default" }: { children: React.ReactNode; variant?: BadgeVariant }) {
  const { bg, color } = variants[variant];
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
      style={{ background: bg, color }}
    >
      {children}
    </span>
  );
}
