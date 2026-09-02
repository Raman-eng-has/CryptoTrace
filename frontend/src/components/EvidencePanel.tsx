import type { Evidence } from "../types/investigation";

interface EvidencePanelProps {
  evidence: Evidence[];
  selectedEvidenceIds?: string[];
}

export function EvidencePanel({
  evidence,
  selectedEvidenceIds = [],
}: EvidencePanelProps) {
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
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            fontSize: "12px",
            color: "#94a3b8",
            letterSpacing: "0.08em",
          }}
        >
          EVIDENCE
        </div>

        {selectedEvidenceIds.length > 0 && (
          <div
            style={{
              fontSize: "11px",
              color: "#60a5fa",
            }}
          >
            {selectedEvidenceIds.length} selected
          </div>
        )}
      </div>

      <div style={{ marginTop: "12px" }}>
        {evidence.map((item) => {
          const selected = selectedEvidenceIds.includes(item.id);

          return (
            <article
              key={item.id}
              style={{
                padding: "14px",
                marginBottom: "8px",
                borderRadius: "8px",
                border: selected
                  ? "1px solid #60a5fa"
                  : "1px solid #1e293b",
                background: selected ? "#172554" : "#020617",
                transition: "all 0.15s ease",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: "12px",
                }}
              >
                <strong>{item.title}</strong>

                <code
                  style={{
                    color: selected ? "#93c5fd" : "#64748b",
                    fontSize: "11px",
                  }}
                >
                  {item.id}
                </code>
              </div>

              <p
                style={{
                  color: "#94a3b8",
                  fontSize: "13px",
                  lineHeight: 1.5,
                  margin: "8px 0",
                }}
              >
                {item.description}
              </p>

              <div
                style={{
                  color: "#64748b",
                  fontSize: "11px",
                }}
              >
                Source: {item.source}
              </div>

              <div
                style={{
                  marginTop: "5px",
                  color: "#64748b",
                  fontSize: "11px",
                }}
              >
                {item.immutable ? "Immutable evidence" : "Derived evidence"}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
