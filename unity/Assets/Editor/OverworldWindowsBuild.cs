using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

/// <summary>Headless Windows x86_64 player build, independent from the Android APK pipeline.</summary>
public static class OverworldWindowsBuild
{
    public static void BuildWindows()
    {
        OverworldSceneBuilder.Build();
        string output = Path.GetFullPath(Path.Combine("..", "build", "StandaloneWindows64", "NecromancerOverworld.exe"));
        Directory.CreateDirectory(Path.GetDirectoryName(output));

        PlayerSettings.companyName = "Takeo";
        PlayerSettings.productName = "Necromancer Overworld";
        PlayerSettings.bundleVersion = "0.3.0";
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.Standalone, ScriptingImplementation.Mono2x);

        var options = new BuildPlayerOptions
        {
            scenes = new[] { "Assets/Scenes/OverworldPrototype.unity" },
            locationPathName = output,
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };
        BuildReport report = BuildPipeline.BuildPlayer(options);
        if (report.summary.result != BuildResult.Succeeded)
            throw new Exception("Windows player build failed: " + report.summary.result);
        Debug.Log("Windows build created: " + output + " (" + report.summary.totalSize + " bytes)");
    }
}
