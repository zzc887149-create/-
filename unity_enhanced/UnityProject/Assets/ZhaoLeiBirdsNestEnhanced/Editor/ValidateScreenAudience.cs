using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.IO;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateScreenAudience {
 public static void Rebuild(){ValidateUpperSeating.RebuildAndValidate();Capture();}
 public static void Capture(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var m=Object.FindFirstObjectByType<VenueModes>();m.SetNight(false);m.showPanel=false;
  var cam=m.viewCamera;cam.transform.position=new Vector3(25,34,146);cam.transform.LookAt(new Vector3(0,29,132));
  BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v24_screen_rear_day.png"));
  cam.transform.position=new Vector3(-25,34,146);cam.transform.LookAt(new Vector3(0,29,132));
  BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/v24_screen_rear_close.png"));
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  Debug.Log("SCREEN_AUDIENCE_CAPTURE_SUCCESS");
 }
}
}
