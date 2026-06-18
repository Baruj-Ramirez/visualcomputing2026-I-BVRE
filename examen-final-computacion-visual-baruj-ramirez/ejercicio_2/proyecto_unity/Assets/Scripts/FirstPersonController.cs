using UnityEngine;
using Cinemachine;

[RequireComponent(typeof(CharacterController))]
public class FirstPersonController : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private Transform cameraPivot;          // Punto donde mira la cámara
    [SerializeField] private Camera playerCamera;            // Cámara principal
    [SerializeField] private CinemachineVirtualCamera vcam;  // Virtual Camera de Cinemachine

    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float gravity = -9.81f;
    [SerializeField] private float jumpHeight = 1.5f;

    [Header("Mouse Look")]
    [SerializeField] private float mouseSensitivity = 2f;
    [SerializeField] private float maxLookAngle = 85f;

    [Header("Interaction")]
    [SerializeField] private float interactDistance = 2.5f;
    [SerializeField] private LayerMask interactMask = ~0;

    private CharacterController characterController;
    private float verticalVelocity;
    private float pitch;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();

        if (playerCamera == null)
            playerCamera = Camera.main;
    }

    private void Start()
    {
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;

        if (vcam != null && cameraPivot != null)
        {
            vcam.Follow = cameraPivot;
            vcam.LookAt = cameraPivot;
        }
    }

    private void Update()
    {
        HandleLook();
        HandleMovement();
        HandleInteraction();
    }

    private void HandleLook()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

        // Giro horizontal del jugador
        transform.Rotate(Vector3.up * mouseX);

        // Giro vertical de la cámara
        pitch -= mouseY;
        pitch = Mathf.Clamp(pitch, -maxLookAngle, maxLookAngle);

        if (cameraPivot != null)
            cameraPivot.localRotation = Quaternion.Euler(pitch, 0f, 0f);
    }

    private void HandleMovement()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        Vector3 move = transform.right * horizontal + transform.forward * vertical;
        characterController.Move(move * moveSpeed * Time.deltaTime);

        if (characterController.isGrounded && verticalVelocity < 0f)
        {
            verticalVelocity = -2f;
        }

        if (Input.GetButtonDown("Jump") && characterController.isGrounded)
        {
            verticalVelocity = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        verticalVelocity += gravity * Time.deltaTime;
        characterController.Move(Vector3.up * verticalVelocity * Time.deltaTime);
    }

    private void HandleInteraction()
    {
        if (!Input.GetKeyDown(KeyCode.E))
            return;

        if (playerCamera == null)
            return;

        Ray ray = new Ray(playerCamera.transform.position, playerCamera.transform.forward);

        if (Physics.Raycast(ray, out RaycastHit hit, interactDistance, interactMask, QueryTriggerInteraction.Ignore))
        {
            if (hit.collider.TryGetComponent<IInteractable>(out IInteractable interactable))
            {
                interactable.Interact();
            }
        }
    }
}

public interface IInteractable
{
    void Interact();
}