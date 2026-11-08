using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Lightweight local obstacle avoidance for summoned allies (not a full pathfinder).</summary>
    [RequireComponent(typeof(OverworldHealth))]
    public sealed class OverworldAllyFollow : MonoBehaviour
    {
        public Transform owner;
        public int slot;
        public float speed = 3.5f;
        public float avoidanceRadius = 0.28f;
        private OverworldHealth health;
        private OverworldHealth ownerHealth;
        private Vector3 preferredSide;
        private float sideUntil;

        private void Awake() { health = GetComponent<OverworldHealth>(); }

        private void Update()
        {
            if (!health.IsAlive || owner == null) return;
            if (ownerHealth == null) ownerHealth = owner.GetComponent<OverworldHealth>();
            if (ownerHealth == null || !ownerHealth.IsAlive) return;

            float angle = (slot % 5) * Mathf.PI * 2f / 5f;
            Vector3 desired = owner.position + new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle)) * 1.8f;
            desired.y = transform.position.y;
            Vector3 delta = desired - transform.position;
            delta.y = 0f;
            if (delta.sqrMagnitude < 0.4f) return;

            Vector3 direction = delta.normalized;
            float distance = Mathf.Min(speed * Time.deltaTime, delta.magnitude);
            if (Blocked(direction, distance))
            {
                Vector3 left = new Vector3(-direction.z, 0f, direction.x);
                Vector3 right = -left;
                if (Time.time >= sideUntil)
                {
                    bool leftOpen = !Blocked((direction + left * 1.5f).normalized, 0.85f);
                    bool rightOpen = !Blocked((direction + right * 1.5f).normalized, 0.85f);
                    preferredSide = leftOpen ? left : rightOpen ? right : left;
                    sideUntil = Time.time + 0.8f;
                }

                Vector3 angled = (direction + preferredSide * 1.5f).normalized;
                if (!Blocked(angled, distance)) direction = angled;
                else if (!Blocked(preferredSide, distance)) direction = preferredSide;
                else return;
            }

            transform.position += direction * distance;
            transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(direction), Mathf.Clamp01(7f * Time.deltaTime));
        }

        private bool Blocked(Vector3 direction, float distance)
        {
            // Ground and character colliders must not prevent navigation; only solid scenery.
            RaycastHit[] hits = Physics.SphereCastAll(transform.position + Vector3.up * 0.85f,
                avoidanceRadius, direction, distance + 0.08f, ~0, QueryTriggerInteraction.Ignore);
            foreach (var hit in hits)
            {
                Transform obstacle = hit.collider.transform;
                if (obstacle == transform || obstacle.IsChildOf(transform) ||
                    obstacle == owner || obstacle.IsChildOf(owner)) continue;
                if (hit.collider is CharacterController) continue;
                return true;
            }
            return false;
        }
    }
}
