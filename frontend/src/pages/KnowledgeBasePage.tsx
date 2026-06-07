import { useEffect, useState } from "react";
import { generateKb, listKbArticles } from "../api/client";
import type { KbArticle } from "../api/types";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { badge, btn, card, colors, pageTitle, sectionTitle } from "../styles";

export default function KnowledgeBasePage() {
  const [articles, setArticles] = useState<KbArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const data = await listKbArticles();
      setArticles(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void (async () => {
      await load();
    })();
  }, []);

  const handleGenerate = async () => {
    setBusy(true);
    setError("");
    try {
      const data = await generateKb();
      setArticles(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Generation failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 style={pageTitle}>Knowledge Base</h1>
        <button onClick={handleGenerate} disabled={busy} style={btn("primary")}>
          {busy ? "Generating..." : "Generate from resolved tickets"}
        </button>
      </div>
      <p style={{ color: colors.textMuted, marginTop: "-0.75rem", marginBottom: "1.5rem" }}>
        Articles are synthesized by clustering resolved tickets that share a product area
        and issue type, distilling their common resolution steps.
      </p>

      {error && <ErrorState message={error} />}
      {loading && <LoadingState message="Loading articles..." />}

      {!loading && articles.length === 0 && (
        <div style={card}>
          <p style={{ color: colors.textMuted }}>
            No articles yet. Upload or sync resolved tickets, then click “Generate”.
          </p>
        </div>
      )}

      {articles.map((a) => (
        <div key={a.id} style={{ ...card, marginBottom: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ ...sectionTitle, marginBottom: "0.5rem" }}>{a.title}</h2>
            <span style={badge(colors.primary)}>{a.ticket_count} tickets</span>
          </div>
          <div style={{ marginBottom: "0.5rem" }}>
            <span style={badge(colors.textMuted)}>{a.product_area}</span>{" "}
            <span style={badge(colors.textMuted)}>{a.issue_type}</span>
          </div>
          <p style={{ color: colors.text, fontSize: "0.9rem" }}>{a.summary}</p>
          {a.resolution_steps && (
            <pre
              style={{
                whiteSpace: "pre-wrap",
                fontFamily: "inherit",
                background: colors.bg,
                padding: "0.75rem 1rem",
                borderRadius: 8,
                fontSize: "0.85rem",
                color: colors.text,
              }}
            >
              {a.resolution_steps}
            </pre>
          )}
          <div style={{ fontSize: "0.8rem", color: colors.textMuted }}>
            Sources:{" "}
            {a.source_ticket_ids.map((id) => (
              <a
                key={id}
                href={`/tickets/${encodeURIComponent(id)}`}
                style={{ color: colors.primary, textDecoration: "none", marginRight: 6 }}
              >
                {id}
              </a>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
