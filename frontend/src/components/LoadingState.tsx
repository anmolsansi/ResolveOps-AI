export default function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div style={{ padding: "2rem", textAlign: "center", color: "#666" }}>
      <p>{message}</p>
    </div>
  );
}
