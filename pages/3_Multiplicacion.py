import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Multiplicación", layout="wide")
st.title("✖️ Multiplicación (A × B)")

with st.sidebar:
    rA = st.number_input("Filas A:", 1, 6, 3)
    cA = st.number_input("Cols A / Filas B:", 1, 6, 3)
    cB = st.number_input("Cols B:", 1, 6, 3)

if st.sidebar.button("🎲 Generar"):
    st.session_state.Amul = pd.DataFrame([[str(random.randint(-5, 5)) for _ in range(cA)] for _ in range(rA)])
    st.session_state.Bmul = pd.DataFrame([[str(random.randint(-5, 5)) for _ in range(cB)] for _ in range(cA)])
    st.rerun()

if 'Amul' not in st.session_state:
    st.session_state.Amul = pd.DataFrame([["1"]*cA for _ in range(rA)])
    st.session_state.Bmul = pd.DataFrame([["1"]*cB for _ in range(cA)])

c1, c2 = st.columns(2)
with c1: A_ed = st.data_editor(st.session_state.Amul, key="m_a")
with c2: B_ed = st.data_editor(st.session_state.Bmul, key="m_b")

if st.button("Calcular Producto"):
    A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
    B = sp.Matrix([[sp.Rational(x) for x in r] for r in B_ed.values])
    # 
    st.latex(sp.latex(A) + "\\times" + sp.latex(B) + "=" + sp.latex(A*B))