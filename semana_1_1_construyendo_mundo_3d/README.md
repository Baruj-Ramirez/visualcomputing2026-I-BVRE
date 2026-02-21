# Taller Construyendo Mundo 3D

Baruj Vladimir Ramírez Escalante
Fecha de entrega: 21/02/2026
Descripción breve: El objetivo del taller es comprender las estructuras básicas de modelos 3D, para esto se desarrollaon 2 códigos en los entornos de Python y Unity, los cuales nos permiten visualizar la malla.

**Implementaciones:**

- **Unity**: Este código se encarga de contar vertices triangulos y sub-mallas de un modelo dado, adicionalmente permite visualizar la malla en el editor.
- **Python**:  Este código se encarga de Contar vertices aristas y caras de un modelo dado, adicionalmente permite visualizar la malla del modelo, coloreando los vertices de rojo, caras de azul y aristas de negro.

**Resultados visuales:**

- **Unity**:
Se puede habilitar y deshabilitar la malla de un modelo dado.
![Gif de barril de Unity con malla "Barrel mesh Unity.gif"](media/Barrel%20mesh%20Unity.gif)
El código genera los siguientes resultados contando vertices triangulos y sub-mallas.
![Captura de pantalla de resultados "Unity count.png" ](media/Unity%20count.png)
- **Python**:
El código permite visualizar el modelo,
![Captura de pantalla de Malla generada" ](media/Chair%20Mesh.png)
y cuenta vertices, aristas y caras.
![Captura de pantalla de resultados "Python count.png" ](media/Python%20Count.png)

**Código relevante:**

- **Unity**:

Principalmente este método se encarga del conteo de los elementos:

```plaintext
    public void PrintMeshInfo()
    {
        if (meshInstance == null)
        {
            Debug.LogWarning("No Mesh found.");
            return;
        }

        int vertexCount = meshInstance.vertexCount;
        int triangleCount = meshInstance.triangles.Length / 3;
        int subMeshCount = meshInstance.subMeshCount;

        Debug.Log($"Mesh Info for {gameObject.name}:\n" +
                  $"Vertices: {vertexCount}\n" +
                  $"Triangles: {triangleCount}\n" +
                  $"SubMeshes: {subMeshCount}");
    }
```

Este segmento de código se encarga de la visualización de la malla mediante gizmos:

```plaintext
        Gizmos.color = Color.green;

        Vector3[] vertices = meshInstance.vertices;
        int[] triangles = meshInstance.triangles;

        for (int i = 0; i < triangles.Length; i += 3)
        {
            Vector3 v0 = transform.TransformPoint(vertices[triangles[i]]);
            Vector3 v1 = transform.TransformPoint(vertices[triangles[i + 1]]);
            Vector3 v2 = transform.TransformPoint(vertices[triangles[i + 2]]);

            Gizmos.DrawLine(v0, v1);
            Gizmos.DrawLine(v1, v2);
            Gizmos.DrawLine(v2, v0);
        }
```

- **Python**: 

Este segmento se encarga del conteo de elementos:

```plaintext
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
```

Este otro permite la visualizacion de los elementos de la malla 

```plaintext
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
```
**Prompts utilizados:**

- **Unity**: Se utilizó el siguiente prompt para la generación del código en ChatGpt:
*hola, necesito un script de Unity que me permita imprimir el número de vértices, triángulos y sub-mallas de un modelo cargado. Adicionalmente necesito activar la visualización en modo wireframe ya sea desde el editor o mediante gizmos, me puedes ayudar?*

- **Python**: Se utilizó el siguiente prompt para la generación del código en ChatGpt:
*Hi, I need a python code that does the following: Given a .obj file, I need to visualize the 3D mesh with different colors for vertexes, edges and faces, also I would like the code to show me information like number of vertexes, edges and faces. Could you help me with this task?*

**Aprendizajes y dificultades:**
Se pudieron visualizar los diversos elementos de las mallas en Python y Unity. Mi principal dificultad fue construyendo el repositorio, con el manejo de markdown para la documentación y la instalación de extenciones.
