using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.IO;
using System.Linq;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateFieldLayout {
 public static void Rebuild(){ValidateUpperSeating.RebuildAndValidate();Capture();}
 public static void Capture(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var m=Object.FindFirstObjectByType<VenueModes>();m.SetNight(false);m.showPanel=false;
  var cam=m.viewCamera;cam.transform.position=new Vector3(0,100,6);cam.transform.rotation=Quaternion.LookRotation(Vector3.down,Vector3.back);cam.orthographic=true;cam.orthographicSize=63;
  BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v25_field_plan.png"));
  cam.orthographic=false;cam.fieldOfView=60;cam.transform.position=new Vector3(68,52,76);cam.transform.LookAt(new Vector3(0,0,0));
  BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v25_field_overview.png"));
  cam.transform.position=new Vector3(24,8,39);cam.transform.LookAt(new Vector3(0,2,22.5f));
  BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v25_control_desk.png"));
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);Debug.Log("FIELD_LAYOUT_CAPTURE_SUCCESS");
 }
}
}
