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
            transform.position = Vector3.MoveTowards(transform.position, desired, speed * Time.deltaTime);
            if (delta.sqrMagnitude > 0.01f)
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(delta), Mathf.Clamp01(7f * Time.deltaTime));
        }
    }
}
