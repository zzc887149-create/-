using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System;
using System.IO;
using System.Linq;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateFohControls {
 public static void RetuneAndDeliver(){BuildEnhancedVenue.RefreshArchitectureLighting();Capture();BuildVenuePlayer.Build();}
 public static void Deliver(){Rebuild();BuildVenuePlayer.Build();}
 public static void Rebuild(){ValidateUpperSeating.RebuildAndValidate();Capture();}
 public static void Capture(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var m=UnityEngine.Object.FindFirstObjectByType<VenueModes>();m.showPanel=false;
  var screen=AssetDatabase.LoadAssetAtPath<Material>(BuildEnhancedVenue.Base+"/Materials/BNE_FOH_DISPLAY.mat");
  var meter=AssetDatabase.LoadAssetAtPath<Material>(BuildEnhancedVenue.Base+"/Materials/BNE_FOH_METER.mat");
  var edge=AssetDatabase.LoadAssetAtPath<Material>(BuildEnhancedVenue.Base+"/Materials/BNE_FOH_EDGE.mat");
  var phone=AssetDatabase.LoadAssetAtPath<Material>(BuildEnhancedVenue.Base+"/Materials/BNE_025.mat");
  foreach(var mat in new[]{screen,meter,edge}){
   if(!mat||mat==phone||m.emissions.Count(e=>e.material==mat)!=1)throw new Exception("Missing or shared FOH emission material");
   if(!m.geometry.GetComponentsInChildren<Renderer>().Any(r=>r.sharedMaterials.Contains(mat)))throw new Exception("Unused FOH material "+mat.name);
  }
  foreach(bool night in new[]{true,false,true}){
   m.SetNight(night);
   foreach(var mat in new[]{screen,meter,edge}){
    Color actual=mat.GetColor("_EmissionColor");
    var setting=m.emissions.Single(e=>e.material==mat);
    if(actual!=(night?setting.night:setting.day)||actual.maxColorComponent<=0||Mathf.Max(actual.r,Mathf.Max(actual.g,actual.b))>.5f)
     throw new Exception("FOH emission regression: "+mat.name);
   }
   if(night&&Mathf.Abs(phone.GetColor("_EmissionColor").b-5)>.001f)throw new Exception("Audience phone brightness changed");
  }
  var cam=m.viewCamera;cam.orthographic=false;cam.fieldOfView=55;
  foreach(bool night in new[]{false,true}){
   m.SetNight(night);string mode=night?"night":"day";
   cam.transform.position=new Vector3(20,4,28);cam.transform.LookAt(new Vector3(13.8f,.9f,22.5f));
   BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v27_foh_stairs_"+mode+".png"));
   cam.transform.position=new Vector3(1.8f,2.8f,20.4f);cam.transform.LookAt(new Vector3(0,1.5f,17.5f));
   BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v27_console_"+mode+".png"));
  }
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/v27_unity_audit.json"),"{\"dedicated_materials\":3,\"day_night_switches\":3,\"phone_emission_preserved\":true,\"failures\":[]}");
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  Debug.Log("FOH_CONTROLS_V27_SUCCESS");
 }
}
}
