"use client";

import { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "ghost" | "outline";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: "sm" | "md";
}

const base =
  "inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 disabled:opacity-50 disabled:pointer-events-none cursor-pointer";

const sizes = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
};

export function Button({
  variant = "primary",
  size = "md",
  className = "",
  style,
  ...props
}: ButtonProps) {
  const variantStyle =
    variant === "primary"
      ? {
          background: "var(--accent)",
          color: "#0f1117",
          fontWeight: 600,
        }
      : variant === "outline"
      ? {
          background: "transparent",
          color: "var(--text-primary)",
          border: "1px solid var(--border)",
        }
      : {
          background: "transparent",
          color: "var(--text-secondary)",
        };

  return (
    <button
      className={`${base} ${sizes[size]} ${className}`}
      style={{ ...variantStyle, ...style }}
      onMouseEnter={(e) => {
        if (variant === "primary") {
          e.currentTarget.style.background = "var(--accent-hover)";
        } else {
          e.currentTarget.style.background = "var(--surface-raised)";
          e.currentTarget.style.color = "var(--text-primary)";
        }
      }}
      onMouseLeave={(e) => {
        Object.assign(e.currentTarget.style, variantStyle);
      }}
      {...props}
    />
  );
}
