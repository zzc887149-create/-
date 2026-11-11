using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateUpperTier {
 static Vector3 P(float[] p){return new Vector3(-p[0],p[2],-p[1]);}
 public static void Check(VenueModes modes){
  var data=JsonUtility.FromJson<JunctionCheckFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/Editor/upper_tier_checks.json"));
  var labels=new[]{"concrete","外碗赭红混凝土","楼梯红色防滑涂层","栏杆细金属"};
  var ids=JsonUtility.FromJson<MaterialFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/materials.json")).materials.Where(r=>labels.Contains(r.label)).Select(r=>r.name).ToArray();
  var colliders=new List<MeshCollider>();var failures=new List<string>();
  try{
   foreach(var r in modes.geometry.GetComponentsInChildren<MeshRenderer>())if(r.sharedMaterials.Any(m=>m&&ids.Contains(m.name))||r.name.StartsWith("Chunk_SEATS_")||r.name.StartsWith("Chunk_CROWD_")||r.name.StartsWith("Chunk_PHONES_")){
    var f=r.GetComponent<MeshFilter>();if(!f||!f.sharedMesh)continue;var c=r.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;colliders.Add(c);
   }
   Physics.SyncTransforms();
   foreach(var s in data.samples){var p=P(s.point);RaycastHit hit;if(!Physics.Raycast(p+Vector3.up*.04f,Vector3.down,out hit,.12f)||Mathf.Abs(hit.point.y-p.y)>.03f)failures.Add("Floor "+s.kind+" bay="+s.bay);if(Physics.Raycast(p+Vector3.up*.04f,Vector3.up,out hit,2.1f))failures.Add("Headroom "+s.kind+" bay="+s.bay+" hit="+hit.collider.name);}
   foreach(var s in data.segments){RaycastHit hit;if(Physics.Linecast(P(s.a),P(s.b),out hit))failures.Add("Blocked "+s.kind+" hit="+hit.collider.name);}
  }finally{foreach(var c in colliders)UnityEngine.Object.DestroyImmediate(c);}
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/upper_tier_unity_validation.txt"),"Upper-tier samples: "+data.samples.Length+"\nRoute segments: "+data.segments.Length+"\nFailures: "+failures.Count+"\n"+string.Join("\n",failures.Take(30)));
  if(failures.Count>0)throw new Exception("Upper-tier check: "+failures[0]);Debug.Log("UPPER_TIER_VALIDATED");
 }
}
}
