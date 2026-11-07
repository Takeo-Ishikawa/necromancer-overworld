using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace NecromancerOverworld
{
    public sealed class OverworldTouchJoystick : MonoBehaviour, IPointerDownHandler, IDragHandler, IPointerUpHandler
    {
        public OverworldPlayerController player;
        public RectTransform knob;
        public float radius = 75f;
        private RectTransform root;

        private void Awake() { root = (RectTransform)transform; }

        public void OnPointerDown(PointerEventData eventData) { OnDrag(eventData); }

        public void OnDrag(PointerEventData eventData)
        {
            if (player == null || knob == null) return;
            Vector2 local;
            if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(root, eventData.position, eventData.pressEventCamera, out local)) return;
            Vector2 direction = Vector2.ClampMagnitude(local / Mathf.Max(1f, radius), 1f);
            knob.anchoredPosition = direction * radius;
            player.SetTouchInput(direction);
        }

        public void OnPointerUp(PointerEventData eventData)
        {
            if (knob != null) knob.anchoredPosition = Vector2.zero;
            if (player != null) player.SetTouchInput(Vector2.zero);
        }
    }
}
