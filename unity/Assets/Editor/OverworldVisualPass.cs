using UnityEditor;
using UnityEngine;

public static class OverworldVisualPass
{
    // Geometry-only art pass. Every prop is an independent GameObject under a named group.
    public static void Apply()
    {
        var stone = MaterialFor("Polished floor tiles", new Color(0.29f, 0.32f, 0.37f));
        var darkStone = MaterialFor("Stone joints", new Color(0.13f, 0.15f, 0.20f));
        var bronze = MaterialFor("Aged bronze", new Color(0.45f, 0.31f, 0.19f));
        var blue = MaterialFor("Arcane blue", new Color(0.13f, 0.68f, 0.85f));
        var violet = MaterialFor("Arcane violet", new Color(0.49f, 0.26f, 0.71f));
        var black = MaterialFor("Necromancer armor", new Color(0.13f, 0.12f, 0.18f));
        var bone = MaterialFor("Pale bone", new Color(0.70f, 0.69f, 0.67f));

        var root = new GameObject("02 - Visual details (modular)").transform;
        var tiles = Group(root, "Floor masonry");
        // Tile seams are separate, low-profile objects. Keep the center clear for navigation.
        for (int x = -10; x <= 10; x += 2)
        for (int z = -8; z <= 8; z += 2)
        {
            var tile = Primitive(PrimitiveType.Cube, "Flagstone " + x + " " + z,
                new Vector3(x, 0.012f, z), new Vector3(1.91f, 0.024f, 1.91f), stone, tiles, false);
            tile.transform.rotation = Quaternion.Euler(0f, ((x + z) % 3) * 0.8f, 0f);
        }

        var pillars = Group(root, "Wall supports");
        foreach (float x in new[] { -10f, -5f, 0f, 5f, 10f })
        {
            Pillar(new Vector3(x, 0f, 9.1f), darkStone, bronze, pillars);
        }
        foreach (float z in new[] { -7f, 0f, 7f })
        {
            Pillar(new Vector3(-11.15f, 0f, z), darkStone, bronze, pillars);
            Pillar(new Vector3(11.15f, 0f, z), darkStone, bronze, pillars);
        }

        var torches = Group(root, "Arcane braziers");
        Brazier(new Vector3(-9.8f, 0f, 2.2f), bronze, violet, torches);
        Brazier(new Vector3(9.8f, 0f, 2.2f), bronze, blue, torches);
        Brazier(new Vector3(-2.2f, 0f, -7.7f), bronze, violet, torches);
        Brazier(new Vector3(2.2f, 0f, -7.7f), bronze, blue, torches);

        var stations = Group(root, "Station accents");
        // Wardrobe door details and handles.
        Primitive(PrimitiveType.Cube, "Wardrobe left door", new Vector3(-3.63f, 1.75f, 7.88f), new Vector3(1.15f, 2.9f, 0.12f), darkStone, stations, false);
        Primitive(PrimitiveType.Cube, "Wardrobe right door", new Vector3(-2.37f, 1.75f, 7.88f), new Vector3(1.15f, 2.9f, 0.12f), darkStone, stations, false);
        Primitive(PrimitiveType.Sphere, "Wardrobe left handle", new Vector3(-3.16f, 1.7f, 7.77f), new Vector3(0.13f, 0.13f, 0.13f), bronze, stations, false);
        Primitive(PrimitiveType.Sphere, "Wardrobe right handle", new Vector3(-2.84f, 1.7f, 7.77f), new Vector3(0.13f, 0.13f, 0.13f), bronze, stations, false);
        // Bedding and pillow.
        Primitive(PrimitiveType.Cube, "Bed pillow", new Vector3(-8f, 0.92f, 8.0f), new Vector3(1.8f, 0.16f, 0.65f), bone, stations, false);
        // Fountain central crystal.
        Primitive(PrimitiveType.Cylinder, "Fountain arcane crystal", new Vector3(5.5f, 1.8f, -4f), new Vector3(0.35f, 0.7f, 0.35f), blue, stations, false);
        // Altar emblem.
        Primitive(PrimitiveType.Sphere, "Altar focus", new Vector3(-8f, 1.72f, -6.4f), new Vector3(0.45f, 0.45f, 0.45f), violet, stations, false);

        var player = GameObject.Find("Necromancer Player");
        if (player != null)
        {
            var silhouette = Group(player.transform, "Visual silhouette (replaceable)");
            Primitive(PrimitiveType.Cylinder, "Shoulder mantle", new Vector3(0f, 1.52f, 0f), new Vector3(0.55f, 0.22f, 0.44f), black, silhouette, false, true);
            Primitive(PrimitiveType.Sphere, "Hood", new Vector3(0f, 1.96f, 0.05f), new Vector3(0.54f, 0.58f, 0.54f), black, silhouette, false, true);
            Primitive(PrimitiveType.Sphere, "Face", new Vector3(0f, 1.93f, 0.32f), new Vector3(0.28f, 0.28f, 0.12f), bone, silhouette, false, true);
            Primitive(PrimitiveType.Cylinder, "Staff", new Vector3(0.48f, 1.1f, 0.24f), new Vector3(0.075f, 1.08f, 0.075f), bronze, silhouette, false, true);
            Primitive(PrimitiveType.Sphere, "Staff gem", new Vector3(0.48f, 2.21f, 0.24f), new Vector3(0.26f, 0.26f, 0.26f), violet, silhouette, false, true);
        }
    }

    private static Transform Group(Transform parent, string name)
    {
        var obj = new GameObject(name);
        obj.transform.SetParent(parent, false);
        return obj.transform;
    }

    private static GameObject Primitive(PrimitiveType type, string name, Vector3 position, Vector3 scale, Material material, Transform parent, bool collision, bool local = false)
    {
        var obj = GameObject.CreatePrimitive(type);
        obj.name = name;
        obj.transform.SetParent(parent, false);
        if (local) obj.transform.localPosition = position;
        else obj.transform.position = position;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = material;
        if (!collision) Object.DestroyImmediate(obj.GetComponent<Collider>());
        return obj;
    }

    private static void Pillar(Vector3 pos, Material stone, Material trim, Transform parent)
    {
        var group = Group(parent, "Pillar " + pos.x + " " + pos.z);
        Primitive(PrimitiveType.Cube, "Column", pos + Vector3.up * 1.7f, new Vector3(0.75f, 3.4f, 0.75f), stone, group, true);
        Primitive(PrimitiveType.Cube, "Foot", pos + Vector3.up * 0.2f, new Vector3(1.0f, 0.4f, 1.0f), trim, group, true);
        Primitive(PrimitiveType.Cube, "Capital", pos + Vector3.up * 3.3f, new Vector3(1.0f, 0.4f, 1.0f), trim, group, true);
    }

    private static void Brazier(Vector3 pos, Material metal, Material flame, Transform parent)
    {
        var group = Group(parent, "Brazier " + pos.x + " " + pos.z);
        Primitive(PrimitiveType.Cylinder, "Pedestal", pos + Vector3.up * 0.65f, new Vector3(0.36f, 0.65f, 0.36f), metal, group, true);
        Primitive(PrimitiveType.Cylinder, "Bowl", pos + Vector3.up * 1.35f, new Vector3(0.62f, 0.14f, 0.62f), metal, group, false);
        Primitive(PrimitiveType.Sphere, "Arcane fire", pos + Vector3.up * 1.65f, new Vector3(0.42f, 0.65f, 0.42f), flame, group, false);
        var lightObject = new GameObject("Local light");
        lightObject.transform.SetParent(group, false);
        lightObject.transform.position = pos + Vector3.up * 1.9f;
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Point;
        light.range = 4.5f;
        light.intensity = 0.7f;
        light.color = flame.color;
        light.shadows = LightShadows.None;
    }

    private static Material MaterialFor(string name, Color color)
    {
        string path = "Assets/Materials/" + name.Replace(" ", "_") + ".mat";
        var material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material != null) { material.color = color; EditorUtility.SetDirty(material); return material; }
        Shader shader = Shader.Find("Standard");
        if (shader == null) shader = Shader.Find("Unlit/Color");
        material = new Material(shader) { name = name, color = color };
        AssetDatabase.CreateAsset(material, path);
        return material;
    }
}
