Shader "BirdsNest/SoftBeam" {
 Properties { _Color("Beam colour",Color)=(.45,.65,1,.11) }
 SubShader { Tags {"Queue"="Transparent" "RenderType"="Transparent"} Blend One One ZWrite Off Cull Off
 Pass { CGPROGRAM
 #pragma vertex vert
 #pragma fragment frag
 #include "UnityCG.cginc"
 struct appdata { float4 vertex:POSITION;float3 normal:NORMAL;float2 uv:TEXCOORD0; };
 struct v2f { float4 pos:SV_POSITION;float3 wp:TEXCOORD0;float3 n:TEXCOORD1;float2 uv:TEXCOORD2; };
 float4 _Color;
 v2f vert(appdata v){v2f o;o.pos=UnityObjectToClipPos(v.vertex);o.wp=mul(unity_ObjectToWorld,v.vertex).xyz;o.n=UnityObjectToWorldNormal(v.normal);o.uv=v.uv;return o;}
 float4 frag(v2f i):SV_Target{float view=pow(saturate(abs(dot(normalize(i.n),normalize(_WorldSpaceCameraPos-i.wp)))),1.3);float fade=pow(1-saturate(i.uv.y),.9)*smoothstep(0,.035,i.uv.y);return float4(_Color.rgb*_Color.a*view*fade,0);}
 ENDCG }
 }
}
