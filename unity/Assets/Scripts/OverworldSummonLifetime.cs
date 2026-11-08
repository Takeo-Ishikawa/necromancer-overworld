using UnityEngine;

namespace NecromancerOverworld
{
    [RequireComponent(typeof(OverworldHealth))]
    public sealed class OverworldSummonLifetime : MonoBehaviour
    {
        public OverworldNecromancy owner;
        private OverworldHealth health;

        private void Awake()
        {
            health = GetComponent<OverworldHealth>();
            health.OnDeath += OnDeath;
        }

        private void OnDeath(OverworldHealth ignored) { Destroy(gameObject); }

        private void OnDestroy()
        {
            if (health != null) health.OnDeath -= OnDeath;
            if (owner != null) owner.NotifyAllyRemoved();
        }
    }
}
