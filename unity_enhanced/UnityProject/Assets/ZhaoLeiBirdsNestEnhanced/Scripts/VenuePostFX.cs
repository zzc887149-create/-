using UnityEngine;
namespace ZhaoLeiBirdsNestV3 {
[ExecuteAlways,RequireComponent(typeof(Camera))]
public class VenuePostFX:MonoBehaviour {
 public Shader effectShader;public float exposure=1.15f,bloom=.22f;Material material;
 void OnRenderImage(RenderTexture src,RenderTexture dst){
  if(!effectShader || !effectShader.isSupported){Graphics.Blit(src,dst);return;}
  if(!material)material=new Material(effectShader){hideFlags=HideFlags.HideAndDontSave};
  var a=RenderTexture.GetTemporary(Mathf.Max(1,src.width/4),Mathf.Max(1,src.height/4),0,RenderTextureFormat.ARGBHalf);
  var b=RenderTexture.GetTemporary(a.width,a.height,0,RenderTextureFormat.ARGBHalf);
  Graphics.Blit(src,a,material,0);
  material.SetVector("_Direction",new Vector4(1.6f,0,0,0));Graphics.Blit(a,b,material,1);
  material.SetVector("_Direction",new Vector4(0,1.6f,0,0));Graphics.Blit(b,a,material,1);
  material.SetTexture("_BloomTex",a);material.SetFloat("_Exposure",exposure);material.SetFloat("_Bloom",bloom);Graphics.Blit(src,dst,material,2);
  RenderTexture.ReleaseTemporary(a);RenderTexture.ReleaseTemporary(b);
 }
 void OnDisable(){if(material){if(Application.isPlaying)Destroy(material);else DestroyImmediate(material);material=null;}}
}
}
