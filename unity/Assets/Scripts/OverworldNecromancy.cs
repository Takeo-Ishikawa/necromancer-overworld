using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Player anima, corpse interaction and allied summon limit.</summary>
    public sealed class OverworldNecromancy : MonoBehaviour
    {
        public float maxAnima = 100f;
        public float anima = 100f;
        public float reviveCost = 25f;
        public float reviveRange = 3.5f;
        public int maxAllies = 5;
        public int AllyCount { get; private set; }
        private float nextInteraction;

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.E) || Input.GetKeyDown(KeyCode.R))
                TryReanimate();
        }

        public bool TryReanimate()
        {
            var health = GetComponent<OverworldHealth>();
            if (health == null || !health.IsAlive || Time.time < nextInteraction) return false;
            if (anima < reviveCost || AllyCount >= maxAllies) return false;

            OverworldCorpse nearest = null;
            float best = reviveRange * reviveRange;
            foreach (var corpse in Object.FindObjectsOfType<OverworldCorpse>())
            {
                Vector3 delta = corpse.transform.position - transform.position;
                delta.y = 0f;
                float dist = delta.sqrMagnitude;
                if (dist < best) { best = dist; nearest = corpse; }
            }
            if (nearest == null) return false;
            Vector3 position = nearest.transform.position;
            Destroy(nearest.gameObject);
            anima -= reviveCost;
            nextInteraction = Time.time + 0.35f;
            SpawnAlly(position);
            return true;
        }

        private void SpawnAlly(Vector3 position)
        {
            var ally = new GameObject("Reanimated Grave Pup");
            ally.transform.position = position;
            var body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            body.name = "Spectral body";
            body.transform.SetParent(ally.transform, false);
            body.transform.localPosition = new Vector3(0f, 0.55f, 0f);
            body.transform.localScale = new Vector3(0.65f, 0.5f, 0.85f);
            Destroy(body.GetComponent<Collider>());
            var shader = Shader.Find("Standard");
            if (shader == null) shader = Shader.Find("Unlit/Color");
            var material = new Material(shader);
            material.color = new Color(0.22f, 0.72f, 0.70f);
            body.GetComponent<Renderer>().material = material;

            var allyHealth = ally.AddComponent<OverworldHealth>();
            allyHealth.SetMaxHealth(50f);
            var combat = ally.AddComponent<OverworldAutoCombat>();
            combat.isPlayer = true;
            combat.damage = 9f;
            combat.range = 1.8f;
            combat.aggroRange = 2.3f;
            combat.attacksPerSecond = 1.0f;
            var follow = ally.AddComponent<OverworldAllyFollow>();
            follow.owner = transform;
            follow.slot = AllyCount;
            var marker = ally.AddComponent<OverworldSummonLifetime>();
            marker.owner = this;
            AllyCount++;
        }

        public void NotifyAllyRemoved()
        {
            AllyCount = Mathf.Max(0, AllyCount - 1);
        }
    }
}
