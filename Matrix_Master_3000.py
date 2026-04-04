import streamlit as st

# 1. Configuración de la página (Casi igual, pero limpia)
st.set_page_config(
    page_title="Matrix Master PRO", 
    layout="wide", 
    page_icon="🧮",
    initial_sidebar_state="expanded"
)

# 2. El CSS para borrar SOLO el rastro de GitHub
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        display: none !important;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        padding-top: 2rem !important;
    }
    
    .stAppDeployButton {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Bienvenido a Matrix Master 🧮")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🛠️ Herramientas Disponibles:
    Selecciona una opción en el menú de la izquierda para comenzar:
    
    1. **🚀 Sistemas de Ecuaciones:** Resolución paso a paso.
    2. **➕ Operaciones Básicas:** Suma y resta de matrices de cualquier dimensión.
    3. **✖️ Multiplicación:** Producto matricial (A × B) con validación de dimensiones.
    4. **🔍 Inversa y Determinante:** Análisis completo de matrices cuadradas.
    5. **📊 Rango y Transpuesta:** Calcula el rango, la transpuesta y la forma escalonada (RREF).
    
    ### 💡 ¿Cómo funciona?
    * **Entrada de datos:** Puedes insertar un sistema de ecuaciones manualmente.
    * **Generación aleatoria:** Usa los controles en el panel lateral para crear ejercicios nuevos al instante.
    * **Cálculo Exacto:** Los resultados se muestran como fracciones exactas, evitando errores decimales.
    """)

with col2:
    st.info("""
    **Nota de Uso:**
    Esta aplicación está diseñada para estudiantes de álgebra lineal. 
    Se usa el metodo y algoritmo de Gauss Jordan, por lo que puede usar otro procedimiento y llegar al mismo resultado.
    """)
    
    # Un pequeño toque visual
    st.success("✅ Estado del Sistema: Listo para operar.")

st.markdown("---")
st.caption("Matrix Master PRO - Saludos profe Tlatoanic ;3.")





