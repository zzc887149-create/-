using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

namespace ZhaoLeiBirdsNestV3 {
[Serializable] public class MaterialRecord {public string name,label,texture,normal;public float[] baseColor,emission;public float roughness,metallic,strength;public bool vertexColor;}
[Serializable] public class MaterialFile {public MaterialRecord[] materials;}
public static class BuildEnhancedVenue {
 public const string Base="Assets/ZhaoLeiBirdsNestEnhanced";
 public const string ScenePath=Base+"/Scenes/BirdsNest_Enhanced.unity";
 static string Model=Base+"/Models/BirdsNest_Enhanced.fbx";
 static Vector3 origin,bx,by,bz;
 static Vector3 B(float x,float y,float z){return origin+bx*x+by*y+bz*z;}
 static Color C(float[] a){return new Color(a[0],a[1],a[2],a.Length>3?a[3]:1);}
 public static string Output{get{return Directory.GetParent(Application.dataPath).Parent.FullName;}}
 [MenuItem("Tools/Zhao Lei Birds Nest/Build Enhanced Day Night Scene")]
 public static void BuildAll(){
  if(!Application.isBatchMode&&!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())return;
  if(GraphicsSettings.currentRenderPipeline!=null)throw new Exception("Enhanced version currently targets Built-in rendering. Open the supplied Unity 6 project.");
  foreach(var sub in new[]{"Materials","Scenes","Prefabs","Generated"})Directory.CreateDirectory(Base+"/"+sub);
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
  PlayerSettings.colorSpace=ColorSpace.Linear;
  var imp=(ModelImporter)AssetImporter.GetAtPath(Model);
  imp.globalScale=1;imp.useFileScale=true;imp.importNormals=ModelImporterNormals.Import;imp.importTangents=ModelImporterTangents.CalculateMikk;
  imp.importCameras=false;imp.importLights=false;imp.importAnimation=false;imp.isReadable=true;imp.generateSecondaryUV=false;imp.SaveAndReimport();
  var records=JsonUtility.FromJson<MaterialFile>(File.ReadAllText(Base+"/materials.json")).materials;
  var maps=new Dictionary<string,Material>();var emission=new List<EmissionSetting>();
  foreach(var v in records){
   bool architecture=v.label=="外层浅灰钢带"||v.label=="外碗赭红混凝土"||v.label=="membrane";
   var shader=Shader.Find(v.vertexColor?"BirdsNest/VertexLit":architecture?"BirdsNest/ArchitecturalLit":"Standard");if(!shader)throw new Exception("Missing venue shader");
   var path=Base+"/Materials/"+v.name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);
   if(!m){m=new Material(shader);AssetDatabase.CreateAsset(m,path);}else m.shader=shader;
   m.enableInstancing=true;m.SetColor("_Color",C(v.baseColor));m.SetFloat("_Glossiness",1-v.roughness);
   if(m.HasProperty("_Metallic"))m.SetFloat("_Metallic",v.metallic);
   Texture2D tex=null;
   if(!string.IsNullOrEmpty(v.texture)){
    string tp=Base+"/Textures/"+v.texture;var ti=(TextureImporter)AssetImporter.GetAtPath(tp);ti.mipmapEnabled=true;ti.anisoLevel=8;ti.maxTextureSize=2048;ti.SaveAndReimport();
    tex=AssetDatabase.LoadAssetAtPath<Texture2D>(tp);m.SetTexture("_MainTex",tex);
   }
   if(!string.IsNullOrEmpty(v.normal)){
    string np=Base+"/Textures/"+v.normal;var ni=(TextureImporter)AssetImporter.GetAtPath(np);ni.textureType=TextureImporterType.NormalMap;ni.maxTextureSize=1024;ni.SaveAndReimport();
    m.SetTexture("_BumpMap",AssetDatabase.LoadAssetAtPath<Texture2D>(np));m.SetFloat("_BumpScale",.35f);m.EnableKeyword("_NORMALMAP");
   }
   if(architecture)emission.Add(ArchitectureEmission(m,v.label));
   else if(v.strength>0&&!v.vertexColor){
    m.EnableKeyword("_EMISSION");m.globalIlluminationFlags=MaterialGlobalIlluminationFlags.None;
    var e=new EmissionSetting{material=m,day=C(v.emission)*.16f,night=C(v.emission)*Mathf.Min(v.strength,3.5f)};
    if(v.label.StartsWith("现场LED_")){m.SetColor("_Color",Color.black);m.SetTexture("_EmissionMap",tex);e.day=Color.white*.8f;e.night=Color.white*1.2f;}
    else if(v.label.Contains("信封")){m.SetTexture("_EmissionMap",tex);e.day=Color.white*.08f;e.night=Color.white*.28f;}
    else if(v.label.Contains("旧墙")){m.SetTexture("_EmissionMap",tex);e.day=Color.black;e.night=new Color(.45f,.18f,.09f)*.14f;}
    else if(v.label=="phone"){e.day=Color.black;e.night=new Color(.55f,.75f,1)*5;}
    else if(v.label=="warm"){e.day=Color.black;e.night=C(v.emission)*.38f;}
    else {e.day=C(v.emission)*.08f;e.night=C(v.emission)*Mathf.Min(v.strength,1.6f);}
    emission.Add(e);
   }
   EditorUtility.SetDirty(m);maps[v.name]=m;imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),v.name),m);
  }
  AssetDatabase.SaveAssets();imp.SaveAndReimport();
  var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
  var root=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(Model));root.name="BirdsNest_Enhanced_360";
  foreach(var r in root.GetComponentsInChildren<Renderer>(true)){
   r.sharedMaterials=r.sharedMaterials.Select(m=>m&&maps.ContainsKey(m.name)?maps[m.name]:m).ToArray();
   bool detailed=r.name.Contains("CROWD")||r.name.Contains("SEATS")||r.name.Contains("CHAIRS")||r.name.Contains("PHONES");
   var flags=StaticEditorFlags.BatchingStatic|StaticEditorFlags.OccludeeStatic;
   // Thin lattice, audience and transparent beams must never become solid occluders.
   if(!detailed&&r.sharedMaterials.Any(m=>m.name==records.First(x=>x.label=="concrete").name||m.name==records.First(x=>x.label=="membrane").name))flags|=StaticEditorFlags.OccluderStatic;
   GameObjectUtility.SetStaticEditorFlags(r.gameObject,flags);
   if(detailed)r.shadowCastingMode=ShadowCastingMode.Off;
  }
  var transforms=root.GetComponentsInChildren<Transform>(true);
  Func<string,Transform> mark=(s)=>transforms.First(t=>t.name.StartsWith(s));
  origin=mark("LOOK_09").position;bz=(mark("LOOK_01").position-origin)/23;
  by=(mark("LOOK_04").position-origin-bz*17)/62;bx=-(mark("VIEW_06").position-origin-bz*20)/90;
  mark("VIEW_07").position=B(124,-22,10);mark("LOOK_07").position=B(122,25,10);
  var lods=new List<LODGroup>();
  foreach(var t in transforms.Where(t=>t.name.StartsWith("LOD_"))){
   var rs=t.GetComponentsInChildren<Renderer>();var near=rs.Where(r=>r.name.EndsWith("_L0")).ToArray();var far=rs.Where(r=>r.name.EndsWith("_L1")).ToArray();
   if(near.Length==0||far.Length==0)throw new Exception("Incomplete LOD group: "+t.name);
   var l=t.gameObject.AddComponent<LODGroup>();l.SetLODs(new[]{new LOD(.30f,near),new LOD(.002f,far)});l.RecalculateBounds();lods.Add(l);
  }
  QualitySettings.antiAliasing=4;QualitySettings.pixelLightCount=4;QualitySettings.shadowDistance=180;QualitySettings.shadowResolution=ShadowResolution.High;QualitySettings.lodBias=1;
  var sun=new GameObject("Venue Sun Moon").AddComponent<Light>();sun.type=LightType.Directional;sun.transform.rotation=Quaternion.Euler(48,-28,0);sun.shadows=LightShadows.Soft;sun.shadowBias=.08f;
  var cam=new GameObject("FullVenue_FreeFly").AddComponent<Camera>();cam.tag="MainCamera";cam.nearClipPlane=.15f;cam.farClipPlane=1500;cam.fieldOfView=60;cam.allowHDR=true;cam.allowMSAA=true;cam.clearFlags=CameraClearFlags.SolidColor;
  cam.gameObject.AddComponent<AudioListener>();var fly=cam.gameObject.AddComponent<BirdsNestFlyCamera>();
  fly.viewpoints=transforms.Where(t=>t.name.StartsWith("VIEW_")).GroupBy(t=>t.name.Substring(5,2)).Select(g=>g.First()).OrderBy(t=>t.name).ToArray();fly.targets=fly.viewpoints.Select(t=>transforms.First(q=>q.name==t.name.Replace("VIEW_","LOOK_"))).ToArray();fly.Jump(3);
  var post=cam.gameObject.AddComponent<VenuePostFX>();post.effectShader=Shader.Find("Hidden/BirdsNest/BloomTone");
  var rig=new GameObject("Concert night lighting");var beams=new List<Transform>();
  var beamMat=GetMaterial("ConcertBeam",Shader.Find("BirdsNest/SoftBeam"));beamMat.SetColor("_Color",new Color(.42f,.62f,1,.16f));
  var warmBeam=GetMaterial("WarmBeam",Shader.Find("BirdsNest/SoftBeam"));warmBeam.SetColor("_Color",new Color(1,.64f,.25f,.12f));
  var cone=Cone();var conePath=Base+"/Generated/SoftBeam.asset";var savedCone=AssetDatabase.LoadAssetAtPath<Mesh>(conePath);
  if(savedCone){EditorUtility.CopySerialized(cone,savedCone);UnityEngine.Object.DestroyImmediate(cone);cone=savedCone;}else AssetDatabase.CreateAsset(cone,conePath);
  for(int i=0;i<26;i++){
   float x=-55+i*110f/25,z=33+(i%3)*2.0f;
   Vector3 p=B(x,63,z),target=B(x*.4f+(i%2==0?16:-16),-15-(i%4)*12,2);
   var go=new GameObject("Light beam "+i);go.transform.SetParent(rig.transform);go.transform.position=p;go.transform.rotation=Quaternion.LookRotation(target-p);
   go.transform.localScale=new Vector3(1,1,Vector3.Distance(p,target)/100);
   go.AddComponent<MeshFilter>().sharedMesh=cone;var mr=go.AddComponent<MeshRenderer>();mr.sharedMaterial=i%4==0?warmBeam:beamMat;mr.shadowCastingMode=ShadowCastingMode.Off;mr.receiveShadows=false;beams.Add(go.transform);
   if(i%4==0)AddSpot(rig.transform,"Stage pool "+i,p,target,i%8==0?new Color(1,.65f,.3f):new Color(.45f,.64f,1),1.1f,110,27);
  }
  AddSpot(rig.transform,"Performer key",B(-10,40,19),B(0,52,3),new Color(1,.82f,.6f),9,60,40).shadows=LightShadows.Soft;
  AddSpot(rig.transform,"Stage warm wash",B(0,52,24),B(0,67,8),new Color(1,.45f,.15f),1.8f,45,90);
  for(int i=0;i<16;i++){
   float a=i*Mathf.PI*2/16;var l=new GameObject("Facade uplight "+i).AddComponent<Light>();l.transform.SetParent(rig.transform);l.transform.position=B(137*Mathf.Cos(a),155*Mathf.Sin(a),5);l.type=LightType.Spot;
   l.transform.rotation=Quaternion.LookRotation(B(139*Mathf.Cos(a),158*Mathf.Sin(a),35)-l.transform.position);l.range=38;l.spotAngle=55;l.intensity=1.3f;l.color=new Color(1,.44f,.18f);l.shadows=LightShadows.None;
  }
  var modes=new GameObject("Venue day night controls").AddComponent<VenueModes>();modes.viewCamera=cam;modes.fly=fly;modes.post=post;modes.sun=sun;modes.nightRig=rig;modes.beams=beams.ToArray();modes.emissions=emission.ToArray();modes.lods=lods.ToArray();modes.geometry=root;modes.SetNight(true);
  var area=new GameObject("Venue visibility bake volume").AddComponent<OcclusionArea>();area.center=new Vector3(0,38,0);area.size=new Vector3(520,120,560);
  PrefabUtility.SaveAsPrefabAsset(root,Base+"/Prefabs/BirdsNest_Enhanced_360.prefab");
  EditorSceneManager.SaveScene(scene,ScenePath);AssetDatabase.SaveAssets();
  EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(ScenePath,true)};
  InstallVenueDetails.Apply(modes);InstallBandDetails.Apply(modes);Validate(root,cam,modes);
  AssetDatabase.ExportPackage(Base,Path.Combine(Output,"BirdsNest_Enhanced.unitypackage"),ExportPackageOptions.Recurse);
  Debug.Log("BIRDSNEST_V3_BUILD_SUCCESS");
 }
 static Material GetMaterial(string name,Shader s){var path=Base+"/Materials/"+name+".mat";var m=AssetDatabase.LoadAssetAtPath<Material>(path);if(!m){m=new Material(s);AssetDatabase.CreateAsset(m,path);}return m;}
 static Light AddSpot(Transform parent,string name,Vector3 p,Vector3 t,Color c,float intensity,float range,float angle){var l=new GameObject(name).AddComponent<Light>();l.transform.SetParent(parent);l.transform.position=p;l.transform.rotation=Quaternion.LookRotation(t-p);l.type=LightType.Spot;l.color=c;l.intensity=intensity;l.range=range;l.spotAngle=angle;l.innerSpotAngle=angle*.65f;l.shadows=LightShadows.None;return l;}
 static Mesh Cone(){
  var v=new List<Vector3>();var uv=new List<Vector2>();var ids=new List<int>();const int n=24,rings=8;
  for(int j=0;j<rings;j++){float t=j/(float)(rings-1);for(int i=0;i<=n;i++){float a=i*Mathf.PI*2/n,r=.12f+t*2.6f;v.Add(new Vector3(Mathf.Cos(a)*r,Mathf.Sin(a)*r,t*100));uv.Add(new Vector2(i/(float)n,t));}}
  for(int j=0;j<rings-1;j++)for(int i=0;i<n;i++){int k=j*(n+1)+i;ids.AddRange(new[]{k,k+1,k+n+1,k+1,k+n+2,k+n+1});}
  var m=new Mesh{name="Soft light cone"};m.SetVertices(v);m.SetUVs(0,uv);m.SetTriangles(ids,0);m.RecalculateNormals();m.RecalculateBounds();return m;
 }
 public static void Validate(GameObject root,Camera camera,VenueModes modes){
  var rs=root.GetComponentsInChildren<Renderer>();var bounds=rs[0].bounds;foreach(var r in rs)bounds.Encapsulate(r.bounds);
  int errors=rs.Sum(r=>r.sharedMaterials.Count(m=>!m||!m.shader||m.shader.name.Contains("InternalError")));
  if(errors!=0||bounds.size.y<60||bounds.size.z<280||modes.fly.viewpoints.Length<9||modes.lods.Length<100)throw new Exception("Venue validation failed");
  var qa=Path.Combine(Output,"checks");Directory.CreateDirectory(qa);
  File.WriteAllText(Path.Combine(qa,"validation.txt"),"Unity: "+Application.unityVersion+"\nPipeline: Built-in Linear HDR + tone mapping\nRenderers incl. inactive LOD alternatives: "+rs.Length+"\nLOD groups: "+modes.lods.Length+"\nBounds: "+bounds+"\nMissing materials: "+errors+"\nCoordinate basis: "+bx+" "+by+" "+bz+"\n");
  if(SystemInfo.graphicsDeviceType!=GraphicsDeviceType.Null){
   foreach(bool night in new[]{false,true}){modes.SetNight(night);for(int i=0;i<modes.fly.viewpoints.Length;i++){modes.fly.Jump(i);Capture(camera,Path.Combine(qa,(night?"Night_":"Day_")+(i+1).ToString("00")+".png"));}}
  }
  modes.SetNight(true);modes.fly.Jump(3);EditorSceneManager.SaveScene(SceneManager.GetActiveScene());AssetDatabase.SaveAssets();
 }
 public static void Capture(Camera cam,string path){
  var rt=new RenderTexture(1440,900,24,RenderTextureFormat.ARGBHalf){antiAliasing=4};cam.targetTexture=rt;cam.Render();RenderTexture.active=rt;
  var tex=new Texture2D(1440,900,TextureFormat.RGB24,false,true);tex.ReadPixels(new Rect(0,0,1440,900),0,0);
  // ARGBHalf is linear; PNG viewers expect sRGB pixels.
  var colors=tex.GetPixels();for(int i=0;i<colors.Length;i++)colors[i]=colors[i].gamma;tex.SetPixels(colors);tex.Apply();File.WriteAllBytes(path,tex.EncodeToPNG());cam.targetTexture=null;RenderTexture.active=null;UnityEngine.Object.DestroyImmediate(tex);rt.Release();UnityEngine.Object.DestroyImmediate(rt);
 }
 static EmissionSetting ArchitectureEmission(Material m,string label){return new EmissionSetting{material=m,day=Color.black,night=label=="外层浅灰钢带"?new Color(.065f,.052f,.04f):label=="外碗赭红混凝土"?new Color(.12f,.006f,.002f):new Color(.007f,.01f,.016f)};}
 public static void RefreshArchitectureLighting(){
  EditorSceneManager.OpenScene(ScenePath);var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();var entries=modes.emissions.ToList();
  var ts=modes.geometry.GetComponentsInChildren<Transform>(true);origin=ts.First(t=>t.name.StartsWith("LOOK_09")).position;bz=(ts.First(t=>t.name.StartsWith("LOOK_01")).position-origin)/23;by=(ts.First(t=>t.name.StartsWith("LOOK_04")).position-origin-bz*17)/62;bx=-(ts.First(t=>t.name.StartsWith("VIEW_06")).position-origin-bz*20)/90;
  foreach(var record in JsonUtility.FromJson<MaterialFile>(File.ReadAllText(Base+"/materials.json")).materials){
   if(record.label!="外层浅灰钢带"&&record.label!="外碗赭红混凝土"&&record.label!="membrane")continue;
   var m=AssetDatabase.LoadAssetAtPath<Material>(Base+"/Materials/"+record.name+".mat");m.shader=Shader.Find("BirdsNest/ArchitecturalLit");m.enableInstancing=true;
   entries.RemoveAll(e=>e.material==m);entries.Add(ArchitectureEmission(m,record.label));EditorUtility.SetDirty(m);
  }
  modes.emissions=entries.ToArray();modes.SetNight(true);EditorUtility.SetDirty(modes);Validate(modes.geometry,modes.viewCamera,modes);
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());AssetDatabase.SaveAssets();Debug.Log("BIRDSNEST_V3_LIGHTING_SUCCESS");
 }
 public static void BakeVisibility(){
  EditorSceneManager.OpenScene(ScenePath);StaticOcclusionCulling.smallestOccluder=4;StaticOcclusionCulling.smallestHole=.25f;StaticOcclusionCulling.backfaceThreshold=100;
  if(!StaticOcclusionCulling.Compute())throw new Exception("Visibility bake did not start");
  EditorApplication.update+=WaitForBake;
 }
 static void WaitForBake(){
  if(StaticOcclusionCulling.isRunning)return;EditorApplication.update-=WaitForBake;
  EditorSceneManager.SaveScene(SceneManager.GetActiveScene());AssetDatabase.SaveAssets();
  string data=Base+"/Scenes/BirdsNest_Enhanced/OcclusionCullingData.asset";bool ok=File.Exists(data)&&new FileInfo(data).Length>0;
  File.WriteAllText(Path.Combine(Output,"checks/occlusion.txt"),"Bake data present: "+ok+"\nSmallest occluder: 4 m\nSmallest hole: 0.25 m\n");
  if(ok){AssetDatabase.ExportPackage(Base,Path.Combine(Output,"BirdsNest_Enhanced.unitypackage"),ExportPackageOptions.Recurse);Debug.Log("BIRDSNEST_V3_OCCLUSION_SUCCESS");}
  if(Application.isBatchMode)EditorApplication.Exit(ok?0:1);
 }
}
}
