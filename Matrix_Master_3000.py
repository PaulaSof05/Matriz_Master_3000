import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .aritmetica-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; background-color: #1e1e1e; color: white; }
    .aritmetica-table td { border: 1px solid #444; padding: 12px; text-align: center; font-family: 'Courier New', monospace; }
    .header-row { background-color: #333; font-weight: bold; color: #00ff00; }
    .res-row { background-color: #004d00; font-weight: bold; border-top: 2px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- CEREBRO MATEMÁTICO (GAUSS-JORDAN PASO A PASO) ---
def tabla_aritmetica(fila_obj, fila_piv, factor, resultado, operacion):
    st.write(f"#### ➕ Aritmética: {operacion}")
    cols_html = "".join([f"<td>{sp.latex(x)}</td>" for x in fila_obj])
    piv_html = "".join([f"<td>{sp.latex(-factor*x)}</td>" for x in fila_piv])
    res_html = "".join([f"<td>{sp.latex(x)}</td>" for x in resultado])
    
    html = f"""
    <table class="aritmetica-table">
        <tr class="header-row"><td>Concepto</td>{"".join([f"<td>Col {i+1}</td>" for i in range(len(fila_obj))])}</tr>
        <tr><td>Renglón Destino</td>{cols_html}</tr>
        <tr><td>Multiplicador $({sp.latex(-factor)}) \\times R_{{piv}}$</td>{piv_html}</tr>
        <tr class="res-row"><td>RESULTADO</td>{res_html}</tr>
    </table>
    """
    st.write(html, unsafe_allow_html=True)

def ejecutar_gauss(M, modo="gauss"):
    n, cols = M.shape
    M_temp = M.copy()
    det_val = 1
    
    st.write(f"### ⚙️ Iniciando {modo.upper()}")
    st.latex(sp.latex(M_temp))

    for i in range(min(n, cols)):
        # Pivoteo
        if M_temp[i, i] == 0:
            for k in range(i + 1, n):
                if M_temp[k, i] != 0:
                    M_temp[i, :], M_temp[k, :] = M_temp[k, :], M_temp[i, :]
                    det_val *= -1
                    st.info(f"🔄 Intercambio: $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_temp))
                    break
        
        pivote = M_temp[i, i]
        if pivote == 0: continue

        # Normalizar (Hacer 1 el pivote)
        if modo != "determinante" and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_temp[i, :] = M_temp[i, :] * inv
            st.write(f"🎯 Normalización: $R_{{{i+1}}} \\to R_{{{i+1}}} / {sp.latex(pivote)}$")
            st.latex(sp.latex(M_temp))

        # Eliminación
        for j in range(n):
            if i != j:
                if modo == "determinante" and j < i: continue
                factor = M_temp[j, i]
                if factor != 0:
                    f_obj = M_temp[j, :].tolist()[0]
                    f_piv = M_temp[i, :].tolist()[0]
                    M_temp[j, :] = M_temp[j, :] - factor * M_temp[i, :]
                    
                    tabla_aritmetica(f_obj, f_piv, factor, M_temp[j, :].tolist()[0], 
                                     f"$R_{{{j+1}}} \\to R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M_temp))

    if modo == "determinante":
        diag = [M_temp[t,t] for t in range(n)]
        res = det_val * np.prod(diag)
        st.success(f"### 🏁 Resultado: {sp.latex(det_val)} × ({' × '.join([sp.latex(x) for x in diag])}) = {sp.latex(res)}")
    else:
        st.success("### 🏁 Matriz Resultante:")
        st.latex(sp.latex(M_temp))

# --- INTERFAZ DINÁMICA ---
st.title("🚀 Matrix Master 3000")

# Usamos columnas para separar Input de Opciones
col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("⌨️ Entrada de Matriz Pro")
    st.markdown("_Escribe números separados por espacios. Presiona **Enter** para nueva fila._")
    
    # El truco: un text_area que procesamos linea por linea
    raw_input = st.text_area("Control de Renglones:", height=100, key="matrix_input", placeholder="1 2 3\n4 5 6")
    
    # Procesamiento inmediato para la vista previa visual
    try:
        filas = [f.split() for f in raw_input.strip().split('\n') if f.strip()]
        if filas:
            max_cols = max(len(f) for f in filas)
            # Rellenar filas cortas con ceros para que sea una tabla perfecta
            matriz_preview = [f + ["0"]*(max_cols - len(f)) for f in filas]
            st.write("### 👁️ Vista Previa Dinámica")
            st.table(pd.DataFrame(matriz_preview))
            M_final = sp.Matrix([[sp.Rational(x) for x in f] for f in matriz_preview])
        else:
            M_final = None
    except:
        st.error("⚠️ Solo números y espacios, por favor.")
        M_final = None

with col_der:
    st.subheader("⚙️ Operaciones")
    op = st.selectbox("¿Qué haremos hoy?", ["Gauss-Jordan", "Inversa", "Determinante (Gauss)"])
    btn = st.button("🚀 CALCULAR AHORA", use_container_width=True, type="primary")

st.markdown("---")

# --- FLUJO DE TRABAJO ---
if btn and M_final is not None:
    if op == "Gauss-Jordan":
        ejecutar_gauss(M_final, "gauss")
    elif op == "Inversa":
        if M_final.shape[0] != M_final.shape[1]:
            st.error("❌ Error: La matriz debe ser cuadrada.")
        else:
            ejecutar_gauss(M_final.row_join(sp.eye(M_final.shape[0])), "inversa")
    elif op == "Determinante (Gauss)":
        if M_final.shape[0] != M_final.shape[1]:
            st.error("❌ Error: La matriz debe ser cuadrada.")
        else:
            ejecutar_gauss(M_final, "determinante")
