using UnityEngine;

namespace NecromancerOverworld
{
    public sealed class OverworldHealth : MonoBehaviour
    {
        public float maxHealth = 100f;
        public float Current { get; private set; }
        public bool IsAlive { get { return Current > 0f; } }
        public System.Action<OverworldHealth> OnDeath;

        private void Awake() { Current = Mathf.Max(1f, maxHealth); }

        public void SetMaxHealth(float value)
        {
            maxHealth = Mathf.Max(1f, value);
            Current = maxHealth;
        }

        public void TakeDamage(float damage)
        {
            if (!IsAlive || damage <= 0f) return;
            float applied = Mathf.Min(Current, damage);
            Current = Mathf.Max(0f, Current - damage);
            var camera = Camera.main;
            if (camera != null)
            {
                var numbers = camera.GetComponent<OverworldDamageNumbers>();
                if (numbers != null)
                {
                    var combat = GetComponent<OverworldAutoCombat>();
                    numbers.Show(transform.position, applied, combat != null && !combat.isPlayer);
                }
            }
            if (!IsAlive && OnDeath != null) OnDeath(this);
        }

        public void Restore()
        {
            Current = Mathf.Max(1f, maxHealth);
        }
    }
}
