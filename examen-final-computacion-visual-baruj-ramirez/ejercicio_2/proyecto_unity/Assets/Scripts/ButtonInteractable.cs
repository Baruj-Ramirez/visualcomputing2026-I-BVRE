using UnityEngine;
using UnityEngine.Events;

public class ButtonInteractable : MonoBehaviour, IInteractable
{
    [SerializeField] private Animator animator;
    [SerializeField] private string triggerName = "Press";
    [SerializeField] private UnityEvent onPressed;

    private bool hasBeenUsed;

    public void Interact()
    {
        if (hasBeenUsed)
            return;

        if (animator != null)
        {
            animator.SetTrigger(triggerName);
        }

        hasBeenUsed = true;

        onPressed?.Invoke();
    }
}