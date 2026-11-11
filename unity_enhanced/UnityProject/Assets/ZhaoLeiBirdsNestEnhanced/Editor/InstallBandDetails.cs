using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UnityEditor.SceneManagement;
using System;
using System.IO;
using System.Linq;
namespace ZhaoLeiBirdsNestV3 {
public static class InstallBandDetails {
 [Serializable] class BandMaterial {public string name,texture;public float[] baseColor;public float roughness,metallic,emission;}
 [Serializable] class BandMaterials {public BandMaterial[] materials;}
 public static void Run(){
  EditorSceneManager.OpenScene(BuildEnhancedVenue.ScenePath);var modes=UnityEngine.Object.FindFirstObjectByType<VenueModes>();Apply(modes);
  EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene());AssetDatabase.SaveAssets();
  BuildEnhancedVenue.RefreshArchitectureLighting();Debug.Log("BIRDSNEST_V5_BAND_SUCCESS");
 }
 public static void RunAndBuildPlayer(){
  Run();
  BuildVenuePlayer.Build();
 }
 public static void Apply(VenueModes modes){
  string path=BuildEnhancedVenue.Base+"/Models/BirdsNest_Band.fbx";if(!File.Exists(path))return;
  foreach(var tn in new[]{"BNE_020_texture.jpg","BNE_021_texture.jpg","BNE_022_texture.jpg"})AssetDatabase.ImportAsset(BuildEnhancedVenue.Base+"/Textures/"+tn,ImportAssetOptions.ForceUpdate);
  AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
  var records=JsonUtility.FromJson<BandMaterials>(File.ReadAllText(BuildEnhancedVenue.Base+"/band_materials.json")).materials;
  var emissions=modes.emissions.ToList();
  foreach(var r in records){
   string mp=BuildEnhancedVenue.Base+"/Materials/"+r.name+".mat";var mat=AssetDatabase.LoadAssetAtPath<Material>(mp);
   if(!mat){mat=new Material(Shader.Find("Standard"));AssetDatabase.CreateAsset(mat,mp);}mat.name=r.name;
   mat.SetColor("_Color",new Color(r.baseColor[0],r.baseColor[1],r.baseColor[2],r.baseColor.Length>3?r.baseColor[3]:1));
   mat.SetFloat("_Glossiness",1-r.roughness);mat.SetFloat("_Metallic",r.metallic);mat.enableInstancing=true;
   if(!string.IsNullOrEmpty(r.texture)){
    string tp=BuildEnhancedVenue.Base+"/Textures/"+r.texture;
    var ti=(TextureImporter)AssetImporter.GetAtPath(tp);
    if(ti!=null){ti.mipmapEnabled=true;ti.anisoLevel=8;ti.maxTextureSize=2048;ti.SaveAndReimport();}
    var tex=AssetDatabase.LoadAssetAtPath<Texture2D>(tp);
    mat.SetColor("_Color",Color.black);mat.SetTexture("_MainTex",tex);mat.SetTexture("_EmissionMap",tex);
    mat.EnableKeyword("_EMISSION");mat.globalIlluminationFlags=MaterialGlobalIlluminationFlags.None;
    emissions.RemoveAll(e=>e.material==mat);
    emissions.Add(new EmissionSetting{material=mat,day=Color.white*.95f,night=Color.white*(r.name=="BN5_提词器屏幕"?r.emission:Mathf.Max(1.25f,r.emission))});
   } else if(r.emission>0.01f){
    var c=new Color(r.baseColor[0],r.baseColor[1],r.baseColor[2],1);
    mat.SetTexture("_MainTex",null);mat.SetTexture("_EmissionMap",null);
    mat.EnableKeyword("_EMISSION");mat.globalIlluminationFlags=MaterialGlobalIlluminationFlags.None;
    emissions.RemoveAll(e=>e.material==mat);
    emissions.Add(new EmissionSetting{material=mat,day=c*(r.emission*.45f),night=c*r.emission});
   }
   EditorUtility.SetDirty(mat);
  }
  modes.emissions=emissions.ToArray();
  var imp=(ModelImporter)AssetImporter.GetAtPath(path);imp.importCameras=false;imp.importLights=false;imp.importAnimation=false;imp.isReadable=true;imp.importNormals=ModelImporterNormals.Import;imp.SaveAndReimport();
  foreach(var mp in AssetDatabase.FindAssets("t:Material",new[]{BuildEnhancedVenue.Base+"/Materials"}).Select(AssetDatabase.GUIDToAssetPath)){
   var mat=AssetDatabase.LoadAssetAtPath<Material>(mp);imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material),mat.name),mat);
  }
  imp.SaveAndReimport();var old=modes.geometry.transform.Find("BirdsNest_Band_V5");if(old)UnityEngine.Object.DestroyImmediate(old.gameObject);
  var band=(GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path));band.name="BirdsNest_Band_V5";band.transform.SetParent(modes.geometry.transform,true);
  foreach(var r in band.GetComponentsInChildren<Renderer>()){
   GameObjectUtility.SetStaticEditorFlags(r.gameObject,StaticEditorFlags.BatchingStatic|StaticEditorFlags.OccludeeStatic);r.shadowCastingMode=ShadowCastingMode.On;
  }
  var ts=modes.geometry.GetComponentsInChildren<Transform>(true);modes.fly.viewpoints=ts.Where(t=>t.name.StartsWith("VIEW_")).GroupBy(t=>t.name.Substring(5,2)).Select(g=>g.First()).OrderBy(t=>t.name).ToArray();
  modes.fly.targets=modes.fly.viewpoints.Select(v=>ts.First(t=>t.name==v.name.Replace("VIEW_","LOOK_"))).ToArray();
  if(modes.fly.viewpoints.Length<13)throw new Exception("Expected at least thirteen views after band installation");
  // Local band key: Auto priority avoids the distant lighting artifacts of forced pixel lights.
  var previous=modes.nightRig.transform.Find("Backline soft key");if(previous)UnityEngine.Object.DestroyImmediate(previous.gameObject);
  var key=new GameObject("Backline soft key").AddComponent<Light>();key.transform.SetParent(modes.nightRig.transform);
  key.transform.position=new Vector3(5.3f,10,-61.5f);key.transform.rotation=Quaternion.LookRotation(new Vector3(5.3f,5,-65.3f)-key.transform.position);
  key.type=LightType.Spot;key.spotAngle=75;key.innerSpotAngle=45;key.range=12;key.intensity=2;key.color=new Color(1,.86f,.67f);key.renderMode=LightRenderMode.Auto;key.shadows=LightShadows.Hard;
  modes.SetNight(true);modes.fly.Jump(3);EditorUtility.SetDirty(modes);EditorUtility.SetDirty(modes.fly);
  PrefabUtility.SaveAsPrefabAsset(modes.geometry,BuildEnhancedVenue.Base+"/Prefabs/BirdsNest_Enhanced_360.prefab");
 }
}
}
