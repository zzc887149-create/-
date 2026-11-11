using UnityEngine;
using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
namespace ZhaoLeiBirdsNestV3 {
// Runs only when explicitly launched with -venueBenchmark <report-directory>.
public class VenueBenchmark:MonoBehaviour {
 string output;
 [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)] static void Initialize(){
  var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,"-venueBenchmark");
  if(i>=0&&i+1<args.Length){var test=new GameObject("Validation runner").AddComponent<VenueBenchmark>();test.output=args[i+1];}
 }
 IEnumerator Start(){
  if(SystemInfo.graphicsDeviceType==UnityEngine.Rendering.GraphicsDeviceType.Null){Debug.LogError("Venue benchmark requires a graphics device");Application.Quit(1);yield break;}
  Directory.CreateDirectory(output);QualitySettings.vSyncCount=0;Application.targetFrameRate=-1;Application.runInBackground=true;
  yield return new WaitForSecondsRealtime(3);
  var modes=FindFirstObjectByType<VenueModes>();modes.showPanel=false;modes.animateBeams=false;
  const int measured=30;
  var lines=new List<string>{"view,mode,optimization,average_render_readback_ms,p95_render_readback_ms,sampled_frames"};
  var camera=modes.viewCamera;var previousTarget=camera.targetTexture;
  var target=new RenderTexture(960,600,24,RenderTextureFormat.ARGBHalf){antiAliasing=4};target.Create();
  var readback=new Texture2D(1,1,TextureFormat.RGBAHalf,false,true);camera.targetTexture=target;
  try{
  for(int view=0;view<modes.fly.viewpoints.Length;view++)foreach(bool night in new[]{false,true})foreach(bool optimized in new[]{false,true}){
   modes.fly.Jump(view);modes.SetNight(night);modes.SetOptimized(optimized);
   for(int w=0;w<10;w++){RenderAndReadback(camera,target,readback);yield return null;}
   var samples=new List<float>();float total=0;
   for(int f=0;f<measured;f++){yield return null;var timer=System.Diagnostics.Stopwatch.StartNew();RenderAndReadback(camera,target,readback);timer.Stop();float dt=(float)timer.Elapsed.TotalMilliseconds;samples.Add(dt);total+=dt;}
   samples.Sort();lines.Add((view+1)+","+(night?"night":"day")+","+optimized+","+(total/measured).ToString("F2",CultureInfo.InvariantCulture)+","+samples[Mathf.CeilToInt(measured*.95f)-1].ToString("F2",CultureInfo.InvariantCulture)+","+measured);
  }
  }finally{camera.targetTexture=previousTarget;target.Release();Destroy(target);Destroy(readback);}
  File.WriteAllLines(Path.Combine(output,"performance.csv"),lines);
  File.WriteAllText(Path.Combine(output,"performance_environment.txt"),"Unity "+Application.unityVersion+"\nGPU: "+SystemInfo.graphicsDeviceName+"\nRender target: 960 x 600, HDR, 4x MSAA\nPipeline: Built-in; balanced quality. Every viewpoint, day/night, optimized/unoptimized.\n30 explicit camera renders per case after 10 warm-up renders. Each render includes synchronous one-pixel GPU readback.\nReported milliseconds include render submission and GPU synchronization; they are NOT interactive window FPS.\nUnoptimized forces near LOD and disables baked occlusion.\n");
  Application.Quit();
 }
 static void RenderAndReadback(Camera camera,RenderTexture target,Texture2D readback){
  camera.Render();var previous=RenderTexture.active;
  try{RenderTexture.active=target;readback.ReadPixels(new Rect(480,300,1,1),0,0,false);}finally{RenderTexture.active=previous;}
 }
}
}
