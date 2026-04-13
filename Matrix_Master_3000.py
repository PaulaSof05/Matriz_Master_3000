import streamlit as st
import pandas as pd
import sympy as sp
import random

# --- CONFIGURACIÓN DE PÁGINA Y OCULTAR MENÚ ---
st.set_page_config(page_title="Matrix Master 3000", layout="wide", initial_sidebar_state="collapsed")

# CSS para eliminar definitivamente el sidebar y el botón de despliegue
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# --- ALGORITMO GAUSS-JORDAN (CORE) ---
def resolver_gauss_jordan(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    
    for i in range(min(n_eqs, n_cols - 1)):
        # 1. Búsqueda de Pivote
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        
        # 2. Hacer el pivote 1
        if pivote != 0 and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        
        # 3. Hacer ceros en la columna
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
    return M_aug

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Matrix Master 3000")
st.markdown("---")

col_ctrl1, col_ctrl2 = st.columns([2, 1])

with col_ctrl1:
    st.subheader("Configuración de Matriz")
    n_vars, n_eqs = 3, 3 # Valores fijos como pediste
    st.info(f"Matriz actual de {n_eqs}x{n_vars}.")

with col_ctrl2:
    if st.button("🎲 Generar Aleatorio", use_container_width=True):
        A = [[random.randint(-9, 9) for _ in range(n_vars)] for _ in range(n_eqs)]
        b = [[random.randint(-9, 9)] for _ in range(n_eqs)]
        st.session_state.Asys = pd.DataFrame([[str(x) for x in r] for r in A])
        st.session_state.bsys = pd.DataFrame([[str(x[0])] for x in b])
        st.rerun()

if 'Asys' not in st.session_state:
    st.session_state.Asys = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.bsys = pd.DataFrame([["0"] for _ in range(n_eqs)])

st.write("### ⌨️ Edita tu Matriz Aumentada")
col_edit1, col_edit2 = st.columns([3, 1])

with col_edit1: 
    A_ed = st.data_editor(st.session_state.Asys, hide_index=True, use_container_width=True, key="editor_A")
with col_edit2: 
    b_ed = st.data_editor(st.session_state.bsys, hide_index=True, use_container_width=True, key="editor_b")

st.session_state.Asys, st.session_state.bsys = A_ed, b_ed

if st.button("🚀 Resolver Paso a Paso", use_container_width=True):
    try:
        A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_ed.values])
        b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_ed.values])
        M_aug = A_sym.row_join(b_sym)
        
        resolver_gauss_jordan(M_aug)
        
        st.markdown("---")
        st.subheader("💡 Solución Final")
        vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
        sols = sp.solve_linear_system(M_aug, *vars_sym)

        if sols is None:
            st.error(r"Sin solución: $\{ \emptyset \}$")
        else:
            lista_soluciones = [sols.get(v, v) for v in vars_sym]
            st.markdown("#### Nivel 1")
            st.latex(rf"\{{ ({','.join([sp.latex(v) for v in vars_sym])}) : {','.join([sp.latex(s) for s in lista_soluciones])} \}}")
            st.markdown("#### Nivel 2")
            st.latex(rf"\{{ {','.join([sp.latex(s) for s in lista_soluciones])} \}}")

    except Exception as e:
        st.error(f"Error: {e}")
