import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS PARA DEJAR LA TABLA "DESNUDA" Y PROFESIONAL ---
st.markdown("""
    <style>
    /* Ocultar encabezados de columnas y números de filas en el editor */
    [data-testid="stTable"] thead, [data-testid="stDataTable"] thead { display: none; }
    [data-testid="stTable"] th, [data-testid="stDataTable"] th { display: none; }
    
    /* Estilo de las tablas de aritmética */
    .op-card {
        background-color: #ffffff;
        border-left: 5px solid #2e7d32;
        padding: 15px;
        margin: 15px 0;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        color: black;
    }
    .arit-table { width: 100%; border-collapse: collapse; text-align: center; }
    .arit-table td { border: 1px solid #ddd; padding: 8px; }
    .res-row { background-color: #e8f5e9; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE APOYO ---
def tabla_aritmetica(f_obj, f_piv, factor, f_res, titulo):
    with st.container():
        st.markdown(f"<div class='op-card'><b>⚡ {titulo}</b>", unsafe_allow_html=True)
        cols_head = "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))])
        html = f"""
        <table class='arit-table'>
            <tr style='background:#f8f9fa; font-weight:bold;'><td>Concepto</td>{cols_head}</tr>
            <tr><td>R. Destino</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])}</tr>
            <tr><td>-({sp.latex(factor)}) * R_piv</td>{"".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv])}</tr>
            <tr class='res-row'><td>Resultado</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_res])}</tr>
        </table></div>
        """
        st.write(html, unsafe_allow_html=True)

def resolver_matriz(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    det_signo = 1
    st.write("### 🏁 Inicio del Proceso")
    st.latex(sp.latex(M_t))

    for i in range(min(n, cols)):
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_signo *= -1
                    st.info(f"🔄 Intercambio: $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_t))
                    break
        
        piv = M_t[i, i]
        if piv == 0: continue

        if modo != "Determinante" and piv != 1:
            inv = sp.Rational(1, piv)
            M_t[i, :] = M_t[i, :] * inv
            st.write(f"🎯 Normalizar pivote: $R_{{{i+1}}} = R_{{{i+1}}} / {sp.latex(piv)}$")
            st.latex(sp.latex(M_t))

        for j in range(n):
            if i != j:
                if modo == "Determinante" and j < i: continue
                factor = M_t[j, i]
                if factor != 0:
                    f_o, f_p = M_t[j,:].tolist()[0], M_t[i,:].tolist()[0]
                    M_t[j, :] = M_t[j, :] - factor * M_t[i, :]
                    tabla_aritmetica(f_o, f_p, factor, M_t[j,:].tolist()[0], f"$R_{{{j+1}}} = R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M_t))

    if modo == "Determinante":
        res = det_signo * np.prod([M_t[x,x] for x in range(n)])
        st.success(f"### 🏁 Resultado Final: **{sp.latex(res)}**")
    else:
        st.success("### 🏁 Resultado Final:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")
st.write("IPN ESCOM - Ciencia de Datos")

col_in, col_op = st.columns([2, 1])

with col_in:
    st.subheader("⌨️ Editor de Matriz")
    st.info("Haz doble clic en cualquier celda para modificarla. Usa los botones de abajo para añadir filas o columnas.")
    
    # Inicializar matriz vacía si no existe
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame([[0, 0], [0, 0]])

    # El Editor Mágico
    edited_df = st.data_editor(
        st.session_state.data,
        num_rows="dynamic", # Permite añadir/quitar filas
        use_container_width=True,
        hide_index=True,    # Oculta el 0, 1, 2 de la izquierda
    )
    st.session_state.data = edited_df

with col_op:
    st.subheader("⚙️ Opciones")
    metodo = st.selectbox("Operación:", ["Gauss-Jordan", "Inversa", "Determinante"])
    
    if st.button("🚀 CALCULAR", use_container_width=True, type="primary"):
        try:
            # Convertir el DataFrame a matriz de Sympy
            M_input = sp.Matrix(edited_df.values.astype(str)).applyfunc(sp.Rational)
            st.session_state.ready_to_calc = True
            st.session_state.matrix_obj = M_input
        except Exception as e:
            st.error("Asegúrate de que todas las celdas tengan números válidos.")

st.markdown("---")

# --- FLUJO DE CÁLCULO ---
if st.session_state.get('ready_to_calc', False):
    M = st.session_state.matrix_obj
    n, m = M.shape
    
    if metodo == "Inversa" or metodo == "Determinante":
        if n != m:
            st.error("La matriz debe ser cuadrada.")
        else:
            m_proc = M.row_join(sp.eye(n)) if metodo == "Inversa" else M
            resolver_matriz(m_proc, metodo)
    else:
        resolver_matriz(M, "Gauss-Jordan")
