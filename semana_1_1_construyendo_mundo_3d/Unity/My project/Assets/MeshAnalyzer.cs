using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

[ExecuteAlways]
[RequireComponent(typeof(MeshFilter))]
public class MeshAnalyzer : MonoBehaviour
{
    [SerializeField] private bool showWireframe = true;
    [SerializeField] private bool logMeshInfo = true;

    private MeshFilter meshFilter;
    private Mesh meshInstance;

    private void OnEnable()
    {
        meshFilter = GetComponent<MeshFilter>();
        UpdateMeshReference();

        if (logMeshInfo)
            PrintMeshInfo();
    }

    private void UpdateMeshReference()
    {
        if (meshFilter != null)
            meshInstance = meshFilter.sharedMesh;
    }

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

#if UNITY_EDITOR
    private void OnDrawGizmos()
    {
        if (!showWireframe || meshInstance == null)
            return;

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
    }
#endif
}
