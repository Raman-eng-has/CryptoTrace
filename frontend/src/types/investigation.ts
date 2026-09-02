export type RiskLevel = "low" | "medium" | "high" | "critical";

export type EvidenceType =
  | "transaction"
  | "address"
  | "attribution"
  | "risk_signal";

export interface Wallet {
  id: string;
  address: string;
  label: string;
  role: "target" | "intermediary" | "exchange" | "unknown";
}

export interface GraphNode {
  id: string;
  walletId: string;
  label: string;
  role: Wallet["role"];
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  transactionId: string;
  amount: number;
  asset: string;
  timestamp: string;
  suspicious?: boolean;
  evidenceIds: string[];
}

export interface Evidence {
  id: string;
  type: EvidenceType;
  title: string;
  description: string;
  source: string;
  timestamp?: string;
  immutable: boolean;
}

export interface RiskFactor {
  id: string;
  name: string;
  contribution: number;
  explanation: string;
  evidenceIds: string[];
}

export interface RiskResult {
  score: number;
  level: RiskLevel;
  factors: RiskFactor[];
}

export interface Attribution {
  entityName: string;
  confidence: number;
  status: "candidate" | "confirmed" | "unresolved";
  evidenceIds: string[];
}

export interface Investigation {
  id: string;
  createdAt: string;
  wallet: Wallet;
  nodes: GraphNode[];
  edges: GraphEdge[];
  evidence: Evidence[];
  risk: RiskResult;
  attribution: Attribution[];
}
