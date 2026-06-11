import { useEffect, useState } from "react";
import {
  clearToken,
  getMe,
  getToken,
  listUsers,
  login,
  register,
  setToken,
  updateUserRole,
} from "../api/client";
import type { UserResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

const ROLES = ["admin", "member", "viewer"];

function roleColor(role: string): string {
  if (role === "admin") return colors.primary;
  if (role === "member") return colors.success;
  return colors.textMuted;
}

export default function AccountPage() {
  const [me, setMe] = useState<UserResponse | null>(null);
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadMe = async () => {
    if (!getToken()) {
      setMe(null);
      return;
    }
    try {
      const user = await getMe();
      setMe(user);
      if (user.role === "admin") {
        const list = await listUsers();
        setUsers(list.users);
      }
    } catch {
      clearToken();
      setMe(null);
    }
  };

  useEffect(() => {
    void (async () => {
      await loadMe();
    })();
  }, []);

  const handleAuth = async () => {
    setBusy(true);
    setError("");
    try {
      const resp = mode === "login" ? await login(email, password) : await register(email, password);
      setToken(resp.access_token);
      setEmail("");
      setPassword("");
      await loadMe();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    setMe(null);
    setUsers([]);
  };

  const handleRoleChange = async (userId: string, role: string) => {
    setError("");
    try {
      await updateUserRole(userId, role);
      await loadMe();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Role update failed");
    }
  };

  return (
    <div>
      <h1 style={pageTitle}>Account &amp; Access</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Authentication and role-based access control. The first registered user becomes an
        admin; admins manage roles and govern the workspace.
      </p>

      {error && <ErrorState message={error} />}

      {!me ? (
        <div style={{ ...card, maxWidth: 420 }}>
          <h2 style={sectionTitle}>{mode === "login" ? "Sign in" : "Create account"}</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <input
              style={input}
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              style={input}
              type="password"
              placeholder="Password (min 8 chars)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleAuth} disabled={busy} style={btn("primary")}>
              {mode === "login" ? "Sign in" : "Register"}
            </button>
            <button
              onClick={() => setMode(mode === "login" ? "register" : "login")}
              style={{ ...btn("secondary"), background: "transparent", color: colors.primary }}
            >
              {mode === "login" ? "Need an account? Register" : "Have an account? Sign in"}
            </button>
          </div>
        </div>
      ) : (
        <>
          <div style={{ ...card, marginBottom: "1.5rem", display: "flex", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600 }}>{me.email}</div>
              <div style={{ marginTop: 4 }}>
                <span style={badge(roleColor(me.role))}>{me.role}</span>
              </div>
            </div>
            <button onClick={handleLogout} style={{ ...btn("secondary"), marginLeft: "auto" }}>
              Sign out
            </button>
          </div>

          {me.role === "admin" && (
            <div style={card}>
              <h2 style={sectionTitle}>Users ({users.length})</h2>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Email</th>
                    <th style={th}>Role</th>
                    <th style={th}>Status</th>
                    <th style={th}>Change role</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td style={td}>{u.email}</td>
                      <td style={td}>
                        <span style={badge(roleColor(u.role))}>{u.role}</span>
                      </td>
                      <td style={td}>{u.is_active ? "active" : "inactive"}</td>
                      <td style={td}>
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                          style={input}
                        >
                          {ROLES.map((r) => (
                            <option key={r} value={r}>
                              {r}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
