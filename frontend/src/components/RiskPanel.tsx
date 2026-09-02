import type { RiskResult } from "../types/investigation";

interface RiskPanelProps {
  risk: RiskResult;
}

export function RiskPanel({ risk }: RiskPanelProps) {
  return (
    <section
      style={{
        background: "#0f172a",
        border: "1px solid #1e293b",
        borderRadius: "12px",
        padding: "20px",
      }}
    >
      <div
        style={{
          fontSize: "12px",
          color: "#94a3b8",
          letterSpacing: "0.08em",
        }}
      >
        RISK ANALYSIS
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          gap: "8px",
          marginTop: "10px",
        }}
      >
        <strong style={{ fontSize: "36px" }}>{risk.score}</strong>
        <span style={{ color: "#94a3b8" }}>/ 100</span>
      </div>

      <div
        style={{
          display: "inline-block",
          marginTop: "4px",
          padding: "4px 8px",
          borderRadius: "6px",
          background: "#450a0a",
          color: "#fca5a5",
          fontSize: "12px",
          fontWeight: 600,
          textTransform: "uppercase",
        }}
      >
        {risk.level}
      </div>

      <div style={{ marginTop: "20px" }}>
        {risk.factors.map((factor) => (
          <div
            key={factor.id}
            style={{
              padding: "12px 0",
              borderTop: "1px solid #1e293b",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: "12px",
              }}
            >
              <strong>{factor.name}</strong>
              <span>+{factor.contribution}</span>
            </div>

            <p
              style={{
                margin: "6px 0 0",
                color: "#94a3b8",
                fontSize: "13px",
                lineHeight: 1.5,
              }}
            >
              {factor.explanation}
            </p>

            <div
              style={{
                marginTop: "6px",
                color: "#64748b",
                fontSize: "11px",
              }}
            >
              Evidence: {factor.evidenceIds.join(", ")}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}