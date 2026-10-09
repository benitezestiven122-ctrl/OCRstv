import streamlit as st
import numpy as np
import pytesseract
from PIL import Image, ImageOps

# ==========================================
# 1. CONFIGURACIÓN Y ESTILO (CYBERPUNK / TERMINAL)
# ==========================================
st.set_page_config(
    page_title="OCR Data-Stream",
    page_icon="👁️",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    html, body, [class*="css"] {
        font-family: 'Share Tech Mono', monospace;
        background-color: #000B00 !important; /* Verde muy oscuro */
        color: #00FF41 !important; /* Verde Matrix */
    }
    
    /* Acentos para la interfaz */
    h1, h2, h3 { color: #00FF41 !important; text-transform: uppercase; }
    
    .data-box {
        background-color: #001F00;
        border: 1px solid #00FF41;
        padding: 15px;
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
    }
    
    .stRadio label { color: #00FF41 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INTERFAZ PRINCIPAL Y PARÁMETROS
# ==========================================
st.title("👁️ OCR Data-Stream")
st.markdown("Digitaliza texto físico del entorno (libros, carteles, notas) y conviértelo en cadenas de caracteres limpias para alimentar generadores de texto en resolume, Blender o TouchDesigner.")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8297/8297120.png", width=80)
    st.subheader("⚙️ Procesador de Señal Óptica")
    
    # Selector de filtros optimizados con Pillow
    filtro = st.radio(
        "Filtro de Pre-procesamiento:",
        ('Alto Contraste (Recomendado)', 'Invertir / Negativo', 'Señal Cruda (Sin filtro)')
    )
    
    st.divider()
    st.caption("Asegúrate de tener buena iluminación para que la red neuronal identifique bien la tipografía.")

col1, col2 = st.columns([1.5, 1])

with col1:
    img_file_buffer = st.camera_input("📸 Capturar entorno analógico")

# ==========================================
# 3. LÓGICA DE PROCESAMIENTO E INFERENCIA
# ==========================================
if img_file_buffer is not None:
    # 3.1. Carga de imagen nativa con Pillow (Sin OpenCV)
    img = Image.open(img_file_buffer)
    
    # 3.2. Aplicación de Filtros para mejorar el OCR
    if filtro == 'Invertir / Negativo':
        # Convierte a RGB para asegurar que se pueda invertir
        img_rgb = img.convert('RGB')
        img_procesada = ImageOps.invert(img_rgb)
        
    elif filtro == 'Alto Contraste (Recomendado)':
        # Convertir a escala de grises
        img_gray = img.convert('L')
        # Binarización pura (Thresholding): Píxeles > 128 se vuelven blancos, los demás negros.
        # Esto elimina las sombras del papel y hace que el texto resalte, mejorando Tesseract un 80%.
        img_procesada = img_gray.point(lambda p: 255 if p > 128 else 0)
        
    else:
        img_procesada = img

    with col2:
        st.write("### 🎛️ Vista de Depuración")
        st.image(img_procesada, caption=f"Filtro Aplicado: {filtro}", use_container_width=True)
        
        with st.spinner("Decodificando caracteres..."):
            try:
                # 3.3. Extracción de texto
                # Usamos config para forzar a Tesseract a buscar bloques de texto (psm 6)
                text = pytesseract.image_to_string(img_procesada, lang='eng+spa', config='--psm 6')
                
                # 3.4. Limpieza del texto extraído
                text_limpio = text.strip()
                
                st.write("### 📡 Data Extracted (Raw Output)")
                
                if text_limpio:
                    # Mostrar como código para fácil copiado
                    st.code(text_limpio, language="text")
                    
                    # Generar una variante "Glitch" separada por comas para TouchDesigner DATs
                    st.write("**Formato CSV para TouchDesigner (Text DAT):**")
                    glitch_format = ",".join(text_limpio.split())
                    st.code(glitch_format, language="csv")
                else:
                    st.warning("No se detectó ningún texto. Intenta acercar la cámara o usar el filtro de Alto Contraste.")
                    
            except Exception as e:
                st.error("Error crítico: El motor Tesseract-OCR no está instalado en el servidor. Asegúrate de haber creado el archivo 'packages.txt'.")
                st.code(str(e))
