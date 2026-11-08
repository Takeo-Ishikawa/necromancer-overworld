using UnityEditor;
using UnityEngine;

/// <summary>Independent cave entrance geometry, generated after the safe chamber.</summary>
public static class OverworldCaveEntrance
{
    public static void Apply()
    {
        var rock = MaterialFor("Cave basalt", new Color(0.15f, 0.17f, 0.21f));
        var path = MaterialFor("Cave path", new Color(0.26f, 0.26f, 0.29f));
        var accent = MaterialFor("Cave crystal", new Color(0.22f, 0.55f, 0.68f));
        var dark = MaterialFor("Cave shadow", new Color(0.09f, 0.10f, 0.14f));

        var root = new GameObject("03 - Cave entrance (modular)").transform;
        var structure = Group(root, "Walkable corridor");
        // The chamber doorway is x=-3..3 at z=-10. This corridor aligns with it.
        Cube("Corridor floor", new Vector3(0f, -0.35f, -17.5f), new Vector3(7.5f, 0.7f, 16f), path, structure, true);
        Cube("West cliff wall", new Vector3(-4.1f, 1.7f, -17.5f), new Vector3(1f, 3.4f, 16f), rock, structure, true);
        Cube("East cliff wall", new Vector3(4.1f, 1.7f, -17.5f), new Vector3(1f, 3.4f, 16f), rock, structure, true);
        // Entrance threshold is kept low so the camera can see through the arch.
        Cube("Entrance lintel", new Vector3(0f, 3.45f, -10.0f), new Vector3(7.5f, 0.7f, 1.1f), rock, structure, true);
        Cube("West entrance pillar", new Vector3(-3.45f, 1.45f, -10.0f), new Vector3(0.75f, 2.9f, 1.0f), rock, structure, true);
        Cube("East entrance pillar", new Vector3(3.45f, 1.45f, -10.0f), new Vector3(0.75f, 2.9f, 1.0f), rock, structure, true);

        var decorations = Group(root, "Cave decorations (no collision)");
        for (int i = 0; i < 6; i++)
        {
            float z = -12f - i * 2.35f;
            float x = i % 2 == 0 ? -3.3f : 3.3f;
            Cube("Broken stone " + i, new Vector3(x, 0.20f, z), new Vector3(0.65f, 0.4f, 0.85f), rock, decorations, false);
        }
        Crystal(new Vector3(-3.1f, 0f, -14.0f), accent, decorations);
        Crystal(new Vector3(3.1f, 0f, -19.0f), accent, decorations);
        Crystal(new Vector3(-3.1f, 0f, -23.0f), accent, decorations);

        // Deliberately sealed at this milestone: no accidental fall off the playable map.
        Cube("Temporary end barrier", new Vector3(0f, 1.35f, -25.4f), new Vector3(7.3f, 2.7f, 0.8f), dark, structure, true);
        Cube("Barrier warning stripe", new Vector3(0f, 1.0f, -24.92f), new Vector3(5.2f, 0.12f, 0.08f), accent, decorations, false);
    }

    private static Transform Group(Transform parent, string name)
    {
        var obj = new GameObject(name);
        obj.transform.SetParent(parent, false);
        return obj.transform;
    }

    private static void Cube(string name, Vector3 pos, Vector3 scale, Material mat, Transform parent, bool collider)
    {
        var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obj.name = name;
        obj.transform.SetParent(parent, false);
        obj.transform.position = pos;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = mat;
        if (!collider) Object.DestroyImmediate(obj.GetComponent<Collider>());
    }

    private static void Crystal(Vector3 pos, Material mat, Transform parent)
    {
        var root = Group(parent, "Crystal cluster " + pos.z);
        for (int i = 0; i < 3; i++)
        {
            var obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            obj.name = "Crystal " + i;
            obj.transform.SetParent(root, false);
            obj.transform.position = pos + new Vector3((i - 1) * 0.24f, 0.35f + i * 0.08f, i * 0.1f);
            obj.transform.localScale = new Vector3(0.17f, 0.42f + i * 0.10f, 0.17f);
            obj.transform.rotation = Quaternion.Euler(0f, i * 37f, (i - 1) * 17f);
            obj.GetComponent<Renderer>().sharedMaterial = mat;
            Object.DestroyImmediate(obj.GetComponent<Collider>());
        }
        var lightObj = new GameObject("Crystal glow");
        lightObj.transform.SetParent(root, false);
        lightObj.transform.position = pos + Vector3.up * 0.75f;
        var light = lightObj.AddComponent<Light>();
        light.type = LightType.Point;
        light.range = 3.0f;
        light.intensity = 0.45f;
        light.color = mat.color;
        light.shadows = LightShadows.None;
    }

    private static Material MaterialFor(string name, Color color)
    {
        string path = "Assets/Materials/" + name.Replace(" ", "_") + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material != null)
        {
            material.color = color;
            EditorUtility.SetDirty(material);
            return material;
        }
        Shader shader = Shader.Find("Standard");
        if (shader == null) shader = Shader.Find("Unlit/Color");
        material = new Material(shader) { name = name, color = color };
        AssetDatabase.CreateAsset(material, path);
        return material;
    }
}
