import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .math-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
    .math-table td { border: 1px solid #ddd; padding: 8px; text-align: center; }
    .op-label { color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CÁLCULO Y ARITMÉTICA VISUAL ---
def mostrar_operacion_aritmetica(fila_orig, fila_pivote, factor, fila_res, label):
    """Genera una tabla visual de la operación entre renglones"""
    with st.expander(f"🔍 Ver aritmética: {label}", expanded=False):
        col1, col2 = st.columns([1, 4])
        with col2:
            html = "<table class='math-table'>"
            # Fila original
            html += f"<tr><td>$R_{{dest}}$ anterior</td>" + "".join([f"<td>{sp.latex(x)}</td>" for x in fila_orig]) + "</tr>"
            # Fila pivote multiplicada
            op_pivote = [-factor * x for x in fila_pivote]
            html += f"<tr><td>$-({sp.latex(factor)}) \\times R_{{pivote}}$</td>" + "".join([f"<td>{sp.latex(x)}</td>" for x in op_pivote]) + "</tr>"
            # Resultado
            html += f"<tr style='border-top: 2px solid black;'><td><b>Resultado</b></td>" + "".join([f"<td><b>{sp.latex(x)}</b></td>" for x in fila_res]) + "</tr>"
            html += "</table>"
            st.write(html, unsafe_allow_html=True)

def resolver(M, modo="gauss"):
    n, m_cols = M.shape
    pasos = 0
    det_factor = 1
    M_trabajo = M.copy()

    st.write(f"## 🛠️ Procedimiento: {modo.upper()}")
    st.latex(sp.latex(M_trabajo))

    for i in range(min(n, m_cols)):
        # 1. Pivoteo
        if M_trabajo[i, i] == 0:
            for j in range(i + 1, n):
                if M_trabajo[j, i] != 0:
                    M_trabajo[i, :], M_trabajo[j, :] = M_trabajo[j, :], M_trabajo[i, :]
                    det_factor *= -1
                    st.write(f"🔄 **Paso {pasos+1}:** Intercambio $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_trabajo))
                    break
        
        pivote = M_trabajo[i, i]
        if pivote == 0: continue

        # 2. Normalización (Hacer 1 el pivote)
        if pivote != 1 and modo != "determinante":
            factor_inv = sp.Rational(1, pivote)
            fila_ant = M_trabajo[i, :].tolist()[0]
            M_trabajo[i, :] = M_trabajo[i, :] * factor_inv
            st.write(f"🎯 **Paso {pasos+2}:** Normalizar fila $R_{{ {i+1} }} = R_{{ {i+1} }} / {sp.latex(pivote)}$")
            st.latex(sp.latex(M_trabajo))
        
        # 3. Eliminación
        for j in range(n):
            if i != j:
                if modo == "determinante" and j < i: continue # Solo ceros abajo para det
                
                factor = M_trabajo[j, i]
                if factor != 0:
                    fila_dest_ant = M_trabajo[j, :].tolist()[0]
                    fila_pivote = M_trabajo[i, :].tolist()[0]
                    
                    M_trabajo[j, :] = M_aug[j, :] - factor * M_trabajo[i, :]
                    
                    st.write(f"⚡ **Paso {pasos+3}:** $R_{{ {j+1} }} \\to R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }}$")
                    mostrar_operacion_aritmetica(fila_dest_ant, fila_pivote, factor, M_trabajo[j, :].tolist()[0], f"R{j+1}")
                    st.latex(sp.latex(M_trabajo))
        pasos += 3

    if modo == "determinante":
        diagonal = [M_trabajo[i,i] for i in range(n)]
        det_final = det_factor * np.prod(diagonal)
        st.write("### 🏁 Resultado")
        st.latex(rf"|A| = {sp.latex(det_factor)} \times ({' \times '.join([sp.latex(x) for x in diagonal])}) = {sp.latex(det_final)}")
    else:
        st.write("### 🏁 Resultado Final")
        st.latex(sp.latex(M_trabajo))

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Matrix Master 3000")
st.markdown("---")

col_input, col_tools = st.columns([2, 1])

with col_input:
    st.subheader("⌨️ Entrada Inteligente")
    txt_input = st.text_area(
        "Escribe tu matriz:",
        placeholder="Ejemplo:\n1 2 3\n4 5 6\n7 8 9",
        help="Espacio = Nueva columna, Enter = Nueva fila. Puedes usar comas también.",
        height=150
    )
    
    # Procesar entrada en tiempo real
    try:
        lineas = txt_input.strip().split('\n')
        matriz_raw = [linea.replace(',', ' ').split() for linea in lineas if linea.strip()]
        if matriz_raw:
            M_aug = sp.Matrix([[sp.Rational(x) for x in fila] for fila in matriz_raw])
            st.write("**Vista previa de tu matriz:**")
            st.latex(sp.latex(M_aug))
        else:
            M_aug = None
    except:
        st.error("⚠️ Formato incorrecto. Asegúrate de usar solo números.")
        M_aug = None

with col_tools:
    st.subheader("🛠️ Acciones")
    opcion = st.radio("¿Qué deseas obtener?", ["Gauss-Jordan (Sistema)", "Matriz Inversa", "Determinante"])
    
    btn_resolver = st.button("🚀 CALCULAR", use_container_width=True, type="primary")

st.markdown("---")

# --- EJECUCIÓN ---
if btn_resolver and M_aug is not None:
    n, m = M_aug.shape
    
    if opcion == "Gauss-Jordan (Sistema)":
        resolver(M_aug, modo="gauss")
        
    elif opcion == "Matriz Inversa":
        if n != m:
            st.error("❌ La matriz debe ser cuadrada para tener inversa.")
        else:
            identidad = sp.eye(n)
            M_inv_prep = M_aug.row_join(identidad)
            st.write("Se añade la matriz identidad a la derecha:")
            resolver(M_inv_prep, modo="inversa")
            
    elif opcion == "Determinante":
        if n != m:
            st.error("❌ El determinante solo existe en matrices cuadradas.")
        else:
            resolver(M_aug, modo="determinante")
