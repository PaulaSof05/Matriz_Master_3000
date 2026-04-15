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
    # Empezamos con un DataFrame vacío pero con estructura
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
            st.write(f"🎯 Hacer 1 el pivote: $R_{{{i+1}}} = R_{{{i+1}}} / {sp.latex(piv)}$")
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
        st.success(f"### 🏁 Determinante Final: **{sp.latex(res)}**")
    else:
        st.success("### 🏁 Resultado Final:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")

col_input, col_ctrl = st.columns([2, 1])

with col_input:
    st.subheader("⌨️ Entrada por Renglón")
    input_renglon = st.chat_input("Escribe los números de la fila (ej: 1 0 3) y presiona Enter")
    
    if input_renglon:
        nueva_fila = input_renglon.split()
        # Creamos un DataFrame temporal con la nueva fila
        temp_df = pd.DataFrame([nueva_fila])
        
        if st.session_state.df_matriz.empty:
            st.session_state.df_matriz = temp_df
        else:
            # Concatenamos y llenamos huecos con 0 si las filas tienen distinto tamaño
            st.session_state.df_matriz = pd.concat([st.session_state.df_matriz, temp_df], ignore_index=True).fillna("0")
        
        # --- EL TRUCO PARA EL ERROR: Forzar nombres de columnas únicos ---
        # Esto renombra las columnas a 0, 1, 2, 3... asegurando que no haya duplicados
        st.session_state.df_matriz.columns = [str(i) for i in range(len(st.session_state.df_matriz.columns))]
        
        st.rerun()

    # MOSTRAR LA MATRIZ COMO TABLA EDITABLE
    if not st.session_state.df_matriz.empty:
        st.write("### 📊 Matriz Detectada (Puedes editar celdas haciendo clic)")
        
        # El editor ahora recibirá columnas con nombres limpios
        matriz_editada = st.data_editor(
            st.session_state.df_matriz,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )
        # Sincronizamos los cambios realizados manualmente en la tabla
        st.session_state.df_matriz = matriz_editada
        
        # Botón para limpiar
        if st.button("🗑️ Borrar Todo"):
            st.session_state.df_matriz = pd.DataFrame()
            st.rerun()
    else:
        st.info("Escribe tu primer renglón abajo para empezar.")

with col_ctrl:
    st.subheader("⚙️ Opciones")
    metodo = st.selectbox("Operación:", ["Gauss-Jordan", "Inversa", "Determinante"])
    
    if st.button("🚀 CALCULAR", use_container_width=True, type="primary"):
        if not st.session_state.df_matriz.empty:
            try:
                # Convertir a Sympy para fracciones exactas
                M_final = sp.Matrix(st.session_state.df_matriz.values.astype(str)).applyfunc(sp.Rational)
                st.session_state.go = True
                st.session_state.m_obj = M_final
            except:
                st.error("Revisa que todos los datos sean números.")
        else:
            st.error("La matriz está vacía.")

st.markdown("---")

# --- PROCESAMIENTO ---
if st.session_state.get('go', False):
    M = st.session_state.m_obj
    n, m = M.shape
    if (metodo == "Inversa" or metodo == "Determinante") and n != m:
        st.error("Debe ser cuadrada.")
    else:
        m_proc = M.row_join(sp.eye(n)) if metodo == "Inversa" else M
        resolver(m_proc, metodo)
