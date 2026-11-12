using UnityEngine;
using UnityEditor.SceneManagement;
using System.IO;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateFieldDetails {
 public static void Rebuild(){
  ValidateUpperSeating.RebuildAndValidate();
  Capture();
 }
 public static void Capture(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var m=Object.FindFirstObjectByType<VenueModes>();m.showPanel=false;
  var cam=m.viewCamera;cam.orthographic=false;cam.fieldOfView=55;
  cam.transform.position=new Vector3(20,4,28);
  cam.transform.LookAt(new Vector3(13.8f,.9f,22.5f));
  foreach(bool night in new[]{false,true}){
   m.SetNight(night);
   BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v26_foh_stairs_"+(night?"night":"day")+".png"));
  }
  m.SetNight(false);cam.fieldOfView=60;
  cam.transform.position=new Vector3(24,8,39);cam.transform.LookAt(new Vector3(0,2,22.5f));
  BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v26_control_desk.png"));
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  Debug.Log("FIELD_DETAILS_V26_CAPTURE_SUCCESS");
 }
}
}
