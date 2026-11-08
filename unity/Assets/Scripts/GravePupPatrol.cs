using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Simple contained patrol for prototype creatures. No combat or damage yet.</summary>
    public sealed class GravePupPatrol : MonoBehaviour
    {
        public Vector3 home;
        public float patrolRadius = 2.5f;
        public float speed = 1.15f;
        public float pauseSeconds = 1f;

        public float chaseRange = 5f;
        public float attackStopRange = 1.35f;
        private OverworldHealth health;
        private Transform player;
        private Vector3 destination;
        private float pauseUntil;

        private void Start()
        {
            home = transform.position;
            health = GetComponent<OverworldHealth>();
            var hero = GameObject.Find("Necromancer Player");
            if (hero != null) player = hero.transform;
            PickDestination();
        }

        private void Update()
        {
            if (health != null && !health.IsAlive) return;
            if (player != null)
            {
                var playerHealth = player.GetComponent<OverworldHealth>();
                Vector3 chase = player.position - transform.position;
                chase.y = 0f;
                // Never chase into the safe chamber; the entrance remains a safe retreat.
                if (playerHealth != null && playerHealth.IsAlive && player.position.z < -26f &&
                    chase.sqrMagnitude <= chaseRange * chaseRange)
                {
                    if (chase.sqrMagnitude > attackStopRange * attackStopRange)
                    {
                        Vector3 next = Vector3.MoveTowards(transform.position, player.position, speed * Time.deltaTime);
                        next.x = Mathf.Clamp(next.x, -9.8f, 9.8f);
                        next.z = Mathf.Clamp(next.z, -45.5f, -26.2f);
                        transform.position = next;
                    }
                    if (chase.sqrMagnitude > 0.01f)
                        transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(chase), Mathf.Clamp01(8f * Time.deltaTime));
                    return;
                }
            }
            if (Time.time < pauseUntil) return;
            Vector3 delta = destination - transform.position;
            delta.y = 0f;
            if (delta.sqrMagnitude < 0.06f)
            {
                pauseUntil = Time.time + pauseSeconds;
                PickDestination();
                return;
            }
            Vector3 direction = delta.normalized;
            transform.position = Vector3.MoveTowards(transform.position, destination, speed * Time.deltaTime);
            transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.LookRotation(direction), Mathf.Clamp01(8f * Time.deltaTime));
        }

        private void PickDestination()
        {
            Vector2 offset = Random.insideUnitCircle * patrolRadius;
            destination = home + new Vector3(offset.x, 0f, offset.y);
            destination.x = Mathf.Clamp(destination.x, -9.8f, 9.8f);
            destination.z = Mathf.Clamp(destination.z, -45.5f, -26.2f);
        }
    }
}
