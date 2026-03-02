import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Rango y Transpuesta", layout="wide")
st.title("📊 Propiedades: Rango y Transpuesta")

with st.sidebar:
    st.header("Configuración")
    rows = st.number_input("Filas:", 1, 10, 3)
    cols = st.number_input("Columnas:", 1, 10, 3)
    
    if st.button("🎲 Generar Aleatoria"):
        # Generamos una matriz con algunos ceros para que el rango sea interesante
        matriz = [[str(random.randint(-5, 5) if random.random() > 0.2 else 0) 
                  for _ in range(cols)] for _ in range(rows)]
        st.session_state.A_prop = pd.DataFrame(matriz)
        st.rerun()

# Inicialización
if 'A_prop' not in st.session_state:
    st.session_state.A_prop = pd.DataFrame([["0"]*cols for _ in range(rows)])

st.subheader("Ingresa tu matriz:")
A_ed = st.data_editor(st.session_state.A_prop, key="prop_editor")

if st.button("Analizar Propiedades", use_container_width=True):
    try:
        # Convertir a matriz de SymPy
        A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.info("### 📐 Matriz Transpuesta ($A^T$)")
            st.write("Intercambiamos filas por columnas:")
            st.latex(sp.latex(A.transpose()))
            
        with col_b:
            st.success("### 🔢 Rango de la Matriz")
            rango = A.rank()
            st.write(f"El rango es el número de filas linealmente independientes.")
            st.latex(f"rank(A) = {rango}")
            
        st.divider()
        
        # Extra: Forma Escalonada Reducida (RREF)
        st.subheader("📑 Forma Escalonada Reducida por Renglones (RREF)")
        st.write("Esta es la matriz simplificada al máximo mediante Gauss-Jordan:")
        rref_matrix, pivots = A.rref()
        st.latex(sp.latex(rref_matrix))
        st.write(f"Columnas con pivotes: {list(pivots)}")

    except Exception as e:
        st.error(f"Error en el cálculo: {e}")

#