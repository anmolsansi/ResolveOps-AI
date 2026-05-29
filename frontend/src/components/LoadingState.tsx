import { colors } from "../styles";

export default function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div style={{ padding: "3rem", textAlign: "center", color: colors.textMuted }}>
      <p style={{ fontSize: "0.95rem" }}>{message}</p>
    </div>
  );
}
