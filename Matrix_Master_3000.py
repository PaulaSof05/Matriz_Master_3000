import streamlit as st
import pandas as pd
import sympy as sp

# 1. Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS REFORMADO: SIN COLUMNA DE CONCEPTO Y MÁS ESPACIADO ---
st.markdown("""
    <style>
    .step-container {
        margin-bottom: 80px; /* Espacio generoso entre procedimientos */
        padding: 20px;
    }
    .table-side {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
        color: #e0e0e0;
        max-width: 500px;
    }
    .arit-table { 
        width: 100%; 
        border-collapse: collapse; 
        text-align: center; 
        font-size: 1.1em; /* Un poco más grande para legibilidad */
    }
    .arit-table td { border: 1px solid #444; padding: 12px; }
    .res-row { background-color: #1b3a24; font-weight: bold; color: #a5d6a7; }
    .header-row { background-color: #333; font-weight: bold; color: #ffffff; }
    /* Eliminamos cualquier rastro de cuadros rojos vacíos */
    .stAlert { display: none; } 
    </style>
    """, unsafe_allow_html=True)

if 'df_matriz' not in st.session_state:
    st.session_state.df_matriz = pd.DataFrame()
if 'go' not in st.session_state:
    st.session_state.go = False

# --- RENDERIZADO DE MATRIZ ---
def render_mat(M, modo, simbolo="\\approx"):
    n, m = M.shape
    # Forzamos fracciones verticales en el LaTeX
    M_tex = sp.latex(M, mat_delim='[') 
    if modo != "Determinante":
        c_str = "c" * (m-1) + "|c"
        M_tex = M_tex.replace(r"\begin{matrix}", rf"\begin{{array}}{{{c_str}}}").replace(r"\end{matrix}", r"\end{array}")
    return f"{simbolo} {M_tex}"

# --- TABLA ARITMÉTICA SIMPLIFICADA ---
def dibujar_paso(M_prev, f_obj, f_piv, factor, f_res, titulo, modo, es_primera=False, es_norm=False):
    simb = "=" if es_primera else "\\approx"
    
    st.markdown("<div class='step-container'>", unsafe_allow_html=True)
    col_mat, col_tab = st.columns([1, 1.2])
    
    with col_mat:
        # Aseguramos fracciones verticales en la operación de texto también
        st.latex(render_mat(M_prev, modo, simb))
        st.markdown(f"#### {titulo}")
    
    with col_tab:
        st.markdown("<div class='table-side'>", unsafe_allow_html=True)
        cols_head = "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))])
        
        # Lógica de filas según el tipo de operación
        if es_norm:
            # Para normalización: R_actual y Resultado
            fila_op = "".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])
            fila_res = "".join([f"<td>{sp.latex(x)}</td>" for x in f_res])
            tabla_html = f"""
            <table class='arit-table'>
                <tr class='header-row'>{cols_head}</tr>
                <tr>{fila_op}</tr>
                <tr class='res-row'>{fila_res}</tr>
            </table>
            """
        else:
            # Para eliminación: R_destino, Operación y Resultado
            fila_dest = "".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])
            fila_op = "".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv])
            fila_res = "".join([f"<td>{sp.latex(x)}</td>" for x in f_res])
            tabla_html = f"""
            <table class='arit-table'>
                <tr class='header-row'>{cols_head}</tr>
                <tr>{fila_dest}</tr>
                <tr>{fila_op}</tr>
                <tr class='res-row'>{fila_res}</tr>
            </table>
            """
        st.write(tabla_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- LÓGICA DE RESOLUCIÓN ---
def resolver(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    es_primera = True
    st.markdown("## Proceso de Resolución")
    
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
        
        # 2. Normalización del Pivote (Hacer 1)
        piv = M_t[i, i]
        if piv != 0:
            M_before = M_t.copy()
            f_o = M_before[i, :].tolist()[0]
            M_t[i, :] = sp.simplify(M_t[i, :] / piv)
            f_r = M_t[i, :].tolist()[0]
            
            # Formato de la operación: R1 / (valor) -> R1
            # Usamos frac para asegurar que sea vertical
            op_text = f"R_{{{i+1}}} / ({sp.latex(piv)}) \\to R_{{{i+1}}}"
            
            dibujar_paso(M_before, f_o, f_o, piv, f_r, f"${op_text}$", modo, es_primera, es_norm=True)
            es_primera = False
            
        # 3. Eliminación (Hacer 0's)
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
