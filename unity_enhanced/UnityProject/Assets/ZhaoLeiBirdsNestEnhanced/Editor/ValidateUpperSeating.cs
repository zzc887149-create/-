using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateUpperSeating {
 [Serializable] class Portal { public int tier,bay; public string band; public float[] point; }
 [Serializable] class Layout { public Portal[] portals; }
 static Vector3 P(float[] p){return new Vector3(-p[0],p[2],-p[1]);}
 public static void Rebuild(){
  BuildEnhancedVenue.BuildAll();
  ApplyConfirmedViews();
  BuildEnhancedVenue.RefreshArchitectureLighting();
 }
 static void ApplyConfirmedViews(){
  var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();
  var layout=JsonUtility.FromJson<Layout>(File.ReadAllText(BuildEnhancedVenue.Base+"/Editor/v23_portals.json"));
  var ts=modes.geometry.GetComponentsInChildren<Transform>(true);
  modes.fly.viewpoints=ts.Where(t=>t.name.StartsWith("VIEW_")).GroupBy(t=>t.name.Substring(5,2)).Select(g=>g.First()).OrderBy(t=>t.name).ToArray();
  modes.fly.targets=modes.fly.viewpoints.Select(v=>ts.First(t=>t.name==v.name.Replace("VIEW_","LOOK_"))).ToArray();
  if(modes.fly.viewpoints.Length!=18)throw new Exception("Expected exactly 18 unique viewpoints");
  EditorUtility.SetDirty(modes.fly);
  // Seating-chart overview: existing ninth button now shows all 26 field blocks.
  modes.fly.viewpoints[8].position=new Vector3(0,70,70);
  modes.fly.targets[8].position=Vector3.zero;
  for(int tier=1;tier<=3;tier++){
   string band=tier==1?"rear":tier==2?"middle":"lower_middle";
   var portal=layout.portals.First(p=>p.tier==tier&&p.band==band&&p.bay==0);
   Vector3 e=P(portal.point),rad=new Vector3(e.x,0,e.z).normalized;
   string number=(13+tier).ToString("00");
   ts.First(t=>t.name.StartsWith("VIEW_"+number+"_")).position=e-rad*(tier==3?8.5f:6f)+Vector3.up*(tier==3?3.6f:1.8f);
   ts.First(t=>t.name.StartsWith("LOOK_"+number+"_")).position=e+Vector3.up*1.1f;
  }
  ts.First(t=>t.name.StartsWith("VIEW_17_")).position=P(new[]{134.5653f,8.6798f,27f});
  ts.First(t=>t.name.StartsWith("LOOK_17_")).position=P(new[]{129.2722f,20.1681f,26f});
  foreach(var t in ts.Where(t=>t.name.StartsWith("VIEW_")||t.name.StartsWith("LOOK_"))){PrefabUtility.RecordPrefabInstancePropertyModifications(t);EditorUtility.SetDirty(t);}
  EditorSceneManager.MarkSceneDirty(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
 }
 public static void RebuildAndValidate(){Rebuild();Run();}
 public static void VerifyAndCapture(){EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);ApplyConfirmedViews();BuildEnhancedVenue.RefreshArchitectureLighting();Run();}
 static bool Supported(Vector3 p,out bool seam){
  seam=false;RaycastHit hit;
  if(Physics.Raycast(p+Vector3.up*.05f,Vector3.down,out hit,.14f)&&Mathf.Abs(hit.point.y-p.y)<=.045f)return true;
  // PhysX can miss an exact shared triangle edge. Accept only if all four
  // corners of a 2 mm footprint have a floor at the expected elevation.
  foreach(float x in new[]{-.001f,.001f})foreach(float z in new[]{-.001f,.001f})
   if(!Physics.Raycast(p+new Vector3(x,.05f,z),Vector3.down,out hit,.14f)||Mathf.Abs(hit.point.y-p.y)>.045f)return false;
  seam=true;return true;
 }
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();
  var data=JsonUtility.FromJson<JunctionCheckFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/Editor/v23_checks.json"));
  var cols=new List<MeshCollider>();var failures=new List<string>();int supportedSeams=0;
  if(!modes.geometry.GetComponentsInChildren<Transform>(true).Any(t=>t.name.StartsWith("Chunk_SEATS_V23_")))throw new Exception("Expected v23 seating model; mixed delivery rejected");
  if(modes.fly.viewpoints.Length!=18||Vector3.Distance(modes.fly.viewpoints[16].position,P(new[]{134.5653f,8.6798f,27f}))>.01f)throw new Exception("Expected saved v23 rear-gallery viewpoint");
  var passages=data.samples.Where(s=>s.kind.StartsWith("L1_")||s.kind.StartsWith("L2_")||s.kind.StartsWith("L3_")).GroupBy(s=>s.kind).ToArray();
  if(passages.Length!=120)failures.Add("Expected 120 independent level passages");
  foreach(var g in passages)if(g.Max(s=>s.point[2])-g.Min(s=>s.point[2])>.001f)failures.Add("Passage elevation change: "+g.Key);
  bool back=Physics.queriesHitBackfaces;Physics.queriesHitBackfaces=true;
  try{
   foreach(var r in modes.geometry.GetComponentsInChildren<MeshRenderer>()){
    if(r.name.EndsWith("_L1")||r.name.Contains("PHONES")||r.name.Contains("LED"))continue;
    var f=r.GetComponent<MeshFilter>();if(!f||!f.sharedMesh||f.sharedMesh.vertexCount==0)continue;
    var c=r.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;cols.Add(c);
   }
   Physics.SyncTransforms();
   foreach(var s in data.samples){var p=P(s.point);RaycastHit hit;
    bool seam;if(!Supported(p,out seam))failures.Add("Floor "+s.kind+" bay="+s.bay+" at="+p.ToString("F6"));else if(seam)supportedSeams++;
    if(Physics.Raycast(p+Vector3.up*.16f,Vector3.up,out hit,1.98f))failures.Add("Headroom "+s.kind+" bay="+s.bay+" at="+p+" hit="+hit.collider.name);
   }
   foreach(var s in data.segments){RaycastHit hit;if(Physics.Linecast(P(s.a),P(s.b),out hit))failures.Add("Blocked "+s.kind+" at="+P(s.a)+" hit="+hit.collider.name);}
   // Independently protect all existing exterior stair flights and their concourse seams.
   for(int bay=0;bay<12;bay++)for(int flight=0;flight<6;flight++)for(int step=0;step<25;step++)foreach(float side in new[]{-.55f,.55f}){
    float dir=flight%2==0?1:-1;var p=Exterior(bay,(flight%2)*2.6f-1.3f+side,(step*.28f-3.4f)*dir,flight*3.75f+(step+1)*.15f+.04f);RaycastHit hit;
    if(Physics.Raycast(p,Vector3.up,out hit,2.1f))failures.Add("Exterior headroom bay="+bay+" flight="+flight+" step="+step+" hit="+hit.collider.name);
   }
   for(int bay=0;bay<12;bay++)foreach(float z in new[]{7.5f,15f,22.5f})foreach(float x in new[]{-1.8f,-.6f,.6f,1.8f})foreach(float y in new[]{-5f,-4.65f,-4.55f,-4.2f,-3.8f}){
    RaycastHit hit;if(!Physics.Raycast(Exterior(bay,x,y,z+.1f),Vector3.down,out hit,.15f)||Mathf.Abs(hit.point.y-z)>.005f)failures.Add("Exterior landing bay="+bay+" floor="+z+" x="+x+" y="+y+" hit="+(hit.collider?hit.collider.name:"none")+" at="+hit.point.ToString("F6"));
   }
  }finally{foreach(var c in cols)UnityEngine.Object.DestroyImmediate(c);Physics.queriesHitBackfaces=back;}
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/v23_unity_validation.txt"),"Flat floor access imported geometry\nSamples: "+data.samples.Length+"\nSegments: "+data.segments.Length+"\nSupported triangle seams (four 1 mm offsets): "+supportedSeams+"\nExterior stair samples: 3600\nExterior landing samples: 720\nFailures: "+failures.Count+"\n"+string.Join("\n",failures));
  if(failures.Count>0)throw new Exception("Flat floor access circulation: "+failures[0]);
  Debug.Log("FLAT_ACCESS_CIRCULATION_SUCCESS");
 }
 static Vector3 Exterior(int bay,float x,float y,float z){float a=bay*Mathf.PI/6+.11f;return new Vector3(-(126.5f*Mathf.Cos(a)+x*Mathf.Cos(a)-y*Mathf.Sin(a)),z,-(143.5f*Mathf.Sin(a)+x*Mathf.Sin(a)+y*Mathf.Cos(a)));}
}
}
