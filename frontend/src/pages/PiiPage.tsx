import { useState } from "react";
import { scanPii } from "../api/client";
import type { PiiScanResponse } from "../api/types";
import ErrorState from "../components/ErrorState";
import { badge, btn, card, colors, input, pageTitle, sectionTitle, td, th } from "../styles";

const SAMPLE =
  "Hi, my email is jane.doe@example.com and my phone is 415-555-0199. " +
  "Card 4111 1111 1111 1111, SSN 123-45-6789, from host 192.168.0.1.";

export default function PiiPage() {
  const [text, setText] = useState(SAMPLE);
  const [result, setResult] = useState<PiiScanResponse | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleScan = async () => {
    setBusy(true);
    setError("");
    try {
      setResult(await scanPii(text));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scan failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h1 style={pageTitle}>PII Detection &amp; Redaction</h1>
      <p style={{ color: colors.textMuted, marginTop: "-1rem", marginBottom: "1.5rem" }}>
        Detect and redact personally identifiable information (emails, phones, SSNs, credit
        cards, IPs) before storing or sharing ticket content.
      </p>

      {error && <ErrorState message={error} />}

      <div style={{ ...card, marginBottom: "1.5rem" }}>
        <h2 style={sectionTitle}>Scan text</h2>
        <textarea
          style={{ ...input, width: "100%", minHeight: 120, resize: "vertical" }}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div style={{ marginTop: "0.75rem" }}>
          <button onClick={handleScan} disabled={busy || !text} style={btn("primary")}>
            Scan &amp; redact
          </button>
        </div>
      </div>

      {result && (
        <>
          <div style={{ ...card, marginBottom: "1.5rem" }}>
            <h2 style={sectionTitle}>Redacted output</h2>
            <pre style={{ whiteSpace: "pre-wrap", margin: 0, fontFamily: "monospace", fontSize: "0.875rem" }}>
              {result.redacted_text}
            </pre>
            <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {Object.entries(result.counts).map(([type, count]) => (
                <span key={type} style={badge(colors.warning)}>
                  {type}: {count}
                </span>
              ))}
              {Object.keys(result.counts).length === 0 && (
                <span style={badge(colors.success)}>No PII detected</span>
              )}
            </div>
          </div>

          {result.matches.length > 0 && (
            <div style={card}>
              <h2 style={sectionTitle}>Matches ({result.matches.length})</h2>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th style={th}>Type</th>
                    <th style={th}>Value</th>
                    <th style={th}>Position</th>
                  </tr>
                </thead>
                <tbody>
                  {result.matches.map((m, i) => (
                    <tr key={i}>
                      <td style={td}>
                        <span style={badge(colors.primary)}>{m.type}</span>
                      </td>
                      <td style={{ ...td, fontFamily: "monospace" }}>{m.value}</td>
                      <td style={td}>
                        {m.start}–{m.end}
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
