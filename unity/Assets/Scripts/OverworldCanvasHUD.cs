using UnityEngine;
using UnityEngine.UI;

namespace NecromancerOverworld
{
    /// <summary>Responsive uGUI combat display, updated without allocations or IMGUI buttons.</summary>
    public sealed class OverworldCanvasHUD : MonoBehaviour
    {
        public OverworldHealth playerHealth;
        public OverworldNecromancy necromancy;
        public Text healthText;
        public Text animaText;
        public Text alliesText;
        public Button reanimateButton;

        private void Start()
        {
            if (reanimateButton != null && necromancy != null)
                reanimateButton.onClick.AddListener(OnReanimate);
        }

        private void OnDestroy()
        {
            if (reanimateButton != null)
                reanimateButton.onClick.RemoveListener(OnReanimate);
        }

        private void OnReanimate()
        {
            if (necromancy != null) necromancy.TryReanimate();
        }

        private void Update()
        {
            if (playerHealth == null || necromancy == null) return;
            if (healthText != null) healthText.text = "VIDA  " + Mathf.CeilToInt(playerHealth.Current) + " / " + Mathf.CeilToInt(playerHealth.maxHealth);
            if (animaText != null) animaText.text = "ANIMA  " + Mathf.CeilToInt(necromancy.anima) + " / " + Mathf.CeilToInt(necromancy.maxAnima);
            if (alliesText != null) alliesText.text = "SERVOS  " + necromancy.AllyCount + " / " + necromancy.maxAllies;
            if (reanimateButton != null)
                reanimateButton.interactable = playerHealth.IsAlive && necromancy.anima >= necromancy.reviveCost &&
                    necromancy.AllyCount < necromancy.maxAllies;
        }
    }
}
