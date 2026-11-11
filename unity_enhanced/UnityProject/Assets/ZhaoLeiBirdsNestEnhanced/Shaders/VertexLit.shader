Shader "BirdsNest/VertexLit" {
 Properties { _Color("Tint",Color)=(1,1,1,1) _Glossiness("Smoothness",Range(0,1))=.15 }
 SubShader { Tags { "RenderType"="Opaque" } LOD 200
 CGPROGRAM
 #pragma surface surf Standard fullforwardshadows vertex:vert
 #pragma target 3.0
 #pragma multi_compile_instancing
 fixed4 _Color; half _Glossiness;
 struct Input { float4 vertexColor:COLOR; };
 void vert(inout appdata_full v,out Input o) { UNITY_INITIALIZE_OUTPUT(Input,o);o.vertexColor=v.color; }
 void surf(Input i,inout SurfaceOutputStandard o){o.Albedo=i.vertexColor.rgb*_Color.rgb;o.Metallic=0;o.Smoothness=_Glossiness;o.Alpha=1;}
 ENDCG
 } FallBack "Diffuse"
}
