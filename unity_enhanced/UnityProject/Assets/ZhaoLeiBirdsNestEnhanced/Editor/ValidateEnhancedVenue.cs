using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using System;
using System.IO;
using System.Collections.Generic;
namespace ZhaoLeiBirdsNestV3 {
[InitializeOnLoad] public static class ValidateEnhancedVenue {
 const string Key="BirdsNestV3QA";static double ready;static int step;static List<string> rows=new List<string>();
 static ValidateEnhancedVenue(){EditorApplication.update+=Tick;}
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);SessionState.SetBool(Key,true);EditorApplication.EnterPlaymode();
 }
 static void Tick(){
  if(!SessionState.GetBool(Key,false)||!EditorApplication.isPlaying)return;
  if(ready==0){ready=EditorApplication.timeSinceStartup+3;return;}if(EditorApplication.timeSinceStartup<ready)return;
  try{
   var m=UnityEngine.Object.FindFirstObjectByType<VenueModes>();if(!m)throw new Exception("Missing runtime controls");
   if(step==0){m.animateBeams=false;m.showPanel=false;rows.Add("mode,view,occlusion_differing_pixels_percent,max_RGB_difference,renderers_in_static_batches");}
   int viewCount=m.fly.viewpoints.Length;
   if(step<viewCount*2){
    bool night=step>=viewCount;int view=step%viewCount;m.SetNight(night);m.fly.Jump(view);m.SetOptimized(true);
    var cam=m.viewCamera;var path=Path.Combine(BuildEnhancedVenue.Output,"checks/Runtime_"+(night?"Night_":"Day_")+(view+1).ToString("00")+".png");
    BuildEnhancedVenue.Capture(cam,path);byte[] enabled=File.ReadAllBytes(path);cam.useOcclusionCulling=false;
    string tmp=Path.Combine(BuildEnhancedVenue.Output,"checks/occlusion_compare.png");BuildEnhancedVenue.Capture(cam,tmp);
    var a=new Texture2D(2,2);var b=new Texture2D(2,2);a.LoadImage(enabled);b.LoadImage(File.ReadAllBytes(tmp));var x=a.GetPixels32();var y=b.GetPixels32();int diff=0,max=0;
    for(int i=0;i<x.Length;i++){int d=Math.Max(Math.Abs(x[i].r-y[i].r),Math.Max(Math.Abs(x[i].g-y[i].g),Math.Abs(x[i].b-y[i].b)));if(d>12)diff++;max=Math.Max(d,max);}
    int batched=0;foreach(var r in m.geometry.GetComponentsInChildren<Renderer>())if(r.isPartOfStaticBatch)batched++;
    rows.Add((night?"night":"day")+","+(view+1)+","+(100.0*diff/x.Length).ToString("F5",System.Globalization.CultureInfo.InvariantCulture)+","+max+","+batched);
    if(diff>0)File.Copy(tmp,Path.Combine(BuildEnhancedVenue.Output,"checks/Unoccluded_"+(night?"Night_":"Day_")+(view+1).ToString("00")+".png"),true);
    UnityEngine.Object.Destroy(a);UnityEngine.Object.Destroy(b);File.Delete(tmp);cam.useOcclusionCulling=true;step++;ready=EditorApplication.timeSinceStartup+.1;
   }else{
    File.WriteAllLines(Path.Combine(BuildEnhancedVenue.Output,"checks/runtime_validation.csv"),rows);m.SetNight(true);m.fly.Jump(3);
    SessionState.SetBool(Key,false);Debug.Log("BIRDSNEST_V3_RUNTIME_SUCCESS");EditorApplication.ExitPlaymode();EditorApplication.delayCall+=()=>EditorApplication.Exit(0);
   }
  }catch(Exception e){SessionState.SetBool(Key,false);Debug.LogException(e);EditorApplication.Exit(1);}
 }
}
}
