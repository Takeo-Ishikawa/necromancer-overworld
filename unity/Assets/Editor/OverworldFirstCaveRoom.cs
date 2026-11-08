using UnityEditor;
using UnityEngine;
using NecromancerOverworld;

/// <summary>First explorable cave room, separate from the safe chamber and corridor.</summary>
public static class OverworldFirstCaveRoom
{
    public static void Apply()
    {
        Material stone = Mat("First room rock", new Color(0.16f, 0.18f, 0.22f));
        Material floor = Mat("First room floor", new Color(0.25f, 0.25f, 0.28f));
        Material bone = Mat("Grave Pup bone", new Color(0.63f, 0.60f, 0.54f));
        Material fur = Mat("Grave Pup fur", new Color(0.25f, 0.24f, 0.29f));
        Material eyes = Mat("Grave Pup eyes", new Color(0.40f, 0.85f, 0.82f));

        Transform root = Group(null, "04 - First cave room (modular)");
        Transform walls = Group(root, "Arena geometry");
        // Room spans x=-11..11 and z=-47..-25; corridor joins at z=-25.
        Cube("Room floor", new Vector3(0f, -0.35f, -36f), new Vector3(22f, 0.7f, 22f), floor, walls, true);
        Cube("West wall", new Vector3(-11f, 1.8f, -36f), new Vector3(1f, 3.6f, 22f), stone, walls, true);
        Cube("East wall", new Vector3(11f, 1.8f, -36f), new Vector3(1f, 3.6f, 22f), stone, walls, true);
        Cube("Far wall", new Vector3(0f, 1.8f, -47f), new Vector3(22f, 3.6f, 1f), stone, walls, true);
        // Keep a 7-unit-wide opening for the corridor.
        Cube("Near wall west", new Vector3(-7.25f, 1.8f, -25f), new Vector3(7.5f, 3.6f, 1f), stone, walls, true);
        Cube("Near wall east", new Vector3(7.25f, 1.8f, -25f), new Vector3(7.5f, 3.6f, 1f), stone, walls, true);

        Transform props = Group(root, "Scenery (nonblocking)");
        for (int i = 0; i < 8; i++)
        {
            float x = i % 2 == 0 ? -9.5f : 9.5f;
            float z = -29f - (i / 2) * 4.2f;
            Cube("Edge rubble " + i, new Vector3(x, 0.25f, z), new Vector3(1f, 0.5f, 1.2f), stone, props, false);
        }

        Transform creatures = Group(root, "Grave Pups (patrolling placeholders)");
        Pup("Grave Pup A", new Vector3(-4f, 0f, -35f), fur, bone, eyes, creatures);
        Pup("Grave Pup B", new Vector3(4f, 0f, -38f), fur, bone, eyes, creatures);
        Pup("Grave Pup C", new Vector3(0f, 0f, -43f), fur, bone, eyes, creatures);
    }

    private static void Pup(string name, Vector3 pos, Material fur, Material bone, Material eyes, Transform parent)
    {
        Transform root = Group(parent, name);
        root.position = pos;
        var patrol = root.gameObject.AddComponent<GravePupPatrol>();
        patrol.patrolRadius = 2f;
        patrol.speed = 0.95f;
        Shape(PrimitiveType.Capsule, "Body", new Vector3(0f, 0.42f, 0f), new Vector3(0.65f, 0.52f, 0.9f), fur, root);
        Shape(PrimitiveType.Sphere, "Head", new Vector3(0f, 0.67f, 0.45f), new Vector3(0.62f, 0.54f, 0.52f), bone, root);
        Shape(PrimitiveType.Cube, "Left ear", new Vector3(-0.22f, 1.05f, 0.42f), new Vector3(0.18f, 0.33f, 0.15f), fur, root);
        Shape(PrimitiveType.Cube, "Right ear", new Vector3(0.22f, 1.05f, 0.42f), new Vector3(0.18f, 0.33f, 0.15f), fur, root);
        Shape(PrimitiveType.Sphere, "Left eye", new Vector3(-0.18f, 0.73f, 0.70f), new Vector3(0.12f, 0.12f, 0.08f), eyes, root);
        Shape(PrimitiveType.Sphere, "Right eye", new Vector3(0.18f, 0.73f, 0.70f), new Vector3(0.12f, 0.12f, 0.08f), eyes, root);
        for (int i = 0; i < 4; i++)
        {
            float x = i % 2 == 0 ? -0.22f : 0.22f;
            float z = i < 2 ? 0.28f : -0.3f;
            Shape(PrimitiveType.Cylinder, "Leg " + i, new Vector3(x, 0.20f, z), new Vector3(0.11f, 0.19f, 0.11f), bone, root);
        }
    }

    private static void Shape(PrimitiveType type, string name, Vector3 pos, Vector3 scale, Material mat, Transform parent)
    {
        var obj = GameObject.CreatePrimitive(type);
        obj.name = name;
        obj.transform.SetParent(parent, false);
        obj.transform.localPosition = pos;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = mat;
        Object.DestroyImmediate(obj.GetComponent<Collider>());
    }

    private static void Cube(string name, Vector3 pos, Vector3 scale, Material mat, Transform parent, bool collision)
    {
        var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obj.name = name;
        obj.transform.SetParent(parent, false);
        obj.transform.position = pos;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = mat;
        if (!collision) Object.DestroyImmediate(obj.GetComponent<Collider>());
    }

    private static Transform Group(Transform parent, string name)
    {
        var obj = new GameObject(name);
        if (parent != null) obj.transform.SetParent(parent, false);
        return obj.transform;
    }

    private static Material Mat(string name, Color color)
    {
        string path = "Assets/Materials/" + name.Replace(" ", "_") + ".mat";
        var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (existing != null) { existing.color = color; EditorUtility.SetDirty(existing); return existing; }
        Shader shader = Shader.Find("Standard");
        if (shader == null) shader = Shader.Find("Unlit/Color");
        var mat = new Material(shader) { name = name, color = color };
        AssetDatabase.CreateAsset(mat, path);
        return mat;
    }
}
