using UnityEngine;

namespace NecromancerOverworld
{
    /// <summary>Temporary interactable remains left by defeated Grave Pups.</summary>
    public sealed class OverworldCorpse : MonoBehaviour
    {
        public float lifetime = 20f;

        public static void Spawn(Vector3 position)
        {
            var corpse = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            corpse.name = "Grave Pup remains (reanimate)";
            corpse.transform.position = position + Vector3.up * 0.18f;
            corpse.transform.localScale = new Vector3(0.75f, 0.30f, 0.9f);
            Destroy(corpse.GetComponent<Collider>());
            var shader = Shader.Find("Standard");
            if (shader == null) shader = Shader.Find("Unlit/Color");
            var material = new Material(shader);
            material.color = new Color(0.43f, 0.64f, 0.58f);
            corpse.GetComponent<Renderer>().material = material;
            corpse.AddComponent<OverworldCorpse>();
        }

        private void Start() { Destroy(gameObject, lifetime); }
    }
}
