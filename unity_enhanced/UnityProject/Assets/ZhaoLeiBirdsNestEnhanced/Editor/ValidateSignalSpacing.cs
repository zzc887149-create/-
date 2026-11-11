using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateSignalSpacing {
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();
  var renderers=modes.geometry.GetComponentsInChildren<Renderer>();
  var letters=Enumerable.Range(14,6).Select(i=>renderers.Single(r=>r.name.StartsWith("Chunk_")&&r.sharedMaterials.Any(m=>m&&m.name=="BNE_"+i.ToString("000")))).ToArray();
  var gaps=Enumerable.Range(0,5).Select(i=>-letters[i+1].bounds.max.x+letters[i].bounds.min.x).ToArray();
  if(gaps.Any(g=>Mathf.Abs(g-1.91776f)>.002f))throw new Exception("SIGNAL spacing mismatch: "+string.Join(",",gaps));
  var camera=modes.viewCamera;var position=camera.transform.position;var rotation=camera.transform.rotation;bool night=modes.night;
  camera.transform.position=new Vector3(-5.75f,5.8f,-43);camera.transform.LookAt(new Vector3(-5.75f,5.8f,-67.6f));
  foreach(bool dark in new[]{false,true}){modes.SetNight(dark);BuildEnhancedVenue.Capture(camera,Path.Combine(BuildEnhancedVenue.Output,"checks/SIGNAL_"+(dark?"night":"day")+".png"));}
  camera.transform.SetPositionAndRotation(position,rotation);modes.SetNight(night);
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/signal_unity_validation.txt"),"SIGNAL visible edge gaps in metres: "+string.Join(", ",gaps)+"\nPASS: each gap within 0.002 m of 1.91776 m.\n");
  EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());AssetDatabase.SaveAssets();
  Debug.Log("SIGNAL_SPACING_VALIDATED");BuildEnhancedVenue.BakeVisibility();
 }
}
}
