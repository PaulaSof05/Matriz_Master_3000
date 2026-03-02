import streamlit as st
import pandas as pd
import sympy as sp
from fpdf import FPDF
import random

# Configuración de la página
st.set_page_config(page_title="Matrix Master", layout="wide", page_icon="🧮")

# --- FUNCIONES DE RESOLUCIÓN PASO A PASO ---

def resolver_gauss_robot(M_aug):
    """Algoritmo estricto: pivote a 1 y ceros arriba/abajo (incluye pasos redundantes)."""
    n_eqs, n_cols = M_aug.shape
    st.write("### Resuelto por Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    st.divider()

    for i in range(min(n_eqs, n_cols - 1)):
        pivote = M_aug[i, i]
        
        # Intercambio si el pivote es 0
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        
        # Convertir pivote a 1 (aunque ya lo sea, se menciona en el modo robot)
        if pivote != 1:
            inverso = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inverso
            st.write(f"**Operación:** $({sp.latex(inverso)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        else:
            st.write(f"**Nota:** El pivote en $R_{{ {i+1} }}$ ya es $1$. No se requiere operación.")
        
        # Hacer ceros en toda la columna (incluyendo si ya es cero)
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                else:
                    st.write(f"**Nota:** El elemento en $R_{{ {j+1} }}, C_{{ {i+1} }}$ ya es $0$. El renglón se mantiene igual.")
    return M_aug

def resolver_gauss_humano(M_aug):
    """Algoritmo humano: busca 1s e intercambia filas antes de operar (más ágil)."""
    n_eqs, n_cols = M_aug.shape
    st.write("### Resuelto por Gauss-Jordan mas Humano")
    st.latex(sp.latex(M_aug))
    st.divider()

    for i in range(min(n_eqs, n_cols - 1)):
        # Buscar un 1 o -1 estratégico
        for j in range(i + 1, n_eqs):
            if abs(M_aug[j, i]) == 1:
                M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$ (Buscando el 1)")
                st.latex(sp.latex(M_aug))
                break
        
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break

        # Mostrar como multiplicación por fracción si no es 1
        if pivote != 0 and pivote != 1:
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
    
# Función para generar el PDF
def generar_pdf(A, b):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Hoja de Practica: Algebra Lineal", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for i in range(len(A)):
        eq_str = ""
        for j in range(len(A[0])):
            coef = A[i][j]
            signo = " + " if j > 0 and not str(coef).startswith('-') else " "
            eq_str += f"{signo}{coef}x{j+1}"
        eq_str += f" = {b[i][0]}"
        pdf.cell(200, 10, txt=eq_str, ln=True)
    return bytes(pdf.output())

st.title("🧮 Matrix Master")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuracion")
    n_vars = st.number_input("Variables:", min_value=1, max_value=6, value=3)
    n_eqs = st.number_input("Ecuaciones:", min_value=1, max_value=6, value=n_vars)
    
    # Selector de Método (Sincronizado con la lógica de abajo)
    metodo_op = st.radio("Estrategia de Resolución:", ["Gauss-Jordan", "Gauss-Jordan mas humano"])
    
    st.subheader("🎲 Generacion")
    rango = st.slider("Rango:", -20, 20, (-9, 9))
    
    if st.button("Generar Sistema de ecuaciones"):
        st.session_state.matrix_A = pd.DataFrame(
            [[str(random.randint(rango[0], rango[1])) for _ in range(n_vars)] for _ in range(n_eqs)]
        )
        st.session_state.vector_b = pd.DataFrame(
            [[str(random.randint(rango[0], rango[1]))] for _ in range(n_eqs)]
        )

# --- INICIALIZACIÓN ---
if 'matrix_A' not in st.session_state:
    st.session_state.matrix_A = pd.DataFrame([["1"]*n_vars for _ in range(n_eqs)])
    st.session_state.vector_b = pd.DataFrame([["0"] for _ in range(n_eqs)])

# --- EDITOR ---
st.subheader("Sistema de Ecuaciones")
col1, col2 = st.columns([3, 1])
with col1:
    A_edit = st.data_editor(st.session_state.matrix_A, key="A_ed")
with col2:
    b_edit = st.data_editor(st.session_state.vector_b, key="b_ed")

# --- BOTONES DE ACCIÓN ---
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Procedimiento Paso a Paso", use_container_width=True):
        try:
            A_sym = sp.Matrix([[sp.Rational(x) for x in row] for row in A_edit.values])
            b_sym = sp.Matrix([[sp.Rational(x[0])] for x in b_edit.values])
            M_aug = A_sym.row_join(b_sym)
            
            st.divider()
            
            # Lógica de selección corregida
            if metodo_op == "Gauss-Jordan":
                res_final = resolver_gauss_robot(M_aug.copy())
            else:
                res_final = resolver_gauss_humano(M_aug.copy())
            
            st.success("✅ ¡Sistema resuelto!")
            
            # Soluciones
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)
            
            if sols:
                st.subheader("💡 Resultado Final:")
                for v in vars_sym:
                    st.latex(f"{sp.latex(v)} = {sp.latex(sols.get(v, sp.symbols('Libre')))}")
            else:
                st.warning("⚠️ El sistema no tiene solución única.")
        except Exception as e:
            st.error(f"Error: {e}")

with c2:
    pdf_data = generar_pdf(A_edit.values.tolist(), b_edit.values.tolist())
    st.download_button(
        label="📥 Descargar Hoja de Ejercicios (PDF)",
        data=pdf_data,
        file_name="ejercicio_matrices.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# --- HERRAMIENTAS EXTRAS ---
with st.expander("🛠️ Otras Operaciones"):
    try:
        A_sym_ex = sp.Matrix([[sp.Rational(x) for x in row] for row in A_edit.values])
        t1, t2 = st.tabs(["Inversa", "Determinante"])
        with t1:
            if n_vars == n_eqs:
                if A_sym_ex.det() != 0:
                    st.latex(r"A^{-1} = " + sp.latex(A_sym_ex.inv()))
                else: st.write("La matriz es singular.")
            else: st.write("Debe ser una matriz cuadrada.")
        with t2:
            if n_vars == n_eqs:
                st.latex(r"|A| = " + sp.latex(A_sym_ex.det()))
            else: st.write("Debe ser una matriz cuadrada.")
    except:
        st.write("Carga datos válidos para ver operaciones.")
