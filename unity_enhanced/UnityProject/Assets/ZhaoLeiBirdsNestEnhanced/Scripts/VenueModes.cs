using UnityEngine;
using UnityEngine.Rendering;
using System;
namespace ZhaoLeiBirdsNestV3 {
[Serializable] public class EmissionSetting { public Material material;public Color day,night; }
public class VenueModes:MonoBehaviour {
 public Camera viewCamera;public BirdsNestFlyCamera fly;public VenuePostFX post;
 public Light sun;public GameObject nightRig;public Transform[] beams;
 public EmissionSetting[] emissions;public LODGroup[] lods;public GameObject geometry;
 public bool night=true,optimized=true,showPanel=true,animateBeams=true;
 public int quality=1;
 Quaternion[] beamRotations;float smoothDelta=.02f;Font uiFont;GUIStyle label,button;bool batched;
 readonly string[] names={"外部全景","另一侧外观","外场地面","正对舞台","反向看台","场内侧面","环廊","舞台背面","内场分区与中控台"};
 void Start(){SetNight(night);SetOptimized(optimized);SetQuality(quality);beamRotations=new Quaternion[beams.Length];for(int i=0;i<beams.Length;i++)beamRotations[i]=beams[i].rotation;uiFont=Font.CreateDynamicFontFromOSFont(new[]{"Microsoft YaHei","Noto Sans CJK SC","Arial"},16);if(geometry&&!batched){bool existing=false;foreach(var r in geometry.GetComponentsInChildren<Renderer>())if(r.isPartOfStaticBatch){existing=true;break;}if(!existing)StaticBatchingUtility.Combine(geometry);batched=true;}}
 public void SetNight(bool value){
  night=value;if(nightRig)nightRig.SetActive(value);
  // Keep decorative stage pools in a consistent lighting path across visibility changes.
  if(nightRig)foreach(var light in nightRig.GetComponentsInChildren<Light>(true))
   if(light.name.StartsWith("Stage pool ",StringComparison.Ordinal)){
    light.renderMode=LightRenderMode.ForceVertex;
   }
  sun.intensity=value?.06f:1.05f;sun.color=value?new Color(.30f,.43f,.7f):new Color(1,.94f,.85f);
  RenderSettings.ambientMode=AmbientMode.Trilight;
  RenderSettings.ambientSkyColor=value?new Color(.055f,.075f,.12f):new Color(.57f,.64f,.75f);
  RenderSettings.ambientEquatorColor=value?new Color(.022f,.028f,.045f):new Color(.34f,.37f,.41f);
  RenderSettings.ambientGroundColor=value?new Color(.013f,.017f,.025f):new Color(.18f,.18f,.19f);
  // Update the probe synchronously: camera previews and day/night switches must not retain a stale sky bake.
  var probe=new SphericalHarmonicsL2();
  probe.AddAmbientLight(value?new Color(.022f,.030f,.048f):new Color(.32f,.36f,.42f));
  probe.AddDirectionalLight(Vector3.up,value?new Color(.045f,.065f,.11f):new Color(.62f,.70f,.82f),value?.12f:.35f);
  RenderSettings.ambientProbe=probe;
  viewCamera.backgroundColor=value?new Color(.003f,.006f,.015f):new Color(.27f,.39f,.55f);
  RenderSettings.fog=false;
  if(post){post.exposure=value?1.10f:1.05f;post.bloom=value?.22f:.04f;}
  foreach(var e in emissions)if(e.material)e.material.SetColor("_EmissionColor",value?e.night:e.day);
 }
 public void SetOptimized(bool value){optimized=value;foreach(var l in lods)l.ForceLOD(value?-1:0);viewCamera.useOcclusionCulling=value;}
 public void SetQuality(int value){
  quality=Mathf.Clamp(value,0,2);QualitySettings.lodBias=quality==0?.6f:quality==1?1:1.8f;
  QualitySettings.shadowDistance=quality==0?80:quality==1?180:260;
  QualitySettings.antiAliasing=quality==0?2:4;QualitySettings.pixelLightCount=quality==0?2:4;
 }
 void Update(){
  smoothDelta=Mathf.Lerp(smoothDelta,Time.unscaledDeltaTime,.07f);
#if ENABLE_INPUT_SYSTEM
  var k=UnityEngine.InputSystem.Keyboard.current;if(k!=null){if(k.nKey.wasPressedThisFrame)SetNight(!night);if(k.hKey.wasPressedThisFrame)showPanel=!showPanel;}
#else
  if(Input.GetKeyDown(KeyCode.N))SetNight(!night);if(Input.GetKeyDown(KeyCode.H))showPanel=!showPanel;
#endif
  if(night&&animateBeams&&beamRotations!=null)for(int i=0;i<beams.Length;i++)beams[i].rotation=beamRotations[i]*Quaternion.Euler(Mathf.Sin(Time.time*.17f+i*.35f)*2.5f,Mathf.Sin(Time.time*.13f+i*.4f)*3.5f,0);
 }
 void OnGUI(){
  if(!showPanel)return;
  float scale=Mathf.Min(Mathf.Clamp(Screen.height/900f,.8f,1.5f),Screen.height/718f,Screen.width/313f);var old=GUI.matrix;GUI.matrix=Matrix4x4.Scale(new Vector3(scale,scale,1));
  if(label==null){label=new GUIStyle(GUI.skin.label){font=uiFont,fontSize=14,wordWrap=true};button=new GUIStyle(GUI.skin.button){font=uiFont,fontSize=14};}
  GUI.Box(new Rect(14,14,285,694),"");
  GUI.Label(new Rect(28,25,255,47),"鸟巢全场 · 内场分区 v25\n"+(night?"赵雷·没有信号｜夜景":"赵雷·没有信号｜日间"),label);
  if(GUI.Button(new Rect(28,78,255,30),night?"切换到日间  [N]":"切换到夜景  [N]",button))SetNight(!night);
  for(int i=0;i<fly.viewpoints.Length&&i<9;i++)if(GUI.Button(new Rect(28,119+i*25,255,23),(i+1)+"  "+names[i],button))fly.Jump(i);
  var closeNames=new[]{"舞台近景","楼梯连通","纪念空座"};for(int i=0;i<3;i++)if(fly.viewpoints.Length>9+i&&GUI.Button(new Rect(28+i*86,348,83,28),closeNames[i],button))fly.Jump(9+i);
  if(fly.viewpoints.Length>12&&GUI.Button(new Rect(28,382,255,28),"乐队平台 · 大锣与键盘打击乐",button))fly.Jump(12);
  if(fly.viewpoints.Length>13&&GUI.Button(new Rect(28,416,255,28),"第一层 · 后排入口与环廊",button))fly.Jump(13);
  if(fly.viewpoints.Length>14&&GUI.Button(new Rect(28,450,255,28),"第二层 · 中入口与两侧梯道",button))fly.Jump(14);
  if(fly.viewpoints.Length>15&&GUI.Button(new Rect(28,484,255,28),"第三层 · 扩充座席与洞口",button))fly.Jump(15);
  if(fly.viewpoints.Length>16&&GUI.Button(new Rect(28,518,255,28),"公共楼梯 · 原梯续接",button))fly.Jump(16);
  if(fly.viewpoints.Length>17&&GUI.Button(new Rect(28,552,255,28),"后方大屏 · 背影歌词提词器",button))fly.Jump(17);
  if(GUI.Button(new Rect(28,590,255,30),"画质："+(quality==0?"流畅":quality==1?"均衡":"精细")+"  · 点击切换",button))SetQuality((quality+1)%3);
  GUI.Label(new Rect(28,629,255,67),"WASD 移动 · Q/E 升降\n按住右键转头 · Shift 加速\nH 隐藏面板  |  "+(1/Mathf.Max(.001f,smoothDelta)).ToString("F0")+" FPS",label);
  GUI.matrix=old;
 }
}
}
