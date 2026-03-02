import streamlit as st
import pandas as pd
import sympy as sp
from fpdf import FPDF
import random

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Matrix Master PRO", layout="wide", page_icon="🧮")

# Inicializar estados si no existen
if 'matriz_A' not in st.session_state:
    st.session_state.matriz_A = pd.DataFrame([["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]])
if 'matriz_B' not in st.session_state:
    st.session_state.matriz_B = pd.DataFrame([["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]])
if 'vector_b' not in st.session_state:
    st.session_state.vector_b = pd.DataFrame([["0"], ["0"], ["0"]])

# --- FUNCIONES DE GAUSS-JORDAN ---

def resolver_gauss_robot(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan Estricto")
    st.latex(sp.latex(M_aug))
    for i in range(min(n_eqs, n_cols - 1)):
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        if pivote != 1:
            inverso = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inverso
            st.write(f"**Operación:** $({sp.latex(inverso)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        else:
            st.write(f"**Nota:** El pivote en $R_{{ {i+1} }}$ ya es $1$.")
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                else:
                    st.write(f"**Nota:** En $R_{{ {j+1} }}$ ya hay un cero.")
    return M_aug

def resolver_gauss_humano(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🧠 Procedimiento: Gauss-Jordan Humano")
    st.latex(sp.latex(M_aug))
    for i in range(min(n_eqs, n_cols - 1)):
        for j in range(i + 1, n_eqs):
            if abs(M_aug[j, i]) == 1:
                M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$ (Pivote ideal)")
                st.latex(sp.latex(M_aug))
                break
        pivote = M_aug[i, i]
        if pivote != 1 and pivote != 0:
            inverso = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inverso
            st.write(f"**Operación:** $({sp.latex(inverso)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        for j in range(n_eqs):
            if i != j and M_aug[j, i] != 0:
                factor = M_aug[j, i]
                M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                st.latex(sp.latex(M_aug))
    return M_aug

# --- UTILIDADES ---

def generar_pdf(A, b=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Matrix Master - Exportacion", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Matriz / Sistema:", ln=True)
    for row in A:
        pdf.cell(200, 10, txt=str(row), ln=True)
    return bytes(pdf.output())

# --- MENÚ LATERAL ---

with st.sidebar:
    st.title("🎮 Panel de Control")
    opcion = st.selectbox(
        "¿Qué quieres hacer?",
        ["Sistemas de Ecuaciones", "Operaciones Básicas (A ± B)", "Multiplicación (A × B)", "Inversa y Determinante"]
    )
    st.divider()
    
    if opcion == "Sistemas de Ecuaciones":
        n_vars = st.number_input("Variables:", 1, 6, 3)
        n_eqs = st.number_input("Ecuaciones:", 1, 6, n_vars)
        metodo = st.radio("Estrategia:", ["Gauss-Jordan", "Gauss-Jordan Humano"])
        dif = st.select_slider("Dificultad:", ["Fácil", "Medio", "Difícil"], "Medio")
    else:
        rows_a = st.number_input("Filas A:", 1, 6, 3)
        cols_a = st.number_input("Cols A:", 1, 6, 3)
        if opcion == "Multiplicación (A × B)":
            cols_b = st.number_input("Cols B:", 1, 6, 3)
            rows_b = cols_a # Por regla de matrices
        elif opcion == "Operaciones Básicas (A ± B)":
            rows_b, cols_b = rows_a, cols_a
        else: # Inversa
            rows_b, cols_b = rows_a, cols_a

    rango = st.slider("Rango de valores:", -20, 20, (-9, 9))

    if st.button("🎲 Generar Aleatorios"):
        if opcion == "Sistemas de Ecuaciones":
            if dif == "Fácil":
                sol = [random.randint(-3, 3) for _ in range(n_vars)]
                A_raw = [[random.randint(rango[0], rango[1]) for _ in range(n_vars)] for _ in range(n_eqs)]
                b_raw = [[sum(A_raw[i][j] * sol[j] for j in range(n_vars))] for i in range(n_eqs)]
            elif dif == "Medio":
                den = random.choice([2, 3])
                sol = [sp.Rational(random.randint(-4, 4), den) for _ in range(n_vars)]
                A_raw = [[random.randint(rango[0], rango[1]) for _ in range(n_vars)] for _ in range(n_eqs)]
                b_raw = [[sum(A_raw[i][j] * sol[j] for j in range(n_vars))] for i in range(n_eqs)]
            else:
                A_raw = [[random.randint(rango[0], rango[1]) for _ in range(n_vars)] for _ in range(n_eqs)]
                b_raw = [[random.randint(rango[0], rango[1])] for _ in range(n_eqs)]
            st.session_state.matriz_A = pd.DataFrame([[str(x) for x in r] for r in A_raw])
            st.session_state.vector_b = pd.DataFrame([[str(x[0])] for x in b_raw])
        else:
            st.session_state.matriz_A = pd.DataFrame([[str(random.randint(rango[0], rango[1])) for _ in range(cols_a)] for _ in range(rows_a)])
            if opcion != "Inversa y Determinante":
                st.session_state.matriz_B = pd.DataFrame([[str(random.randint(rango[0], rango[1])) for _ in range(cols_b)] for _ in range(rows_b)])
        st.rerun()

# --- ÁREA DE TRABAJO ---

st.title(f"✨ {opcion}")

if opcion == "Sistemas de Ecuaciones":
    col1, col2 = st.columns([3, 1])
    with col1: A_ed = st.data_editor(st.session_state.matriz_A)
    with col2: b_ed = st.data_editor(st.session_state.vector_b)
    
    if st.button("🚀 Resolver Paso a Paso", use_container_width=True):
        try:
            A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_ed.values])
            b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_ed.values])
            M_aug = A_sym.row_join(b_sym)
            if metodo == "Gauss-Jordan": resolver_gauss_robot(M_aug)
            else: resolver_gauss_humano(M_aug)
            
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)
            st.subheader("💡 Resultado Final:")
            if sols:
                for v in vars_sym: st.latex(f"{sp.latex(v)} = {sp.latex(sols.get(v, 'Libre'))}")
            else: st.warning("Sistema sin solución única.")
        except Exception as e: st.error(f"Error: {e}")

elif opcion == "Operaciones Básicas (A ± B)":
    c1, c2 = st.columns(2)
    with c1: st.write("Matriz A"); A_ed = st.data_editor(st.session_state.matriz_A)
    with c2: st.write("Matriz B"); B_ed = st.data_editor(st.session_state.matriz_B)
    
    op = st.radio("Operación:", ["Suma (A + B)", "Resta (A - B)"], horizontal=True)
    if st.button("Calcular"):
        A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
        B = sp.Matrix([[sp.Rational(x) for x in r] for r in B_ed.values])
        res = A + B if "Suma" in op else A - B
        st.latex(sp.latex(A) + ("+" if "Suma" in op else "-") + sp.latex(B) + "=" + sp.latex(res))

elif opcion == "Multiplicación (A × B)":
    c1, c2 = st.columns(2)
    with c1: st.write("Matriz A"); A_ed = st.data_editor(st.session_state.matriz_A)
    with c2: st.write("Matriz B"); B_ed = st.data_editor(st.session_state.matriz_B)
    
    if st.button("Calcular Producto"):
        if A_ed.shape[1] == B_ed.shape[0]:
            A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
            B = sp.Matrix([[sp.Rational(x) for x in r] for r in B_ed.values])
            st.latex(sp.latex(A) + "\\times" + sp.latex(B) + "=" + sp.latex(A*B))
        else: st.error("Las columnas de A deben coincidir con las filas de B.")

elif opcion == "Inversa y Determinante":
    A_ed = st.data_editor(st.session_state.matriz_A)
    if st.button("Analizar Matriz"):
        A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
        if A.is_square:
            st.write(f"**Determinante:**")
            st.latex(f"|A| = {A.det()}")
            if A.det() != 0:
                st.write(f"**Matriz Inversa:**")
                st.latex(f"A^{{-1}} = {sp.latex(A.inv())}")
            else: st.warning("La matriz es singular (no tiene inversa).")
        else: st.error("La matriz debe ser cuadrada.")

# --- FOOTER ---
st.divider()
if st.download_button("📥 Descargar PDF de la vista actual", generar_pdf(st.session_state.matriz_A.values.tolist()), "matrix.pdf"):
    st.balloons()
