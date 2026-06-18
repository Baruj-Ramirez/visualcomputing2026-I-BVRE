using UnityEngine;
using System.Collections;

public class SetCelebration : MonoBehaviour
{
    [SerializeField]
    private Animator celebrationAnimator;

    [SerializeField]
    private float waitTime = 4f;

    public void StartCelebration()
    {
        StartCoroutine(TriggerCelebration());
    }

    private IEnumerator TriggerCelebration()
    {
        yield return new WaitForSeconds(waitTime);
        if (celebrationAnimator != null)
        {
            celebrationAnimator.SetTrigger("Anim");
        }

        yield return null;
    }
}
