using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System;
using System.IO;
using System.Collections.Generic;
namespace ZhaoLeiBirdsNestV3 {
public static class DiagnoseEntranceLighting {
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);
  var m=UnityEngine.Object.FindFirstObjectByType<VenueModes>();m.SetNight(true);m.SetOptimized(true);m.fly.Jump(13);m.animateBeams=false;
  var lights=UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None);
  var shadows=new LightShadows[lights.Length];var renderModes=new LightRenderMode[lights.Length];
  for(int i=0;i<lights.Length;i++){shadows[i]=lights[i].shadows;renderModes[i]=lights[i].renderMode;}
  var rows=new List<string>();var folder=Path.Combine(BuildEnhancedVenue.Output,"checks/v11_diagnostic");Directory.CreateDirectory(folder);
  var variants=new List<string>{"baseline","pixel","no_shadows","no_lights","no_post"};for(int i=0;i<lights.Length;i++)if(lights[i].type!=LightType.Directional&&Vector3.Distance(lights[i].transform.position,m.viewCamera.transform.position)<lights[i].range+20)variants.Add("light_"+i);
  foreach(string variant in variants){
   for(int i=0;i<lights.Length;i++){lights[i].enabled=variant!="no_lights";lights[i].shadows=variant=="no_shadows"?LightShadows.None:shadows[i];lights[i].renderMode=variant=="pixel"||variant=="light_"+i?LightRenderMode.ForcePixel:renderModes[i];}m.post.enabled=variant!="no_post";
   m.viewCamera.useOcclusionCulling=true;BuildEnhancedVenue.Capture(m.viewCamera,Path.Combine(folder,"warmup.png"));
   string a=Path.Combine(folder,variant+"_on.png"),b=Path.Combine(folder,variant+"_off.png");BuildEnhancedVenue.Capture(m.viewCamera,a);m.viewCamera.useOcclusionCulling=false;BuildEnhancedVenue.Capture(m.viewCamera,b);
   var ta=new Texture2D(2,2);var tb=new Texture2D(2,2);ta.LoadImage(File.ReadAllBytes(a));tb.LoadImage(File.ReadAllBytes(b));var pa=ta.GetPixels32();var pb=tb.GetPixels32();int count=0,max=0;
   for(int i=0;i<pa.Length;i++){int d=Math.Max(Math.Abs(pa[i].r-pb[i].r),Math.Max(Math.Abs(pa[i].g-pb[i].g),Math.Abs(pa[i].b-pb[i].b)));if(d>12)count++;max=Math.Max(max,d);}rows.Add(variant+",pixels="+count+",max="+max);UnityEngine.Object.DestroyImmediate(ta);UnityEngine.Object.DestroyImmediate(tb);
  }for(int i=0;i<lights.Length;i++)rows.Add("light_"+i+"="+lights[i].name);File.WriteAllLines(Path.Combine(folder,"results.txt"),rows);Debug.Log("ENTRANCE_DIAG_COMPLETE");
 }
}
}
