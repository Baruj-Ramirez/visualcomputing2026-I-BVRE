using UnityEngine;

public class RandomMotion : MonoBehaviour
{
    [Header("Traslación Aleatoria")]
    [SerializeField] private float moveInterval = 2f;        // Tiempo entre movimientos
    [SerializeField] private float moveAmount = 1f;          // Magnitud de la traslación

    [Header("Rotación Constante")]
    [SerializeField] private Vector3 rotationSpeed = new Vector3(0f, 90f, 0f); // Grados por segundo

    [Header("Escalado Oscilante")]
    [SerializeField] private float scaleAmplitude = 0.5f;    // Qué tanto oscila
    [SerializeField] private float scaleFrequency = 1f;      // Velocidad de oscilación

    private float timer;
    private Vector3 initialScale;

    private void Start()
    {
        initialScale = transform.localScale;
        timer = moveInterval;
    }

    private void Update()
    {
        HandleTranslation();
        HandleRotation();
        HandleScaling();
    }

    private void HandleTranslation()
    {
        timer -= Time.deltaTime;

        if (timer <= 0f)
        {
            float direction = Random.value > 0.5f ? 1f : -1f;

            if (Random.value > 0.5f)
            {
                // Movimiento en X
                transform.Translate(Vector3.right * direction * moveAmount);
            }
            else
            {
                // Movimiento en Y
                transform.Translate(Vector3.up * direction * moveAmount);
            }

            timer = moveInterval;
        }
    }

    private void HandleRotation()
    {
        transform.Rotate(rotationSpeed * Time.deltaTime);
    }

    private void HandleScaling()
    {
        float scaleFactor = 1 + Mathf.Sin(Time.time * scaleFrequency) * scaleAmplitude;
        transform.localScale = initialScale * scaleFactor;
    }
}