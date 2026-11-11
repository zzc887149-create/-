Shader "BirdsNest/ArchitecturalLit" {
 Properties { _Color("Paint",Color)=(.57,.56,.54,1) _Glossiness("Smoothness",Range(0,1))=.4 _Metallic("Metallic",Range(0,1))=.16 [HDR]_EmissionColor("Architectural night fill",Color)=(0,0,0,1) }
 SubShader { Tags { "RenderType"="Opaque" } LOD 200
 CGPROGRAM
 #pragma surface surf Standard fullforwardshadows
 #pragma target 3.0
 #pragma multi_compile_instancing
 fixed4 _Color;half _Glossiness,_Metallic;float4 _EmissionColor;
 struct Input { float3 worldPos;float3 worldNormal; };
 void surf(Input i,inout SurfaceOutputStandard o){
  o.Albedo=_Color.rgb;o.Metallic=_Metallic;o.Smoothness=_Glossiness;o.Alpha=1;
  float2 radial=normalize(i.worldPos.xz+float2(.001,.001));
  float outward=saturate(dot(i.worldNormal.xz,radial));
  // Broad facade illumination without spilling light through the open lattice into the audience.
  o.Emission=_EmissionColor.rgb*(.18+.82*outward);
 }
 ENDCG
 } FallBack "Standard"
}
