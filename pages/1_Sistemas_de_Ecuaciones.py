import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Sistemas de Ecuaciones", layout="wide")

# --- ALGORITMO GAUSS-JORDAN (ROBOT) ---
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

st.title("🚀 Sistemas de Ecuaciones")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    n_vars = st.number_input("Variables:", 1, 6, 3, key="n_vars")
    n_eqs = st.number_input("Ecuaciones:", 1, 6, 3, key="n_eqs")
    
    st.markdown("---")
    dif = st.select_slider("Dificultad:", ["Fácil", "Medio", "Difícil"], "Fácil")
    rango = st.slider("Rango de números:", -15, 15, (-9, 9))

    if st.button("🎲 Generar Aleatorio"):
        if dif == "Fácil":
            sol = [random.randint(-3, 3) for _ in range(n_vars)]
            A = [[random.randint(rango[0], rango[1]) for _ in range(n_vars)] for _ in range(n_eqs)]
            b = [[sum(A[i][j] * sol[j] for j in range(n_vars))] for i in range(n_eqs)]
        elif dif == "Medio":
            den = random.choice([2, 3])
            sol = [sp.Rational(random.randint(-4, 4), den) for _ in range(n_vars)]
            A = [[random.randint(rango[0], rango[1]) for _ in range(n_vars)] for _ in range(n_eqs)]
            b = [[sum(A[i][j] * sol[j] for j in range(n_vars))] for i in range(n_eqs)]
        else:
            A = [[random.randint(rango[0], rango[1]) for _ in range(n_vars)] for _ in range(n_eqs)]
            b = [[random.randint(rango[0], rango[1])] for _ in range(n_eqs)]
        
        st.session_state.Asys = pd.DataFrame([[str(x) for x in r] for r in A])
        st.session_state.bsys = pd.DataFrame([[str(x[0])] for x in b])
        st.rerun()

# --- LÓGICA DE ACTUALIZACIÓN AUTOMÁTICA DE TABLAS ---
if 'Asys' not in st.session_state:
    st.session_state.Asys = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.bsys = pd.DataFrame([["0"] for _ in range(n_eqs)])

# Si el tamaño cambió en el sidebar, reajustamos el DataFrame sin borrar datos previos
if st.session_state.Asys.shape != (n_eqs, n_vars):
    # Crear nuevos DFs con el tamaño actual
    new_A = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    new_b = pd.DataFrame([["0"] for _ in range(n_eqs)])
    
    # Intentar copiar valores viejos a los nuevos
    for r in range(min(n_eqs, st.session_state.Asys.shape[0])):
        for c in range(min(n_vars, st.session_state.Asys.shape[1])):
            new_A.iloc[r, c] = st.session_state.Asys.iloc[r, c]
        if r < st.session_state.bsys.shape[0]:
            new_b.iloc[r, 0] = st.session_state.bsys.iloc[r, 0]
            
    st.session_state.Asys = new_A
    st.session_state.bsys = new_b

# --- INTERFAZ DE EDICIÓN ---
st.write("### ⌨️ Edita tu Matriz Aumentada")
col1, col2 = st.columns([3, 1])

# data_editor permite cambios rápidos. 
with col1: 
    A_ed = st.data_editor(st.session_state.Asys, hide_index=True, use_container_width=True, key="editor_A")
with col2: 
    b_ed = st.data_editor(st.session_state.bsys, hide_index=True, use_container_width=True, key="editor_b")

# Guardar cambios del editor en el session_state para no perderlos
st.session_state.Asys = A_ed
st.session_state.bsys = b_ed

if st.button("🚀 Resolver Paso a Paso", use_container_width=True):
    try:
        A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_ed.values])
        b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_ed.values])
        M_aug = A_sym.row_join(b_sym)
        
        # Ejecutar algoritmo
        resolver_gauss_jordan(M_aug)
        
        # --- RESULTADOS POR NIVELES ---
        st.markdown("---")
        st.subheader("💡 Resolución por Niveles")

        vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
        sols = sp.solve_linear_system(M_aug, *vars_sym)

        if sols is None:
            st.error(r"Resultado: $\{ \emptyset \}$")
        else:
            libres = [v for v in vars_sym if v not in sols]
            lista_soluciones = [sols.get(v, v) for v in vars_sym]
            
            # Nivel 1
            st.markdown("#### Nivel 1")
            txt_vars = ",".join([sp.latex(v) for v in vars_sym])
            txt_vals = ",".join([sp.latex(s) for s in lista_soluciones])
            st.latex(rf"\{{ ({txt_vars}) : {txt_vals} \}}")

            # Nivel 2
            st.markdown("#### Nivel 2")
            st.latex(rf"\{{ {txt_vals} \}}")

            # Nivel 3
            if libres:
                st.markdown("#### Nivel 3")
                constantes = [s.subs({v: 0 for v in libres}) for s in lista_soluciones]
                txt_const = ",".join([sp.latex(c) for c in constantes])
                partes_n3 = [f"({txt_const})"]
                for v_libre in libres:
                    directores = [sp.diff(s, v_libre) for s in lista_soluciones]
                    txt_dir = ",".join([sp.latex(d) for d in directores])
                    partes_n3.append(f"{sp.latex(v_libre)}({txt_dir})")
                st.latex(rf"\{{ {' + '.join(partes_n3)} \}}")
            else:
                st.info("Nota: No se requiere Nivel 3 (Solución única).")

    except Exception as e:
        st.error(f"Error en los datos: Asegúrate de ingresar números o fracciones válidas. Detalle: {e}")
