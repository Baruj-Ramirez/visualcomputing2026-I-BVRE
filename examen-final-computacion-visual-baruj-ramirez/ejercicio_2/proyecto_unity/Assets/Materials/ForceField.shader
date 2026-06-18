Shader "Custom/ForceField"
{
    Properties
    {
        [Header(Colores)]
        _BaseColor("Color Base", Color) = (0.2, 0.6, 1.0, 0.15)
        _EdgeColor("Color de Borde (Fresnel)", Color) = (0.6, 0.9, 1.0, 1.0)

        [Header(Fresnel Brillo de Borde)]
        _FresnelPower("Fresnel Power", Range(0.1, 8.0)) = 3.0
        _FresnelIntensity("Fresnel Intensity", Range(0.0, 5.0)) = 2.0

        [Header(Ondulacion de Vertices)]
        _WaveAmplitude("Amplitud", Range(0.0, 0.2)) = 0.02
        _WaveFrequency("Frecuencia", Range(0.0, 20.0)) = 3.0
        _WaveSpeed("Velocidad", Range(0.0, 10.0)) = 1.0

        [Header(Ruido Energia Interna)]
        _NoiseScale("Escala de Ruido", Range(0.1, 20.0)) = 4.0
        _NoiseSpeed("Velocidad de Ruido", Range(0.0, 5.0)) = 0.5
        _DistortionStrength("Fuerza del Ruido", Range(0.0, 1.0)) = 0.3

        [Header(Lineas de Energia)]
        _ScanlineFrequency("Frecuencia", Range(0.0, 50.0)) = 10.0
        _ScanlineSpeed("Velocidad", Range(-5.0, 5.0)) = 1.0
        _ScanlineIntensity("Intensidad", Range(0.0, 2.0)) = 0.3

        [Header(Transparencia)]
        _AlphaBase("Alpha Base", Range(0.0, 1.0)) = 0.15
    }

    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" "RenderPipeline"="UniversalPipeline" "IgnoreProjector"="True" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseColor;
            float4 _EdgeColor;
            float _FresnelPower;
            float _FresnelIntensity;
            float _WaveAmplitude;
            float _WaveFrequency;
            float _WaveSpeed;
            float _NoiseScale;
            float _NoiseSpeed;
            float _DistortionStrength;
            float _ScanlineFrequency;
            float _ScanlineSpeed;
            float _ScanlineIntensity;
            float _AlphaBase;
        CBUFFER_END

        struct Attributes
        {
            float4 positionOS : POSITION;
            float3 normalOS   : NORMAL;
            float2 uv         : TEXCOORD0;
        };

        struct Varyings
        {
            float4 positionCS : SV_POSITION;
            float3 positionWS : TEXCOORD0;
            float3 normalWS   : TEXCOORD1;
            float2 uv         : TEXCOORD2;
        };

        // Ruido tipo Perlin 2D simple basado en hashing, no requiere texturas
        float2 Hash22(float2 p)
        {
            p = float2(dot(p, float2(127.1, 311.7)), dot(p, float2(269.5, 183.3)));
            return -1.0 + 2.0 * frac(sin(p) * 43758.5453123);
        }

        float Noise2D(float2 p)
        {
            float2 i = floor(p);
            float2 f = frac(p);
            float2 u = f * f * (3.0 - 2.0 * f);

            float a = dot(Hash22(i + float2(0.0, 0.0)), f - float2(0.0, 0.0));
            float b = dot(Hash22(i + float2(1.0, 0.0)), f - float2(1.0, 0.0));
            float c = dot(Hash22(i + float2(0.0, 1.0)), f - float2(0.0, 1.0));
            float d = dot(Hash22(i + float2(1.0, 1.0)), f - float2(1.0, 1.0));

            return lerp(lerp(a, b, u.x), lerp(c, d, u.x), u.y);
        }

        Varyings vert(Attributes IN)
        {
            Varyings OUT;

            // Leve ondulacion: desplaza el vertice a lo largo de su normal con una onda senoidal animada
            float wave = sin(IN.positionOS.y * _WaveFrequency + _Time.y * _WaveSpeed) * _WaveAmplitude;
            float3 displacedPosOS = IN.positionOS.xyz + IN.normalOS * wave;

            VertexPositionInputs vertexInput = GetVertexPositionInputs(displacedPosOS);

            OUT.positionCS = vertexInput.positionCS;
            OUT.positionWS = vertexInput.positionWS;
            OUT.normalWS   = TransformObjectToWorldNormal(IN.normalOS);
            OUT.uv         = IN.uv;

            return OUT;
        }

        half4 frag(Varyings IN, bool frontFace : SV_IsFrontFace) : SV_Target
        {
            // Si es una cara trasera (la vemos desde dentro del cubo), invertimos la normal
            float3 normalWS = frontFace ? IN.normalWS : -IN.normalWS;
            float3 viewDirWS = normalize(GetWorldSpaceViewDir(IN.positionWS));

            // Fresnel: brillo en los bordes / silueta del objeto
            float fresnel = pow(1.0 - saturate(dot(normalWS, viewDirWS)), _FresnelPower) * _FresnelIntensity;

            // Ruido animado para dar sensacion de energia interna fluctuante
            float2 noiseUV = IN.uv * _NoiseScale + float2(0.0, _Time.y * _NoiseSpeed);
            float n = Noise2D(noiseUV) * 0.5 + 0.5;

            // Lineas de energia que se desplazan verticalmente
            float scan = sin((IN.positionWS.y - _Time.y * _ScanlineSpeed) * _ScanlineFrequency) * 0.5 + 0.5;
            scan *= _ScanlineIntensity;

            float3 color = lerp(_BaseColor.rgb, _EdgeColor.rgb, saturate(fresnel));
            color += n * _DistortionStrength * _EdgeColor.rgb * 0.5;

            float alpha = _AlphaBase + fresnel + n * _DistortionStrength + scan;
            alpha = saturate(alpha);

            return half4(color, alpha);
        }
        ENDHLSL

        // Primera pasada: caras de atras (lo que se ve "desde dentro" del cubo)
        Pass
        {
            Name "BackFaces"
            Tags { "LightMode" = "UniversalForward" }
            Cull Front
            ZWrite Off
            Blend SrcAlpha OneMinusSrcAlpha

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            ENDHLSL
        }

        // Segunda pasada: caras de adelante (lo normal, vistas desde fuera)
        Pass
        {
            Name "FrontFaces"
            Tags { "LightMode" = "UniversalForward" }
            Cull Back
            ZWrite Off
            Blend SrcAlpha OneMinusSrcAlpha

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            ENDHLSL
        }
    }

    FallBack "Universal Render Pipeline/Unlit"
}
