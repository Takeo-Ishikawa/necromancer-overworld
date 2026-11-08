using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Resets player to sanctuary or respawns enemy at its original point.</summary>
    [RequireComponent(typeof(OverworldHealth))]
    public sealed class OverworldCombatLifecycle : MonoBehaviour
    {
        public bool isPlayer;
        public float respawnSeconds = 8f;
        public Vector3 sanctuaryPosition = new Vector3(0f, 0.08f, 0f);
        private OverworldHealth health;
        private Vector3 spawn;
        private float respawnAt = -1f;
        private Renderer[] renderers;

        private void Awake()
        {
            health = GetComponent<OverworldHealth>();
            spawn = transform.position;
            renderers = GetComponentsInChildren<Renderer>();
            health.OnDeath += HandleDeath;
        }

        private void OnDestroy()
        {
            if (health != null) health.OnDeath -= HandleDeath;
        }

        private void HandleDeath(OverworldHealth ignored)
        {
            respawnAt = Time.time + (isPlayer ? 2f : respawnSeconds);
            if (!isPlayer) OverworldCorpse.Spawn(transform.position);
            foreach (var r in renderers) if (r != null) r.enabled = false;
        }

        private void Update()
        {
            if (respawnAt < 0f || Time.time < respawnAt) return;
            var cc = GetComponent<CharacterController>();
            if (cc != null) cc.enabled = false;
            transform.position = isPlayer ? sanctuaryPosition : spawn;
            if (cc != null) cc.enabled = true;
            health.Restore();
            foreach (var r in renderers) if (r != null) r.enabled = true;
            respawnAt = -1f;
        }
    }
}
