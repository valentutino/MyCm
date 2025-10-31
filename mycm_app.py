import streamlit as st
import google.generativeai as genai
import os
import requests
import base64

# -------------------------------------------------------------------
# 1. CONFIGURACIÓN DE APIS (¡MODIFICADO PARA DEPLOYMENT!)
# -------------------------------------------------------------------

# Intenta obtener las claves desde Streamlit Secrets (cuando esté online)
# Si no las encuentra (porque estamos testeando local), las toma de las variables de entorno
# (En el Paso 3 te muestro cómo configurar esto en la nube)

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY"))
STABILITY_API_KEY = st.secrets.get("STABILITY_API_KEY", os.environ.get("STABILITY_API_KEY"))

# Configuración de Google Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    text_model = genai.GenerativeModel('models/gemini-2.5-flash')
except Exception as e:
    st.error(f"Error al configurar la API de Google: {e}")
    st.stop()

# Verificación de la API de Stability
if not STABILITY_API_KEY:
    st.error("Falta la API Key de Stability AI en los secretos de Streamlit.")
    st.stop()

# ... (El resto de tu código, 'def generar_post_mycm(...)' etc., queda exactamente igual) ...
# -------------------------------------------------------------------
# 2. FUNCIÓN DE GENERACIÓN DE TEXTO (Gemini)
# -------------------------------------------------------------------
def generar_post_mycm(perfil_negocio, idea_post):
    """
    Genera el texto del post y el prompt para la imagen usando Gemini.
    """
    prompt_template = f"""
    **Rol:** Eres 'MyCm', un Community Manager experto en IA para PYMES de Argentina.
    Tu objetivo es crear un posteo de Instagram listo para publicar.
    
    **Datos del Negocio (Cliente):**
    * Nombre: {perfil_negocio['nombre']}
    * Descripción y Tono: {perfil_negocio['descripcion']}
    * Ubicación: {perfil_negocio['ubicacion']}

    **Tarea:**
    Debes generar el contenido para un posteo de Instagram basado en la siguiente idea:
    * Idea del Post: "{idea_post}"

    **Reglas de Generación:**
    1.  **Texto (Copy):** Escribe un texto (copy) que sea atractivo, cercano y en español de Argentina (usá "vos", "tenés", etc.).
    2.  **Tono:** El tono debe ser coherente con la descripción del negocio.
    3.  **CTA:** Incluye un Call-to-Action (Llamado a la Acción) claro y amigable.
    4.  **Hashtags:** Genera una lista de 7 a 10 hashtags RELEVANTES (hiper-locales, producto, rubro).
    5.  **Descripción de Imagen:** Genera un prompt para un generador de imágenes de IA (como Stable Diffusion). Debe ser conciso, descriptivo y en inglés. Debe estar optimizado para crear una imagen fotográfica y atractiva.

    **Formato de Respuesta (OBLIGATORIO):**
    COPY:
    [Aquí el texto del posteo. Debe tener saltos de línea y emojis.]
    ---
    HASHTAGS:
    [#hashtag1, #hashtag2, #hashtag3, #hashtag4, #hashtag5, #hashtag6, #hashtag7]
    ---
    IMAGEN_PROMPT:
    [Aquí el prompt de la imagen en inglés.]
    """
    
    try:
        response = text_model.generate_content(prompt_template)
        partes = response.text.split("---")
        
        if len(partes) != 3:
            st.error(f"Error de formato de la IA. Respuesta recibida:\n{response.text}")
            return None, None, None
            
        copy = partes[0].replace("COPY:", "").strip()
        hashtags = partes[1].replace("HASHTAGS:", "").strip()
        imagen_prompt = partes[2].replace("IMAGEN_PROMPT:", "").strip()

        return copy, hashtags, imagen_prompt
    
    except Exception as e:
        st.error(f"Error al contactar la API de Gemini: {e}")
        return None, None, None

# -------------------------------------------------------------------
# 3. FUNCIÓN DE GENERACIÓN DE IMAGEN (Stability AI)
# -------------------------------------------------------------------
def generar_imagen_con_stability(prompt_imagen):
    """
    Genera una imagen usando la API de Stability AI (Stable Diffusion 3).
    """
    engine_id = "stable-diffusion-xl-1024-v1-0"
    api_host = "https://api.stability.ai"
    url = f"{api_host}/v1/generation/{engine_id}/text-to-image"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {STABILITY_API_KEY}"
    }

    payload = {
        "text_prompts": [
            {
                "text": prompt_imagen,
                "weight": 1.0 # Puedes ajustar el peso del prompt
            },
            {
                "text": "blurry, bad, ugly, low quality, watermark, text", # Prompt negativo
                "weight": -1.0
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            st.error(f"Error de Stability AI (HTTP {response.status_code}): {response.text}")
            return None

        data = response.json()
        
        # La imagen viene codificada en base64
        image_data = data["artifacts"][0]["base64"]
        return image_data

    except Exception as e:
        st.error(f"Error al generar la imagen con Stability AI: {e}")
        return None

# -------------------------------------------------------------------
# 4. EL "FRONT-END" (La App Web con Streamlit)
# -------------------------------------------------------------------

st.set_page_config(page_title="MyCm App", page_icon="🚀", layout="centered")
st.title("🚀 MyCm: Tu CM de Bolsillo (Demo)")
st.write("Esta es la demo del front-end que simula el 'Momento Mágico'.")

# --- Barra Lateral: Simulación del "Registro" ---
st.sidebar.header("Perfil del Negocio (Registro)")
st.sidebar.write("Aquí el dueño cargaría sus datos una sola vez.")

nombre_negocio = st.sidebar.text_input("Nombre del Negocio", "La Tostadería")
descripcion = st.sidebar.text_area(
    "Descripción y Tono", 
    "Soy 'La Tostadería', una cafetería de especialidad en Villa Crespo. Mi onda es rústica y amigable. Vendemos café de grano, medialunas caseras y brunch.",
    height=150
)
ubicacion = st.sidebar.text_input("Ubicación (Barrio, Ciudad)", "Villa Crespo, CABA, Argentina")

negocio_perfil = {"nombre": nombre_negocio, "descripcion": descripcion, "ubicacion": ubicacion}

# --- Pantalla Principal: El "Momento Mágico" ---
st.header("Generador de Contenido")
st.write(f"¡Hola, **{nombre_negocio}**! Listo para crear tu próximo post.")

idea_contextual = st.text_input(
    "Idea para el posteo de hoy (esto lo haría la IA en la app real):", 
    "Posteo para un día de lluvia, ideal para un café caliente y algo rico."
)

if st.button("✨ ¡Generar Post Mágico!"):
    if not nombre_negocio or not descripcion or not ubicacion or not idea_contextual:
        st.error("Por favor, completa todos los campos en la barra lateral y la idea del post.")
    else:
        with st.spinner("[MyCm]... Generando texto con Gemini..."):
            copy_generado, hashtags_generados, imagen_prompt_generado = generar_post_mycm(negocio_perfil, idea_contextual)
        
        if copy_generado and imagen_prompt_generado:
            st.divider()
            st.subheader("📲 ¡Tu post de mañana está listo para aprobar!")
            
            with st.spinner("[MyCm]... Generando imagen con Stability AI..."):
                imagen_base64 = generar_imagen_con_stability(imagen_prompt_generado)
            
            if imagen_base64:
                # Muestra la imagen decodificada desde base64
                st.image(base64.b64decode(imagen_base64), caption=f"Imagen generada para: '{imagen_prompt_generado}'")
            else:
                st.warning("No se pudo generar la imagen con Stability AI.")
            
            # --- Contenido de texto ---
            st.subheader("--- Texto del Posteo (Copy) ---")
            st.markdown(copy_generado) 
            
            st.subheader("--- Hashtags ---")
            st.code(hashtags_generados)
            
            st.success("¡Post generado con éxito!")
            
            # Simulación de los botones de aprobación
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                st.button("✅ Aprobar y Programar", type="primary")
            with col2:
                st.button("🔄 Pedir otra versión")
        else:
            st.error("No se pudo generar el contenido del post. Revisa la consola para más detalles.")