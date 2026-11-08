using System.Collections.Generic;
using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Short-lived screen-space damage feedback, no prefab or per-hit GameObject allocations.</summary>
    public sealed class OverworldDamageNumbers : MonoBehaviour
    {
        private struct Hit { public Vector3 world; public int amount; public float time; public bool enemy; }
        private readonly List<Hit> hits = new List<Hit>();
        private Camera sceneCamera;
        private GUIStyle style;
        private const float Duration = 0.85f;

        private void Awake()
        {
            sceneCamera = GetComponent<Camera>();
            style = new GUIStyle(GUI.skin.label) { alignment = TextAnchor.MiddleCenter, fontSize = 19, fontStyle = FontStyle.Bold };
        }

        public void Show(Vector3 position, float damage, bool enemy)
        {
            if (hits.Count >= 30) hits.RemoveAt(0);
            hits.Add(new Hit { world = position + Vector3.up * 1.2f, amount = Mathf.CeilToInt(damage), time = Time.time, enemy = enemy });
        }

        private void OnGUI()
        {
            if (sceneCamera == null) return;
            for (int i = hits.Count - 1; i >= 0; i--)
            {
                Hit hit = hits[i];
                float elapsed = Time.time - hit.time;
                if (elapsed >= Duration) { hits.RemoveAt(i); continue; }
                Vector3 point = sceneCamera.WorldToScreenPoint(hit.world + Vector3.up * (elapsed * 1.1f));
                if (point.z <= 0f) continue;
                Color color = hit.enemy ? new Color(1f, 0.64f, 0.42f, 1f - elapsed / Duration) : new Color(0.95f, 0.35f, 0.35f, 1f - elapsed / Duration);
                style.normal.textColor = color;
                GUI.Label(new Rect(point.x - 40f, Screen.height - point.y - 15f, 80f, 30f), "-" + hit.amount, style);
            }
        }
    }
}
