import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS PARA CUADRÍCULA Y ARITMÉTICA ---
st.markdown("""
    <style>
    .matrix-table { border-collapse: collapse; margin: auto; background-color: white; color: black; border: 3px solid #333; }
    .matrix-table td { border: 2px solid #666; padding: 15px; min-width: 60px; text-align: center; font-weight: bold; font-size: 1.2rem; }
    .op-card { background-color: #ffffff; border-radius: 10px; padding: 15px; margin: 15px 0; border: 1px solid #ddd; color: black; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .arit-table { width: 100%; border-collapse: collapse; text-align: center; margin-top: 10px; }
    .arit-table td { border: 1px solid #eee; padding: 8px; }
    .res-row { background-color: #d4edda; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'filas' not in st.session_state: st.session_state.filas = []
if 'input_val' not in st.session_state: st.session_state.input_val = ""

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

# --- MOTOR DE CÁLCULO ---
def resolver(M, modo):
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
            st.write(f"🎯 Normalizar: $R_{{{i+1}}} = R_{{{i+1}}} / {sp.latex(piv)}$")
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
        st.success(f"### 🏁 Resultado: {sp.latex(res)}")
    else:
        st.success("### 🏁 Resultado Final:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")

c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("⌨️ Entrada de Renglones")
    
    # El input de chat es genial porque limpia la barra al dar enter
    entrada = st.chat_input("Escribe el renglón (ej: 1 0 5) y presiona Enter")
    
    if entrada:
        st.session_state.filas.append(entrada.split())
        st.rerun()

    # BOTONES DE CONTROL
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("✏️ Editar/Corregir Último", use_container_width=True):
            if st.session_state.filas:
                ultimo = " ".join(st.session_state.filas.pop())
                st.warning(f"Copiado al portapapeles: {ultimo}. Escríbelo corregido abajo.")
                # Nota: Streamlit no permite setear el valor de chat_input, 
                # pero sacarlo de la lista permite al usuario volver a escribirlo.
                st.rerun()
    with col_b2:
        if st.button("🗑️ Reiniciar Todo", use_container_width=True):
            st.session_state.filas = []
            st.rerun()

    # TABLA VISUAL
    if st.session_state.filas:
        max_c = max(len(l) for l in st.session_state.filas)
        html_m = "<table class='matrix-table'>"
        for f in st.session_state.filas:
            f_full = f + ["0"] * (max_c - len(f))
            html_m += "<tr>" + "".join([f"<td>{x}</td>" for x in f_full]) + "</tr>"
        html_m += "</table>"
        st.write("### 📊 Matriz Actual")
        st.write(html_m, unsafe_allow_html=True)
        M_ready = sp.Matrix([[sp.Rational(x) for x in (f + ["0"]*(max_c - len(f)))] for f in st.session_state.filas])
    else:
        M_ready = None

with c2:
    st.subheader("⚙️ Opciones")
    metodo = st.selectbox("Operación:", ["Gauss-Jordan", "Inversa", "Determinante"])
    if st.button("🚀 CALCULAR", use_container_width=True, type="primary"):
        if M_ready: st.session_state.go = True
        else: st.error("Ingresa datos primero.")

st.markdown("---")

if st.session_state.get('go', False) and M_ready:
    n, m = M_ready.shape
    if metodo == "Inversa" and n != m: st.error("Debe ser cuadrada.")
    elif metodo == "Determinante" and n != m: st.error("Debe ser cuadrada.")
    else:
        m_calc = M_ready.row_join(sp.eye(n)) if metodo == "Inversa" else M_ready
        resolver(m_calc, metodo)
