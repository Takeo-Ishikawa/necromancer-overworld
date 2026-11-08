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

        private Vector3 destination;
        private float pauseUntil;

        private void Start()
        {
            home = transform.position;
            PickDestination();
        }

        private void Update()
        {
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
        }
    }
}
