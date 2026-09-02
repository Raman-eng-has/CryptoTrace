import { useEffect, useMemo, useState } from "react";

import { EvidencePanel } from "./components/EvidencePanel";
import { RiskPanel } from "./components/RiskPanel";
import { TransactionGraph } from "./components/TransactionGraph";

import type {
  GraphEdge,
  Investigation,
} from "./types/investigation";

import "./App.css";

function shortHash(value: string, left = 8, right = 6): string {
  if (value.length <= left + right + 1) {
    return value;
  }

  return `${value.slice(0, left)}…${value.slice(-right)}`;
}

function formatAmount(amount: number, asset: string): string {
  return `${amount.toLocaleString(undefined, {
    maximumFractionDigits: 4,
  })} ${asset}`;
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function App() {
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null);

  const [selectedEvidenceIds, setSelectedEvidenceIds] =
    useState<string[]>([]);

  const [, setSelectedNodeId] =
  useState<string | null>(null);

  const [selectedEdgeId, setSelectedEdgeId] =
    useState<string | null>(null);

  const [traceEdge, setTraceEdge] =
    useState<GraphEdge | null>(null);

  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");

  const [loadingQuestion, setLoadingQuestion] =
    useState(false);

  const [backendOnline, setBackendOnline] =
    useState(true);

  /*
   * ---------------------------------------------------------
   * LOAD INVESTIGATION
   * ---------------------------------------------------------
   */

  useEffect(() => {
    let mounted = true;

    async function loadInvestigation() {
      try {
        const response = await fetch("/investigation");

        if (!response.ok) {
          throw new Error(
            `Investigation request failed: ${response.status}`,
          );
        }

        const data =
          (await response.json()) as Investigation;

        if (!mounted) {
          return;
        }

        setInvestigation(data);
        setBackendOnline(true);
      } catch (error) {
        console.error(
          "Failed to load investigation:",
          error,
        );

        if (mounted) {
          setBackendOnline(false);
        }
      }
    }

    void loadInvestigation();

    return () => {
      mounted = false;
    };
  }, []);

  /*
   * ---------------------------------------------------------
   * SORT TRANSACTIONS BY TIME
   * ---------------------------------------------------------
   */

  const sortedEdges = useMemo<GraphEdge[]>(() => {
    if (!investigation) {
      return [];
    }

    return [...investigation.edges].sort(
      (a: GraphEdge, b: GraphEdge) =>
        new Date(a.timestamp).getTime() -
        new Date(b.timestamp).getTime(),
    );
  }, [investigation]);

  /*
   * ---------------------------------------------------------
   * SELECTED TRANSACTION
   * ---------------------------------------------------------
   */

  const selectedEdge = useMemo<GraphEdge | null>(() => {
    if (!investigation || !selectedEdgeId) {
      return null;
    }

    return (
      investigation.edges.find(
        (edge: GraphEdge) =>
          edge.id === selectedEdgeId,
      ) ?? null
    );
  }, [investigation, selectedEdgeId]);

  /*
   * Current transaction displayed by the telemetry layer.
   *
   * Priority:
   * 1. Explicitly selected transaction
   * 2. Current replay transaction
   * 3. First transaction
   */

  const currentEdge: GraphEdge | null =
    selectedEdge ??
    traceEdge ??
    sortedEdges[0] ??
    null;

  /*
   * ---------------------------------------------------------
   * CURRENT TIMELINE POSITION
   * ---------------------------------------------------------
   */

  const currentIndex = currentEdge
    ? Math.max(
        sortedEdges.findIndex(
          (edge: GraphEdge) =>
            edge.id === currentEdge.id,
        ),
        0,
      )
    : 0;

  /*
   * Transactions visible up to the current
   * point in the investigation timeline.
   */

  const visibleEdges: GraphEdge[] =
    sortedEdges.slice(0, currentIndex + 1);

  /*
   * ---------------------------------------------------------
   * INVESTIGATION TELEMETRY
   * ---------------------------------------------------------
   */

  const totalObserved = visibleEdges.reduce(
    (
      sum: number,
      edge: GraphEdge,
    ) => sum + edge.amount,
    0,
  );

  const suspiciousCount = visibleEdges.filter(
    (edge: GraphEdge) =>
      Boolean(edge.suspicious),
  ).length;

  const elapsedMinutes =
    sortedEdges.length > 1
      ? Math.max(
          0,
          (
            new Date(
              sortedEdges[currentIndex]?.timestamp ?? "",
            ).getTime() -
            new Date(
              sortedEdges[0]?.timestamp ?? "",
            ).getTime()
          ) /
            60000,
        )
      : 0;

  /*
   * ---------------------------------------------------------
   * NODE SELECTION
   * ---------------------------------------------------------
   */

  const handleNodeSelect = (
    nodeId: string | null,
  ) => {
    setSelectedNodeId(nodeId);
    setSelectedEdgeId(null);

    if (!investigation || !nodeId) {
      setSelectedEvidenceIds([]);
      return;
    }

    const evidence = investigation.edges
      .filter(
        (edge: GraphEdge) =>
          edge.source === nodeId ||
          edge.target === nodeId,
      )
      .flatMap(
        (edge: GraphEdge) =>
          edge.evidenceIds ?? [],
      );

    setSelectedEvidenceIds([
      ...new Set(evidence),
    ]);
  };

  /*
   * ---------------------------------------------------------
   * TRANSACTION SELECTION
   * ---------------------------------------------------------
   */

  const handleEdgeSelect = (
    edgeId: string,
  ) => {
    if (!investigation) {
      return;
    }

    const edge =
      investigation.edges.find(
        (item: GraphEdge) =>
          item.id === edgeId,
      );

    if (!edge) {
      return;
    }

    setSelectedEdgeId(edgeId);
    setSelectedNodeId(null);

    setSelectedEvidenceIds(
      edge.evidenceIds ?? [],
    );

    setTraceEdge(edge);
  };

  /*
   * ---------------------------------------------------------
   * TRACE REPLAY
   * ---------------------------------------------------------
   */

  const handleTraceStep = (
    edge: GraphEdge | null,
  ) => {
    setTraceEdge(edge);

    if (!edge) {
      return;
    }

    setSelectedEdgeId(edge.id);
    setSelectedNodeId(null);

    setSelectedEvidenceIds(
      edge.evidenceIds ?? [],
    );
  };

  /*
   * ---------------------------------------------------------
   * COPILOT / QA
   * ---------------------------------------------------------
   */

  const handleSubmitQuestion = async (
    prompt = question,
  ) => {
    if (
      !prompt.trim() ||
      !investigation ||
      loadingQuestion
    ) {
      return;
    }

    setQuestion(prompt);
    setLoadingQuestion(true);
    setAnswer("");

    try {
      const response = await fetch(
        "/qa",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: prompt.trim(),
            evidence:
              investigation.evidence,
          }),
        },
      );

      if (!response.ok) {
        throw new Error(
          `QA request failed: ${response.status}`,
        );
      }

      const data =
        (await response.json()) as {
          answer: string;
        };

      setAnswer(data.answer);
      setBackendOnline(true);
    } catch (error) {
      console.error(
        "QA request failed:",
        error,
      );

      setBackendOnline(false);

      setAnswer(
        "Copilot could not reach the investigation service. Check that the FastAPI server is running on port 8000.",
      );
    } finally {
      setLoadingQuestion(false);
    }
  };

  /*
   * ---------------------------------------------------------
   * LOADING STATE
   * ---------------------------------------------------------
   */

  if (!investigation) {
    return (
      <div className="boot-screen">
        <div className="boot-card">
          <div className="brand-mark">
            CT
          </div>

          <div>
            <div className="eyebrow">
              CRYPTOTRACE AI
            </div>

            <h1>
              Initializing investigation
              workspace
            </h1>

            <p>
              {backendOnline
                ? "Loading evidence graph…"
                : "Backend connection unavailable."}
            </p>
          </div>

          <div className="boot-line">
            <span />
          </div>
        </div>
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * MAIN APPLICATION
   * ---------------------------------------------------------
   */

  return (
    <main className="app-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />

      {/* =====================================================
          TOP BAR
          ===================================================== */}

      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            CT
          </div>

          <div>
            <div className="brand-name">
              CRYPTOTRACE{" "}
              <span>AI</span>
            </div>

            <div className="brand-subtitle">
              DIGITAL ASSET FORENSICS //
              INVESTIGATION CONSOLE
            </div>
          </div>
        </div>

        <div className="topbar-right">
          <div
            className={`connection-pill ${
              backendOnline
                ? "online"
                : "offline"
            }`}
          >
            <span className="status-dot" />

            {backendOnline
              ? "BACKEND ONLINE"
              : "BACKEND OFFLINE"}
          </div>

          <div className="case-pill">
            <span>CASE</span>

            <strong>
              {investigation.id}
            </strong>
          </div>
        </div>
      </header>

      {/* =====================================================
          HERO
          ===================================================== */}

      <section className="hero-row">
        <div>
          <div className="eyebrow">
            ACTIVE INVESTIGATION
          </div>

          <h1 className="hero-title">
            Trace the money.
            <br />
            <span>Expose the path.</span>
          </h1>

          <p className="hero-copy">
            Evidence-first transaction
            reconstruction with deterministic
            risk analysis and an
            evidence-grounded investigation
            Copilot.
          </p>
        </div>

        <div className="target-card">
          <div className="card-label">
            INVESTIGATION TARGET
          </div>

          <div className="target-name">
            {investigation.wallet.label}
          </div>

          <code>
            {shortHash(
              investigation.wallet.address,
              14,
              10,
            )}
          </code>

          <div className="target-meta">
            <span>ETH NETWORK</span>
            <span>•</span>
            <span>
              {investigation.nodes.length}{" "}
              WALLET NODES
            </span>
            <span>•</span>
            <span>
              {investigation.edges.length}{" "}
              TRANSFERS
            </span>
          </div>
        </div>
      </section>

      {/* =====================================================
          METRICS
          ===================================================== */}

      <section className="metric-grid">
        <div className="metric-card risk-card">
          <div className="metric-top">
            <span>RISK SCORE</span>

            <span className="metric-live">
              DETERMINISTIC
            </span>
          </div>

          <div className="metric-value risk-value">
            {investigation.risk.score}
            <small>/100</small>
          </div>

          <div className="metric-foot">
            <span className="risk-dot" />

            {investigation.risk.level.toUpperCase()}{" "}
            RISK
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>OBSERVED FLOW</span>
            <span>REPLAY</span>
          </div>

          <div className="metric-value">
            {formatAmount(
              currentEdge?.amount ?? 0,
              currentEdge?.asset ?? "ETH",
            )}
          </div>

          <div className="metric-foot">
            {currentEdge
              ? `${currentEdge.source} → ${currentEdge.target}`
              : "Awaiting trace"}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>TRACE WINDOW</span>
            <span>UTC</span>
          </div>

          <div className="metric-value">
            {elapsedMinutes.toFixed(0)}
            <small> min</small>
          </div>

          <div className="metric-foot">
            {currentEdge
              ? formatTime(
                  currentEdge.timestamp,
                )
              : "—"}
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-top">
            <span>
              SUSPICIOUS HOPS
            </span>

            <span>FLAGGED</span>
          </div>

          <div className="metric-value">
            {suspiciousCount}
            <small>
              /{visibleEdges.length || 0}
            </small>
          </div>

          <div className="metric-foot">
            Evidence-linked observations
          </div>
        </div>
      </section>

      {/* =====================================================
          MAIN WORKSPACE
          ===================================================== */}

      <section className="workspace-grid">
        {/* ===================================================
            GRAPH COLUMN
            =================================================== */}

        <div className="graph-column">
          <div className="panel-heading">
            <div>
              <div className="eyebrow">
                NETWORK RECONSTRUCTION
              </div>

              <h2>
                Transaction Universe
              </h2>
            </div>

            <div className="legend">
              <span>
                <i className="legend-dot target" />
                TARGET
              </span>

              <span>
                <i className="legend-dot intermediary" />
                INTERMEDIARY
              </span>

              <span>
                <i className="legend-dot exchange" />
                CANDIDATE EXCHANGE
              </span>
            </div>
          </div>

          <TransactionGraph
            investigation={investigation}
            onEvidenceSelect={
              setSelectedEvidenceIds
            }
            onNodeSelect={
              handleNodeSelect
            }
            onTransactionSelect={
              handleEdgeSelect
            }
            onTraceStep={
              handleTraceStep
            }
          />

          {/* ===============================================
              GRAPH TELEMETRY
              =============================================== */}

          <div className="telemetry-grid">
            <div className="telemetry-card">
              <div className="telemetry-label">
                CURRENT TRANSFER
              </div>

              <div className="telemetry-route">
                <span>
                  {currentEdge?.source ??
                    "—"}
                </span>

                <b>→</b>

                <span>
                  {currentEdge?.target ??
                    "—"}
                </span>
              </div>

              <div className="telemetry-amount">
                {currentEdge
                  ? formatAmount(
                      currentEdge.amount,
                      currentEdge.asset,
                    )
                  : "—"}
              </div>

              <div className="telemetry-hash">
                {currentEdge
                  ? currentEdge.transactionId
                  : "No transaction selected"}
              </div>
            </div>

            <div className="telemetry-card">
              <div className="telemetry-label">
                TRACE STATE
              </div>

              <div className="state-row">
                <span>
                  Observed value
                </span>

                <strong>
                  {formatAmount(
                    totalObserved,
                    "ETH",
                  )}
                </strong>
              </div>

              <div className="state-row">
                <span>Hop</span>

                <strong>
                  {currentIndex + 1} /{" "}
                  {sortedEdges.length}
                </strong>
              </div>

              <div className="state-row">
                <span>
                  Evidence linked
                </span>

                <strong>
                  {currentEdge
                    ?.evidenceIds
                    ?.length ?? 0}
                </strong>
              </div>
            </div>
          </div>
        </div>

        {/* ===================================================
            SIDE COLUMN
            =================================================== */}

        <aside className="side-column">
          {/* RISK */}
          <RiskPanel
            risk={investigation.risk}
          />

          {/* ===============================================
              ATTRIBUTION
              =============================================== */}

          <div className="attribution-panel panel">
            <div className="panel-title-row">
              <div>
                <div className="eyebrow">
                  ENTITY INTELLIGENCE
                </div>

                <h3>
                  Attribution
                </h3>
              </div>

              <span className="confidence-badge">
                CANDIDATE
              </span>
            </div>

            {investigation.attribution.map(
              (item) => (
                <div
                  className="attribution-item"
                  key={item.entityName}
                >
                  <div className="entity-icon">
                    ◎
                  </div>

                  <div className="entity-copy">
                    <strong>
                      {item.entityName}
                    </strong>

                    <span>
                      {Math.round(
                        item.confidence *
                          100,
                      )}
                      % confidence ·{" "}
                      {item.status}
                    </span>

                    <small>
                      Evidence:{" "}
                      {item.evidenceIds.join(
                        ", ",
                      )}
                    </small>
                  </div>
                </div>
              ),
            )}

            <div className="disclaimer">
              Attribution is a candidate
              inference, not a confirmed
              identity.
            </div>
          </div>

          {/* ===============================================
              COPILOT
              =============================================== */}

          <div className="copilot panel">
            <div className="panel-title-row">
              <div>
                <div className="eyebrow">
                  NEMOTRON-READY
                </div>

                <h3>
                  Investigation Copilot
                </h3>
              </div>

              <span className="ai-orb">
                ✦
              </span>
            </div>

            <div className="quick-prompts">
              {[
                "Why is this investigation high risk?",
                "Explain the transaction flow.",
                "What evidence supports the exchange attribution?",
              ].map((prompt) => (
                <button
                  key={prompt}
                  onClick={() =>
                    void handleSubmitQuestion(
                      prompt,
                    )
                  }
                >
                  {prompt}
                </button>
              ))}
            </div>

            <div className="copilot-input">
              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value,
                  )
                }
                placeholder="Ask about the case, risk, flow or evidence…"
                onKeyDown={(event) => {
                  if (
                    event.key ===
                      "Enter" &&
                    (event.ctrlKey ||
                      event.metaKey)
                  ) {
                    void handleSubmitQuestion();
                  }
                }}
              />

              <button
                className="send-button"
                disabled={
                  loadingQuestion ||
                  !question.trim()
                }
                onClick={() =>
                  void handleSubmitQuestion()
                }
              >
                {loadingQuestion
                  ? "ANALYZING…"
                  : "ASK COPILOT  ↗"}
              </button>
            </div>

            {answer && (
              <div className="copilot-answer">
                <div className="answer-header">
                  <span>
                    ANALYSIS
                  </span>

                  <span>
                    GROUNDED
                  </span>
                </div>

                <div className="answer-body">
                  {answer}
                </div>
              </div>
            )}
          </div>
        </aside>
      </section>

      {/* =====================================================
          EVIDENCE LEDGER
          ===================================================== */}

      <section className="evidence-section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">
              CHAIN OF CUSTODY
            </div>

            <h2>
              Evidence Ledger
            </h2>
          </div>

          <div className="evidence-count">
            {selectedEvidenceIds.length >
            0
              ? `${selectedEvidenceIds.length} SELECTED`
              : `${investigation.evidence.length} IMMUTABLE RECORDS`}
          </div>
        </div>

        <EvidencePanel
          evidence={
            investigation.evidence
          }
          selectedEvidenceIds={
            selectedEvidenceIds
          }
        />
      </section>

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="footer">
        <span>
          CRYPTOTRACE AI · INVESTIGATION
          CONSOLE
        </span>

        <span>
          Evidence-first · Deterministic
          risk · Human-verifiable
          attribution
        </span>
      </footer>
    </main>
  );
}

export default App;