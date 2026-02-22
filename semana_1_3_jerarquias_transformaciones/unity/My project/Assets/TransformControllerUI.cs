using UnityEngine;
using UnityEngine.UI;

public class TransformControllerUI : MonoBehaviour
{
    [Header("Objeto a controlar")]
    [SerializeField] private Transform target;

    [Header("Sliders Posición")]
    [SerializeField] private Slider posX;
    [SerializeField] private Slider posY;
    [SerializeField] private Slider posZ;

    [Header("Sliders Rotación")]
    [SerializeField] private Slider rotX;
    [SerializeField] private Slider rotY;
    [SerializeField] private Slider rotZ;

    [Header("Sliders Escala")]
    [SerializeField] private Slider scaleX;
    [SerializeField] private Slider scaleY;
    [SerializeField] private Slider scaleZ;

    [Header("Movimiento Automático")]
    [SerializeField] private float autoMoveSpeed = 50f;

    private Vector3 initialPosition;
    private Quaternion initialRotation;
    private Vector3 initialScale;

    private bool autoMoveActive = false;

    private void Start()
    {
        if (target == null)
        {
            Debug.LogError("No hay objeto asignado.");
            return;
        }

        // Guardamos estado inicial
        initialPosition = target.position;
        initialRotation = target.rotation;
        initialScale = target.localScale;

        UpdateSlidersFromTransform();
    }

    private void Update()
    {
        if (target == null) return;

        if (autoMoveActive)
        {
            target.Rotate(Vector3.up * autoMoveSpeed * Time.deltaTime);
            PrintTransformValues();
        }
    }

    // ===============================
    // Métodos llamados por los Sliders
    // ===============================

    public void UpdatePosition()
    {
        Vector3 newPosition = new Vector3(posX.value, posY.value, posZ.value);
        target.position = newPosition;
        PrintTransformValues();
    }

    public void UpdateRotation()
    {
        Vector3 newRotation = new Vector3(rotX.value, rotY.value, rotZ.value);
        target.rotation = Quaternion.Euler(newRotation);
        PrintTransformValues();
    }

    public void UpdateScale()
    {
        Vector3 newScale = new Vector3(scaleX.value, scaleY.value, scaleZ.value);
        target.localScale = newScale;
        PrintTransformValues();
    }

    // ===============================
    // Botones
    // ===============================

    public void ResetTransform()
    {
        target.position = initialPosition;
        target.rotation = initialRotation;
        target.localScale = initialScale;

        UpdateSlidersFromTransform();
        PrintTransformValues();
    }

    public void ToggleAutoMove()
    {
        autoMoveActive = !autoMoveActive;
    }

    // ===============================
    // Utilidades
    // ===============================

    private void UpdateSlidersFromTransform()
    {
        Vector3 pos = target.position;
        posX.value = pos.x;
        posY.value = pos.y;
        posZ.value = pos.z;

        Vector3 rot = target.eulerAngles;
        rotX.value = rot.x;
        rotY.value = rot.y;
        rotZ.value = rot.z;

        Vector3 scale = target.localScale;
        scaleX.value = scale.x;
        scaleY.value = scale.y;
        scaleZ.value = scale.z;
    }

    private void PrintTransformValues()
    {
        Debug.Log(
            $"Posición: {target.position}\n" +
            $"Rotación: {target.eulerAngles}\n" +
            $"Escala: {target.localScale}"
        );
    }
}
