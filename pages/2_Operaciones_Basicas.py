import streamlit as st
import pandas as pd
import sympy as sp
import random

st.set_page_config(page_title="Suma y Resta", layout="wide")
st.title("➕ Operaciones Básicas (A ± B)")

rows = st.sidebar.number_input("Filas:", 1, 6, 3)
cols = st.sidebar.number_input("Columnas:", 1, 6, 3)

if st.sidebar.button("🎲 Generar Aleatorios"):
    st.session_state.A_bas = pd.DataFrame([[str(random.randint(-9, 9)) for _ in range(cols)] for _ in range(rows)])
    st.session_state.B_bas = pd.DataFrame([[str(random.randint(-9, 9)) for _ in range(cols)] for _ in range(rows)])
    st.rerun()

if 'A_bas' not in st.session_state:
    st.session_state.A_bas = pd.DataFrame([["0"]*cols for _ in range(rows)])
    st.session_state.B_bas = pd.DataFrame([["0"]*cols for _ in range(rows)])

c1, c2 = st.columns(2)
with c1: st.write("**Matriz A**"); A_ed = st.data_editor(st.session_state.A_bas, key="bas_a")
with c2: st.write("**Matriz B**"); B_ed = st.data_editor(st.session_state.B_bas, key="bas_b")

op = st.radio("Operación:", ["Suma (A + B)", "Resta (A - B)"], horizontal=True)

if st.button("Calcular"):
    A = sp.Matrix([[sp.Rational(x) for x in r] for r in A_ed.values])
    B = sp.Matrix([[sp.Rational(x) for x in r] for r in B_ed.values])
    res = A + B if "+" in op else A - B
    # 
    st.latex(sp.latex(A) + ("+" if "+" in op else "-") + sp.latex(B) + "=" + sp.latex(res))