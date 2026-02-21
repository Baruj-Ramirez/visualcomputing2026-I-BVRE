"""
3D Mesh Analyzer & Converter
Supports: .OBJ, .STL, .GLTF/.GLB
Features: vertex/face/normal analysis, duplicate detection, visualization, format conversion
"""

import os
import sys
import argparse
import numpy as np
import trimesh
import trimesh.exchange
from pathlib import Path

# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────

def load_mesh(filepath: str) -> trimesh.Trimesh:
    """Load a mesh from .obj, .stl, or .gltf/.glb."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = path.suffix.lower()
    supported = {".obj", ".stl", ".gltf", ".glb"}
    if ext not in supported:
        raise ValueError(f"Unsupported format '{ext}'. Supported: {supported}")

    loaded = trimesh.load(str(path), force="mesh")

    # trimesh.load may return a Scene for GLTF; concatenate all meshes
    if isinstance(loaded, trimesh.Scene):
        meshes = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not meshes:
            raise ValueError("No triangle meshes found in scene.")
        loaded = trimesh.util.concatenate(meshes)

    return loaded


def find_duplicate_vertices(mesh: trimesh.Trimesh, tol: float = 1e-6):
    """Return indices of duplicate vertex groups."""
    verts = mesh.vertices
    # Round to tolerance then find duplicates via unique
    rounded = np.round(verts / tol).astype(np.int64)
    _, inverse, counts = np.unique(rounded, axis=0, return_inverse=True, return_counts=True)
    dup_groups = []
    for uid in np.where(counts > 1)[0]:
        group = np.where(inverse == uid)[0].tolist()
        dup_groups.append(group)
    return dup_groups


def find_duplicate_faces(mesh: trimesh.Trimesh):
    """Return indices of duplicate face groups."""
    faces = np.sort(mesh.faces, axis=1)
    _, inverse, counts = np.unique(faces, axis=0, return_inverse=True, return_counts=True)
    dup_groups = []
    for uid in np.where(counts > 1)[0]:
        group = np.where(inverse == uid)[0].tolist()
        dup_groups.append(group)
    return dup_groups


def analyze_mesh(filepath: str, tol: float = 1e-6) -> dict:
    """Full analysis of a mesh file."""
    mesh = load_mesh(filepath)

    dup_verts = find_duplicate_vertices(mesh, tol)
    dup_faces = find_duplicate_faces(mesh)

    # Normals
    has_vertex_normals = (
        hasattr(mesh, "vertex_normals") and mesh.vertex_normals is not None
        and len(mesh.vertex_normals) > 0
    )
    has_face_normals = (
        hasattr(mesh, "face_normals") and mesh.face_normals is not None
        and len(mesh.face_normals) > 0
    )

    bounds = mesh.bounds  # [[xmin,ymin,zmin],[xmax,ymax,zmax]]

    info = {
        "file": str(filepath),
        "format": Path(filepath).suffix.lower(),
        "vertices": len(mesh.vertices),
        "faces": len(mesh.faces),
        "edges": len(mesh.edges),
        "has_vertex_normals": has_vertex_normals,
        "has_face_normals": has_face_normals,
        "num_vertex_normals": len(mesh.vertex_normals) if has_vertex_normals else 0,
        "num_face_normals": len(mesh.face_normals) if has_face_normals else 0,
        "duplicate_vertex_groups": len(dup_verts),
        "total_duplicate_vertices": sum(len(g) - 1 for g in dup_verts),
        "duplicate_face_groups": len(dup_faces),
        "total_duplicate_faces": sum(len(g) - 1 for g in dup_faces),
        "is_watertight": mesh.is_watertight,
        "is_volume": mesh.is_volume,
        "euler_number": mesh.euler_number,
        "surface_area": float(mesh.area),
        "volume": float(mesh.volume) if mesh.is_volume else None,
        "bounds_min": bounds[0].tolist(),
        "bounds_max": bounds[1].tolist(),
        "center_mass": mesh.center_mass.tolist(),
        "mesh": mesh,  # keep reference for viz/conversion
    }
    return info


def print_report(info: dict):
    """Pretty-print analysis results."""
    sep = "─" * 55
    print(f"\n{'═'*55}")
    print(f"  3D MESH ANALYSIS REPORT")
    print(f"{'═'*55}")
    print(f"  File   : {info['file']}")
    print(f"  Format : {info['format'].upper()}")
    print(sep)

    print(f"  GEOMETRY")
    print(f"    Vertices       : {info['vertices']:,}")
    print(f"    Faces          : {info['faces']:,}")
    print(f"    Edges          : {info['edges']:,}")
    print(sep)

    print(f"  NORMALS")
    print(f"    Vertex normals : {'Yes' if info['has_vertex_normals'] else 'No'}"
          + (f"  ({info['num_vertex_normals']:,})" if info['has_vertex_normals'] else ""))
    print(f"    Face normals   : {'Yes' if info['has_face_normals'] else 'No'}"
          + (f"  ({info['num_face_normals']:,})" if info['has_face_normals'] else ""))
    print(sep)

    print(f"  DUPLICATES")
    print(f"    Duplicate vertex groups : {info['duplicate_vertex_groups']:,}  "
          f"(+{info['total_duplicate_vertices']:,} extra vertices)")
    print(f"    Duplicate face groups   : {info['duplicate_face_groups']:,}  "
          f"(+{info['total_duplicate_faces']:,} extra faces)")
    print(sep)

    print(f"  TOPOLOGY & INTEGRITY")
    print(f"    Watertight     : {info['is_watertight']}")
    print(f"    Is volume      : {info['is_volume']}")
    print(f"    Euler number   : {info['euler_number']}")
    print(sep)

    print(f"  SPATIAL")
    print(f"    Surface area   : {info['surface_area']:.4f}")
    print(f"    Volume         : {info['volume']:.4f}" if info['volume'] is not None else
          f"    Volume         : N/A (not a closed volume)")
    bmin = info['bounds_min']
    bmax = info['bounds_max']
    print(f"    Bounds min     : ({bmin[0]:.3f}, {bmin[1]:.3f}, {bmin[2]:.3f})")
    print(f"    Bounds max     : ({bmax[0]:.3f}, {bmax[1]:.3f}, {bmax[2]:.3f})")
    cm = info['center_mass']
    print(f"    Center of mass : ({cm[0]:.3f}, {cm[1]:.3f}, {cm[2]:.3f})")
    print(f"{'═'*55}\n")


# ─────────────────────────────────────────────
# COMPARISON
# ─────────────────────────────────────────────

def compare_meshes(files: list):
    """Compare multiple mesh files side-by-side."""
    reports = []
    for f in files:
        print(f"Loading: {f} ...")
        try:
            info = analyze_mesh(f)
            reports.append(info)
        except Exception as e:
            print(f"  ERROR: {e}")

    if len(reports) < 2:
        print("Need at least 2 valid meshes to compare.")
        return reports

    keys_to_compare = [
        ("vertices", "Vertices"),
        ("faces", "Faces"),
        ("edges", "Edges"),
        ("has_vertex_normals", "Has Vertex Normals"),
        ("has_face_normals", "Has Face Normals"),
        ("duplicate_vertex_groups", "Dup. Vertex Groups"),
        ("duplicate_face_groups", "Dup. Face Groups"),
        ("is_watertight", "Watertight"),
        ("surface_area", "Surface Area"),
        ("volume", "Volume"),
    ]

    col_w = 22
    header = f"{'Property':<28}" + "".join(
        Path(r["file"]).name[:col_w].ljust(col_w) for r in reports
    )
    print(f"\n{'═'*80}")
    print("  COMPARISON TABLE")
    print(f"{'═'*80}")
    print(header)
    print("─" * 80)
    for key, label in keys_to_compare:
        row = f"  {label:<26}"
        for r in reports:
            val = r.get(key)
            if isinstance(val, float):
                val = f"{val:.3f}"
            row += str(val).ljust(col_w)
        print(row)
    print(f"{'═'*80}\n")

    return reports


# ─────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────

def visualize_mesh(info: dict, show_normals: bool = False):
    """Open trimesh's built-in viewer."""
    mesh = info["mesh"]
    fname = Path(info["file"]).name

    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name="mesh")

    if show_normals and info["has_face_normals"]:
        # Draw face normal arrows
        origins = mesh.triangles_center
        normals = mesh.face_normals
        scale = min(mesh.scale * 0.05, 0.1)
        ends = origins + normals * scale

        for o, e in zip(origins[::max(1, len(origins)//200)],
                        ends[::max(1, len(ends)//200)]):
            seg = trimesh.load_path(np.array([[o, e]]))
            scene.add_geometry(seg)

    print(f"\nOpening viewer for: {fname}  (close window to continue)")
    scene.show(caption=f"{fname} | V:{info['vertices']} F:{info['faces']}")


def visualize_all(reports: list, show_normals: bool = False):
    """Visualize multiple meshes in a single scene with different colors."""
    palette = [
        [220, 80, 80, 200],
        [80, 180, 220, 200],
        [80, 220, 130, 200],
        [240, 200, 80, 200],
        [180, 80, 220, 200],
    ]
    scene = trimesh.Scene()
    for i, info in enumerate(reports):
        mesh = info["mesh"].copy()
        color = palette[i % len(palette)]
        mesh.visual.face_colors = color
        scene.add_geometry(mesh, node_name=Path(info["file"]).stem)

    caption = " | ".join(Path(r["file"]).name for r in reports)
    print(f"\nOpening combined viewer for: {caption}")
    scene.show(caption=caption)


# ─────────────────────────────────────────────
# CONVERSION
# ─────────────────────────────────────────────

FORMAT_EXPORTERS = {
    ".obj":  "obj",
    ".stl":  "stl",
    ".gltf": "gltf",
    ".glb":  "glb",
    ".ply":  "ply",
    ".dae":  "dae",
}


def convert_mesh(info: dict, output_path: str):
    """Convert a loaded mesh to another format."""
    mesh = info["mesh"]
    out = Path(output_path)
    ext = out.suffix.lower()

    if ext not in FORMAT_EXPORTERS:
        raise ValueError(
            f"Unsupported output format '{ext}'. "
            f"Supported: {list(FORMAT_EXPORTERS.keys())}"
        )

    exporter = FORMAT_EXPORTERS[ext]

    # Use trimesh.exchange to export
    if ext == ".gltf":
        data = trimesh.exchange.gltf.export_gltf(mesh)
        # data is a dict of filename->bytes; save the .gltf part
        for filename, content in data.items():
            save_path = out.parent / filename
            save_path.write_bytes(content)
            print(f"  Saved: {save_path}")
    elif ext == ".glb":
        data = trimesh.exchange.gltf.export_glb(mesh)
        out.write_bytes(data)
        print(f"  Saved: {out}")
    elif ext == ".obj":
        data = trimesh.exchange.obj.export_obj(mesh)
        out.write_text(data if isinstance(data, str) else data.decode())
        print(f"  Saved: {out}")
    elif ext == ".stl":
        data = trimesh.exchange.stl.export_stl(mesh)
        out.write_bytes(data)
        print(f"  Saved: {out}")
    elif ext == ".ply":
        data = trimesh.exchange.ply.export_ply(mesh)
        out.write_bytes(data)
        print(f"  Saved: {out}")
    else:
        # Fallback to trimesh generic export
        mesh.export(str(out))
        print(f"  Saved: {out}")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        description="3D Mesh Analyzer & Converter (.OBJ / .STL / .GLTF)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="Analyze a single mesh file")
    p_analyze.add_argument("file", help="Path to mesh file (.obj/.stl/.gltf/.glb)")
    p_analyze.add_argument("--tol", type=float, default=1e-6,
                           help="Duplicate detection tolerance (default: 1e-6)")
    p_analyze.add_argument("--visualize", action="store_true",
                           help="Open 3D viewer after analysis")
    p_analyze.add_argument("--normals", action="store_true",
                           help="Show normals in viewer (requires --visualize)")

    # --- compare ---
    p_compare = sub.add_parser("compare", help="Compare multiple mesh files side-by-side")
    p_compare.add_argument("files", nargs="+", help="Two or more mesh files to compare")
    p_compare.add_argument("--tol", type=float, default=1e-6)
    p_compare.add_argument("--visualize", action="store_true",
                           help="Open combined 3D viewer")
    p_compare.add_argument("--normals", action="store_true")

    # --- convert ---
    p_convert = sub.add_parser("convert", help="Convert a mesh to another format")
    p_convert.add_argument("input", help="Input mesh file")
    p_convert.add_argument("output", help="Output mesh file (extension determines format)")
    p_convert.add_argument("--analyze", action="store_true",
                           help="Print analysis of input mesh before converting")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "analyze":
        print(f"\nAnalyzing: {args.file}")
        info = analyze_mesh(args.file, tol=args.tol)
        print_report(info)
        if args.visualize:
            visualize_mesh(info, show_normals=args.normals)

    elif args.command == "compare":
        reports = compare_meshes(args.files)
        for r in reports:
            print_report(r)
        if args.visualize and reports:
            visualize_all(reports, show_normals=args.normals)

    elif args.command == "convert":
        print(f"\nLoading: {args.input}")
        info = analyze_mesh(args.input)
        if args.analyze:
            print_report(info)
        print(f"\nConverting → {args.output}")
        convert_mesh(info, args.output)
        print("Done.")


if __name__ == "__main__":
    main()
