import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS CSS PARA LA TABLA PERFECTA ---
st.markdown("""
    <style>
    /* Tabla de previsualización */
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        background-color: white;
        color: #1f1f1f;
        margin-bottom: 20px;
    }
    .matrix-table td {
        border: 2px solid #dee2e6;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    /* Estilo para las tablas de aritmética */
    .aritmetica-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        background-color: #fdfdfd;
    }
    .aritmetica-table td {
        border: 1px solid #ccc;
        padding: 10px;
        text-align: center;
    }
    .row-header { background-color: #f0f0f0; font-weight: bold; }
    .row-res { background-color: #d4edda; font-weight: bold; border-top: 2px solid #28a745; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CÁLCULO ---
def tabla_aritmetica(f_obj, f_piv, factor, f_res, op_text):
    st.write(f"#### ➕ {op_text}")
    html = f"<table class='aritmetica-table'>"
    html += f"<tr class='row-header'><td>Concepto</td>" + "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))]) + "</tr>"
    html += f"<tr><td>R. Destino</td>" + "".join([f"<td>{sp.latex(x)}</td>" for x in f_obj]) + "</tr>"
    html += f"<tr><td>-({sp.latex(factor)})*R_piv</td>" + "".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv]) + "</tr>"
    html += f"<tr class='row-res'><td>Resultado</td>" + "".join([f"<td>{sp.latex(x)}</td>" for x in f_res]) + "</tr>"
    html += "</table>"
    st.write(html, unsafe_allow_html=True)

def resolver(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    det_signo = 1
    st.write("### 🏁 Inicio del proceso")
    st.latex(sp.latex(M_t))

    for i in range(min(n, cols)):
        # Pivoteo
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_signo *= -1
                    st.info(f"🔄 Intercambio $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_t))
                    break
        
        piv = M_t[i, i]
        if piv == 0: continue

        if modo != "Determinante" and piv != 1:
            inv = sp.Rational(1, piv)
            M_t[i, :] = M_t[i, :] * inv
            st.write(f"🎯 Hacer 1 el pivote: $R_{{{i+1}}} \\to R_{{{i+1}}} / {sp.latex(piv)}$")
            st.latex(sp.latex(M_t))

        for j in range(n):
            if i != j:
                if modo == "Determinante" and j < i: continue
                factor = M_t[j, i]
                if factor != 0:
                    f_o = M_t[j, :].tolist()[0]
                    f_p = M_t[i, :].tolist()[0]
                    M_t[j, :] = M_t[j, :] - factor * M_t[i, :]
                    tabla_aritmetica(f_o, f_p, factor, M_t[j,:].tolist()[0], f"$R_{{{j+1}}} = R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M_t))

    if modo == "Determinante":
        diag = [M_t[x,x] for x in range(n)]
        st.success(f"### Resultado: {sp.latex(det_signo * np.prod(diag))}")
    else:
        st.success("### Resultado Final:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("⌨️ Entrada de Datos")
    # Este componente se actualiza más rápido
    raw = st.text_area("Escribe números (espacio=col, enter=fila):", height=150, key="input_raw")
    
    if raw:
        lineas = [l.split() for l in raw.strip().split('\n') if l.strip()]
        if lineas:
            max_c = max(len(l) for l in lineas)
            # Dibujamos la tabla MANUALMENTE con HTML para quitar los índices
            html_tabla = "<table class='matrix-table'>"
            for fila in lineas:
                # Rellenar faltantes
                fila_full = fila + [""] * (max_c - len(fila))
                html_tabla += "<tr>" + "".join([f"<td>{x}</td>" for x in fila_full]) + "</tr>"
            html_tabla += "</table>"
            
            st.write("### 📊 Matriz Detectada")
            st.write(html_tabla, unsafe_allow_html=True)
            
            M_ready = sp.Matrix([[sp.Rational(x) if x != "" else 0 for x in f] for f in [l + [""]*(max_c - len(l)) for l in lineas]])
        else: M_ready = None
    else: M_ready = None

with col2:
    st.subheader("⚙️ Opciones")
    op = st.selectbox("Acción:", ["Gauss-Jordan", "Inversa", "Determinante"])
    if st.button("🚀 CALCULAR", use_container_width=True, type="primary"):
        st.session_state.run = True

if st.session_state.get('run', False) and M_ready:
    resolver(M_ready, op)
