import { useState, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Grid } from "@react-three/drei";

// ─── SLIDER ──────────────────────────────────────────────────────────────────
function Slider({ label, value, min, max, step = 0.01, onChange, color }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 11, letterSpacing: "0.08em", color: "#aaa", textTransform: "uppercase" }}>{label}</span>
        <span style={{ fontSize: 11, fontFamily: "monospace", color: color || "#fff" }}>{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{
          width: "100%",
          accentColor: color || "#4af",
          cursor: "pointer",
          height: 4,
        }}
      />
    </div>
  );
}

// ─── SCENE CONTENT ────────────────────────────────────────────────────────────
function Scene({ parent }) {
  const groupRef = useRef();

  return (
    <>
      {/* Grid helper */}
      <Grid
        args={[20, 20]}
        position={[0, -2, 0]}
        cellColor="#334"
        sectionColor="#445"
        fadeDistance={30}
        infiniteGrid
      />

      {/* Ambient + directional light */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={1.2} castShadow />
      <pointLight position={[-5, 5, -5]} intensity={0.6} color="#4af" />

      {/* ── FATHER GROUP ── */}
      <group
        ref={groupRef}
        position={[parent.px, parent.py, parent.pz]}
        rotation={[parent.rx, parent.ry, parent.rz]}
        scale={parent.scale}
      >
        {/* Father mesh – central cube */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="#4af" metalness={0.4} roughness={0.3} />
        </mesh>

        {/* Axis lines to visualise orientation */}
        <arrowHelper args={[undefined, undefined, 1.2, 0xff4444]} />

        {/* ── CHILD 1 – sphere (right) ── */}
        <group position={[2.2, 0, 0]}>
          <mesh castShadow>
            <sphereGeometry args={[0.5, 32, 32]} />
            <meshStandardMaterial color="#f84" metalness={0.2} roughness={0.5} />
          </mesh>
          {/* grandchild – tiny ring */}
          <mesh position={[0, 1.1, 0]} rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[0.3, 0.06, 16, 40]} />
            <meshStandardMaterial color="#ffd" emissive="#ffd" emissiveIntensity={0.3} />
          </mesh>
        </group>

        {/* ── CHILD 2 – cone (left) ── */}
        <group position={[-2.2, 0, 0]}>
          <mesh castShadow>
            <coneGeometry args={[0.5, 1, 32]} />
            <meshStandardMaterial color="#a4f" metalness={0.3} roughness={0.4} />
          </mesh>
          {/* grandchild – small cube */}
          <mesh position={[0, -1.2, 0]}>
            <boxGeometry args={[0.3, 0.3, 0.3]} />
            <meshStandardMaterial color="#fff" emissive="#fff" emissiveIntensity={0.2} />
          </mesh>
        </group>

        {/* ── CHILD 3 – torus (top) ── */}
        <group position={[0, 2.2, 0]}>
          <mesh castShadow>
            <torusGeometry args={[0.5, 0.18, 16, 50]} />
            <meshStandardMaterial color="#4f8" metalness={0.5} roughness={0.2} />
          </mesh>
        </group>

        {/* ── CHILD 4 – cylinder (front) ── */}
        <group position={[0, 0, 2.2]}>
          <mesh castShadow>
            <cylinderGeometry args={[0.3, 0.5, 1, 32]} />
            <meshStandardMaterial color="#f4a" metalness={0.3} roughness={0.5} />
          </mesh>
        </group>
      </group>
    </>
  );
}

// ─── PANEL ────────────────────────────────────────────────────────────────────
function Panel({ title, color, children }) {
  return (
    <div style={{
      marginBottom: 18,
      background: "rgba(255,255,255,0.04)",
      borderRadius: 8,
      padding: "12px 14px",
      border: `1px solid ${color}33`,
    }}>
      <div style={{
        fontSize: 10,
        letterSpacing: "0.15em",
        textTransform: "uppercase",
        color,
        marginBottom: 12,
        fontWeight: 700,
      }}>{title}</div>
      {children}
    </div>
  );
}

// ─── APP ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [parent, setParent] = useState({
    px: 0, py: 0, pz: 0,
    rx: 0, ry: 0, rz: 0,
    scale: 1,
  });

  const set = (key) => (val) => setParent((p) => ({ ...p, [key]: val }));

  return (
    <div style={{
      display: "flex",
      height: "100vh",
      width: "100vw",
      background: "#0b0d12",
      fontFamily: "'Courier New', monospace",
      color: "#eee",
      overflow: "hidden",
    }}>
      {/* ── CONTROLS PANEL ── */}
      <div style={{
        width: 280,
        minWidth: 280,
        padding: "20px 16px",
        background: "#0e1018",
        borderRight: "1px solid #1e2230",
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        gap: 4,
      }}>
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: "0.06em", color: "#fff" }}>
            Scene Hierarchy
          </div>
          <div style={{ fontSize: 10, color: "#556", marginTop: 4, letterSpacing: "0.05em" }}>
            TRANSFORM FATHER → CHILDREN FOLLOW
          </div>
        </div>

        {/* Hierarchy tree */}
        <div style={{
          background: "#070910",
          borderRadius: 6,
          padding: "10px 12px",
          marginBottom: 16,
          fontSize: 11,
          lineHeight: 1.9,
          color: "#789",
          border: "1px solid #1a1e2a",
        }}>
          <div style={{ color: "#4af" }}>▸ &lt;group&gt; Father</div>
          <div style={{ paddingLeft: 14 }}>├ &lt;mesh&gt; Cube <span style={{ color: "#f84" }}>●</span></div>
          <div style={{ paddingLeft: 14 }}>├ &lt;group&gt; Child Sphere</div>
          <div style={{ paddingLeft: 28 }}>└ &lt;mesh&gt; Ring <span style={{ color: "#ffd" }}>●</span></div>
          <div style={{ paddingLeft: 14 }}>├ &lt;group&gt; Child Cone</div>
          <div style={{ paddingLeft: 28 }}>└ &lt;mesh&gt; Cube <span style={{ color: "#fff" }}>●</span></div>
          <div style={{ paddingLeft: 14 }}>├ &lt;group&gt; Child Torus <span style={{ color: "#4f8" }}>●</span></div>
          <div style={{ paddingLeft: 14 }}>└ &lt;group&gt; Child Cylinder <span style={{ color: "#f4a" }}>●</span></div>
        </div>

        {/* Translation */}
        <Panel title="Translation (Father)" color="#4af">
          <Slider label="Position X" value={parent.px} min={-5} max={5} onChange={set("px")} color="#4af" />
          <Slider label="Position Y" value={parent.py} min={-5} max={5} onChange={set("py")} color="#4af" />
          <Slider label="Position Z" value={parent.pz} min={-5} max={5} onChange={set("pz")} color="#4af" />
        </Panel>

        {/* Rotation */}
        <Panel title="Rotation (Father)" color="#f84">
          <Slider label="Rotate X" value={parent.rx} min={-Math.PI} max={Math.PI} onChange={set("rx")} color="#f84" />
          <Slider label="Rotate Y" value={parent.ry} min={-Math.PI} max={Math.PI} onChange={set("ry")} color="#f84" />
          <Slider label="Rotate Z" value={parent.rz} min={-Math.PI} max={Math.PI} onChange={set("rz")} color="#f84" />
        </Panel>

        {/* Scale */}
        <Panel title="Scale (Father)" color="#4f8">
          <Slider label="Uniform Scale" value={parent.scale} min={0.1} max={3} onChange={set("scale")} color="#4f8" />
        </Panel>

        {/* Reset */}
        <button
          onClick={() => setParent({ px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0, scale: 1 })}
          style={{
            marginTop: 8,
            padding: "9px 0",
            background: "transparent",
            border: "1px solid #334",
            color: "#778",
            borderRadius: 6,
            cursor: "pointer",
            fontSize: 11,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            transition: "all 0.2s",
          }}
          onMouseOver={(e) => { e.target.style.borderColor = "#4af"; e.target.style.color = "#4af"; }}
          onMouseOut={(e) => { e.target.style.borderColor = "#334"; e.target.style.color = "#778"; }}
        >
          Reset All
        </button>

        <div style={{ marginTop: "auto", paddingTop: 20, fontSize: 9, color: "#334", lineHeight: 1.8 }}>
          Drag the 3D scene to orbit.<br />
          Scroll to zoom.
        </div>
      </div>

      {/* ── 3D CANVAS ── */}
      <div style={{ flex: 1, position: "relative" }}>
        {/* Overlay labels */}
        <div style={{
          position: "absolute", top: 16, left: 16, zIndex: 10,
          fontSize: 10, color: "#445", letterSpacing: "0.1em",
          textTransform: "uppercase",
          lineHeight: 2,
        }}>
          <div><span style={{ color: "#4af" }}>■</span> Father (cube)</div>
          <div><span style={{ color: "#f84" }}>■</span> Child — Sphere + Ring</div>
          <div><span style={{ color: "#a4f" }}>■</span> Child — Cone + Cube</div>
          <div><span style={{ color: "#4f8" }}>■</span> Child — Torus</div>
          <div><span style={{ color: "#f4a" }}>■</span> Child — Cylinder</div>
        </div>

        <Canvas
          camera={{ position: [6, 5, 8], fov: 50 }}
          shadows
          style={{ background: "#0b0d12" }}
        >
          <fog attach="fog" args={["#0b0d12", 20, 40]} />
          <Scene parent={parent} />
          <OrbitControls makeDefault />
        </Canvas>
      </div>
    </div>
  );
}
