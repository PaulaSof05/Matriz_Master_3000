import streamlit as st
import pandas as pd
import sympy as sp

# 1. Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS MEJORADO PARA PROPORCIONES Y LEGIBILIDAD ---
st.markdown("""
    <style>
    .table-side {
        background-color: #1e1e1e;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #ff4b4b;
        color: #e0e0e0;
        max-width: 600px; /* Controla que la tabla no sea gigante */
    }
    .arit-table { 
        width: 100%; 
        border-collapse: collapse; 
        text-align: center; 
        font-size: 0.9em;
    }
    .arit-table td { border: 1px solid #444; padding: 6px; }
    .res-row { background-color: #1b3a24; font-weight: bold; color: #a5d6a7; }
    .header-row { background-color: #333; font-weight: bold; color: #ffffff; }
    .concepto-col { text-align: left; font-weight: bold; padding-left: 10px !important; width: 120px; }
    </style>
    """, unsafe_allow_html=True)

if 'df_matriz' not in st.session_state:
    st.session_state.df_matriz = pd.DataFrame()
if 'go' not in st.session_state:
    st.session_state.go = False

# --- RENDERIZADO DE MATRIZ CON FRACCIONES VERTICALES ---
def render_mat(M, modo, simbolo="\\approx"):
    n, m = M.shape
    M_tex = sp.latex(M) 
    if modo != "Determinante":
        c_str = "c" * (m-1) + "|c"
        M_tex = M_tex.replace(r"\begin{matrix}", rf"\begin{{array}}{{{c_str}}}").replace(r"\end{matrix}", r"\end{array}")
    return f"{simbolo} {M_tex}"

# --- TABLA ARITMÉTICA ---
def dibujar_paso(M_prev, f_obj, f_piv, factor, f_res, titulo, modo, es_primera=False, es_norm=False):
    simb = "=" if es_primera else "\\approx"
    col_mat, col_tab = st.columns([1, 1.5]) # Ajuste de proporción matriz vs tabla
    
    with col_mat:
        st.latex(render_mat(M_prev, modo, simb))
        st.markdown(f"**{titulo}**")
    
    with col_tab:
        st.markdown("<div class='table-side'>", unsafe_allow_html=True)
        cols_head = "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))])
        
        # Ajuste de etiquetas de concepto para mayor legibilidad
        concepto_piv = f"1/{sp.latex(1/factor)} * R_piv" if es_norm else f"-({sp.latex(factor)}) * R_piv"
        concepto_dest = "R. Actual" if es_norm else "R. Destino"
        
        html = f"""
        <table class='arit-table'>
            <tr class='header-row'><td class='concepto-col'>Concepto</td>{cols_head}</tr>
            <tr><td class='concepto-col'>{concepto_dest}</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])}</tr>
            <tr><td class='concepto-col'>{concepto_piv}</td>{"".join([f"<td>{sp.latex(x if not es_norm else x/factor)}</td>" for x in f_piv])}</tr>
            <tr class='res-row'><td class='concepto-col'>Resultado</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_res])}</tr>
        </table></div>
        """
        st.write(html, unsafe_allow_html=True)

# --- LÓGICA DE RESOLUCIÓN ---
def resolver(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    es_primera = True
    st.markdown("### Proceso de Resolución")
    
    for i in range(min(n, cols)):
        # 1. Pivoteo
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_old = M_t.copy()
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    st.latex(render_mat(M_old, modo, "=" if es_primera else "\\approx"))
                    st.info(f"$R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    es_primera = False
                    break
        
        # 2. Hacer 1 el pivote (Tabla agregada)
        piv = M_t[i, i]
        if piv != 0:
            M_before = M_t.copy()
            f_o = M_before[i, :].tolist()[0]
            M_t[i, :] = sp.simplify(M_t[i, :] / piv)
            f_r = M_t[i, :].tolist()[0]
            
            # Tabla para el paso de normalización
            dibujar_paso(M_before, f_o, f_o, piv, f_r, 
                         f"$R_{{{i+1}}} / ({sp.latex(piv)}) \\to R_{{{i+1}}}$", 
                         modo, es_primera, es_norm=True)
            es_primera = False
            
        # 3. Hacer 0's
        for j in range(n):
            if i != j:
                factor = M_t[j, i]
                if factor != 0:
                    f_o = M_t[j, :].tolist()[0]
                    f_p = M_t[i, :].tolist()[0]
                    M_old_step = M_t.copy()
                    M_t[j, :] = sp.simplify(M_t[j, :] - factor * M_t[i, :])
                    f_r = M_t[j, :].tolist()[0]
                    
                    dibujar_paso(M_old_step, f_o, f_p, factor, f_r, 
                                 f"$R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}} \\to R_{{{j+1}}}$", 
                                 modo, es_primera)
                    es_primera = False
                    
    st.markdown("---")
    st.success("### Resultado Final:")
    st.latex(render_mat(M_t, modo, "\\approx"))

# --- INTERFAZ ---
st.markdown("#### Grupo 2AM2")
st.title("🚀 Matrix Master 3000")

col_in, col_ct = st.columns([2, 1])
with col_in:
    entrada = st.chat_input("Escribe los números (ej: 1 0 3) y presiona Enter")
    if entrada:
        fila = entrada.split()
        df_temp = pd.DataFrame([fila])
        if st.session_state.df_matriz.empty:
            st.session_state.df_matriz = df_temp
        else:
            df_temp.columns = [str(k) for k in range(len(fila))]
            st.session_state.df_matriz.columns = [str(k) for k in range(len(st.session_state.df_matriz.columns))]
            st.session_state.df_matriz = pd.concat([st.session_state.df_matriz, df_temp], ignore_index=True).fillna("0")
        st.session_state.df_matriz.columns = [str(k) for k in range(len(st.session_state.df_matriz.columns))]
        st.rerun()

    if not st.session_state.df_matriz.empty:
        st.session_state.df_matriz = st.data_editor(st.session_state.df_matriz, use_container_width=True, hide_index=True, num_rows="dynamic")
        if st.button("🗑️ Borrar Todo"):
            st.session_state.df_matriz = pd.DataFrame(); st.session_state.go = False; st.rerun()

with col_ct:
    metodo = st.radio("Operación:", ["Gauss-Jordan", "Inversa", "Determinante"])
    if st.button("CALCULAR", use_container_width=True, type="primary"):
        if not st.session_state.df_matriz.empty:
            st.session_state.m_obj = sp.Matrix(st.session_state.df_matriz.values).applyfunc(lambda x: sp.sympify(x))
            st.session_state.go = True

if st.session_state.go:
    M_val = st.session_state.m_obj
    m_proc = M_val.row_join(sp.eye(M_val.rows)) if metodo == "Inversa" else M_val
    resolver(m_proc, metodo)
