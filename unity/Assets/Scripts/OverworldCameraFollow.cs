using UnityEngine;

namespace NecromancerOverworld
{
    [RequireComponent(typeof(Camera))]
    public sealed class OverworldCameraFollow : MonoBehaviour
    {
        public Transform target;
        public Vector3 offset = new Vector3(-11f, 14f, -11f);
        public float smoothness = 8f;

        private void LateUpdate()
        {
            if (target == null) return;
            Vector3 desired = target.position + offset;
            transform.position = Vector3.Lerp(transform.position, desired, 1f - Mathf.Exp(-smoothness * Time.deltaTime));
            transform.rotation = Quaternion.LookRotation(target.position + Vector3.up * 1.0f - transform.position);
        }
    }
}
