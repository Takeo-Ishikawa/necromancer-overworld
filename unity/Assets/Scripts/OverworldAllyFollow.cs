using UnityEngine;

namespace NecromancerOverworld
{
    [RequireComponent(typeof(OverworldHealth))]
    public sealed class OverworldAllyFollow : MonoBehaviour
    {
        public Transform owner;
        public int slot;
        public float speed = 3.5f;
        private OverworldHealth health;

        private void Awake() { health = GetComponent<OverworldHealth>(); }

        private void Update()
        {
            if (!health.IsAlive || owner == null) return;
            var ownerHealth = owner.GetComponent<OverworldHealth>();
            if (ownerHealth == null || !ownerHealth.IsAlive) return;
            float angle = (slot % 5) * Mathf.PI * 2f / 5f;
            Vector3 desired = owner.position + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * 1.8f;
            desired.y = transform.position.y;
            Vector3 delta = desired - transform.position;
            if (delta.sqrMagnitude < 0.4f) return;
            Vector3 step = Vector3.MoveTowards(transform.position, desired, speed * Time.deltaTime) - transform.position;
            // Stop at solid world geometry. Decorative and character renderers have no colliders.
            RaycastHit hit;
            Vector3 origin = transform.position + Vector3.up * 0.65f;
            if (Physics.SphereCast(origin, 0.28f, step.normalized, out hit, step.magnitude + 0.05f,
                ~0, QueryTriggerInteraction.Ignore) && hit.collider.transform != transform &&
                !hit.collider.transform.IsChildOf(transform) &&
                (owner == null || !hit.collider.transform.IsChildOf(owner)))
                return;
            transform.position += step;
            if (delta.sqrMagnitude > 0.01f)
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(delta), Mathf.Clamp01(7f * Time.deltaTime));
        }
    }
}
