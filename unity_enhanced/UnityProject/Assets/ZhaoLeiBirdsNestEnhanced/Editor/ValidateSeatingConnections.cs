using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
[Serializable] public class SeatingPort { public int bay,level,step_count;public float[] entry,rad,tan;public float height,concourse,length,step_run; }
[Serializable] public class SeatingPortFile { public SeatingPort[] ports; }
public static class ValidateSeatingConnections {
 static Vector3 Point(SeatingPort p,float t,float w,float z){return new Vector3(-(p.entry[0]+p.rad[0]*t+p.tan[0]*w),z,-(p.entry[1]+p.rad[1]*t+p.tan[1]*w));}
 public static void Check(VenueModes modes){
  var ports=JsonUtility.FromJson<SeatingPortFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/Editor/seating_entries.json")).ports;
  var records=JsonUtility.FromJson<MaterialFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/materials.json")).materials;
  var labels=new[]{"concrete","外碗赭红混凝土","楼梯红色防滑涂层","栏杆细金属"};var ids=records.Where(r=>labels.Contains(r.label)).Select(r=>r.name).ToArray();
  var colliders=new List<MeshCollider>();var failures=new List<string>();int surfaces=0,paths=0;
  try{
   foreach(var r in modes.geometry.GetComponentsInChildren<MeshRenderer>())if(r.sharedMaterials.Any(m=>m&&ids.Contains(m.name))){
    var f=r.GetComponent<MeshFilter>();if(!f||!f.sharedMesh)continue;var c=r.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;colliders.Add(c);
   }
   Physics.SyncTransforms();
   foreach(var p in ports){
    var ts=new List<float>{-.14f,-.05f};for(int i=0;i<(int)((p.length-p.step_run)/.23f);i++)ts.Add(i*.23f);
    for(int i=0;i<p.step_count;i++)ts.Add(p.length-(i+.5f)*.28f);ts.Add(p.length+.05f);ts.Add(p.length+.3f);ts.Sort();
    foreach(float w in new[]{-.75f,0,.75f}){
     Vector3 previous=Vector3.zero;bool first=true;
     foreach(float t in ts){
      float top=t<p.length-p.step_run?p.height:t<p.length?p.concourse+Mathf.Min(p.step_count,Mathf.FloorToInt((p.length-t)/.28f)+1)*(p.height-p.concourse)/p.step_count:p.concourse;
      var q=Point(p,t,w,top+.05f);RaycastHit hit;surfaces++;
      if(!Physics.Raycast(q,Vector3.down,out hit,.1f)||Mathf.Abs(hit.point.y-top)>.025f)failures.Add("Floor bay="+p.bay+" F="+p.level+" t="+t+" w="+w);
      if(Physics.Raycast(q,Vector3.up,out hit,2.1f))failures.Add("Headroom bay="+p.bay+" F="+p.level+" t="+t+" hit="+hit.collider.name);
      var body=q+Vector3.up*1.25f;if(!first){paths++;if(Physics.Linecast(previous,body,out hit))failures.Add("Blocked path bay="+p.bay+" F="+p.level+" t="+t+" hit="+hit.collider.name);}previous=body;first=false;
     }
    }
   }
  }finally{foreach(var c in colliders)UnityEngine.Object.DestroyImmediate(c);}
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/seating_unity_validation.txt"),"Imported FBX connections: "+ports.Length+"\nFloor/headroom samples: "+surfaces+"\nBody path segments: "+paths+"\nFailures: "+failures.Count+"\n"+string.Join("\n",failures.Take(40)));
  if(failures.Count>0)throw new Exception("Seating connections validation failed: "+failures[0]);
  var cam=modes.viewCamera;var pos=cam.transform.position;var rot=cam.transform.rotation;bool occ=cam.useOcclusionCulling;cam.useOcclusionCulling=false;
  foreach(var p in ports.Where(p=>p.bay==0)){
   modes.SetNight(false);cam.transform.position=Point(p,p.length+1,0,p.concourse+1.8f);cam.transform.LookAt(Point(p,-3,0,p.height+1.5f));
   BuildEnhancedVenue.Capture(cam,Path.Combine(BuildEnhancedVenue.Output,"checks/Seating_entry_F"+p.level+".png"));
  }
  cam.transform.SetPositionAndRotation(pos,rot);cam.useOcclusionCulling=occ;Debug.Log("SEATING_CONNECTIONS_VALIDATED");
 }
}
}
