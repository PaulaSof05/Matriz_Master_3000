import streamlit as st
import pandas as pd
import sympy as sp

# 1. Configuracion de pagina - Estilo Fijo
st.set_page_config(page_title="Matrices", layout="wide")

# --- CSS PARA ESTILO PROFESIONAL (SIN EMOJIS) ---
st.markdown("""
    <style>
    [data-testid="stTable"] thead, [data-testid="stDataTable"] thead { display: none; }
    .arit-table { width: 100%; border-collapse: collapse; text-align: center; margin-top: 10px; }
    .arit-table td { border: 1px solid #ddd; padding: 8px; }
    .res-row { background-color: #f1f8e9; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACION DEL ESTADO ---
if 'df_matriz' not in st.session_state:
    st.session_state.df_matriz = pd.DataFrame()
if 'go' not in st.session_state:
    st.session_state.go = False

# --- FUNCIONES BASADAS EN LOS DIAGRAMAS DE CLASE ---

def tabla_aritmetica(f_obj, f_piv, factor, f_res, titulo):
    st.markdown(f"**{titulo}**")
    cols_head = "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))])
    html = f"""
    <table class='arit-table'>
        <tr style='background:#f8f9fa; font-weight:bold;'><td>Concepto</td>{cols_head}</tr>
        <tr><td>R. Destino</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])}</tr>
        <tr><td>-({sp.latex(factor)}) * R_piv</td>{"".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv])}</tr>
        <tr class='res-row'><td>Resultado</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in f_res])}</tr>
    </table>
    """
    st.write(html, unsafe_allow_html=True)

def ceros_arriba(M, i_pivote):
    # Logica Equipo 1
    k = i_pivote - 1
    while k >= 0:
        factor = M[k, i_pivote]
        if factor != 0:
            f_o = M[k, :].tolist()[0]
            f_p = M[i_pivote, :].tolist()[0]
            M[k, :] = sp.simplify(M[k, :] - factor * M[i_pivote, :])
            tabla_aritmetica(f_o, f_p, factor, M[k, :].tolist()[0], f"R{k+1} = R{k+1} - ({sp.latex(factor)})R{i_pivote+1}")
            st.latex(sp.latex(M))
        k = k - 1
    return M

def ceros_abajo(M, i_pivote):
    # Logica Equipo 2
    n, _ = M.shape
    k = i_pivote + 1
    while k < n:
        factor = M[k, i_pivote]
        if factor != 0:
            f_o = M[k, :].tolist()[0]
            f_p = M[i_pivote, :].tolist()[0]
            M[k, :] = sp.simplify(M[k, :] - factor * M[i_pivote, :])
            tabla_aritmetica(f_o, f_p, factor, M[k, :].tolist()[0], f"R{k+1} = R{k+1} - ({sp.latex(factor)})R{i_pivote+1}")
            st.latex(sp.latex(M))
        k = k + 1
    return ceros_arriba(M, i_pivote)

def hacer_1_pivote(M, i_pivote):
    # Logica Equipo 3
    piv_val = M[i_pivote, i_pivote]
    if piv_val != 1 and piv_val != 0:
        M[i_pivote, :] = sp.simplify(M[i_pivote, :] / piv_val)
        st.write(f"Normalizacion: R{i_pivote+1} = R{i_pivote+1} / {sp.latex(piv_val)}")
        st.latex(sp.latex(M))
    return ceros_abajo(M, i_pivote)

def flujo_principal(M):
    # Logica Equipo 4
    n, cols = M.shape
    for j in range(min(n, cols)):
        if M[j, j] == 0:
            for k in range(j + 1, n):
                if M[k, j] != 0:
                    M[j, :], M[k, :] = M[k, :], M[j, :]
                    st.info(f"Intercambio: R{j+1} <-> R{k+1}")
                    st.latex(sp.latex(M))
                    break
        M = hacer_1_pivote(M, j)
    return M

# --- INTERFAZ ---
st.write("Grupo 2AM2")
st.subheader("Entrada por Renglón")

col_in, col_op = st.columns([2, 1])

with col_in:
    input_r = st.chat_input("Escribe los numeros del renglon y presiona Enter")
    if input_r:
        nueva_f = input_r.split()
        temp = pd.DataFrame([nueva_f])
        if st.session_state.df_matriz.empty:
            st.session_state.df_matriz = temp
            st.session_state.df_matriz.columns = [str(i) for i in range(len(nueva_f))]
        else:
            n_c = len(st.session_state.df_matriz.columns)
            if len(nueva_f) > n_c:
                for i in range(n_c, len(nueva_f)): st.session_state.df_matriz[str(i)] = "0"
            st.session_state.df_matriz = pd.concat([st.session_state.df_matriz, temp], ignore_index=True).fillna("0")
        st.rerun()

    if not st.session_state.df_matriz.empty:
        st.session_state.df_matriz = st.data_editor(st.session_state.df_matriz, use_container_width=True, hide_index=True)
        if st.button("Borrar Todo"):
            st.session_state.df_matriz = pd.DataFrame()
            st.session_state.go = False
            st.rerun()

with col_op:
    metodo = st.radio("Operacion:", ["Gauss-Jordan", "Inversa"])
    if st.button("CALCULAR", use_container_width=True, type="primary"):
        if not st.session_state.df_matriz.empty:
            st.session_state.m_obj = sp.Matrix(st.session_state.df_matriz.values).applyfunc(lambda x: sp.sympify(x))
            st.session_state.go = True

if st.session_state.go:
    st.markdown("---")
    M_calc = st.session_state.m_obj
    if metodo == "Inversa":
        if M_calc.rows != M_calc.cols: st.error("Debe ser cuadrada.")
        else:
            res = flujo_principal(M_calc.row_join(sp.eye(M_calc.rows)))
            st.success("Matriz Inversa Resultante:")
            st.latex(sp.latex(res[:, M_calc.rows:]))
    else:
        res = flujo_principal(M_calc)
        st.success("Resultado Final:")
        st.latex(sp.latex(res))
