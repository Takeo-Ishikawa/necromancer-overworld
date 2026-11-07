using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class OverworldAndroidBuild
{
    public static void BuildAndroid()
    {
        OverworldSceneBuilder.Build();
        string output = Path.GetFullPath(Path.Combine("..", "build", "Android", "necromancer-overworld-preview.apk"));
        Directory.CreateDirectory(Path.GetDirectoryName(output));

        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.takeo.necromancer.overworld");
        PlayerSettings.Android.bundleVersionCode = Mathf.Max(1, GetRunNumber());
        PlayerSettings.bundleVersion = "0.1." + PlayerSettings.Android.bundleVersionCode;
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);

        string keystore = Environment.GetEnvironmentVariable("PREVIEW_KEYSTORE_PATH");
        string password = Environment.GetEnvironmentVariable("PREVIEW_KEYSTORE_PASSWORD");
        string alias = Environment.GetEnvironmentVariable("PREVIEW_KEY_ALIAS");
        string keyPassword = Environment.GetEnvironmentVariable("PREVIEW_KEY_PASSWORD");
        if (!string.IsNullOrEmpty(keystore) && !string.IsNullOrEmpty(password) &&
            !string.IsNullOrEmpty(alias) && !string.IsNullOrEmpty(keyPassword))
        {
            PlayerSettings.Android.useCustomKeystore = true;
            PlayerSettings.Android.keystoreName = Path.GetFullPath(keystore);
            PlayerSettings.Android.keystorePass = password;
            PlayerSettings.Android.keyaliasName = alias;
            PlayerSettings.Android.keyaliasPass = keyPassword;
        }
        else
        {
            PlayerSettings.Android.useCustomKeystore = false;
            Debug.LogWarning("Preview signed with default debug key; updates across CI runs are not guaranteed.");
        }

        var options = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/OverworldPrototype.unity" },
            locationPathName = output,
            target = BuildTarget.Android,
            options = BuildOptions.Development
        };
        var result = BuildPipeline.BuildPlayer(options);
        if (result.summary.result != BuildResult.Succeeded)
            throw new Exception("Unity Android build failed: " + result.summary.result);
        Debug.Log("Android APK generated: " + output + " (" + result.summary.totalSize + " bytes)");
    }

    private static int GetRunNumber()
    {
        string value = Environment.GetEnvironmentVariable("GITHUB_RUN_NUMBER");
        int number;
        return int.TryParse(value, out number) ? number : 1;
    }
}
