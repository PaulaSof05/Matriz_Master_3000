import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- CSS PARA ESTILO PROFESIONAL ---
st.markdown("""
    <style>
    /* Estilo para que el editor de matriz se vea como cuadrícula matemática */
    [data-testid="stTable"] thead, [data-testid="stDataTable"] thead { display: none; }
    .op-card {
        background-color: #ffffff;
        border-left: 5px solid #d32f2f;
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

# --- INICIALIZACIÓN DEL ESTADO ---
if 'df_matriz' not in st.session_state:
    st.session_state.df_matriz = pd.DataFrame()

# --- FUNCIONES DE CÁLCULO ---
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

def resolver(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    det_signo = 1
    st.latex(sp.latex(M_t))

    for i in range(min(n, cols)):
        # 1. Pivoteo (Intercambio de renglones si el pivote es 0)
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_signo *= -1
                    st.info(f"$R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_t))
                    break
        
        piv = M_t[i, i]
        if piv == 0: continue

        # 2. Normalización del pivote (Hacerlo 1)
        if modo != "Determinante" and piv != 1:
            M_t[i, :] = sp.simplify(M_t[i, :] / piv)
            st.write(f"$R_{{{i+1}}} = R_{{{i+1}}} / ({sp.latex(piv)})$")
            st.latex(sp.latex(M_t))

        # 3. Eliminación de las demás celdas en la columna
        for j in range(n):
            if i != j:
                if modo == "Determinante" and j < i: continue
                
                factor = M_t[j, i]
                if factor != 0:
                    f_o = M_t[j, :].tolist()[0]
                    f_p = M_t[i, :].tolist()[0]
                    M_t[j, :] = sp.simplify(M_t[j, :] - factor * M_t[i, :])
                    
                    tabla_aritmetica(
                        f_o, 
                        f_p, 
                        factor, 
                        M_t[j, :].tolist()[0], 
                        f"$R_{{{j+1}}} = R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$"
                    )
                    st.latex(sp.latex(M_t))

    # --- RESULTADOS FINALES ---
    if modo == "Determinante":
        diagonal = [M_t[x, x] for x in range(n)]
        det_final = sp.simplify(det_signo * sp.Mul(*diagonal))
        st.success(f"### Resultado: **{sp.latex(det_final)}**")
    
    elif modo == "Inversa":
        # Extraemos la parte derecha de la matriz aumentada (la inversa)
        M_inversa = M_t[:, n:]
        st.success("###Matriz Inversa Resultante ($A^{-1}$):")
        st.latex(sp.latex(M_inversa))
        
    else:
        st.success("###Resultado Final (Forma Escalonada Reducida):")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.write("Grupo 2AM2")

col_input, col_ctrl = st.columns([2, 1])

with col_input:
    st.subheader("Entrada por Renglón")
    input_renglon = st.chat_input("Escribe los números deL reglón (ej: 1 0 3) y presiona Enter")
    
    if input_renglon:
        nueva_fila = input_renglon.split()
        temp_df = pd.DataFrame([nueva_fila])
        
        if st.session_state.df_matriz.empty:
            st.session_state.df_matriz = temp_df
            st.session_state.df_matriz.columns = [str(i) for i in range(len(nueva_fila))]
        else:
            n_cols_actual = len(st.session_state.df_matriz.columns)
            n_cols_nueva = len(nueva_fila)
            
            if n_cols_nueva > n_cols_actual:
                for i in range(n_cols_actual, n_cols_nueva):
                    st.session_state.df_matriz[str(i)] = "0"
            
            temp_df.columns = [str(i) for i in range(n_cols_nueva)]
            st.session_state.df_matriz = pd.concat(
                [st.session_state.df_matriz, temp_df], 
                ignore_index=True
            ).fillna("0")
        
        st.session_state.df_matriz.columns = [str(i) for i in range(len(st.session_state.df_matriz.columns))]
        st.rerun()

    if not st.session_state.df_matriz.empty:
        st.write("### Matriz Detectada (Puedes editar celdas haciendo clic)")
        matriz_editada = st.data_editor(
            st.session_state.df_matriz,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
        st.session_state.df_matriz = matriz_editada
        
        if st.button("Borrar Todo"):
            st.session_state.df_matriz = pd.DataFrame()
            st.session_state.go = False
            st.rerun()
    else:
        st.info("Escribe tu primer renglón para empezar.")

with col_ctrl:
    
    metodo = st.radio(
        "Selecciona la operación:",
        ["Gauss-Jordan", "Inversa", "Determinante"],
        help="Gauss-Jordan funciona para cualquier matriz. Inversa y Determinante requieren matrices cuadradas."
    )
    
    if metodo in ["Inversa", "Determinante"]:
        st.warning("Asegúrate de que la matriz sea cuadrada.")
    
    if st.button("CALCULAR", use_container_width=True, type="primary"):
        if not st.session_state.df_matriz.empty:
            try:
                # sp.sympify permite manejar números y letras
                M_final = sp.Matrix(st.session_state.df_matriz.values).applyfunc(lambda x: sp.sympify(x))
                st.session_state.go = True
                st.session_state.m_obj = M_final
            except Exception as e:
                st.error(f"Error en el formato: {e}")
        else:
            st.error("La matriz está vacía.")

st.markdown("---")

# --- PROCESAMIENTO ---
if st.session_state.get('go', False):
    M = st.session_state.m_obj
    n, m = M.shape
    if (metodo == "Inversa" or metodo == "Determinante") and n != m:
        st.error("Debe ser cuadrada para esta operación.")
    else:
        # Para la inversa, aumentamos la matriz con la Identidad
        m_proc = M.row_join(sp.eye(n)) if metodo == "Inversa" else M
        resolver(m_proc, metodo)
