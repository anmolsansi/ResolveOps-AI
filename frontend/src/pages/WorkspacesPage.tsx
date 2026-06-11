import { useEffect, useState } from "react";
import {
  addMember,
  createWorkspace,
  getToken,
  listMembers,
  listWorkspaces,
} from "../api/client";
import type { MemberResponse, WorkspaceResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

export default function WorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<WorkspaceResponse[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [members, setMembers] = useState<MemberResponse[]>([]);
  const [name, setName] = useState("");
  const [memberEmail, setMemberEmail] = useState("");
  const [memberRole, setMemberRole] = useState("member");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    try {
      const list = await listWorkspaces();
      setWorkspaces(list.workspaces);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load workspaces");
    }
  };

  useEffect(() => {
    void (async () => {
      await refresh();
    })();
  }, []);

  const openMembers = async (id: string) => {
    setSelected(id);
    setError("");
    try {
      const res = await listMembers(id);
      setMembers(res.members);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load members");
    }
  };

  const handleCreate = async () => {
    setBusy(true);
    setError("");
    try {
      await createWorkspace(name);
      setName("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed");
    } finally {
      setBusy(false);
    }
  };

  const handleAddMember = async () => {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      await addMember(selected, memberEmail, memberRole);
      setMemberEmail("");
      await openMembers(selected);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Add member failed");
    } finally {
      setBusy(false);
    }
  };

  if (!getToken()) {
    return (
      <div>
        <h1 style={pageTitle}>Workspaces</h1>
        <ErrorState message="Please sign in from the Account page to manage workspaces." />
      </div>
    );
  }

  return (
    <div>
      <h1 style={pageTitle}>Workspaces</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Team workspaces with per-workspace membership and roles. Creating a workspace makes
        you its admin.
      </p>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Create workspace</h2>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <input
            style={{ ...input, flex: "1 1 240px" }}
            placeholder="Workspace name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button onClick={handleCreate} disabled={busy || !name} style={btn("primary")}>
            Create
          </button>
        </div>
      </div>

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Workspaces ({workspaces.length})</h2>
        {workspaces.length === 0 ? (
          <p style={{ color: colors.textMuted }}>No workspaces yet.</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Name</th>
                <th style={th}>Slug</th>
                <th style={th}>Members</th>
                <th style={th}></th>
              </tr>
            </thead>
            <tbody>
              {workspaces.map((w) => (
                <tr key={w.id}>
                  <td style={td}>{w.name}</td>
                  <td style={td}>
                    <code>{w.slug}</code>
                  </td>
                  <td style={td}>{w.member_count}</td>
                  <td style={td}>
                    <button onClick={() => openMembers(w.id)} style={btn("secondary")}>
                      Members
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selected && (
        <div style={card}>
          <h2 style={sectionTitle}>Members</h2>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            <input
              style={{ ...input, flex: "1 1 220px" }}
              placeholder="Existing user email"
              value={memberEmail}
              onChange={(e) => setMemberEmail(e.target.value)}
            />
            <select value={memberRole} onChange={(e) => setMemberRole(e.target.value)} style={input}>
              {["admin", "member", "viewer"].map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
            <button onClick={handleAddMember} disabled={busy || !memberEmail} style={btn("primary")}>
              Add member
            </button>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Email</th>
                <th style={th}>Role</th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <tr key={m.membership_id}>
                  <td style={td}>{m.email}</td>
                  <td style={td}>
                    <span style={badge(m.role === "admin" ? colors.primary : colors.success)}>
                      {m.role}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
