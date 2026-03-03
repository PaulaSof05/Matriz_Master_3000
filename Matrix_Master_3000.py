import streamlit as st

# Configuración global para todas las páginas
import streamlit as st

# Configuración global para ocultar el icono de GitHub
st.set_page_config(
    page_title="Matrix Master PRO", 
    layout="wide", 
    page_icon="🧮",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None  # Esto quita la mayor parte del menú
    }
)

# ESTO ES LO QUE REALMENTE QUITA EL BOTÓN DE "VIEW SOURCE" / GITHUB
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none;}
    .viewerBadge_container__1QS1n {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Welcome to Matrix Master PRO 🧮")

# Layout de dos columnas para la bienvenida
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🛠️ Herramientas Disponibles:
    Selecciona una opción en el menú de la izquierda para comenzar:
    
    1. **🚀 Sistemas de Ecuaciones:** Resolución paso a paso con métodos *Robot* o *Humano*.
    2. **➕ Operaciones Básicas:** Suma y resta de matrices de cualquier dimensión.
    3. **✖️ Multiplicación:** Producto matricial (A × B) con validación de dimensiones.
    4. **🔍 Inversa y Determinante:** Análisis completo de matrices cuadradas.
    5. **📊 Rango y Transpuesta:** Calcula el rango, la transpuesta y la forma escalonada (RREF).
    
    ### 💡 ¿Cómo funciona?
    * **Entrada de datos:** Puedes editar las celdas de las tablas manualmente.
    * **Generación aleatoria:** Usa los controles en el panel lateral para crear ejercicios nuevos al instante.
    * **Cálculo Exacto:** Gracias a **SymPy**, todos los resultados se muestran como fracciones exactas, evitando errores decimales.
    """)

with col2:
    st.info("""
    **Nota de Uso:**
    Esta aplicación está diseñada para estudiantes de álgebra lineal. 
    Te recomendamos usar la opción **Gauss-Jordan Humano** si estás practicando para un examen, 
    ya que busca los pasos más lógicos que haría una persona.
    """)
    
    # Un pequeño toque visual
    st.success("✅ Estado del Sistema: Listo para operar.")

st.markdown("---")
st.caption("Matrix Master PRO - Desarrollado para el aprendizaje interactivo de Álgebra Lineal.")

