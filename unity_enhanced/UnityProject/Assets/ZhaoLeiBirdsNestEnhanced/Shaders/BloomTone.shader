Shader "Hidden/BirdsNest/BloomTone" {
 Properties { _MainTex("Source",2D)="white"{} _BloomTex("Bloom",2D)="black"{} }
 SubShader { Cull Off ZWrite Off ZTest Always
 CGINCLUDE
 #include "UnityCG.cginc"
 sampler2D _MainTex,_BloomTex;float4 _MainTex_TexelSize;float2 _Direction;float _Exposure,_Bloom;
 float4 threshold(v2f_img i):SV_Target {float3 c=tex2D(_MainTex,i.uv).rgb;return float4(max(c-.85,0),1);}
 float4 blur(v2f_img i):SV_Target {float2 d=_MainTex_TexelSize.xy*_Direction;float3 c=tex2D(_MainTex,i.uv).rgb*.4;c+=tex2D(_MainTex,i.uv+d).rgb*.24;c+=tex2D(_MainTex,i.uv-d).rgb*.24;c+=tex2D(_MainTex,i.uv+d*2).rgb*.06;c+=tex2D(_MainTex,i.uv-d*2).rgb*.06;return float4(c,1);}
 float4 finish(v2f_img i):SV_Target {float3 c=(tex2D(_MainTex,i.uv).rgb+tex2D(_BloomTex,i.uv).rgb*_Bloom)*_Exposure;float3 t=saturate((c*(2.51*c+.03))/(c*(2.43*c+.59)+.14));return float4(t,1);}
 ENDCG
 Pass { CGPROGRAM
 #pragma vertex vert_img
 #pragma fragment threshold
 ENDCG }
 Pass { CGPROGRAM
 #pragma vertex vert_img
 #pragma fragment blur
 ENDCG }
 Pass { CGPROGRAM
 #pragma vertex vert_img
 #pragma fragment finish
 ENDCG }
 }
}
