using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using System;
using System.IO;
namespace ZhaoLeiBirdsNestV3 {
public static class BuildVenuePlayer {
 [MenuItem("Tools/Zhao Lei Birds Nest/Open Enhanced Scene")]
 public static void OpenPreview(){EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);EditorApplication.ExecuteMenuItem("Window/General/Game");}
 public static void Build(){
  ValidateUpperSeating.VerifyAndCapture();
  PlayerSettings.companyName="Venue Study";PlayerSettings.productName="Birds Nest - Zhao Lei";
  PlayerSettings.defaultScreenWidth=1440;PlayerSettings.defaultScreenHeight=900;PlayerSettings.fullScreenMode=FullScreenMode.Windowed;
  PlayerSettings.runInBackground=true;QualitySettings.vSyncCount=0;
  var folder=Path.Combine(BuildEnhancedVenue.Output,"WindowsPreview_v25");Directory.CreateDirectory(folder);
  var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{BuildEnhancedVenue.ScenePath},locationPathName=Path.Combine(folder,"BirdsNest.exe"),target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
  if(report.summary.result!=BuildResult.Succeeded)throw new Exception("Player build: "+report.summary.result);
  AssetDatabase.ExportPackage(BuildEnhancedVenue.Base,Path.Combine(BuildEnhancedVenue.Output,"BirdsNest_Enhanced.unitypackage"),ExportPackageOptions.Recurse);
  Debug.Log("BIRDSNEST_V3_PLAYER_SUCCESS "+report.summary.totalSize);
 }
}
}
