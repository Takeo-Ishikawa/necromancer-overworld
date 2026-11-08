using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Minimal shared HUD for desktop and touch builds; replaced by a Canvas later.</summary>
    public sealed class OverworldCombatHUD : MonoBehaviour
    {
        public OverworldHealth playerHealth;
        public OverworldNecromancy necromancy;

        private void OnGUI()
        {
            if (playerHealth == null || necromancy == null) return;
            float scale = Mathf.Max(0.75f, Mathf.Min(Screen.width / 1000f, Screen.height / 560f));
            var previous = GUI.matrix;
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1f));
            GUI.Box(new Rect(12f, 12f, 265f, 106f), "NECROMANCER");
            GUI.Label(new Rect(24f, 40f, 245f, 22f), "Vida: " + Mathf.CeilToInt(playerHealth.Current) + " / " + Mathf.CeilToInt(playerHealth.maxHealth));
            GUI.Label(new Rect(24f, 61f, 245f, 22f), "Anima: " + Mathf.CeilToInt(necromancy.anima) + " / " + Mathf.CeilToInt(necromancy.maxAnima));
            GUI.Label(new Rect(24f, 82f, 245f, 22f), "Servos: " + necromancy.AllyCount + " / " + necromancy.maxAllies);
            float w = Screen.width / scale;
            float h = Screen.height / scale;
            // Keep reanimation on the right, separated from the movement joystick on the left.
            float buttonWidth = Mathf.Min(176f, w * 0.25f);
            float buttonHeight = Mathf.Min(82f, h * 0.18f);
            if (GUI.Button(new Rect(w - buttonWidth - 20f, h - buttonHeight - 30f, buttonWidth, buttonHeight), "REANIMAR (E)"))
                necromancy.TryReanimate();
            GUI.matrix = previous;
        }
    }
}
