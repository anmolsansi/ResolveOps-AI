import { card, colors } from "../styles";

interface MetricCardProps {
  label: string;
  value: string | number;
  accent?: string;
  explanation?: string;
}

export default function MetricCard({ label, value, accent, explanation }: MetricCardProps) {
  return (
    <div
      style={{ ...card, minWidth: 140, textAlign: "center", flex: "1 1 140px" }}
      title={explanation}
    >
      <div style={{ fontSize: "1.6rem", fontWeight: 700, color: accent || colors.primary }}>
        {value}
      </div>
      <div style={{ fontSize: "0.78rem", color: colors.textMuted, marginTop: 4, fontWeight: 500 }}>
        {label}
      </div>
    </div>
  );
}
