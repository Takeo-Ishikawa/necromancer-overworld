using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Prototype automatic melee attacks, with no anima cost.</summary>
    [RequireComponent(typeof(OverworldHealth))]
    public sealed class OverworldAutoCombat : MonoBehaviour
    {
        public bool isPlayer;
        public float range = 2.0f;
        public float damage = 12f;
        public float attacksPerSecond = 1.0f;
        public float aggroRange = 5f;
        private float nextAttack;
        private OverworldHealth health;

        private void Awake() { health = GetComponent<OverworldHealth>(); }

        private void Update()
        {
            if (!health.IsAlive || Time.time < nextAttack) return;
            OverworldHealth target = FindTarget();
            if (target == null) return;
            Vector3 delta = target.transform.position - transform.position;
            delta.y = 0f;
            if (delta.sqrMagnitude > range * range) return;
            if (delta.sqrMagnitude > 0.001f)
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(delta), Mathf.Clamp01(10f * Time.deltaTime));
            target.TakeDamage(damage);
            nextAttack = Time.time + 1f / Mathf.Max(0.1f, attacksPerSecond);
        }

        private OverworldHealth FindTarget()
        {
            OverworldHealth[] candidates = Object.FindObjectsOfType<OverworldHealth>();
            OverworldHealth nearest = null;
            float best = aggroRange * aggroRange;
            foreach (var candidate in candidates)
            {
                if (candidate == health || !candidate.IsAlive) continue;
                var combat = candidate.GetComponent<OverworldAutoCombat>();
                if (combat == null || combat.isPlayer == isPlayer) continue;
                Vector3 delta = candidate.transform.position - transform.position;
                delta.y = 0f;
                float sqr = delta.sqrMagnitude;
                if (sqr < best) { best = sqr; nearest = candidate; }
            }
            return nearest;
        }
    }
}
