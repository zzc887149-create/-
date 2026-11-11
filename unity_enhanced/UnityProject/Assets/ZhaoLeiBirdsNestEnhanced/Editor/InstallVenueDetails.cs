using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using System;
using System.IO;
using System.Linq;
namespace ZhaoLeiBirdsNestV3 {
public static class InstallVenueDetails {
 public static void DiagnoseLighting(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);var m=UnityEngine.Object.FindFirstObjectByType<VenueModes>();m.SetNight(true);m.fly.Jump(3);
  var output=Path.Combine(BuildEnhancedVenue.Output,"checks");
  BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(output,"Diagnostic_full.png"));
  var detailRig=m.nightRig.transform.Find("Concourse detail lights");
  detailRig.Find("Stage spill near memorial").GetComponent<Light>().enabled=false;
  BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(output,"Diagnostic_noMemorialSpill.png"));
  foreach(var light in detailRig.GetComponentsInChildren<Light>())light.enabled=light.name=="Stage spill near memorial";
  BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(output,"Diagnostic_memorialSpillOnly.png"));
  detailRig.gameObject.SetActive(false);
  BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(output,"Diagnostic_noDetails.png"));
  foreach(var l in m.nightRig.GetComponentsInChildren<Light>(true))l.enabled=false;
  BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(output,"Diagnostic_noRigLights.png"));
  m.sun.enabled=false;BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(output,"Diagnostic_noLights.png"));
  Debug.Log("BIRDSNEST_DIAGNOSTIC_SUCCESS");
 }
 static void ConfigureConcourseLight(Light light){
  light.type=LightType.Spot;light.transform.rotation=Quaternion.Euler(90,0,0);light.spotAngle=110;light.innerSpotAngle=65;
  light.color=new Color(1,.85f,.68f);light.intensity=1.3f;light.range=12;light.shadows=LightShadows.Hard;light.shadowResolution=LightShadowResolution.Medium;light.shadowBias=.02f;light.shadowNormalBias=.1f;light.renderMode=LightRenderMode.Auto;
 }
 public static void RefineLighting(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();
  foreach(var light in modes.nightRig.GetComponentsInChildren<Light>(true))if(light.name=="Concourse soft pool")ConfigureConcourseLight(light);
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());AssetDatabase.SaveAssets();BuildEnhancedVenue.RefreshArchitectureLighting();
  Debug.Log("BIRDSNEST_V4_CONCOURSE_LIGHT_SUCCESS");
 }
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();Apply(modes);
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());AssetDatabase.SaveAssets();
  BuildEnhancedVenue.RefreshArchitectureLighting();Debug.Log("BIRDSNEST_V4_DETAILS_SUCCESS");
 }
 public static void Apply(VenueModes modes){
  var path=BuildEnhancedVenue.Base+"/Models/BirdsNest_Details.fbx";if(!File.Exists(path))return;
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);var imp=(ModelImporter)AssetImporter.GetAtPath(path);
  imp.importCameras=false;imp.importLights=false;imp.importAnimation=false;imp.isReadable=true;imp.importNormals=ModelImporterNormals.Import;imp.SaveAndReimport();
  foreach(var matPath in AssetDatabase.FindAssets("t:Material",new[]{BuildEnhancedVenue.Base+"/Materials"}).Select(AssetDatabase.GUIDToAssetPath)){
   var mat=AssetDatabase.LoadAssetAtPath<Material>(matPath);imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),mat.name),mat);
  }
  string lampPath=BuildEnhancedVenue.Base+"/Materials/BND_环廊灯罩.mat";var lamp=AssetDatabase.LoadAssetAtPath<Material>(lampPath);
  if(!lamp){lamp=new Material(Shader.Find("Standard"));AssetDatabase.CreateAsset(lamp,lampPath);}
  lamp.SetColor("_Color",new Color(.8f,.74f,.6f));lamp.EnableKeyword("_EMISSION");lamp.SetFloat("_Glossiness",.2f);lamp.globalIlluminationFlags=MaterialGlobalIlluminationFlags.None;
  imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),"BND_环廊灯罩"),lamp);imp.SaveAndReimport();
  var old=modes.geometry.transform.Find("BirdsNest_Detail_V4");if(old)UnityEngine.Object.DestroyImmediate(old.gameObject);
  var detail=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));detail.name="BirdsNest_Detail_V4";detail.transform.SetParent(modes.geometry.transform,true);
  foreach(var r in detail.GetComponentsInChildren<Renderer>()){
   // The thin rails and signs are not occluders. Existing floor plates remain the main occlusion surfaces.
   GameObjectUtility.SetStaticEditorFlags(r.gameObject,StaticEditorFlags.BatchingStatic|StaticEditorFlags.OccludeeStatic);
   r.shadowCastingMode=ShadowCastingMode.On;
  }
  var ts=modes.geometry.GetComponentsInChildren<Transform>(true);modes.fly.viewpoints=ts.Where(t=>t.name.StartsWith("VIEW_")).GroupBy(t=>t.name.Substring(5,2)).Select(g=>g.First()).OrderBy(t=>t.name).ToArray();
  modes.fly.targets=modes.fly.viewpoints.Select(v=>ts.First(t=>t.name==v.name.Replace("VIEW_","LOOK_"))).ToArray();
  if(modes.fly.viewpoints.Length<12)throw new Exception("Expected at least twelve views after detail installation");
  modes.emissions=modes.emissions.Where(e=>e.material!=lamp).Concat(new[]{new EmissionSetting{material=lamp,day=new Color(.12f,.11f,.09f),night=new Color(1,.8f,.52f)*1.4f}}).ToArray();
  var lights=modes.nightRig.transform.Find("Concourse detail lights");if(lights)UnityEngine.Object.DestroyImmediate(lights.gameObject);
  var rig=new GameObject("Concourse detail lights");rig.transform.SetParent(modes.nightRig.transform,false);
  foreach(float z in new[]{6.3f,13.8f,21.3f})for(int i=0;i<4;i++){
   float a=i*Mathf.PI*.5f+.11f;var light=new GameObject("Concourse soft pool").AddComponent<Light>();light.transform.SetParent(rig.transform);
   light.transform.position=new Vector3(-125*Mathf.Cos(a),z,-142*Mathf.Sin(a));ConfigureConcourseLight(light);
  }
  // A restrained stage spill makes the foreground flowers readable in the night study.
  var spill=new GameObject("Stage spill near memorial").AddComponent<Light>();spill.transform.SetParent(rig.transform);
  spill.transform.position=new Vector3(2.2f,3.2f,-42.8f);spill.type=LightType.Point;spill.color=new Color(1,.8f,.58f);spill.intensity=1.1f;spill.range=7;spill.shadows=LightShadows.None;spill.renderMode=LightRenderMode.ForcePixel;
  modes.SetNight(true);modes.fly.Jump(3);EditorUtility.SetDirty(modes);EditorUtility.SetDirty(modes.fly);
  PrefabUtility.SaveAsPrefabAsset(modes.geometry,BuildEnhancedVenue.Base+"/Prefabs/BirdsNest_Enhanced_360.prefab");
 }
}
}
