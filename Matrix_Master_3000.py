import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ALGORITMO GAUSS-JORDAN (CORE) ---
def resolver_gauss_jordan(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    
    for i in range(min(n_eqs, n_cols - 1)):
        # 1. Búsqueda de Pivote (Consistente con Diagrama Equipo 4)
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        
        # 2. Hacer el pivote 1 (Consistente con Diagrama Equipo 3)
        if pivote != 0 and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        
        # 3. Hacer ceros en la columna (Consistente con Diagramas Equipos 1 y 2)
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
    return M_aug

st.title("🚀 Matrix Master 3000")
st.markdown("---")

# --- ÁREA DE CONTROL PRINCIPAL (Sustituye a la barra lateral) ---
col_ctrl1, col_ctrl2 = st.columns([2, 1])

with col_ctrl1:
    st.subheader("Configuración de Matriz")
    # Valores por defecto fijos para evitar "preguntar" constantemente
    n_vars = 3
    n_eqs = 3
    st.info(f"Matriz actual de {n_eqs}x{n_vars}. Puedes editar los valores directamente abajo.")

with col_ctrl2:
    if st.button("🎲 Generar Aleatorio", use_container_width=True):
        # Generación rápida para pruebas
        A = [[random.randint(-9, 9) for _ in range(n_vars)] for _ in range(n_eqs)]
        b = [[random.randint(-9, 9)] for _ in range(n_eqs)]
        st.session_state.Asys = pd.DataFrame([[str(x) for x in r] for r in A])
        st.session_state.bsys = pd.DataFrame([[str(x[0])] for x in b])
        st.rerun()

# --- INICIALIZACIÓN DE DATOS ---
if 'Asys' not in st.session_state:
    st.session_state.Asys = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.bsys = pd.DataFrame([["0"] for _ in range(n_eqs)])

# --- INTERFAZ DE EDICIÓN (Look & Feel centralizado) ---
st.write("### ⌨️ Edita tu Matriz Aumentada")
col_edit1, col_edit2 = st.columns([3, 1])

with col_edit1: 
    A_ed = st.data_editor(st.session_state.Asys, hide_index=True, use_container_width=True, key="editor_A")
with col_edit2: 
    b_ed = st.data_editor(st.session_state.bsys, hide_index=True, use_container_width=True, key="editor_b")

# Guardar cambios
st.session_state.Asys = A_ed
st.session_state.bsys = b_ed

if st.button("🚀 Resolver Paso a Paso", use_container_width=True):
    try:
        # Convertir datos del editor a objetos de Sympy
        A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_ed.values])
        b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_ed.values])
        M_aug = A_sym.row_join(b_sym)
        
        # Ejecutar algoritmo de Gauss-Jordan
        resolver_gauss_jordan(M_aug)
        
        # --- RESULTADOS Y NIVELES ---
        st.markdown("---")
        st.subheader("💡 Solución Final")

        vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
        sols = sp.solve_linear_system(M_aug, *vars_sym)

        if sols is None:
            st.error(r"El sistema no tiene solución: $\{ \emptyset \}$")
        else:
            libres = [v for v in vars_sym if v not in sols]
            lista_soluciones = [sols.get(v, v) for v in vars_sym]
            
            # Formateo de niveles solicitado
            st.markdown("#### Nivel 1")
            txt_vars = ",".join([sp.latex(v) for v in vars_sym])
            txt_vals = ",".join([sp.latex(s) for s in lista_soluciones])
            st.latex(rf"\{{ ({txt_vars}) : {txt_vals} \}}")

            st.markdown("#### Nivel 2")
            st.latex(rf"\{{ {txt_vals} \}}")

            if libres:
                st.markdown("#### Nivel 3 (Vectorial)")
                constantes = [s.subs({v: 0 for v in libres}) for s in lista_soluciones]
                txt_const = ",".join([sp.latex(c) for c in constantes])
                partes_n3 = [f"({txt_const})"]
                for v_libre in libres:
                    directores = [sp.diff(s, v_libre) for s in lista_soluciones]
                    txt_dir = ",".join([sp.latex(d) for d in directores])
                    partes_n3.append(f"{sp.latex(v_libre)}({txt_dir})")
                st.latex(rf"\{{ {' + '.join(partes_n3)} \}}")

    except Exception as e:
        st.error(f"Error en los datos: {e}")
