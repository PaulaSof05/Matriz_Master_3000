import streamlit as st
import pandas as pd
import sympy as sp

st.set_page_config(page_title="Matrices", layout="wide")

# Estilos de la interfaz
st.markdown("""
    <style>
    [data-testid="stTable"] thead, [data-testid="stDataTable"] thead { display: none; }
    .op-card {
        background-color: #ffffff;
        border-left: 5px solid #d32f2f;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        color: black;
    }
    .arit-table { width: 100%; border-collapse: collapse; text-align: center; }
    .arit-table td { border: 1px solid #ddd; padding: 8px; }
    .res-row { background-color: #e8f5e9; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'df_matriz' not in st.session_state:
    st.session_state.df_matriz = pd.DataFrame()

def tabla_aritmetica(f_obj, f_piv, factor, f_res, titulo):
    with st.container():
        st.markdown(f"<div class='op-card'><b>{titulo}</b>", unsafe_allow_html=True)
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

# --- IMPLEMENTACIÓN DE LOS DIAGRAMAS ---

def ceros_arriba(M, i_pivote):
    # Basado en Diagrama Equipo 1
    # Inicio -> F = i -> k = i - 1 -> k < 0?
    n, cols = M.shape
    k = i_pivote - 1
    
    while k >= 0:
        factor = M[k, i_pivote]
        if factor != 0:
            f_obj = M[k, :].tolist()[0]
            f_piv = M[i_pivote, :].tolist()[0]
            M[k, :] = sp.simplify(M[k, :] - factor * M[i_pivote, :])
            
            tabla_aritmetica(f_obj, f_piv, factor, M[k, :].tolist()[0], 
                           f"Equipo 1 (Ceros arriba): $R_{{{k+1}}} = R_{{{k+1}}} - ({sp.latex(factor)})R_{{{i_pivote+1}}}$")
            st.latex(sp.latex(M))
        k = k - 1
    return M

def ceros_abajo(M, i_pivote):
    # Basado en Diagrama Equipo 2
    # Definir L = i -> Mientras ak+1 <= m -> Sea K = ai y K != 0
    n, cols = M.shape
    k = i_pivote + 1
    
    while k < n:
        factor = M[k, i_pivote]
        if factor != 0:
            f_obj = M[k, :].tolist()[0]
            f_piv = M[i_pivote, :].tolist()[0]
            M[k, :] = sp.simplify(M[k, :] - factor * M[i_pivote, :])
            
            tabla_aritmetica(f_obj, f_piv, factor, M[k, :].tolist()[0], 
                           f"Equipo 2 (Ceros abajo): $R_{{{k+1}}} = R_{{{k+1}}} - ({sp.latex(factor)})R_{{{i_pivote+1}}}$")
            st.latex(sp.latex(M))
        k = k + 1
    
    # El diagrama del Equipo 2 conecta con "O's arriba"
    return ceros_arriba(M, i_pivote)

def hacer_1_pivote(M, i_pivote):
    # Basado en Diagrama Equipo 3
    # Leer R[i], pivote -> i=0 -> i < TAM -> Arr[i] = R[i]/a
    n, cols = M.shape
    pivote_val = M[i_pivote, i_pivote]
    
    if pivote_val != 1 and pivote_val != 0:
        M[i_pivote, :] = sp.simplify(M[i_pivote, :] / pivote_val)
        st.write(f"Equipo 3 (Hacer 1 pivote): $R_{{{i_pivote+1}}} = R_{{{i_pivote+1}}} / {sp.latex(pivote_val)}$")
        st.latex(sp.latex(M))
    
    # El diagrama del Equipo 3 llama a "Hacer 0's abajo"
    return ceros_abajo(M, i_pivote)

def encontrar_cambiar_pivote(M):
    # Basado en Diagrama Equipo 4
    n, cols = M.shape
    # Nota: Se ajusta el i, j para iterar sobre la diagonal principal en orden
    for j in range(min(n, cols)):
        i = j
        if M[i, j] == 0:
            # Buscar aij != 0
            for k in range(i + 1, n):
                if M[k, j] != 0:
                    # Rx = R1, R1 = Ri, Ri = Rx
                    M[i, :], M[k, :] = M[k, :], M[i, :]
                    st.info(f"Equipo 4 (Cambio): $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M))
                    break
        
        # El diagrama llama a "Hacer 1 pivote"
        M = hacer_1_pivote(M, j)
    return M

# --- INTERFAZ ---
st.markdown("#### Grupo 2AM2")
st.title("Calculadora de Matrices")

col_input, col_ctrl = st.columns([2, 1], gap="large")

with col_input:
    st.markdown("### Entrada de Datos")
    input_renglon = st.chat_input("Escribe los numeros del renglon (ej: 1 0 3) y presiona Enter")
    
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
        st.markdown("##### Matriz Actual (Editable)")
        matriz_editada = st.data_editor(
            st.session_state.df_matriz,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
        st.session_state.df_matriz = matriz_editada
        
        if st.button("Limpiar Matriz", use_container_width=False):
            st.session_state.df_matriz = pd.DataFrame()
            st.session_state.go = False
            st.rerun()
    else:
        st.info("Utiliza el cuadro de texto inferior para ingresar los renglones.")

with col_ctrl:
    st.markdown("### Configuracion")
    metodo = st.radio(
        "Operacion a realizar:",
        ["Gauss-Jordan", "Inversa", "Determinante"],
        help="Gauss-Jordan para cualquier matriz. Inversa y Determinante solo para cuadradas."
    )
    
    if metodo in ["Inversa", "Determinante"]:
        st.caption("Nota: La matriz debe ser cuadrada.")
    
    if st.button("EJECUTAR CALCULO", use_container_width=True, type="primary"):
        if not st.session_state.df_matriz.empty:
            try:
                # sp.sympify para manejo simbolico (letras y numeros)
                M_final = sp.Matrix(st.session_state.df_matriz.values).applyfunc(lambda x: sp.sympify(x))
                st.session_state.go = True
                st.session_state.m_obj = M_final
            except Exception as e:
                st.error(f"Error en el formato de datos: {e}")
        else:
            st.error("Ingrese una matriz para continuar.")

# --- PROCESAMIENTO ---
if st.session_state.go:
    st.markdown("---")
    M = st.session_state.m_obj
    n, m = M.shape
    if (metodo == "Inversa" or metodo == "Determinante") and n != m:
        st.error("Error: La operacion requiere una matriz cuadrada.")
    else:
        m_proc = M.row_join(sp.eye(n)) if metodo == "Inversa" else M
        resolver(m_proc, metodo)
