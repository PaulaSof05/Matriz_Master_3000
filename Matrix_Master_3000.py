import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS PARA CUADRÍCULA LIMPIA ---
st.markdown("""
    <style>
    .matrix-table { border-collapse: collapse; margin: auto; background-color: white; color: black; }
    .matrix-table td { border: 2px solid #333; padding: 15px; min-width: 50px; text-align: center; font-weight: bold; }
    .op-card { background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin: 10px 0; border: 1px solid #ddd; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
if 'filas_matriz' not in st.session_state:
    st.session_state.filas_matriz = []

# --- FUNCIONES DE CÁLCULO (Mismas que antes pero compactas) ---
def tabla_aritmetica(f_obj, f_piv, factor, f_res, op):
    st.markdown(f"<div class='op-card'><b>⚡ {op}</b>", unsafe_allow_html=True)
    cols = "".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])
    piv = "".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv])
    res = "".join([f"<td>{sp.latex(x)}</td>" for x in f_res])
    html = f"<table style='width:100%; border:1px solid #ccc; text-align:center;'><tr><td>Anterior</td>{cols}</tr><tr><td>Operación</td>{piv}</tr><tr style='background:#d4edda;'><td>Nuevo</td>{res}</tr></table></div>"
    st.write(html, unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("⌨️ Entrada de Renglones")
    st.info("Escribe los números de un renglón (ej: 1 2 3) y presiona **Enter**. Se agregará a la tabla automáticamente.")
    
    # Entrada de flujo continuo
    nuevo_renglon = st.chat_input("Escribe los números del renglón aquí...")
    
    if nuevo_renglon:
        st.session_state.filas_matriz.append(nuevo_renglon.split())

    # Botón para borrar y empezar de nuevo
    if st.button("🗑️ Borrar Matriz"):
        st.session_state.filas_matriz = []
        st.rerun()

    # Visualización de la tabla
    if st.session_state.filas_matriz:
        lineas = st.session_state.filas_matriz
        max_c = max(len(l) for l in lineas)
        
        html_m = "<table class='matrix-table'>"
        for f in lineas:
            f_full = f + ["0"] * (max_c - len(f))
            html_m += "<tr>" + "".join([f"<td>{x}</td>" for x in f_full]) + "</tr>"
        html_m += "</table>"
        
        st.write("### 📊 Matriz Actual")
        st.write(html_m, unsafe_allow_html=True)
        
        M_ready = sp.Matrix([[sp.Rational(x) for x in (f + ["0"]*(max_c - len(f)))] for f in lineas])
    else:
        M_ready = None

with col2:
    st.subheader("⚙️ Opciones")
    opcion = st.selectbox("Acción:", ["Gauss-Jordan", "Inversa", "Determinante"])
    if st.button("🚀 RESOLVER AHORA", use_container_width=True, type="primary"):
        if M_ready:
            st.session_state.calcular = True
        else:
            st.warning("Agrega al menos un renglón.")

st.markdown("---")

# --- LÓGICA DE GAUSS ---
if st.session_state.get('calcular', False) and M_ready:
    # (Aquí va tu función de resolver_matriz anterior)
    # Para ahorrar espacio en esta respuesta, asume que llama a la lógica de Gauss que ya tenemos.
    st.write("### 🏁 Procesando...")
    # ... (lógica de resolución)
