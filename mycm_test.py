import google.generativeai as genai
import os

# -------------------------------------------------------------------
# 1. CONFIGURACIÓN
# ¡IMPORTANTE! Pega tu clave API de Google AI Studio aquí
# -------------------------------------------------------------------
try:
    genai.configure(api_key="AIzaSyCbUSbs8EonxV-iMsUhXflX-omgQWCXfhw")
except AttributeError:
    print("Error: La API key no está configurada o la librería no se instaló correctamente.")
    # Si usas un entorno como Google Colab, puedes usar secrets:
    # from google.colab import userdata
    # genai.configure(api_key=userdata.get('GEMINI_API_KEY'))
    exit()

# Inicializa el modelo de IA (Gemini)
model = genai.GenerativeModel('gemini-2.5-pro')

# -------------------------------------------------------------------
# 2. SIMULACIÓN DEL REGISTRO (Punto 4.1 del Pitch Deck)
# -------------------------------------------------------------------
# Simulamos la base de datos del cliente.
# Esto es lo que MyCm sabría del negocio.
negocio = {
    "nombre": "La Tostadería",
    "descripcion": "Soy 'La Tostadería', una cafetería de especialidad en Villa Crespo. Mi onda es rústica y amigable. Vendemos café de grano, medialunas caseras y brunch.",
    "colores_marca": ["Marrón tierra", "Beige", "Verde oliva"],
    "logo_path": "/logos/la_tostaderia_logo.png", # Simulado
    "ubicacion": "Villa Crespo, CABA, Argentina"
}

# -------------------------------------------------------------------
# 3. EL "CEREBRO" DE MyCm (Función de IA)
# -------------------------------------------------------------------
def generar_post_mycm(perfil_negocio, idea_post):
    """
    Toma el perfil del negocio y una idea, y genera el contenido del post.
    """
    
    # --- INGENIERÍA DE PROMPT ---
    # Este es el corazón de tu app. Es el "prompt" que le damos a Gemini.
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
    2.  **Tono:** El tono debe ser coherente con la descripción del negocio: "{perfil_negocio['descripcion'].split('Mi onda es ')[-1]}".
    3.  **CTA:** Incluye un Call-to-Action (Llamado a la Acción) claro y amigable (ej. "¡Vení a probarlo!", "Etiquetá a tu amigo fanático del café").
    4.  **Hashtags:** Genera una lista de 7 a 10 hashtags RELEVANTES. Deben incluir:
        * Hiper-locales (basados en {perfil_negocio['ubicacion']}).
        * Específicos del producto (ej. #CafeDeEspecialidad).
        * Generales del rubro (ej. #Cafeteria).

    **Formato de Respuesta (OBLIGATORIO):**
    COPY:
    [Aquí el texto del posteo. Debe tener saltos de línea y emojis.]
    ---
    HASHTAGS:
    [#hashtag1, #hashtag2, #hashtag3, #hashtag4, #hashtag5, #hashtag6, #hashtag7]
    """
    
    print("\n[MyCm]... Contactando al motor de IA para generar el post...\n")
    
    try:
        # Enviamos la solicitud a la API de Gemini
        response = model.generate_content(prompt_template)
        
        # Procesamos la respuesta para que sea fácil de usar
        # (El formato que pedimos ayuda a "parsear" esto)
        partes = response.text.split("---")
        copy = partes[0].replace("COPY:", "").strip()
        hashtags = partes[1].replace("HASHTAGS:", "").strip()
        
        return copy, hashtags

    except Exception as e:
        print(f"Error al contactar la API de Gemini: {e}")
        return None, None

# -------------------------------------------------------------------
# 4. SIMULACIÓN DEL "MOMENTO MÁGICO" (Punto 4.2, 4.3 y 4.4)
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("--- Iniciando Simulación de MyCm (Prueba de Concepto) ---")
    print(f"Negocio Conectado: {negocio['nombre']} ({negocio['ubicacion']})")
    
    # 4.2. La IA Planifica (Simulado)
    # En la app real, esto vendría de un calendario inteligente.
    # Aquí lo definimos manually para la prueba.
    idea_contextual = "Posteo para un día de lluvia, ideal para un café caliente y algo rico."
    # idea_contextual = "Promoción de 2x1 en medialunas para el finde largo."
    # idea_contextual = "Foto del equipo preparando la apertura del local."

    print(f"Idea del día (Planificador): {idea_contextual}")
    
    # 4.3. El Momento Mágico (Generación)
    copy_generado, hashtags_generados = generar_post_mycm(negocio, idea_contextual)
    
    if copy_generado:
        print("=" * 40)
        print("📲 [NOTIFICACIÓN DE MyCm]")
        print("¡Tu post de mañana está listo para aprobar!")
        print("=" * 40)
        
        # 4.4. Aprobación (15 seg)
        print("\n--- VISTA PREVIA DEL POST ---\n")
        
        # Simulación de la imagen que usaría la plantilla de la marca
        print(f"[IMAGEN SIMULADA: 🖼️]")
        print(f"(Se generaría una imagen usando la paleta de colores '{negocio['colores_marca']}' y el logo '{negocio['logo_path']}')\n")
        
        # Contenido generado por IA
        print("--- Texto del Posteo ---")
        print(copy_generado)
        print("\n--- Hashtags ---")
        print(hashtags_generados)
        
        print("\n" + "=" * 40)
        
        # Simulación de la acción del usuario
        aprobacion = input("¿Aprobás este post para publicar mañana? (s/n): ").lower()
        
        # --- ESTA ES LA LÍNEA CORREGIDA ---
        if aprobacion == 's':
            print("\n✅ ¡Perfecto! El post se programó automáticamente.")
        else:
            print("\n❌ Post rechazado. (En la app real, podrías pedir 'Regenerar' o 'Editar').")
            
    else:
        print("No se pudo generar el posteo. Revisa la API Key o el error.")