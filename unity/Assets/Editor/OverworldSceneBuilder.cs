using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using NecromancerOverworld;

public static class OverworldSceneBuilder
{
    private const string ScenePath = "Assets/Scenes/OverworldPrototype.unity";

    [MenuItem("Necromancer/Build Prototype Scene")]
    public static void Build()
    {
        EnsureFolder("Assets/Scenes");
        EnsureFolder("Assets/Materials");
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        RenderSettings.ambientLight = new Color(0.32f, 0.36f, 0.46f);
        RenderSettings.fog = true;
        RenderSettings.fogColor = new Color(0.09f, 0.11f, 0.15f);
        RenderSettings.fogDensity = 0.012f;

        Material floor = Mat("Slate floor", new Color(0.23f, 0.27f, 0.32f));
        Material wall = Mat("Stone walls", new Color(0.18f, 0.20f, 0.25f));
        Material metal = Mat("Iron", new Color(0.30f, 0.28f, 0.32f));
        Material cloth = Mat("Bedding", new Color(0.36f, 0.18f, 0.24f));
        Material magic = Mat("Magic water", new Color(0.12f, 0.68f, 0.78f));
        Material gold = Mat("Altar trim", new Color(0.55f, 0.40f, 0.18f));
        Material hero = Mat("Hero cloak", new Color(0.19f, 0.12f, 0.28f));

        // The playable floor is 24 x 20 units; obstacles remain outside the central route.
        Block("Chamber floor", new Vector3(0f, -0.35f, 0f), new Vector3(24f, 0.7f, 20f), floor);
        Block("North wall", new Vector3(0f, 2f, 10f), new Vector3(24f, 4f, 1f), wall);
        Block("West wall", new Vector3(-12f, 2f, 0f), new Vector3(1f, 4f, 20f), wall);
        Block("East wall", new Vector3(12f, 2f, 0f), new Vector3(1f, 4f, 20f), wall);
        Block("South wall left", new Vector3(-7.5f, 2f, -10f), new Vector3(9f, 4f, 1f), wall);
        Block("South wall right", new Vector3(7.5f, 2f, -10f), new Vector3(9f, 4f, 1f), wall);

        // Functional locations are placeholders, individually editable.
        Block("Bed frame", new Vector3(-8f, 0.35f, 6.5f), new Vector3(3f, 0.7f, 4f), metal);
        Block("Bed mattress", new Vector3(-8f, 0.76f, 6.5f), new Vector3(2.6f, 0.2f, 3.6f), cloth);
        Block("Wardrobe", new Vector3(-3f, 1.65f, 8.7f), new Vector3(2.6f, 3.3f, 1.5f), metal);
        Block("Mount resting area", new Vector3(8f, 0.08f, 5.8f), new Vector3(5f, 0.16f, 5f), cloth);
        Block("Meditation dais", new Vector3(-8f, 0.2f, -5.5f), new Vector3(4f, 0.4f, 3f), wall);
        Block("Meditation altar", new Vector3(-8f, 0.95f, -6.4f), new Vector3(2f, 1.1f, 0.9f), gold);
        Cylinder("Fountain basin", new Vector3(5.5f, 0.35f, -4f), new Vector3(3.3f, 0.35f, 3.3f), wall);
        Cylinder("Fountain water", new Vector3(5.5f, 0.56f, -4f), new Vector3(2.7f, 0.06f, 2.7f), magic);
        Cylinder("Fountain center", new Vector3(5.5f, 1.05f, -4f), new Vector3(0.55f, 1.0f, 0.55f), gold);

        GameObject character = new GameObject("Necromancer Player");
        character.transform.position = new Vector3(0f, 0.08f, 0f);
        var capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        capsule.name = "Temporary protagonist mesh";
        capsule.transform.SetParent(character.transform, false);
        capsule.transform.localPosition = new Vector3(0f, 0.95f, 0f);
        capsule.transform.localScale = new Vector3(0.65f, 0.95f, 0.65f);
        Object.DestroyImmediate(capsule.GetComponent<Collider>());
        capsule.GetComponent<Renderer>().sharedMaterial = hero;
        var cc = character.AddComponent<CharacterController>();
        cc.height = 1.9f;
        cc.radius = 0.36f;
        cc.center = new Vector3(0f, 0.95f, 0f);
        var movement = character.AddComponent<OverworldPlayerController>();
        var playerHealth = character.AddComponent<OverworldHealth>();
        playerHealth.maxHealth = 100f;
        var playerCombat = character.AddComponent<OverworldAutoCombat>();
        playerCombat.isPlayer = true;
        playerCombat.range = 2.3f;
        playerCombat.damage = 20f;
        playerCombat.attacksPerSecond = 1.3f;
        playerCombat.aggroRange = 2.3f;
        var playerLifecycle = character.AddComponent<OverworldCombatLifecycle>();
        playerLifecycle.isPlayer = true;
        var necromancy = character.AddComponent<OverworldNecromancy>();
        var combatHud = character.AddComponent<OverworldCombatHUD>();
        combatHud.playerHealth = playerHealth;
        combatHud.necromancy = necromancy;

        GameObject cameraObject = new GameObject("Main Camera");
        cameraObject.tag = "MainCamera";
        var camera = cameraObject.AddComponent<Camera>();
        camera.orthographic = true;
        camera.orthographicSize = 11f;
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0.07f, 0.08f, 0.11f);
        cameraObject.AddComponent<AudioListener>();
        var follow = cameraObject.AddComponent<OverworldCameraFollow>();
        follow.target = character.transform;
        var healthBars = cameraObject.AddComponent<OverworldHealthBars>();
        healthBars.worldCamera = camera;
        cameraObject.AddComponent<OverworldDamageNumbers>();
        cameraObject.transform.position = character.transform.position + follow.offset;
        cameraObject.transform.LookAt(character.transform.position + Vector3.up);

        GameObject lightObject = new GameObject("Directional Moonlight");
        var light = lightObject.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 0.9f;
        light.color = new Color(0.66f, 0.76f, 1f);
        light.shadows = LightShadows.Soft;
        lightObject.transform.rotation = Quaternion.Euler(55f, -30f, 0f);

        var fountainLight = new GameObject("Fountain glow");
        fountainLight.transform.position = new Vector3(5.5f, 2.2f, -4f);
        var glow = fountainLight.AddComponent<Light>();
        glow.type = LightType.Point;
        glow.color = new Color(0.2f, 0.8f, 1f);
        glow.range = 6f;
        glow.intensity = 1.5f;
        glow.shadows = LightShadows.None;

        OverworldVisualPass.Apply();
        OverworldCaveEntrance.Apply();
        OverworldFirstCaveRoom.Apply();
        CreateJoystick(movement);
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene, ScenePath);
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        PlayerSettings.companyName = "Takeo";
        PlayerSettings.productName = "Necromancer Overworld";
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.takeo.necromancer.overworld");
        PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
        AssetDatabase.SaveAssets();
        Debug.Log("Necromancer Overworld prototype scene created: " + ScenePath);
    }

    private static void EnsureFolder(string path)
    {
        if (!AssetDatabase.IsValidFolder(path)) AssetDatabase.CreateFolder("Assets", path.Substring("Assets/".Length));
    }

    private static Material Mat(string name, Color color)
    {
        Shader shader = Shader.Find("Standard");
        if (shader == null) shader = Shader.Find("Unlit/Color");
        var material = new Material(shader) { name = name, color = color };
        string assetPath = "Assets/Materials/" + name.Replace(" ", "_") + ".mat";
        var existing = AssetDatabase.LoadAssetAtPath<Material>(assetPath);
        if (existing != null) { existing.color = color; EditorUtility.SetDirty(existing); Object.DestroyImmediate(material); return existing; }
        AssetDatabase.CreateAsset(material, assetPath);
        return material;
    }

    private static GameObject Block(string name, Vector3 position, Vector3 scale, Material material)
    {
        var obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
        obj.name = name;
        obj.transform.position = position;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = material;
        return obj;
    }

    private static GameObject Cylinder(string name, Vector3 position, Vector3 scale, Material material)
    {
        var obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        obj.name = name;
        obj.transform.position = position;
        obj.transform.localScale = scale;
        obj.GetComponent<Renderer>().sharedMaterial = material;
        return obj;
    }

    private static void CreateJoystick(OverworldPlayerController player)
    {
        var eventSystem = new GameObject("EventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
        var canvasObject = new GameObject("Mobile Controls", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        var canvas = canvasObject.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = canvasObject.GetComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920f, 1080f);

        var baseObject = new GameObject("Movement Joystick", typeof(RectTransform), typeof(Image), typeof(OverworldTouchJoystick));
        baseObject.transform.SetParent(canvasObject.transform, false);
        var rect = baseObject.GetComponent<RectTransform>();
        rect.anchorMin = new Vector2(0f, 0f);
        rect.anchorMax = new Vector2(0f, 0f);
        rect.pivot = new Vector2(0.5f, 0.5f);
        rect.anchoredPosition = new Vector2(180f, 180f);
        rect.sizeDelta = new Vector2(210f, 210f);
        baseObject.GetComponent<Image>().color = new Color(0.65f, 0.72f, 0.85f, 0.30f);

        var knobObject = new GameObject("Knob", typeof(RectTransform), typeof(Image));
        knobObject.transform.SetParent(baseObject.transform, false);
        var knob = knobObject.GetComponent<RectTransform>();
        knob.anchorMin = knob.anchorMax = new Vector2(0.5f, 0.5f);
        knob.anchoredPosition = Vector2.zero;
        knob.sizeDelta = new Vector2(88f, 88f);
        knobObject.GetComponent<Image>().color = new Color(0.65f, 0.82f, 1f, 0.75f);
        var joystick = baseObject.GetComponent<OverworldTouchJoystick>();
        joystick.player = player;
        joystick.knob = knob;
        joystick.radius = 75f;
    }
}
