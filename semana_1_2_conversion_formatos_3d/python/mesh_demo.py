"""
mesh_demo.py — Example usage of mesh_analyzer as a Python module.
Run this to see how to call functions programmatically.
"""

from mesh_analyzer import analyze_mesh, print_report, compare_meshes, convert_mesh, visualize_mesh, visualize_all

import os
'''
# ── 1. Analyze a single file ──────────────────────────────────────────────────
info = analyze_mesh(os.path.join(os.path.dirname(__file__), "tree.obj"))
print_report(info)

# ── 2. Visualize it ───────────────────────────────────────────────────────────
visualize_mesh(info, show_normals=True)
'''

# ── 3. Compare multiple files ─────────────────────────────────────────────────
reports = compare_meshes([os.path.join(os.path.dirname(__file__), "tree.obj"), os.path.join(os.path.dirname(__file__), "output_tree.stl"), os.path.join(os.path.dirname(__file__), "model.obj")])
for r in reports:
     print_report(r)
visualize_all(reports)
'''
# ── 4. Convert formats ────────────────────────────────────────────────────────
info = analyze_mesh(os.path.join(os.path.dirname(__file__), "tree.obj"))
convert_mesh(info, os.path.join(os.path.dirname(__file__), "output_tree.stl"))   # OBJ → STL
convert_mesh(info, os.path.join(os.path.dirname(__file__), "output_tree.glb"))   # OBJ → GLB
convert_mesh(info, os.path.join(os.path.dirname(__file__), "output_tree.gltf"))  # OBJ → GLTF
'''
'''
print("mesh_demo.py: Uncomment the examples above to use with your own files.")
print()
print("CLI usage examples:")
print("  python mesh_analyzer.py analyze model.obj --visualize")
print("  python mesh_analyzer.py analyze model.stl --visualize --normals")
print("  python mesh_analyzer.py compare a.obj b.stl c.gltf --visualize")
print("  python mesh_analyzer.py convert model.obj output.stl")
print("  python mesh_analyzer.py convert model.gltf output.obj --analyze")
'''