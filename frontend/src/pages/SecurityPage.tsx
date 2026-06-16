import { useReducer, useEffect } from "react";
import {
  listApiKeys,
  createApiKey,
  revokeApiKey,
  getSecuritySettings,
  updateSecuritySettings,
  listIpAllowlist,
  addIpAllowlist,
  removeIpAllowlist,
  listLoginAttempts,
} from "../api/client";
import type { ApiKey, SecuritySettings, IpAllowlistEntry, LoginAttempt } from "../api/types";

interface State {
  tab: "keys" | "rate" | "logins" | "ips";
  apiKeys: ApiKey[];
  settings: SecuritySettings | null;
  ipList: IpAllowlistEntry[];
  logins: LoginAttempt[];
  loading: boolean;
  error: string | null;
  keyForm: { name: string; scopes: string; expires_days: string };
  ipForm: { ip_address: string; note: string };
  newRawKey: string | null;
}

type Action =
  | { type: "LOAD_START" }
  | { type: "LOAD_DONE"; data: Partial<State> }
  | { type: "LOAD_ERROR"; error: string }
  | { type: "SET_TAB"; value: State["tab"] }
  | { type: "SET_KEY_FORM"; field: string; value: string }
  | { type: "SET_IP_FORM"; field: string; value: string }
  | { type: "SET_RAW_KEY"; value: string | null }
  | { type: "UPDATE_SETTING"; field: string; value: number | boolean };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "LOAD_START":
      return { ...state, loading: true, error: null };
    case "LOAD_DONE":
      return { ...state, loading: false, ...action.data };
    case "LOAD_ERROR":
      return { ...state, loading: false, error: action.error };
    case "SET_TAB":
      return { ...state, tab: action.value };
    case "SET_KEY_FORM":
      return { ...state, keyForm: { ...state.keyForm, [action.field]: action.value } };
    case "SET_IP_FORM":
      return { ...state, ipForm: { ...state.ipForm, [action.field]: action.value } };
    case "SET_RAW_KEY":
      return { ...state, newRawKey: action.value };
    case "UPDATE_SETTING":
      if (!state.settings) return state;
      return { ...state, settings: { ...state.settings, [action.field]: action.value } };
    default:
      return state;
  }
}

export default function SecurityPage() {
  const [state, dispatch] = useReducer(reducer, {
    tab: "keys",
    apiKeys: [],
    settings: null,
    ipList: [],
    logins: [],
    loading: true,
    error: null,
    keyForm: { name: "", scopes: "read", expires_days: "" },
    ipForm: { ip_address: "", note: "" },
    newRawKey: null,
  });

  const loadTab = () => {
    dispatch({ type: "LOAD_START" });
    const loaders: Record<string, () => Promise<unknown>> = {
      keys: () => listApiKeys().then((r) => dispatch({ type: "LOAD_DONE", data: { apiKeys: r.items } })),
      rate: () =>
        Promise.all([getSecuritySettings(), listLoginAttempts()]).then(([s, l]) =>
          dispatch({ type: "LOAD_DONE", data: { settings: s, logins: l.items } })
        ),
      logins: () => listLoginAttempts().then((r) => dispatch({ type: "LOAD_DONE", data: { logins: r.items } })),
      ips: () => listIpAllowlist().then((r) => dispatch({ type: "LOAD_DONE", data: { ipList: r.items } })),
    };
    loaders[state.tab]().catch((e) => dispatch({ type: "LOAD_ERROR", error: String(e) }));
  };

  useEffect(loadTab, [state.tab]);

  const handleCreateKey = async () => {
    try {
      const scopes = state.keyForm.scopes.split(",").map((s) => s.trim()).filter(Boolean);
      const expires = state.keyForm.expires_days ? parseInt(state.keyForm.expires_days) : undefined;
      const result = await createApiKey({ name: state.keyForm.name, scopes, expires_days: expires });
      dispatch({ type: "SET_RAW_KEY", value: result.raw_key });
      dispatch({ type: "SET_KEY_FORM", field: "name", value: "" });
      loadTab();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleRevokeKey = async (id: string) => {
    await revokeApiKey(id);
    loadTab();
  };

  const handleUpdateSetting = async (field: string, value: number | boolean) => {
    dispatch({ type: "UPDATE_SETTING", field, value });
    try {
      await updateSecuritySettings({ [field]: value });
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleAddIp = async () => {
    try {
      await addIpAllowlist({ ip_address: state.ipForm.ip_address, note: state.ipForm.note });
      dispatch({ type: "SET_IP_FORM", field: "ip_address", value: "" });
      dispatch({ type: "SET_IP_FORM", field: "note", value: "" });
      loadTab();
    } catch (e) {
      dispatch({ type: "LOAD_ERROR", error: String(e) });
    }
  };

  const handleRemoveIp = async (id: string) => {
    await removeIpAllowlist(id);
    loadTab();
  };

  const tabs = [
    { key: "keys", label: "API Keys" },
    { key: "rate", label: "Rate Limits" },
    { key: "logins", label: "Login Security" },
    { key: "ips", label: "IP Allowlist" },
  ] as const;

  return (
    <div>
      <h2>Security Settings</h2>
      <p style={{ color: "#666", fontSize: "0.875rem", marginBottom: 20 }}>
        Manage API keys, rate limiting, brute-force protection, and IP allowlisting.
      </p>

      {state.error && <div style={{ color: "#d32f2f", marginBottom: 16 }}>{state.error}</div>}

      <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: "2px solid #e0e0e0", paddingBottom: 4 }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => dispatch({ type: "SET_TAB", value: t.key })}
            style={{
              padding: "8px 16px",
              borderRadius: "6px 6px 0 0",
              border: "none",
              background: state.tab === t.key ? "#1976d2" : "transparent",
              color: state.tab === t.key ? "#fff" : "#666",
              cursor: "pointer",
              fontWeight: state.tab === t.key ? 600 : 400,
              fontSize: "0.875rem",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {state.loading ? (
        <div style={{ color: "#999" }}>Loading...</div>
      ) : (
        <>
          {state.tab === "keys" && (
            <div>
              {state.newRawKey && (
                <div style={{ padding: 16, background: "#e8f5e9", borderRadius: 8, marginBottom: 16, border: "1px solid #c8e6c9" }}>
                  <strong style={{ color: "#2e7d32" }}>API Key Created</strong>
                  <p style={{ fontSize: "0.85rem", margin: "8px 0" }}>
                    Copy this key now. It will not be shown again.
                  </p>
                  <code style={{ display: "block", padding: 8, background: "#fff", borderRadius: 4, fontSize: "0.8rem", wordBreak: "break-all" }}>
                    {state.newRawKey}
                  </code>
                  <button
                    onClick={() => dispatch({ type: "SET_RAW_KEY", value: null })}
                    style={{ marginTop: 8, padding: "6px 12px", borderRadius: 4, border: "none", background: "#2e7d32", color: "#fff", cursor: "pointer" }}
                  >
                    I have copied it
                  </button>
                </div>
              )}

              <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                <input
                  placeholder="Key name"
                  value={state.keyForm.name}
                  onChange={(e) => dispatch({ type: "SET_KEY_FORM", field: "name", value: e.target.value })}
                  style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd", flex: 1 }}
                />
                <input
                  placeholder="Scopes (comma-separated)"
                  value={state.keyForm.scopes}
                  onChange={(e) => dispatch({ type: "SET_KEY_FORM", field: "scopes", value: e.target.value })}
                  style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd", width: 180 }}
                />
                <input
                  placeholder="Expires (days)"
                  value={state.keyForm.expires_days}
                  onChange={(e) => dispatch({ type: "SET_KEY_FORM", field: "expires_days", value: e.target.value })}
                  style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd", width: 120 }}
                />
                <button
                  onClick={handleCreateKey}
                  disabled={!state.keyForm.name}
                  style={{ padding: "8px 16px", borderRadius: 4, border: "none", background: state.keyForm.name ? "#1976d2" : "#ccc", color: "#fff", cursor: state.keyForm.name ? "pointer" : "default", fontWeight: 600 }}
                >
                  Create
                </button>
              </div>

              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                    <th style={{ padding: "8px 12px" }}>Name</th>
                    <th style={{ padding: "8px 12px" }}>Prefix</th>
                    <th style={{ padding: "8px 12px" }}>Scopes</th>
                    <th style={{ padding: "8px 12px" }}>Last Used</th>
                    <th style={{ padding: "8px 12px" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {state.apiKeys.map((k) => (
                    <tr key={k.id} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: "8px 12px" }}>{k.name}</td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{k.key_prefix}...</td>
                      <td style={{ padding: "8px 12px" }}>{k.scopes.join(", ")}</td>
                      <td style={{ padding: "8px 12px", fontSize: "0.8rem", color: "#666" }}>
                        {k.last_used_at ? new Date(k.last_used_at).toLocaleDateString() : "Never"}
                      </td>
                      <td style={{ padding: "8px 12px" }}>
                        <button
                          onClick={() => handleRevokeKey(k.id)}
                          style={{ background: "none", border: "none", color: "#d32f2f", cursor: "pointer" }}
                        >
                          Revoke
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {state.tab === "rate" && state.settings && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
              <div>
                <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Rate Limiting</h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span>Requests per minute</span>
                    <input
                      type="number"
                      value={state.settings.rate_limit_requests_per_minute}
                      onChange={(e) => handleUpdateSetting("rate_limit_requests_per_minute", parseInt(e.target.value) || 60)}
                      style={{ width: 100, padding: "6px 8px", borderRadius: 4, border: "1px solid #ddd" }}
                    />
                  </label>
                  <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span>Burst limit</span>
                    <input
                      type="number"
                      value={state.settings.rate_limit_burst}
                      onChange={(e) => handleUpdateSetting("rate_limit_burst", parseInt(e.target.value) || 10)}
                      style={{ width: 100, padding: "6px 8px", borderRadius: 4, border: "1px solid #ddd" }}
                    />
                  </label>
                </div>
              </div>
              <div>
                <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Session</h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span>Session timeout (minutes)</span>
                    <input
                      type="number"
                      value={state.settings.session_timeout_minutes}
                      onChange={(e) => handleUpdateSetting("session_timeout_minutes", parseInt(e.target.value) || 480)}
                      style={{ width: 100, padding: "6px 8px", borderRadius: 4, border: "1px solid #ddd" }}
                    />
                  </label>
                </div>
              </div>
            </div>
          )}

          {state.tab === "logins" && (
            <div>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Brute-Force Protection</h3>
              {state.settings && (
                <div style={{ display: "flex", gap: 24, marginBottom: 24 }}>
                  <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    <span style={{ fontSize: "0.85rem" }}>Max login attempts</span>
                    <input
                      type="number"
                      value={state.settings.max_login_attempts}
                      onChange={(e) => handleUpdateSetting("max_login_attempts", parseInt(e.target.value) || 5)}
                      style={{ width: 80, padding: "6px 8px", borderRadius: 4, border: "1px solid #ddd" }}
                    />
                  </label>
                  <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    <span style={{ fontSize: "0.85rem" }}>Lockout duration (min)</span>
                    <input
                      type="number"
                      value={state.settings.lockout_duration_minutes}
                      onChange={(e) => handleUpdateSetting("lockout_duration_minutes", parseInt(e.target.value) || 15)}
                      style={{ width: 80, padding: "6px 8px", borderRadius: 4, border: "1px solid #ddd" }}
                    />
                  </label>
                </div>
              )}

              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>Recent Login Attempts</h3>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                    <th style={{ padding: "8px 12px" }}>Email</th>
                    <th style={{ padding: "8px 12px" }}>IP</th>
                    <th style={{ padding: "8px 12px" }}>Result</th>
                    <th style={{ padding: "8px 12px" }}>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {state.logins.map((l) => (
                    <tr key={l.id} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: "8px 12px" }}>{l.email}</td>
                      <td style={{ padding: "8px 12px" }}>{l.ip_address}</td>
                      <td style={{ padding: "8px 12px" }}>
                        <span style={{ color: l.success ? "#2e7d32" : "#d32f2f" }}>
                          {l.success ? "Success" : "Failed"}
                        </span>
                      </td>
                      <td style={{ padding: "8px 12px", fontSize: "0.8rem", color: "#666" }}>
                        {new Date(l.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {state.tab === "ips" && (
            <div>
              <h3 style={{ fontSize: "1rem", marginBottom: 12 }}>IP Allowlist</h3>
              <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                <input
                  placeholder="IP address"
                  value={state.ipForm.ip_address}
                  onChange={(e) => dispatch({ type: "SET_IP_FORM", field: "ip_address", value: e.target.value })}
                  style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd", width: 160 }}
                />
                <input
                  placeholder="Note (optional)"
                  value={state.ipForm.note}
                  onChange={(e) => dispatch({ type: "SET_IP_FORM", field: "note", value: e.target.value })}
                  style={{ padding: "8px 12px", borderRadius: 4, border: "1px solid #ddd", flex: 1 }}
                />
                <button
                  onClick={handleAddIp}
                  disabled={!state.ipForm.ip_address}
                  style={{ padding: "8px 16px", borderRadius: 4, border: "none", background: state.ipForm.ip_address ? "#1976d2" : "#ccc", color: "#fff", cursor: state.ipForm.ip_address ? "pointer" : "default", fontWeight: 600 }}
                >
                  Add
                </button>
              </div>

              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #e0e0e0", textAlign: "left" }}>
                    <th style={{ padding: "8px 12px" }}>IP Address</th>
                    <th style={{ padding: "8px 12px" }}>Note</th>
                    <th style={{ padding: "8px 12px" }}>Added By</th>
                    <th style={{ padding: "8px 12px" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {state.ipList.map((ip) => (
                    <tr key={ip.id} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{ip.ip_address}</td>
                      <td style={{ padding: "8px 12px" }}>{ip.note || "-"}</td>
                      <td style={{ padding: "8px 12px", fontSize: "0.8rem", color: "#666" }}>{ip.created_by}</td>
                      <td style={{ padding: "8px 12px" }}>
                        <button
                          onClick={() => handleRemoveIp(ip.id)}
                          style={{ background: "none", border: "none", color: "#d32f2f", cursor: "pointer" }}
                        >
                          Remove
                        </button>
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
