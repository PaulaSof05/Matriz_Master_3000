import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTable { background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .aritmetica-container {
        background-color: #ffffff;
        border-left: 5px solid #ff4b4b;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .step-header { color: #1f77b4; font-weight: bold; border-bottom: 2px solid #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CÁLCULO ---
def tabla_paso_a_paso(f_obj, f_piv, factor, f_res, texto):
    """Genera la tabla de aritmética que el profe quiere ver"""
    with st.container():
        st.markdown(f"<div class='aritmetica-container'>", unsafe_allow_html=True)
        st.write(f"**Operación:** {texto}")
        
        # Crear DataFrame para la tabla aritmética
        data = {
            "Concepto": ["Renglón a modificar", f"-({sp.latex(factor)}) * R_pivote", "Resultado Final"],
            **{f"Col {i+1}": [sp.latex(f_obj[i]), sp.latex(-factor*f_piv[i]), sp.latex(f_res[i])] for i in range(len(f_obj))}
        }
        st.table(pd.DataFrame(data))
        st.markdown("</div>", unsafe_allow_html=True)

def resolver_todo(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    det_acumulado = 1
    
    st.markdown(f"### 🏁 Procedimiento: {modo.upper()}")
    st.write("Matriz Inicial:")
    st.latex(sp.latex(M_t))

    for i in range(min(n, cols)):
        # 1. Pivoteo
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_acumulado *= -1
                    st.info(f"🔄 Intercambio: $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_t))
                    break
        
        pivote = M_t[i, i]
        if pivote == 0: continue

        # 2. Normalización (Hacer 1 el pivote)
        if modo != "Determinante" and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_t[i, :] = M_t[i, :] * inv
            st.write(f"🎯 **Hacer 1 el pivote:** $R_{{{i+1}}} \\to R_{{{i+1}}} / {sp.latex(pivote)}$")
            st.latex(sp.latex(M_t))

        # 3. Eliminación
        for j in range(n):
            if i != j:
                if modo == "Determinante" and j < i: continue # Triangular para det
                factor = M_t[j, i]
                if factor != 0:
                    f_old = M_t[j, :].tolist()[0]
                    f_piv = M_t[i, :].tolist()[0]
                    M_t[j, :] = M_t[j, :] - factor * M_t[i, :]
                    
                    tabla_paso_a_paso(f_old, f_piv, factor, M_t[j, :].tolist()[0], 
                                     f"$R_{{{j+1}}} \\to R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M_t))

    if modo == "Determinante":
        diag = [M_t[x,x] for x in range(n)]
        res_det = det_acumulado * np.prod(diag)
        st.success(f"### Resultado Final del Determinante: {sp.latex(res_det)}")
    else:
        st.success("### Resultado Final:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Matrix Master 3000")
st.write("Desarrollado para Data Science - IPN ESCOM")

# Layout de columnas
col_izq, col_der = st.columns([1.5, 1])

with col_izq:
    st.subheader("⌨️ Entrada de Datos")
    st.markdown("""
    **Instrucciones:**
    1. Escribe los números de tu matriz abajo.
    2. Usa **espacio** para separar columnas y **Enter** para nuevas filas.
    3. La tabla se dibujará automáticamente abajo.
    """)
    
    # El área de texto que no pierde el foco
    raw_text = st.text_area("Escribe aquí:", height=150, placeholder="1 0 2\n0 1 -1\n3 2 0", key="input_principal")
    
    # Procesar entrada para la tabla visual
    if raw_text:
        try:
            lineas = [l.split() for l in raw_text.strip().split('\n') if l.strip()]
            max_c = max(len(l) for l in lineas)
            # Rellenar con ceros si falta algo (a prueba de tontos)
            matriz_final = [l + ["0"]*(max_c - len(l)) for l in lineas]
            
            st.write("### 📊 Matriz Detectada")
            st.table(pd.DataFrame(matriz_final)) # Aquí está tu tabla visual
            
            M_ready = sp.Matrix([[sp.Rational(x) for x in fila] for fila in matriz_final])
        except:
            st.error("⚠️ Solo se permiten números y espacios.")
            M_ready = None
    else:
        M_ready = None

with col_der:
    st.subheader("⚙️ Opciones del Sistema")
    opcion = st.selectbox("Selecciona la operación:", ["Gauss-Jordan", "Inversa", "Determinante"])
    
    st.warning("Asegúrate de que la matriz sea cuadrada para Inversa o Determinante.")
    
    if st.button("🚀 CALCULAR AHORA", use_container_width=True, type="primary"):
        if M_ready:
            st.session_state.do_math = True
        else:
            st.error("Primero ingresa una matriz.")

st.markdown("---")

# --- ÁREA DE PROCEDIMIENTO ---
if st.session_state.get('do_math', False) and M_ready:
    n, m = M_ready.shape
    
    if opcion == "Gauss-Jordan":
        resolver_todo(M_ready, "Gauss-Jordan")
    elif opcion == "Inversa":
        if n != m: st.error("No es cuadrada.")
        else: resolver_todo(M_ready.row_join(sp.eye(n)), "Inversa")
    elif opcion == "Determinante":
        if n != m: st.error("No es cuadrada.")
        else: resolver_todo(M_ready, "Determinante")
