using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
public static class InspectSeatingMouths {
 public static Vector3 Point(SeatingPort p,float t,float w,float z){return new Vector3(-(p.entry[0]+p.rad[0]*t+p.tan[0]*w),z,-(p.entry[1]+p.rad[1]*t+p.tan[1]*w));}
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);var modes=Object.FindFirstObjectByType<VenueModes>();Capture(modes);
 }
 public static void Capture(VenueModes modes){
  var pos=modes.viewCamera.transform.position;var rot=modes.viewCamera.transform.rotation;var occ=modes.viewCamera.useOcclusionCulling;modes.SetNight(false);modes.viewCamera.useOcclusionCulling=false;
  var ports=JsonUtility.FromJson<SeatingPortFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/Editor/seating_entries.json")).ports;
  foreach(var p in ports.Where(p=>p.bay==0)){
   modes.viewCamera.transform.position=Point(p,-6,5,p.height+4);modes.viewCamera.transform.LookAt(Point(p,1,0,p.height+.5f));
   BuildEnhancedVenue.Capture(modes.viewCamera,Path.Combine(BuildEnhancedVenue.Output,"checks/Mouth_F"+p.level+".png"));
  }
  Debug.Log("MOUTH_VIEWS_CAPTURED");
  modes.viewCamera.transform.SetPositionAndRotation(pos,rot);modes.viewCamera.useOcclusionCulling=occ;
 }
}
}
