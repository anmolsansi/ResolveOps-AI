import type { CSSProperties } from "react";

export const colors = {
  primary: "#4f46e5",
  primaryLight: "#818cf8",
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
  bg: "#f8fafc",
  card: "#ffffff",
  border: "#e2e8f0",
  text: "#1e293b",
  textMuted: "#64748b",
  navBg: "#0f172a",
  navAccent: "#818cf8",
};

export const card: CSSProperties = {
  background: colors.card,
  border: `1px solid ${colors.border}`,
  borderRadius: 12,
  padding: "1.25rem",
  boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
};

export const sectionTitle: CSSProperties = {
  fontSize: "1.1rem",
  fontWeight: 600,
  color: colors.text,
  marginBottom: "1rem",
  marginTop: 0,
};

export const badge = (color: string): CSSProperties => ({
  display: "inline-block",
  background: color + "18",
  color,
  padding: "2px 10px",
  borderRadius: 999,
  fontSize: "0.8rem",
  fontWeight: 600,
});

export const th: CSSProperties = {
  textAlign: "left",
  padding: "0.6rem 0.75rem",
  borderBottom: `2px solid ${colors.border}`,
  fontSize: "0.8rem",
  fontWeight: 600,
  color: colors.textMuted,
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};

export const td: CSSProperties = {
  padding: "0.6rem 0.75rem",
  borderBottom: `1px solid ${colors.border}`,
  fontSize: "0.875rem",
  color: colors.text,
};

export const btn = (variant: "primary" | "secondary" | "danger" = "primary"): CSSProperties => {
  const map = {
    primary: { bg: colors.primary, text: "#fff" },
    secondary: { bg: colors.border, text: colors.text },
    danger: { bg: colors.danger, text: "#fff" },
  };
  const v = map[variant];
  return {
    background: v.bg,
    color: v.text,
    border: "none",
    borderRadius: 8,
    padding: "0.5rem 1rem",
    fontWeight: 600,
    fontSize: "0.875rem",
    cursor: "pointer",
  };
};

export const input: CSSProperties = {
  border: `1px solid ${colors.border}`,
  borderRadius: 8,
  padding: "0.5rem 0.75rem",
  fontSize: "0.875rem",
  outline: "none",
  color: colors.text,
};

export const pageTitle: CSSProperties = {
  fontSize: "1.5rem",
  fontWeight: 700,
  color: colors.text,
  marginBottom: "1.5rem",
  marginTop: 0,
};
