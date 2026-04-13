import streamlit as st
import pandas as pd
import sympy as sp
import random

# Configuración básica para usar todo el ancho de la pantalla
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ALGORITMO GAUSS-JORDAN (CORE) ---
def resolver_gauss_jordan(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    
    for i in range(min(n_eqs, n_cols - 1)):
        # 1. Búsqueda de Pivote (Consistente con Equipo 4)
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        
        # 2. Hacer el pivote 1 (Consistente con Equipo 3)
        if pivote != 0 and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        
        # 3. Hacer ceros en la columna (Consistente con Equipos 1 y 2)
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
    return M_aug

# --- TÍTULO Y CABECERA ---
st.title("🚀 Matrix Master 3000")
st.markdown("---")

# --- PANEL DE CONTROL (Generación Aleatoria) ---
col_info, col_btn = st.columns([3, 1])

with col_info:
    n_vars, n_eqs = 3, 3 # Dimensiones fijas según tus requerimientos
    st.info(f"Matriz de trabajo: **{n_eqs} ecuaciones** con **{n_vars} variables**.")

with col_btn:
    if st.button("🎲 Generar Valores Aleatorios", use_container_width=True):
        # Generamos números enteros para facilitar la edición inicial
        A = [[random.randint(-9, 9) for _ in range(n_vars)] for _ in range(n_eqs)]
        b = [[random.randint(-9, 9)] for _ in range(n_eqs)]
        st.session_state.Asys = pd.DataFrame([[str(x) for x in r] for r in A])
        st.session_state.bsys = pd.DataFrame([[str(x[0])] for x in b])
        st.rerun()

# Inicialización de datos en Session State
if 'Asys' not in st.session_state:
    st.session_state.Asys = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.bsys = pd.DataFrame([["0"] for _ in range(n_eqs)])

# --- INTERFAZ DE EDICIÓN (Look & Feel de tus notas) ---
st.write("### ⌨️ Entrada de Datos: Matriz Aumentada")
col_A, col_b = st.columns([3, 1])

with col_A: 
    A_ed = st.data_editor(st.session_state.Asys, hide_index=True, use_container_width=True, key="editor_A")
with col_b: 
    b_ed = st.data_editor(st.session_state.bsys, hide_index=True, use_container_width=True, key="editor_b")

# Sincronizamos cambios
st.session_state.Asys, st.session_state.bsys = A_ed, b_ed

# --- BOTÓN DE ACCIÓN ---
if st.button("🚀 Resolver con Gauss-Jordan", use_container_width=True, type="primary"):
    try:
        # Conversión a Sympy para manejo exacto de fracciones
        A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_ed.values])
        b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_ed.values])
        M_aug = A_sym.row_join(b_sym)
        
        # Ejecución del algoritmo paso a paso
        resolver_gauss_jordan(M_aug)
        
        # --- SOLUCIÓN FINAL POR NIVELES ---
        st.markdown("---")
        st.subheader("💡 Conjunto Solución")
        
        vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
        sols = sp.solve_linear_system(M_aug, *vars_sym)

        if sols is None:
            st.error(r"El sistema es Inconsistente (Sin solución): $\{ \emptyset \}$")
        else:
            lista_soluciones = [sols.get(v, v) for v in vars_sym]
            
            st.markdown("**Nivel 1 (Formato de conjunto):**")
            st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_soluciones])}) \}}")
            
            st.markdown("**Nivel 2 (Valores directos):**")
            st.latex(rf"S = \{{ {','.join([sp.latex(s) for s in lista_soluciones])} \}}")

    except Exception as e:
        st.error(f"⚠️ Error en el formato de datos: Ingresa solo números o fracciones (ej: 1/3).")
