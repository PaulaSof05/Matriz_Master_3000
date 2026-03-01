import streamlit as st
import pandas as pd
from fractions import Fraction
import sympy as sp
from fpdf import FPDF
import base64

# Configuración de la página
st.set_page_config(page_title="Matrix Master PRO", layout="wide", page_icon="🧮")

# Función para generar el PDF
def generar_pdf(A, b):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Hoja de Práctica: Álgebra Lineal", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Resuelve el siguiente sistema por el método de Gauss-Jordan:", ln=True)
    pdf.ln(5)
    
    # Escribir el sistema de ecuaciones
    for i in range(len(A)):
        eq_str = ""
        for j in range(len(A[0])):
            coef = A[i][j]
            signo = " + " if j > 0 and not str(coef).startswith('-') else " "
            eq_str += f"{signo}{coef}x{j+1}"
        eq_str += f" = {b[i][0]}"
        pdf.cell(200, 10, txt=eq_str, ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="_________________ Procedimiento _________________", ln=True, align='C')
    
    return bytes(pdf.output())

st.title("🧮 Matrix Master: Edition Antigravity")
st.write("Generador de sistemas, resolución exacta y exportación a PDF.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuración")
    n_vars = st.number_input("Variables:", min_value=1, max_value=6, value=3)
    n_eqs = st.number_input("Ecuaciones:", min_value=1, max_value=6, value=n_vars)
    
    st.subheader("🎲 Generación")
    rango = st.slider("Rango de enteros:", -20, 20, (-9, 9))
    
    if st.button("Generar Sistema Aleatorio"):
        st.session_state.matrix_A = pd.DataFrame(
            [[str(sp.randint(rango[0], rango[1]+1)) for _ in range(n_vars)] for _ in range(n_eqs)]
        )
        st.session_state.vector_b = pd.DataFrame(
            [[str(sp.randint(rango[0], rango[1]+1))] for _ in range(n_eqs)]
        )

# --- INICIALIZACIÓN ---
if 'matrix_A' not in st.session_state:
    st.session_state.matrix_A = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.vector_b = pd.DataFrame([["0"] for _ in range(n_eqs)])

# --- EDITOR ---
st.subheader("✍️ Sistema de Ecuaciones (Matriz Aumentada)")
col1, col2 = st.columns([3, 1])
with col1:
    A_edit = st.data_editor(st.session_state.matrix_A, key="A_ed")
with col2:
    b_edit = st.data_editor(st.session_state.vector_b, key="b_ed")

# --- BOTONES DE ACCIÓN ---
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Resolver con Paso a Paso", use_container_width=True):
        try:
            A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_edit.values])
            b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_edit.values])
            M_aug = A_sym.row_join(b_sym)
            
            st.divider()
            st.latex(r"\text{Matriz Inicial: } " + sp.latex(M_aug))
            
            # Resultado RREF
            res_rref, pivots = M_aug.rref()
            st.success("✅ Forma Escalonada Reducida (Gauss-Jordan):")
            st.latex(sp.latex(res_rref))
            
            # Soluciones
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)
            
            if sols:
                st.subheader("💡 Resultado Final:")
                for v in vars_sym:
                    st.latex(f"{sp.latex(v)} = {sp.latex(sols.get(v, sp.symbols('Libre')))}")
            else:
                st.warning("⚠️ El sistema no tiene solución única.")
        except:
            st.error("Error: Revisa que todos los campos tengan números o fracciones (ej. 1/2).")

with c2:
    # Generar PDF
    pdf_data = generar_pdf(A_edit.values.tolist(), b_edit.values.tolist())
    st.download_button(
        label="📥 Descargar Hoja de Práctica (PDF)",
        data=pdf_data,
        file_name="ejercicio_matrices.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# --- HERRAMIENTAS EXTRAS ---
with st.expander("🛠️ Otras Operaciones"):
    A_sym_ex = sp.Matrix([[sp.Rational(x) for x in row] for row in A_edit.values])
    t1, t2 = st.tabs(["Inversa", "Determinante"])
    with t1:
        if n_vars == n_eqs:
            if A_sym_ex.det() != 0:
                st.latex(r"A^{-1} = " + sp.latex(A_sym_ex.inv()))
            else: st.write("La matriz es singular.")
    with t2:
        if n_vars == n_eqs:
            st.latex(r"|A| = " + sp.latex(A_sym_ex.det()))