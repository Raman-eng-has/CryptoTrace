import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  Billboard,
  Html,
  Line,
  OrbitControls,
  PerspectiveCamera,
  Stars,
  Text,
} from "@react-three/drei";
import * as THREE from "three";
import type { GraphEdge, Investigation } from "../types/investigation";

interface TransactionGraphProps {
  investigation: Investigation;
  onEvidenceSelect?: (evidenceIds: string[]) => void;
  onNodeSelect?: (nodeId: string | null) => void;
  onTransactionSelect?: (edgeId: string) => void;
  onTraceStep?: (edge: GraphEdge | null) => void;
}

type Position = { x: number; y: number; z: number };

const C = {
  bg: "#020617",
  cyan: "#22d3ee",
  cyanSoft: "#67e8f9",
  red: "#fb3b55",
  purple: "#a78bfa",
  blue: "#60a5fa",
  white: "#f8fafc",
  muted: "#64748b",
  grid: "#1e293b",
};

const PLAYBACK_MS = 1700;

function positionFor(index: number, nodes: Investigation["nodes"]): Position {
  const node = nodes[index];
  if (!node) return { x: 0, y: 0, z: 0 };
  if (node.role === "target") return { x: -7.2, y: 0, z: 0 };
  if (node.role === "exchange") return { x: 7.2, y: 0, z: 0 };

  const intermediaries = nodes.filter((item) => item.role === "intermediary");
  const i = intermediaries.findIndex((item) => item.id === node.id);
  const spread = Math.max(intermediaries.length - 1, 1);

  return {
    x: -3.7 + (i / spread) * 7.4,
    y: Math.sin(i * 1.55) * 1.45,
    z: Math.cos(i * 1.25) * 1.25,
  };
}

function roleColor(role: string) {
  if (role === "target") return C.red;
  if (role === "exchange") return C.blue;
  return C.purple;
}

function roleLabel(role: string) {
  if (role === "target") return "TARGET";
  if (role === "exchange") return "CANDIDATE EXCHANGE";
  return "INTERMEDIARY";
}

function amountLabel(edge: GraphEdge) {
  return `${edge.amount.toFixed(2)} ${edge.asset}`;
}

function timeLabel(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return timestamp;
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function FlowParticle({
  start,
  end,
  active,
  suspicious,
  phase,
}: {
  start: Position;
  end: Position;
  active: boolean;
  suspicious: boolean;
  phase: number;
}) {
  const ref = useRef<THREE.Mesh>(null);
  const progress = useRef(phase);

  useFrame((_, delta) => {
    if (!ref.current) return;
    progress.current = (progress.current + delta * (active ? 0.8 : 0.24)) % 1;
    const t = progress.current;

    ref.current.position.set(
      start.x + (end.x - start.x) * t,
      start.y + (end.y - start.y) * t,
      start.z + (end.z - start.z) * t,
    );
    ref.current.scale.setScalar(active ? 1.7 : 0.85);
  });

  return (
    <mesh ref={ref} position={[start.x, start.y, start.z]}>
      <sphereGeometry args={[active ? 0.09 : 0.055, 12, 12]} />
      <meshBasicMaterial
        color={suspicious ? C.red : C.cyanSoft}
        transparent
        opacity={active ? 1 : 0.65}
      />
    </mesh>
  );
}

function WalletNode({
  node,
  position,
  selected,
  active,
  hovered,
  showLabels,
  onSelect,
  onHover,
}: {
  node: Investigation["nodes"][number];
  position: Position;
  selected: boolean;
  active: boolean;
  hovered: boolean;
  showLabels: boolean;
  onSelect: () => void;
  onHover: (value: boolean) => void;
}) {
  const group = useRef<THREE.Group>(null);
  const color = roleColor(node.role);

  useFrame(({ clock }) => {
    if (!group.current) return;
    const pulse = 1 + Math.sin(clock.elapsedTime * (node.role === "target" ? 4 : 2.2)) * 0.035;
    const focus = selected || active || hovered ? 1.16 : 1;
    group.current.scale.setScalar(pulse * focus);
    group.current.rotation.y += active ? 0.004 : 0.001;
  });

  return (
    <group
      ref={group}
      position={[position.x, position.y, position.z]}
      onClick={(event) => {
        event.stopPropagation();
        onSelect();
      }}
      onPointerOver={(event) => {
        event.stopPropagation();
        onHover(true);
        document.body.style.cursor = "pointer";
      }}
      onPointerOut={() => {
        onHover(false);
        document.body.style.cursor = "default";
      }}
    >
      <mesh>
        <sphereGeometry args={[selected || active ? 1.02 : 0.84, 32, 32]} />
        <meshBasicMaterial color={color} transparent opacity={selected || active ? 0.16 : 0.055} />
      </mesh>

      <mesh>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={selected || active ? 1.1 : 0.38}
          metalness={0.75}
          roughness={0.2}
        />
      </mesh>

      <mesh>
        <sphereGeometry args={[0.19, 20, 20]} />
        <meshBasicMaterial color={C.white} />
      </mesh>

      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.7, active ? 0.045 : 0.025, 12, 64]} />
        <meshBasicMaterial color={color} transparent opacity={0.9} />
      </mesh>

      {active && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[1.05, 0.018, 10, 64]} />
          <meshBasicMaterial color={C.white} transparent opacity={0.75} />
        </mesh>
      )}

      {showLabels && (
        <Billboard position={[0, 1.18, 0]}>
          <Text
            fontSize={0.24}
            color={C.white}
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.012}
            outlineColor={C.bg}
          >
            {node.label}
          </Text>
          <Text
            position={[0, -0.3, 0]}
            fontSize={0.12}
            color={color}
            anchorX="center"
            anchorY="middle"
          >
            {roleLabel(node.role)}
          </Text>
        </Billboard>
      )}

      {hovered && (
        <Html position={[0, 1.75, 0]} center distanceFactor={9}>
          <div className="graph-tooltip">
            <strong>{node.label}</strong>
            <span>{roleLabel(node.role)}</span>
            <small>{node.walletId}</small>
          </div>
        </Html>
      )}
    </group>
  );
}

function TransactionEdge({
  edge,
  start,
  end,
  active,
  selected,
  onSelect,
}: {
  edge: GraphEdge;
  start: Position;
  end: Position;
  active: boolean;
  selected: boolean;
  onSelect: () => void;
}) {
  const midpoint = useMemo(
    () => ({
      x: (start.x + end.x) / 2,
      y: (start.y + end.y) / 2,
      z: (start.z + end.z) / 2,
    }),
    [start, end],
  );

  const direction = useMemo(
    () =>
      new THREE.Vector3(
        end.x - start.x,
        end.y - start.y,
        end.z - start.z,
      ),
    [start, end],
  );

  const quaternion = useMemo(() => {
    const q = new THREE.Quaternion();
    q.setFromUnitVectors(
      new THREE.Vector3(0, 1, 0),
      direction.clone().normalize(),
    );
    return q;
  }, [direction]);

  const suspicious = edge.suspicious ?? false;
  const color = active || selected ? C.white : suspicious ? C.red : C.cyan;
  const width = active ? 5 : selected ? 4 : suspicious ? 3 : 1.7;

  return (
    <group>
      <mesh
        position={[midpoint.x, midpoint.y, midpoint.z]}
        quaternion={quaternion}
        onClick={(event) => {
          event.stopPropagation();
          onSelect();
        }}
        onPointerOver={() => {
          document.body.style.cursor = "crosshair";
        }}
        onPointerOut={() => {
          document.body.style.cursor = "default";
        }}
      >
        <cylinderGeometry args={[0.18, 0.18, direction.length(), 8]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>

      <Line
        points={[
          [start.x, start.y, start.z],
          [end.x, end.y, end.z],
        ]}
        color={color}
        lineWidth={width}
        transparent
        opacity={active || selected ? 1 : suspicious ? 0.9 : 0.58}
      />

      <mesh
        position={[
          end.x * 0.88 + start.x * 0.12,
          end.y * 0.88 + start.y * 0.12,
          end.z * 0.88 + start.z * 0.12,
        ]}
        quaternion={quaternion}
      >
        <coneGeometry args={[0.14, 0.34, 8]} />
        <meshBasicMaterial color={color} />
      </mesh>

      {Array.from({ length: active ? 5 : 2 }).map((_, index) => (
        <FlowParticle
          key={`${edge.id}-particle-${index}`}
          start={start}
          end={end}
          active={active}
          suspicious={suspicious}
          phase={index / (active ? 5 : 2)}
        />
      ))}

      <Billboard position={[midpoint.x, midpoint.y + 0.48, midpoint.z]}>
        <Text
          fontSize={active ? 0.22 : 0.16}
          color={color}
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.008}
          outlineColor={C.bg}
        >
          {amountLabel(edge)}
        </Text>
        {active && (
          <Text
            position={[0, -0.25, 0]}
            fontSize={0.105}
            color={C.muted}
            anchorX="center"
            anchorY="middle"
          >
            {timeLabel(edge.timestamp)}
          </Text>
        )}
      </Billboard>
    </group>
  );
}

function Scene({
  investigation,
  selectedNodeId,
  selectedEdgeId,
  activeEdgeId,
  showLabels,
  hoveredNodeId,
  onNodeSelect,
  onNodeHover,
  onEdgeSelect,
}: {
  investigation: Investigation;
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  activeEdgeId: string | null;
  showLabels: boolean;
  hoveredNodeId: string | null;
  onNodeSelect: (id: string | null) => void;
  onNodeHover: (id: string | null) => void;
  onEdgeSelect: (id: string) => void;
}) {
  const positions = useMemo(() => {
    const result = new Map<string, Position>();
    investigation.nodes.forEach((node, index) => {
      result.set(node.id, positionFor(index, investigation.nodes));
    });
    return result;
  }, [investigation.nodes]);

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 3.5, 15.5]} fov={48} />
      <ambientLight intensity={0.5} />
      <pointLight position={[0, 5, 7]} intensity={24} distance={30} />
      <pointLight position={[-7, 0, 4]} intensity={16} distance={16} color={C.red} />
      <pointLight position={[7, 0, 4]} intensity={16} distance={16} color={C.blue} />

      <Stars radius={45} depth={24} count={900} factor={1.2} saturation={0} fade speed={0.35} />

      <gridHelper
        args={[32, 32, C.grid, "#0b1220"]}
        position={[0, -2.65, 0]}
      />

      {investigation.edges.map((edge) => {
        const start = positions.get(edge.source);
        const end = positions.get(edge.target);
        if (!start || !end) return null;

        return (
          <TransactionEdge
            key={edge.id}
            edge={edge}
            start={start}
            end={end}
            active={edge.id === activeEdgeId}
            selected={edge.id === selectedEdgeId}
            onSelect={() => onEdgeSelect(edge.id)}
          />
        );
      })}

      {investigation.nodes.map((node) => {
        const position = positions.get(node.id);
        if (!position) return null;

        const active = investigation.edges.some(
          (edge) =>
            edge.id === activeEdgeId &&
            (edge.source === node.id || edge.target === node.id),
        );

        return (
          <WalletNode
            key={node.id}
            node={node}
            position={position}
            selected={node.id === selectedNodeId}
            active={active}
            hovered={node.id === hoveredNodeId}
            showLabels={showLabels}
            onSelect={() => onNodeSelect(node.id)}
            onHover={(value) => onNodeHover(value ? node.id : null)}
          />
        );
      })}

      <OrbitControls
        enableDamping
        dampingFactor={0.08}
        minDistance={7}
        maxDistance={28}
        rotateSpeed={0.55}
        zoomSpeed={0.8}
        panSpeed={0.6}
        autoRotate
        autoRotateSpeed={0.25}
      />
    </>
  );
}

export function TransactionGraph({
  investigation,
  onEvidenceSelect,
  onNodeSelect,
  onTransactionSelect,
  onTraceStep,
}: TransactionGraphProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [playbackIndex, setPlaybackIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [showLabels, setShowLabels] = useState(true);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  const sortedEdges = useMemo(
    () =>
      [...investigation.edges].sort(
        (a, b) =>
          new Date(a.timestamp).getTime() -
          new Date(b.timestamp).getTime(),
      ),
    [investigation.edges],
  );

  const activeEdge = sortedEdges[playbackIndex] ?? null;

  useEffect(() => {
    if (!playing || sortedEdges.length === 0) return;

    const timer = window.setInterval(() => {
      setPlaybackIndex((current) => {
        if (current >= sortedEdges.length - 1) {
          setPlaying(false);
          return current;
        }
        return current + 1;
      });
    }, PLAYBACK_MS);

    return () => window.clearInterval(timer);
  }, [playing, sortedEdges.length]);

  useEffect(() => {
    onTraceStep?.(activeEdge);
  }, [activeEdge, onTraceStep]);

  useEffect(() => {
    setPlaybackIndex(0);
    setPlaying(false);
    setSelectedEdgeId(null);
    setSelectedNodeId(null);
  }, [investigation.id]);

  const selectEdge = (edgeId: string) => {
    const edge = investigation.edges.find((item) => item.id === edgeId);
    if (!edge) return;

    setSelectedEdgeId(edgeId);
    setSelectedNodeId(null);
    setPlaybackIndex(Math.max(sortedEdges.findIndex((item) => item.id === edgeId), 0));
    onEvidenceSelect?.(edge.evidenceIds ?? []);
    onNodeSelect?.(null);
    onTransactionSelect?.(edgeId);
    onTraceStep?.(edge);
  };

  const selectNode = (nodeId: string | null) => {
    setSelectedNodeId(nodeId);
    setSelectedEdgeId(null);
    onNodeSelect?.(nodeId);

    if (!nodeId) {
      onEvidenceSelect?.([]);
      return;
    }

    const evidence = investigation.edges
      .filter((edge) => edge.source === nodeId || edge.target === nodeId)
      .flatMap((edge) => edge.evidenceIds ?? []);

    onEvidenceSelect?.([...new Set(evidence)]);
  };

  const start = () => {
    if (!sortedEdges.length) return;
    if (playbackIndex >= sortedEdges.length - 1) setPlaybackIndex(0);
    setPlaying(true);
  };

  const reset = () => {
    setPlaying(false);
    setPlaybackIndex(0);
    setSelectedEdgeId(null);
    onTraceStep?.(sortedEdges[0] ?? null);
  };

  const step = (direction: 1 | -1) => {
    setPlaying(false);
    setPlaybackIndex((current) =>
      Math.min(
        Math.max(current + direction, 0),
        Math.max(sortedEdges.length - 1, 0),
      ),
    );
  };

  if (!investigation.nodes.length) {
    return <div className="graph-empty">No transaction graph data available.</div>;
  }

  return (
    <div className="trace-canvas">
      <div className="trace-hud">
        <div>
          <div className="trace-title">3D TRANSACTION UNIVERSE</div>
          <div className="trace-subtitle">
            {investigation.nodes.length} wallets · {investigation.edges.length} transfers · evidence-linked
          </div>
        </div>
        <div className={`replay-state ${playing ? "active" : ""}`}>
          <span />
          {playing ? "TRACE REPLAY ACTIVE" : "TRACE READY"}
        </div>
      </div>

      <Canvas
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        onPointerMissed={() => {
          selectNode(null);
          setSelectedEdgeId(null);
          onTransactionSelect?.("");
        }}
      >
        <Scene
          investigation={investigation}
          selectedNodeId={selectedNodeId}
          selectedEdgeId={selectedEdgeId}
          activeEdgeId={playing || activeEdge ? activeEdge.id : null}
          showLabels={showLabels}
          hoveredNodeId={hoveredNodeId}
          onNodeSelect={selectNode}
          onNodeHover={setHoveredNodeId}
          onEdgeSelect={selectEdge}
        />
      </Canvas>

      <div className="trace-help">DRAG ROTATE · SCROLL ZOOM · CLICK NODE / TRANSFER</div>

      {activeEdge && (
        <div className="active-transfer">
          <div className="active-transfer-label">ACTIVE TRANSFER</div>
          <strong>{activeEdge.source} <span>→</span> {activeEdge.target}</strong>
          <div>
            {amountLabel(activeEdge)} · {timeLabel(activeEdge.timestamp)}
            {activeEdge.suspicious ? <b className="danger-text"> · SUSPICIOUS</b> : ""}
          </div>
        </div>
      )}

      <div className="trace-controls">
        <div className="trace-control-top">
          <div>
            <span className="eyebrow">TRACE TIMELINE</span>
            <b>{sortedEdges.length ? `${playbackIndex + 1} / ${sortedEdges.length}` : "0 / 0"}</b>
          </div>
          <div className="trace-buttons">
            <button title="Previous transaction" onClick={() => step(-1)}>‹</button>
            <button className="primary-control" title={playing ? "Pause" : "Play"} onClick={() => playing ? setPlaying(false) : start()}>
              {playing ? "Ⅱ" : "▶"}
            </button>
            <button title="Next transaction" onClick={() => step(1)}>›</button>
            <button title="Reset" onClick={reset}>↺</button>
          </div>
          <button className={`label-toggle ${showLabels ? "on" : ""}`} onClick={() => setShowLabels((value) => !value)}>
            {showLabels ? "LABELS ON" : "LABELS OFF"}
          </button>
        </div>

        <div className="trace-track">
          <div className="trace-track-line" />
          {sortedEdges.map((edge, index) => {
            const left = sortedEdges.length <= 1 ? 0 : (index / (sortedEdges.length - 1)) * 100;
            const active = index === playbackIndex;
            return (
              <button
                key={edge.id}
                className={`trace-stop ${active ? "active" : ""} ${edge.suspicious ? "suspicious" : ""}`}
                style={{ left: `${left}%` }}
                title={`${amountLabel(edge)} · ${timeLabel(edge.timestamp)}`}
                onClick={() => {
                  setPlaying(false);
                  setPlaybackIndex(index);
                  selectEdge(edge.id);
                }}
              />
            );
          })}
        </div>

        <div className="trace-times">
          <span>{sortedEdges[0] ? timeLabel(sortedEdges[0].timestamp) : "—"}</span>
          <span>{activeEdge ? timeLabel(activeEdge.timestamp) : "—"}</span>
          <span>{sortedEdges[sortedEdges.length - 1] ? timeLabel(sortedEdges[sortedEdges.length - 1].timestamp) : "—"}</span>
        </div>
      </div>
    </div>
  );
}
