using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
[Serializable] public class JunctionSample { public string kind;public int bay;public float[] point; }
[Serializable] public class JunctionRoute { public string kind;public float[][] points; }
[Serializable] public class JunctionFile { public JunctionSample[] samples;public JunctionRoute[] routes; }
public static class ValidateSeatingJunctions {
 static Vector3 P(float[] p){return new Vector3(-p[0],p[2],-p[1]);}
 public static void Check(VenueModes modes){
  // JsonUtility does not support nested arrays; route segments are flattened in the exported check file.
  var data=JsonUtility.FromJson<JunctionCheckFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/Editor/junction_checks.json"));
  var labels=new[]{"concrete","外碗赭红混凝土","楼梯红色防滑涂层","栏杆细金属"};
  var ids=JsonUtility.FromJson<MaterialFile>(File.ReadAllText(BuildEnhancedVenue.Base+"/materials.json")).materials.Where(r=>labels.Contains(r.label)).Select(r=>r.name).ToArray();
  var colliders=new List<MeshCollider>();var failures=new List<string>();
  try{
   foreach(var r in modes.geometry.GetComponentsInChildren<MeshRenderer>())if(r.sharedMaterials.Any(m=>m&&ids.Contains(m.name))||r.name.StartsWith("Chunk_SEATS_")||r.name.StartsWith("Chunk_CROWD_")){var f=r.GetComponent<MeshFilter>();if(!f||!f.sharedMesh)continue;var c=r.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;colliders.Add(c);}
   Physics.SyncTransforms();
   foreach(var s in data.samples){var p=P(s.point);RaycastHit hit;
    if(!Physics.Raycast(p+Vector3.up*.04f,Vector3.down,out hit,.1f)||Mathf.Abs(hit.point.y-p.y)>.025f)failures.Add("Floor "+s.kind+" bay="+s.bay+" point="+p);
    if(Physics.Raycast(p+Vector3.up*.04f,Vector3.up,out hit,2.1f))failures.Add("Headroom "+s.kind+" bay="+s.bay+" hit="+hit.collider.name);
   }
   foreach(var s in data.segments){RaycastHit hit;if(Physics.Linecast(P(s.a),P(s.b),out hit))failures.Add("Blocked route "+s.kind+" hit="+hit.collider.name);}
  }finally{foreach(var c in colliders)UnityEngine.Object.DestroyImmediate(c);}
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/junction_unity_validation.txt"),"Landing/aisle samples: "+data.samples.Length+"\nPath segments: "+data.segments.Length+"\nFailures: "+failures.Count+"\n"+string.Join("\n",failures.Take(30)));
  if(failures.Count>0)throw new Exception("Junction check: "+failures[0]);
  InspectSeatingMouths.Capture(modes);Debug.Log("SEATING_JUNCTIONS_VALIDATED");
 }
}
[Serializable] public class JunctionSegment { public string kind;public float[] a,b; }
[Serializable] public class JunctionCheckFile { public JunctionSample[] samples;public JunctionSegment[] segments; }
}
