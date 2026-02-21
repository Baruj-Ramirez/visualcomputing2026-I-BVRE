import { useState, useRef, useEffect, Suspense, useMemo } from "react";
import { Canvas, useFrame, useThree, useLoader } from "@react-three/fiber";
import { OrbitControls, useGLTF, Grid, Environment } from "@react-three/drei";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";

// ─── Procedural Model Generators ────────────────────────────────────────────
// Since we can't load real files in this sandbox, we generate representative
// geometry that mirrors what each format would produce.

function createOBJGeometry() {
  // OBJ: flat-shaded, faceted look — uses indexed geometry with sharp normals
  const geo = new THREE.IcosahedronGeometry(1.2, 1); // low-poly, faceted
  geo.computeVertexNormals();
  // Simulate OBJ flat shading by duplicating vertices (non-indexed)
  const nonIndexed = geo.toNonIndexed();
  nonIndexed.computeVertexNormals();
  return nonIndexed;
}

function createSTLGeometry() {
  // STL: binary/ascii, always non-indexed, purely geometric, no UV/material
  const geo = new THREE.TorusKnotGeometry(0.9, 0.3, 64, 8);
  const nonIndexed = geo.toNonIndexed();
  nonIndexed.computeVertexNormals();
  return nonIndexed;
}

function createGLTFGeometry() {
  // GLTF: smooth, indexed, PBR materials, UVs, tangents
  const geo = new THREE.SphereGeometry(1.2, 64, 64);
  geo.computeVertexNormals();
  return geo;
}

// ─── Model Components ────────────────────────────────────────────────────────


function OBJModel({ onMetadata }) {
  const mesh = useRef();
  const obj = useLoader(OBJLoader, "/models/model.obj");

  useEffect(() => {
    let vertexCount = 0;
    obj.traverse((child) => {
      if (child.isMesh) {
        vertexCount += child.geometry.attributes.position.count;
      }
    });
    onMetadata({
      format: "OBJ",
      vertices: vertexCount,
      indexed: false,
      description: "Wavefront OBJ — flat-shaded, Phong material",
      smoothness: "Faceted",
      material: "Phong / Lambert",
      textures: "MTL file (if present)",
    });
  }, [obj]);

  useFrame((state) => {
    if (mesh.current) mesh.current.rotation.y = state.clock.elapsedTime * 0.3;
  });

  return <primitive ref={mesh} object={obj} />;
}

function STLModel({ onMetadata }) {
  const mesh = useRef();
  const geo = useLoader(STLLoader, "/models/model.stl");

  useEffect(() => {
    geo.computeVertexNormals();
    onMetadata({
      format: "STL",
      vertices: geo.attributes.position.count,
      indexed: geo.index !== null,
      description: "STL — binary mesh, pure geometry, no materials",
      smoothness: "Smooth normals (computed)",
      material: "MeshNormal / Solid",
      textures: "None",
    });
  }, [geo]);

  useFrame((state) => {
    if (mesh.current) mesh.current.rotation.y = state.clock.elapsedTime * 0.4;
  });

  return (
    <mesh ref={mesh} geometry={geo} castShadow>
      <meshNormalMaterial />
    </mesh>
  );
}

function GLTFModel({ onMetadata }) {
  const mesh = useRef();
  const { scene } = useGLTF("/models/model.glb");

  useEffect(() => {
    let vertexCount = 0;
    scene.traverse((child) => {
      if (child.isMesh) {
        vertexCount += child.geometry.attributes.position.count;
      }
    });
    onMetadata({
      format: "GLTF",
      vertices: vertexCount,
      indexed: true,
      description: "GLTF — PBR materials, tangents, UVs, animations",
      smoothness: "Smooth (interpolated normals)",
      material: "PBR / Physically-Based",
      textures: "Albedo, Normal, Roughness, Metalness",
    });
  }, [scene]);

  useFrame((state) => {
    if (mesh.current) mesh.current.rotation.y = state.clock.elapsedTime * 0.25;
  });

  return <primitive ref={mesh} object={scene} />;
}

// ─── Scene ───────────────────────────────────────────────────────────────────

function Scene({ active, onMetadata }) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={1.5} castShadow shadow-mapSize={[2048, 2048]} />
      <directionalLight position={[-4, 2, -4]} intensity={0.4} color="#88aaff" />
      <pointLight position={[0, -3, 0]} intensity={0.3} color="#ff6644" />

      <Environment preset="city" />

      {active === "OBJ" && <OBJModel onMetadata={onMetadata} />}
      {active === "STL" && <STLModel onMetadata={onMetadata} />}
      {active === "GLTF" && <GLTFModel onMetadata={onMetadata} />}

      <Grid
        position={[0, -1.8, 0]}
        args={[20, 20]}
        cellSize={0.5}
        cellThickness={0.5}
        cellColor="#1a2a3a"
        sectionSize={2.5}
        sectionThickness={1}
        sectionColor="#0a3a5a"
        fadeDistance={18}
        fadeStrength={1.5}
        infiniteGrid
      />

      <OrbitControls
        enableDamping
        dampingFactor={0.06}
        rotateSpeed={0.7}
        zoomSpeed={0.8}
        minDistance={2}
        maxDistance={12}
      />
    </>
  );
}

// ─── UI Components ───────────────────────────────────────────────────────────

const formats = [
  {
    id: "OBJ",
    label: "Wavefront OBJ",
    color: "#e8a030",
    accent: "#ffcc66",
    icon: "◈",
    year: "1984",
  },
  {
    id: "STL",
    label: "Stereo­litho­graphy",
    color: "#cc44aa",
    accent: "#ff88dd",
    icon: "◉",
    year: "1987",
  },
  {
    id: "GLTF",
    label: "GL Transmission",
    color: "#4488ff",
    accent: "#88bbff",
    icon: "◎",
    year: "2015",
  },
];

// ─── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [active, setActive] = useState("GLTF");
  const [metadata, setMetadata] = useState(null);
  const [hovered, setHovered] = useState(null);

  const currentFormat = formats.find((f) => f.id === active);

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "#020c14",
        fontFamily: "'Courier New', monospace",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* ── Ambient scan lines ── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,200,0.015) 2px, rgba(0,255,200,0.015) 4px)",
          pointerEvents: "none",
          zIndex: 10,
        }}
      />

      {/* ── Canvas ── */}
      <Canvas
        shadows
        camera={{ position: [0, 1.5, 4.5], fov: 55 }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.1 }}
        style={{ position: "absolute", inset: 0 }}
      >
        <Suspense fallback={null}>
          <Scene active={active} onMetadata={setMetadata} />
        </Suspense>
      </Canvas>

      {/* ── Header ── */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          padding: "20px 28px 16px",
          background: "linear-gradient(to bottom, rgba(2,12,20,0.95) 60%, transparent)",
          zIndex: 20,
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
        }}
      >
        <div>
          <div
            style={{
              fontSize: "9px",
              letterSpacing: "4px",
              color: "#0af",
              textTransform: "uppercase",
              marginBottom: "4px",
            }}
          >
            ▸ FORMAT COMPARISON VIEWER
          </div>
          <div
            style={{
              fontSize: "22px",
              fontWeight: "bold",
              color: "#e8f4ff",
              letterSpacing: "1px",
            }}
          >
            3D Mesh{" "}
            <span style={{ color: currentFormat?.color }}>
              {currentFormat?.id}
            </span>
          </div>
        </div>
        <div
          style={{
            textAlign: "right",
            fontSize: "10px",
            color: "#3a6a8a",
            letterSpacing: "1px",
          }}
        >
          <div>ORBIT DRAG TO ROTATE</div>
          <div>SCROLL TO ZOOM</div>
          <div style={{ color: "#0af", marginTop: "4px" }}>
            R3F + THREE.JS
          </div>
        </div>
      </div>

      {/* ── Format Selector ── */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          transform: "translateX(-50%)",
          bottom: "28px",
          zIndex: 20,
          display: "flex",
          gap: "10px",
        }}
      >
        {formats.map((fmt) => {
          const isActive = active === fmt.id;
          const isHovered = hovered === fmt.id;
          return (
            <button
              key={fmt.id}
              onClick={() => setActive(fmt.id)}
              onMouseEnter={() => setHovered(fmt.id)}
              onMouseLeave={() => setHovered(null)}
              style={{
                background: isActive
                  ? `linear-gradient(135deg, ${fmt.color}22, ${fmt.color}44)`
                  : isHovered
                  ? "rgba(255,255,255,0.06)"
                  : "rgba(2,12,20,0.8)",
                border: `1px solid ${isActive ? fmt.color : isHovered ? fmt.color + "66" : "#1a3a5a"}`,
                borderRadius: "8px",
                padding: "12px 22px",
                cursor: "pointer",
                color: isActive ? fmt.color : isHovered ? fmt.accent : "#4a7a9a",
                fontFamily: "'Courier New', monospace",
                fontSize: "11px",
                letterSpacing: "2px",
                textTransform: "uppercase",
                transition: "all 0.2s ease",
                backdropFilter: "blur(8px)",
                boxShadow: isActive
                  ? `0 0 20px ${fmt.color}40, inset 0 1px 0 ${fmt.color}30`
                  : "none",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "4px",
                minWidth: "100px",
              }}
            >
              <span style={{ fontSize: "18px", lineHeight: 1 }}>{fmt.icon}</span>
              <span style={{ fontWeight: "bold" }}>.{fmt.id}</span>
              <span
                style={{
                  fontSize: "9px",
                  opacity: 0.6,
                  letterSpacing: "1px",
                }}
              >
                est. {fmt.year}
              </span>
            </button>
          );
        })}
      </div>

      {/* ── Metadata Panel ── */}
      {metadata && (
        <div
          style={{
            position: "absolute",
            right: "20px",
            top: "50%",
            transform: "translateY(-50%)",
            zIndex: 20,
            background: "rgba(2,12,20,0.85)",
            border: `1px solid ${currentFormat?.color}44`,
            borderRadius: "10px",
            padding: "20px",
            width: "230px",
            backdropFilter: "blur(12px)",
            boxShadow: `0 0 30px ${currentFormat?.color}22`,
          }}
        >
          <div
            style={{
              fontSize: "9px",
              letterSpacing: "3px",
              color: currentFormat?.color,
              textTransform: "uppercase",
              marginBottom: "14px",
              borderBottom: `1px solid ${currentFormat?.color}33`,
              paddingBottom: "8px",
            }}
          >
            ▸ Model Metadata
          </div>

          {[
            ["FORMAT", metadata.format],
            ["VERTICES", metadata.vertices.toLocaleString()],
            ["INDEXED", metadata.indexed ? "YES" : "NO"],
            ["SMOOTHNESS", metadata.smoothness],
            ["MATERIAL", metadata.material],
            ["TEXTURES", metadata.textures],
          ].map(([label, value]) => (
            <div key={label} style={{ marginBottom: "10px" }}>
              <div
                style={{
                  fontSize: "8px",
                  letterSpacing: "2px",
                  color: "#3a6a8a",
                  marginBottom: "2px",
                }}
              >
                {label}
              </div>
              <div
                style={{
                  fontSize: "11px",
                  color:
                    label === "FORMAT"
                      ? currentFormat?.color
                      : label === "VERTICES"
                      ? currentFormat?.accent
                      : "#c8e4f8",
                  fontWeight: label === "FORMAT" || label === "VERTICES" ? "bold" : "normal",
                  letterSpacing: "0.5px",
                  lineHeight: 1.4,
                }}
              >
                {value}
              </div>
            </div>
          ))}

          <div
            style={{
              marginTop: "14px",
              paddingTop: "10px",
              borderTop: `1px solid ${currentFormat?.color}22`,
              fontSize: "9px",
              color: "#2a5a7a",
              lineHeight: 1.6,
            }}
          >
            {metadata.description}
          </div>
        </div>
      )}

      {/* ── Comparison Legend (left) ── */}
      <div
        style={{
          position: "absolute",
          left: "20px",
          top: "50%",
          transform: "translateY(-50%)",
          zIndex: 20,
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        {[
          { label: "Smoothness", values: { OBJ: "⬛⬛⬜⬜⬜", STL: "⬛⬛⬛⬜⬜", GLTF: "⬛⬛⬛⬛⬛" } },
          { label: "Material", values: { OBJ: "⬛⬛⬜⬜⬜", STL: "⬛⬜⬜⬜⬜", GLTF: "⬛⬛⬛⬛⬛" } },
          { label: "Textures", values: { OBJ: "⬛⬛⬜⬜⬜", STL: "⬜⬜⬜⬜⬜", GLTF: "⬛⬛⬛⬛⬛" } },
          { label: "File Size", values: { OBJ: "⬛⬛⬛⬜⬜", STL: "⬛⬛⬜⬜⬜", GLTF: "⬛⬛⬛⬛⬜" } },
        ].map(({ label, values }) => (
          <div
            key={label}
            style={{
              background: "rgba(2,12,20,0.8)",
              border: "1px solid #0a2a3a",
              borderRadius: "6px",
              padding: "8px 12px",
              backdropFilter: "blur(8px)",
              minWidth: "160px",
            }}
          >
            <div
              style={{
                fontSize: "8px",
                letterSpacing: "2px",
                color: "#3a6a8a",
                marginBottom: "4px",
                textTransform: "uppercase",
              }}
            >
              {label}
            </div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: "9px",
              }}
            >
              {formats.map((fmt) => (
                <div
                  key={fmt.id}
                  style={{
                    textAlign: "center",
                    opacity: active === fmt.id ? 1 : 0.4,
                    transition: "opacity 0.3s",
                  }}
                >
                  <div style={{ color: fmt.color, fontWeight: "bold" }}>
                    .{fmt.id}
                  </div>
                  <div style={{ fontSize: "7px", marginTop: "2px" }}>
                    {values[fmt.id]}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* ── Corner decoration ── */}
      <div
        style={{
          position: "absolute",
          bottom: "14px",
          left: "20px",
          fontSize: "8px",
          color: "#0a2a3a",
          letterSpacing: "2px",
          zIndex: 20,
        }}
      >
        REACT THREE FIBER · THREE.JS r{THREE.REVISION}
      </div>
    </div>
  );
}
