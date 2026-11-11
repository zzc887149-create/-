using UnityEngine;
using System;
using System.IO;
using System.Collections.Generic;
namespace ZhaoLeiBirdsNestV3 {
public static class ValidateRearDeck {
 public static void Check(VenueModes m){
  var cols=new List<MeshCollider>();var failures=new List<string>();int samples=0;
  try{
   foreach(var r in m.geometry.GetComponentsInChildren<MeshRenderer>())if(r.name.StartsWith("Chunk_ARCH_")){
    var f=r.GetComponent<MeshFilter>();if(!f||!f.sharedMesh)continue;var c=r.gameObject.AddComponent<MeshCollider>();c.sharedMesh=f.sharedMesh;cols.Add(c);
   }Physics.SyncTransforms();
   for(int i=0;i<720;i++)foreach(float t in new[]{.015f,.25f,.5f,.75f,.985f}){
    float a=(i+.5f)*Mathf.PI*2/720;var p=new Vector3(-(96.7f+(101.48f-96.7f)*t)*Mathf.Cos(a),13.086f,-(126.7f+(130.98f-126.7f)*t)*Mathf.Sin(a));RaycastHit hit;samples++;
    if(!Physics.Raycast(p+Vector3.up*.04f,Vector3.down,out hit,.12f)||Mathf.Abs(hit.point.y-p.y)>.02f)failures.Add("Floor "+i+" t="+t);
    if(t>.1f&&t<.9f&&Physics.Raycast(p+Vector3.up*.05f,Vector3.up,out hit,2.1f))failures.Add("Headroom "+i+" t="+t+" hit="+hit.collider.name);
   }
  }finally{foreach(var c in cols)UnityEngine.Object.DestroyImmediate(c);}
  File.WriteAllText(Path.Combine(BuildEnhancedVenue.Output,"checks/rear_deck_unity_validation.txt"),"Floor samples including boundary seams: "+samples+"\nHeadroom samples in clear walking area: 2160\nFailures: "+failures.Count+"\n"+string.Join("\n",failures));
  if(failures.Count>0)throw new Exception("Rear deck: "+failures[0]);Debug.Log("REAR_DECK_VALIDATED");
 }
}
}
