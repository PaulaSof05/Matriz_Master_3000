import streamlit as st
import pandas as pd
import sympy as sp

# 1. Configuracion de pagina
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS PARA RESTAURAR EL DISEÑO OSCURO PROFESIONAL ---
st.markdown("""
    <style>
    /* Estilo general del contenedor de operaciones */
    .op-card {
        background-color: #1e1e1e;
        border-left: 5px solid #ff4b4b;
        padding: 20px;
        margin: 15px 0;
        border-radius: 5px;
        color: white;
    }
    /* Tabla aritmética con estilo oscuro */
    .arit-table { 
        width: 100%; 
        border-collapse: collapse; 
        text-align: center; 
        margin-top: 15px;
        color: #e0e0e0;
    }
    .arit-table td { border: 1px solid #444; padding: 10px; }
    .res-row { background-color: #1b3a24; font-weight: bold; color: #a5d6a7; }
    .header-row { background-color: #333; font-weight: bold; }
    
    /* Ajuste de editor de datos */
    [data-testid="stTable"] thead { display: none; }
    </style>
    """, unsafe_allow_html=True)

if 'df_matriz' not in st.session_state:
    st.session_state.df_matriz = pd.DataFrame()
if 'go' not in st.session_state:
    st.session_state.go = False

# --- FUNCIÓN PARA RENDERIZAR MATRIZ CON RAYA DIVISORIA ---
def mostrar_matriz_aumentada(M, modo):
    if modo == "Determinante":
        st.latex(sp.latex(M))
    else:
        # Crea la representación LaTeX con la línea vertical antes de la última columna
        n, m = M.shape
        c_str = "c" * (m-1) + "|c"
        lat_str = sp.latex(M).replace(r"\begin{matrix}", rf"\begin{{array}}{{{c_str}}}").replace(r"\end{matrix}", r"\end{array}")
        st.latex(lat_str)

# --- TABLA DE OPERACIONES CON DISEÑO CORREGIDO ---
def tabla_aritmetica(f_obj, f_piv, factor, f_res, titulo):
    with st.container():
        st.markdown(f"<div class='op-card'><b>{titulo}</b>", unsafe_allow_html=True)
        cols_head = "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))])
        html = f"""
        <table class='arit-table'>
            <tr class='header-row'><td>Concepto</td>{cols_head}</tr>
            <tr><td>R. Destino</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])}</tr>
            <tr><td>-({sp.latex(factor)}) * R_piv</td>{"".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv])}</tr>
            <tr class='res-row'><td>Resultado</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_res])}</tr>
        </table></div>
        """
        st.write(html, unsafe_allow_html=True)

# --- LÓGICA DE RESOLUCIÓN ---
def resolver(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    det_signo = 1
    
    st.markdown("### Proceso de Resolución")
    mostrar_matriz_aumentada(M_t, modo)

    for i in range(min(n, cols)):
        # Equipo 4: Pivoteo
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_signo *= -1
                    st.info(f"Intercambio: $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    mostrar_matriz_aumentada(M_t, modo)
                    break
        
        piv = M_t[i, i]
        if piv == 0: continue

        # Equipo 3: Normalización (Hacer 1 pivote)
        if modo != "Determinante" and piv != 1:
            M_t[i, :] = sp.simplify(M_t[i, :] / piv)
            st.write(f"Normalización: $R_{{{i+1}}} = R_{{{i+1}}} / ({sp.latex(piv)})$")
            mostrar_matriz_aumentada(M_t, modo)

        # Equipos 2 y 1: Eliminación (Ceros abajo y arriba)
        for j in range(n):
            if i != j:
                if modo == "Determinante" and j < i: continue
                factor = M_t[j, i]
                if factor != 0:
                    f_o = M_t[j, :].tolist()[0]
                    f_p = M_t[i, :].tolist()[0]
                    M_t[j, :] = sp.simplify(M_t[j, :] - factor * M_t[i, :])
                    
                    tabla_aritmetica(f_o, f_p, factor, M_t[j, :].tolist()[0], 
                                   f"Operación: $R_{{{j+1}}} = R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    mostrar_matriz_aumentada(M_t, modo)

    st.markdown("---")
    if modo == "Determinante":
        det_final = sp.simplify(det_signo * sp.Mul(*[M_t[x, x] for x in range(n)]))
        st.success(f"### Valor del Determinante: **{sp.latex(det_final)}**")
    elif modo == "Inversa":
        st.success("### Matriz Inversa Resultante ($A^{-1}$):")
        st.latex(sp.latex(M_t[:, n:]))
    else:
        st.success("### Resultado Final:")
        mostrar_matriz_aumentada(M_t, modo)

# --- INTERFAZ ---
st.markdown("#### Grupo 2AM2")
st.title("🚀 Matrix Master 3000")

col_in, col_ct = st.columns([2, 1])

with col_in:
    st.markdown("### ⌨️ Entrada por Renglón")
    entrada = st.chat_input("Escribe los números (ej: 1 2 3) y presiona Enter")
    if entrada:
        fila = entrada.split()
        df_temp = pd.DataFrame([fila])
        if st.session_state.df_matriz.empty:
            st.session_state.df_matriz = df_temp
        else:
            df_temp.columns = st.session_state.df_matriz.columns if len(fila) == len(st.session_state.df_matriz.columns) else [str(k) for k in range(len(fila))]
            st.session_state.df_matriz = pd.concat([st.session_state.df_matriz, df_temp], ignore_index=True).fillna("0")
        st.rerun()

    if not st.session_state.df_matriz.empty:
        st.session_state.df_matriz = st.data_editor(st.session_state.df_matriz, use_container_width=True, hide_index=True, num_rows="dynamic")
        if st.button("🗑️ Borrar Todo"):
            st.session_state.df_matriz = pd.DataFrame()
            st.session_state.go = False
            st.rerun()

with col_ct:
    st.markdown("### ⚙️ Configuración")
    metodo = st.radio("Selecciona la operación:", ["Gauss-Jordan", "Inversa", "Determinante"])
    if st.button("CALCULAR", use_container_width=True, type="primary"):
        if not st.session_state.df_matriz.empty:
            st.session_state.m_obj = sp.Matrix(st.session_state.df_matriz.values).applyfunc(lambda x: sp.sympify(x))
            st.session_state.go = True

if st.session_state.go:
    M_val = st.session_state.m_obj
    if (metodo in ["Inversa", "Determinante"]) and M_val.rows != M_val.cols:
        st.error("Error: La matriz debe ser cuadrada.")
    else:
        m_proc = M_val.row_join(sp.eye(M_val.rows)) if metodo == "Inversa" else M_val
        resolver(m_proc, metodo)
