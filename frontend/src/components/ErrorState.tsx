import { colors } from "../styles";

export default function ErrorState({ message }: { message: string }) {
  return (
    <div
      style={{
        padding: "1rem 1.25rem",
        background: `${colors.danger}08`,
        border: `1px solid ${colors.danger}30`,
        borderRadius: 10,
        color: colors.danger,
        fontSize: "0.875rem",
        marginBottom: "1rem",
      }}
    >
      <strong>Error:</strong> {message}
    </div>
  );
}
