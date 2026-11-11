using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateStairConnections {
 static Vector3 Point(int bay,float x,float y,float z){float a=bay*Mathf.PI/6+.11f;return new Vector3(-(126.5f*Mathf.Cos(a)+x*Mathf.Cos(a)-y*Mathf.Sin(a)),z,-(143.5f*Mathf.Sin(a)+x*Mathf.Sin(a)+y*Mathf.Cos(a)));}
 public static void Run(){
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();InstallVenueDetails.Apply(modes);InstallBandDetails.Apply(modes);
  ValidateRearDeck.Check(modes);
  ValidateUpperTier.Check(modes);
  ValidateSeatingJunctions.Check(modes);
  ValidateSeatingConnections.Check(modes);
  var records=JsonUtility.FromJson<MaterialFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/materials.json")).materials;
  var ids=records.Where(r=>r.label=="concrete"||r.label=="外碗赭红混凝土").Select(r=>r.name).ToArray();
  var colliders=new List<MeshCollider>();var failures=new List<string>();int headSamples=0,seamSamples=0;
  try {
   foreach(var r in modes.geometry.GetComponentsInChildren<MeshRenderer>())if(r.sharedMaterials.Any(m=>m&&ids.Contains(m.name))){
    var filter=r.GetComponent<MeshFilter>();if(!filter||!filter.sharedMesh)continue;
    var col=r.gameObject.AddComponent<MeshCollider>();col.sharedMesh=filter.sharedMesh;colliders.Add(col);
   }
   Physics.SyncTransforms();
   for(int bay=0;bay<12;bay++)for(int flight=0;flight<6;flight++)for(int step=0;step<25;step++)foreach(float side in new[]{-.55f,.55f}){
    float dir=flight%2==0?1:-1;var p=Point(bay,(flight%2)*2.6f-1.3f+side,(step*.28f-3.4f)*dir,flight*3.75f+(step+1)*.15f+.04f);
    RaycastHit hit;headSamples++;if(Physics.Raycast(p,Vector3.up,out hit,2.1f))failures.Add("Headroom bay="+bay+" flight="+flight+" step="+step+" hit="+hit.collider.name);
   }
   for(int bay=0;bay<12;bay++)foreach(float z in new[]{7.5f,15f,22.5f})foreach(float x in new[]{-1.8f,-.6f,.6f,1.8f})foreach(float y in new[]{-5f,-4.65f,-4.55f,-4.2f,-3.8f}){
    RaycastHit hit;seamSamples++;if(!Physics.Raycast(Point(bay,x,y,z+.1f),Vector3.down,out hit,.15f)||Mathf.Abs(hit.point.y-z)>.005f)failures.Add("Landing gap bay="+bay+" floor="+z+" x="+x+" y="+y);
   }
  } finally {foreach(var c in colliders)UnityEngine.Object.DestroyImmediate(c);}
  var path=Path.Combine(BuildEnhancedVenue.Output,"checks/stair_unity_validation.txt");File.WriteAllText(path,"Imported FBX check\nHeadroom samples: "+headSamples+"\nLanding seam samples: "+seamSamples+"\nFailures: "+failures.Count+"\n"+string.Join("\n",failures.Take(30)));
  if(failures.Count>0)throw new Exception("Stair geometry validation failed: "+failures[0]);
  var cam=modes.viewCamera;var p0=cam.transform.position;var q0=cam.transform.rotation;
  foreach(int bay in new[]{0,3,4})foreach(float floor in new[]{7.5f,15f}){
   modes.SetNight(false);cam.transform.position=Point(bay,-6,-8,floor+4);cam.transform.LookAt(Point(bay,0,.7f,floor+.2f));
   BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/Stair_bay"+bay+"_floor"+floor.ToString("F1",System.Globalization.CultureInfo.InvariantCulture)+".png"));
  }
  cam.transform.SetPositionAndRotation(p0,q0);modes.SetNight(true);modes.fly.Jump(3);
  EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());AssetDatabase.SaveAssets();
  BuildEnhancedVenue.RefreshArchitectureLighting();Debug.Log("STAIR_CONNECTIONS_VALIDATED");BuildEnhancedVenue.BakeVisibility();
 }
}
}
