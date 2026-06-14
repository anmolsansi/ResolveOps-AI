import { useEffect, useReducer } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getCustomer } from "../api/client";
import type { CustomerProfileDetailResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, card, colors, pageTitle, sectionTitle } from "../styles";

const STATUS_COLORS: Record<string, string> = {
  open: colors.primary,
  waiting_for_customer: colors.warning,
  escalated: colors.danger,
  resolved: colors.success,
};

interface State {
  data: CustomerProfileDetailResponse | null;
  loading: boolean;
  error: string;
}

type Action =
  | { type: "loading" }
  | { type: "loaded"; data: CustomerProfileDetailResponse }
  | { type: "error"; error: string };

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "loading":
      return { ...state, loading: true, error: "" };
    case "loaded":
      return { ...state, data: action.data, loading: false };
    case "error":
      return { ...state, error: action.error, loading: false };
  }
};

const initialState: State = { data: null, loading: true, error: "" };

export default function CustomerProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [state, dispatch] = useReducer(reducer, initialState);
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;
    dispatch({ type: "loading" });
    getCustomer(id)
      .then((data) => dispatch({ type: "loaded", data }))
      .catch((e) => dispatch({ type: "error", error: e.message }));
  }, [id]);

  if (state.loading) return <LoadingState />;
  if (state.error) return <ErrorState message={state.error} />;
  if (!state.data) return <ErrorState message="Customer not found" />;

  const { profile, timeline } = state.data;

  return (
    <div>
      <h1 style={pageTitle}>Customer Profile</h1>

      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <div style={{ ...card, flex: "1 1 300px" }}>
          <h3 style={sectionTitle}>Profile</h3>
          <div style={{ fontSize: "1.1rem", fontWeight: 600 }}>{profile.name || profile.email || "Anonymous"}</div>
          {profile.email && <div style={{ color: colors.textMuted, fontSize: "0.85rem" }}>{profile.email}</div>}
          {profile.company && <div style={{ color: colors.textMuted, fontSize: "0.85rem" }}>{profile.company}</div>}
          <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: "0.72rem", color: colors.textMuted }}>              Tier</div>
              <span style={badge(colors.primary)}>{profile.customer_tier}</span>
            </div>
            <div>
              <div style={{ fontSize: "0.72rem", color: colors.textMuted }}>Sentiment</div>
              <strong>{(profile.sentiment_score * 100).toFixed(0)}%</strong>
            </div>
            <div>
              <div style={{ fontSize: "0.72rem", color: colors.textMuted }}>Conversations</div>
              <strong>{profile.total_conversations}</strong>
            </div>
            <div>
              <div style={{ fontSize: "0.72rem", color: colors.textMuted }}>Unresolved</div>
              <strong>{profile.unresolved_issues}</strong>
            </div>
          </div>
          <div style={{ marginTop: "0.75rem", fontSize: "0.82rem", color: colors.textMuted }}>
            Last seen: {profile.last_seen_at ? new Date(profile.last_seen_at).toLocaleString() : "Never"}
          </div>
        </div>

        <div style={{ ...card, flex: "2 1 400px" }}>
          <h3 style={sectionTitle}>Conversation Timeline</h3>
          {timeline.length === 0 ? (
            <div style={{ color: colors.textMuted, fontSize: "0.85rem" }}>No conversations yet.</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {timeline.map((t) => (
                <div
                  key={t.conversation_id}
                  onClick={() => navigate(`/conversations/${t.conversation_id}`)}
                  style={{
                    padding: "0.75rem",
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    cursor: "pointer",
                    display: "flex",
                    gap: "0.75rem",
                    alignItems: "center",
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "0.88rem", fontWeight: 500 }}>{t.subject || "No subject"}</div>
                    <div style={{ fontSize: "0.78rem", color: colors.textMuted }}>
                      <span style={badge(colors.primary)}>{t.channel}</span> <span style={badge(STATUS_COLORS[t.status] || colors.textMuted)}>{t.status}</span>
                    </div>
                  </div>
                  <div style={{ fontSize: "0.78rem", color: colors.textMuted, whiteSpace: "nowrap" }}>
                    {new Date(t.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
