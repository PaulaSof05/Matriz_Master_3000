import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Inversa y Det", layout="wide")
st.title("🔍 Inversa y Determinante")

dim = st.sidebar.number_input("Dimensión (n x n):", 1, 6, 3)

if st.sidebar.button("🎲 Generar"):
    st.session_state.Ainv = pd.DataFrame([[str(random.randint(-9, 9)) for _ in range(dim)] for _ in range(dim)])
    st.rerun()

if 'Ainv' not in st.session_state:
    st.session_state.Ainv = pd.DataFrame([["1" if i==j else "0" for j in range(dim)] for i in range(dim)])

A_ed = st.data_editor(st.session_state.Ainv, key="inv_a")

if st.button("Analizar"):
    A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
    st.write(f"**Determinante:**")
    st.latex(f"|A| = {A.det()}")
    if A.det() != 0:
        st.write(f"**Inversa:**")
        st.latex(f"A^{{-1}} = {sp.latex(A.inv())}")
    else: st.warning("Matriz singular (Determinante = 0). No tiene inversa.")