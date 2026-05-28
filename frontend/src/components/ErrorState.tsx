export default function ErrorState({ message }: { message: string }) {
  return (
    <div
      style={{
        padding: "1rem",
        background: "#fff3f3",
        border: "1px solid #f5c6cb",
        borderRadius: 8,
        color: "#721c24",
      }}
    >
      <strong>Error:</strong> {message}
    </div>
  );
}
