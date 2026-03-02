import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Sistemas de Ecuaciones", layout="wide")

# --- FUNCIONES DE RESOLUCIÓN ---
def resolver_gauss_robot(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    for i in range(min(n_eqs, n_cols - 1)):
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug)); pivote = M_aug[i, i]; break
        if pivote != 1:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        else: st.write(f"**Nota:** El pivote en $R_{{ {i+1} }}$ ya es $1$.")
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                else: st.write(f"**Nota:** El elemento en $R_{{ {j+1} }}, C_{{ {i+1} }}$ ya es $0$.")
    return M_aug

def resolver_gauss_humano(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🧠 Procedimiento: Gauss-Jordan mas Humano")
    st.latex(sp.latex(M_aug))
    for i in range(min(n_eqs, n_cols - 1)):
        for j in range(i + 1, n_eqs):
            if abs(M_aug[j, i]) == 1:
                M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$ (Pivote ideal)")
                st.latex(sp.latex(M_aug)); break
        pivote = M_aug[i, i]
        if pivote != 1 and pivote != 0:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        for j in range(n_eqs):
            if i != j and M_aug[j, i] != 0:
                factor = M_aug[j, i]
                M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                st.latex(sp.latex(M_aug))
    return M_aug

st.title("🚀 Sistemas de Ecuaciones")

with st.sidebar:
    n_vars = st.number_input("Variables:", 1, 6, 3)
    n_eqs = st.number_input("Ecuaciones:", 1, 6, 3)
    metodo = st.radio("Método:", ["Gauss-Jordan", "Gauss-Jordan Humano"])
    dif = st.select_slider("Dificultad:", ["Fácil", "Medio", "Aleatorio"], "Fácil")
    rango = st.slider("Rango:", -15, 15, (-9, 9))

    if st.button("🎲 Generar Sistema"):
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

# Inicialización de tablas
if 'Asys' not in st.session_state:
    st.session_state.Asys = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.bsys = pd.DataFrame([["0"] for _ in range(n_eqs)])

col1, col2 = st.columns([3, 1])
with col1: A_ed = st.data_editor(st.session_state.Asys, key="ed_Asys")
with col2: b_ed = st.data_editor(st.session_state.bsys, key="ed_bsys")

if st.button("🚀 Resolver Paso a Paso", use_container_width=True):
    try:
        A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_ed.values])
        b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_ed.values])
        M_aug = A_sym.row_join(b_sym)
        if "Robot" in metodo: resolver_gauss_robot(M_aug)
        else: resolver_gauss_humano(M_aug)
        
        # --- LÓGICA DE LOS 3 NIVELES (FORMATO HORIZONTAL Y CONJUNTOS) ---
        st.subheader("💡 Resolución por Niveles")

        vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
        sols = sp.solve_linear_system(M_aug, *vars_sym)

        if sols is None:
            st.error(r"Resultado: $\{ \emptyset \}$")
        else:
            libres = [v for v in vars_sym if v not in sols]
            # Lista de expresiones (valores o variables libres)
            lista_soluciones = [sols.get(v, v) for v in vars_sym]
            
            # --- NIVEL 1: DEFINICIÓN DE VARIABLES ---
            # Formato: { (x1,x2,x3) : val1, val2... }
            st.markdown("#### Nivel 1")
            txt_vars = ",".join([sp.latex(v) for v in vars_sym])
            txt_vals = ",".join([sp.latex(s) for s in lista_soluciones])
            st.latex(rf"\{{ ({txt_vars}) : {txt_vals} \}}")

            # --- NIVEL 2: CONJUNTO SOLUCIÓN GENERAL ---
            # Formato: { val1, val2, val3 }
            st.markdown("#### Nivel 2")
            st.latex(rf"\{{ {txt_vals} \}}")

            # --- NIVEL 3: DESCOMPOSICIÓN VECTORIAL HORIZONTAL ---
            if libres:
                st.markdown("#### Nivel 3")
                # Vector constante (libres = 0)
                constantes = [s.subs({v: 0 for v in libres}) for s in lista_soluciones]
                txt_const = ",".join([sp.latex(c) for c in constantes])
                
                partes_n3 = [f"({txt_const})"]
                
                for v_libre in libres:
                    # Obtenemos el "vector" director derivando cada componente
                    directores = [sp.diff(s, v_libre) for s in lista_soluciones]
                    txt_dir = ",".join([sp.latex(d) for d in directores])
                    partes_n3.append(f"{sp.latex(v_libre)}({txt_dir})")
                
                suma_n3 = " + ".join(partes_n3)
                st.latex(rf"\{{ {suma_n3} \}}")
            else:
                st.info("Nota: No se requiere Nivel 3 (Solución única).")

    except Exception as e: st.error(f"Error: {e}")

