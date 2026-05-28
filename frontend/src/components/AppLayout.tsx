import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard" },
  { to: "/upload", label: "Upload" },
  { to: "/tickets", label: "Tickets" },
  { to: "/rag", label: "RAG Playground" },
  { to: "/eval", label: "Eval Runs" },
];

export default function AppLayout() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", margin: 0, minHeight: "100vh" }}>
      <nav
        style={{
          display: "flex",
          gap: "1rem",
          padding: "0.75rem 1.5rem",
          background: "#1a1a2e",
          color: "#fff",
          alignItems: "center",
        }}
      >
        <strong style={{ marginRight: "1.5rem", fontSize: "1.1rem" }}>ResolveOps AI</strong>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              color: isActive ? "#4fc3f7" : "#ccc",
              textDecoration: "none",
              fontWeight: isActive ? 600 : 400,
            })}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <main style={{ padding: "1.5rem", maxWidth: 1200, margin: "0 auto" }}>
        <Outlet />
      </main>
    </div>
  );
}
