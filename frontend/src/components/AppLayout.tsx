import { NavLink, Outlet } from "react-router-dom";
import { colors } from "../styles";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard" },
  { to: "/upload", label: "Upload" },
  { to: "/tickets", label: "Tickets" },
  { to: "/rag", label: "RAG Playground" },
  { to: "/eval", label: "Eval Runs" },
];

export default function AppLayout() {
  return (
    <div style={{ fontFamily: "'Inter', system-ui, sans-serif", margin: 0, minHeight: "100vh", background: colors.bg }}>
      <nav
        style={{
          display: "flex",
          gap: "0.25rem",
          padding: "0 1.5rem",
          background: colors.navBg,
          color: "#fff",
          alignItems: "center",
          height: 56,
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <strong style={{ marginRight: "2rem", fontSize: "1.05rem", letterSpacing: "-0.01em" }}>
          ResolveOps AI
        </strong>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              color: isActive ? "#fff" : "rgba(255,255,255,0.6)",
              textDecoration: "none",
              fontWeight: isActive ? 600 : 400,
              fontSize: "0.875rem",
              padding: "0.5rem 0.75rem",
              borderRadius: 6,
              background: isActive ? "rgba(255,255,255,0.1)" : "transparent",
              transition: "all 0.15s",
            })}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <main style={{ padding: "2rem", maxWidth: 1280, margin: "0 auto" }}>
        <Outlet />
      </main>
    </div>
  );
}
