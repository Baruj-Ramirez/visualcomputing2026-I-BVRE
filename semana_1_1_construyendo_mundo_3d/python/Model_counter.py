import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Load OBJ file
file_path = "model.obj"  # <-- change this to your file path
mesh = trimesh.load(file_path)

# Ensure mesh is triangular
if not isinstance(mesh, trimesh.Trimesh):
    mesh = mesh.dump().sum()

# Extract data
vertices = mesh.vertices
faces = mesh.faces
edges = mesh.edges_unique

# Print mesh information
print("Mesh Information:")
print("-------------------")
print(f"Number of vertices: {len(vertices)}")
print(f"Number of edges: {len(edges)}")
print(f"Number of faces: {len(faces)}")

# Create 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot faces (light blue, semi-transparent)
face_vertices = vertices[faces]
face_collection = Poly3DCollection(face_vertices,
                                    facecolor='lightblue',
                                    edgecolor='none',
                                    alpha=0.5)
ax.add_collection3d(face_collection)

# Plot edges (black)
for edge in edges:
    points = vertices[edge]
    ax.plot(points[:, 0], points[:, 1], points[:, 2], color='black', linewidth=0.5)

# Plot vertices (red dots)
ax.scatter(vertices[:, 0],
           vertices[:, 1],
           vertices[:, 2],
           color='red',
           s=5)

# Auto scale to mesh size
scale = vertices.flatten()
ax.auto_scale_xyz(scale, scale, scale)

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("3D Mesh Visualization")

plt.tight_layout()
plt.show()