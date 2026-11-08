using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>World-space health bars projected onto the screen, without per-enemy canvases.</summary>
    public sealed class OverworldHealthBars : MonoBehaviour
    {
        public Camera worldCamera;
        private GUIStyle textStyle;
        private Texture2D white;

        private void Awake()
        {
            white = Texture2D.whiteTexture;
            textStyle = new GUIStyle(GUI.skin.label);
            textStyle.alignment = TextAnchor.MiddleCenter;
            textStyle.fontSize = 12;
            textStyle.normal.textColor = Color.white;
        }

        private void OnGUI()
        {
            if (worldCamera == null) worldCamera = Camera.main;
            if (worldCamera == null) return;
            foreach (var health in Object.FindObjectsOfType<OverworldHealth>())
            {
                if (!health.IsAlive) continue;
                Vector3 screen = worldCamera.WorldToScreenPoint(health.transform.position + Vector3.up * 1.65f);
                if (screen.z <= 0f) continue;
                float x = screen.x - 36f;
                float y = Screen.height - screen.y;
                if (x < -72f || x > Screen.width || y < 0f || y > Screen.height) continue;
                float fraction = Mathf.Clamp01(health.Current / Mathf.Max(1f, health.maxHealth));
                Draw(new Rect(x - 2f, y - 2f, 76f, 12f), new Color(0.04f, 0.04f, 0.07f, 0.85f));
                var combat = health.GetComponent<OverworldAutoCombat>();
                Color fill = combat != null && !combat.isPlayer ? new Color(0.84f, 0.22f, 0.25f) : new Color(0.28f, 0.77f, 0.57f);
                Draw(new Rect(x, y, 72f * fraction, 8f), fill);
            }
        }

        private void Draw(Rect rect, Color color)
        {
            Color old = GUI.color;
            GUI.color = color;
            GUI.DrawTexture(rect, white);
            GUI.color = old;
        }
    }
}
