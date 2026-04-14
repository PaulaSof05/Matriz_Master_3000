import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .aritmetica-table { width: 100%; border: 2px solid #4CAF50; border-collapse: collapse; margin-bottom: 20px; }
    .aritmetica-table td { border: 1px solid #ddd; padding: 10px; text-align: center; font-family: monospace; }
    .header-row { background-color: #f2f2f2; font-weight: bold; }
    .res-row { background-color: #e8f5e9; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE ARITMÉTICA VISUAL ---
def tabla_aritmetica(fila_obj, fila_piv, factor, resultado, operacion):
    """Genera la tabla de operaciones que pidió el profe"""
    st.write(f"**Operación detallada:** {operacion}")
    html = f"""
    <table class="aritmetica-table">
        <tr class="header-row"><td>Componente</td>{"".join([f"<td>Col {i+1}</td>" for i in range(len(fila_obj))])}</tr>
        <tr><td>Renglón Objetivo</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in fila_obj])}</tr>
        <tr><td>-({sp.latex(factor)}) × R_pivote</td>{"".join([f"<td>{sp.latex(-factor*x)}</td>" for x in fila_piv])}</tr>
        <tr class="res-row"><td>Nuevo Renglón</td>{"".join([f"<td>{sp.latex(x)}</td>" for x in resultado])}</tr>
    </table>
    """
    st.write(html, unsafe_allow_html=True)

# --- LÓGICA DE GAUSS-JORDAN ---
def resolver_matriz(matriz, modo="gauss"):
    M = matriz.copy()
    n, cols = M.shape
    st.write(f"## 🛠️ Procedimiento: {modo.upper()}")
    
    # Determinante por Gauss (multiplicación de diagonal)
    det_acumulado = 1
    
    for i in range(min(n, cols)):
        # 1. Pivoteo
        if M[i, i] == 0:
            for k in range(i + 1, n):
                if M[k, i] != 0:
                    M[i, :], M[k, :] = M[k, :], M[i, :]
                    det_acumulado *= -1
                    st.write(f"🔄 Intercambio $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M))
                    break

        pivote = M[i, i]
        if pivote == 0: continue

        # 2. Normalización (Excepto para determinante puro para evitar fracciones feas antes de tiempo)
        if modo != "determinante" and pivote != 1:
            factor_inv = sp.Rational(1, pivote)
            M[i, :] = M[i, :] * factor_inv
            st.write(f"🎯 Hacer 1 el pivote: $R_{{{i+1}}} \\to R_{{{i+1}}} / {sp.latex(pivote)}$")
            st.latex(sp.latex(M))

        # 3. Eliminación
        for j in range(n):
            if i != j:
                # Si es determinante, solo hacemos ceros abajo (triangular)
                if modo == "determinante" and j < i: continue
                
                factor = M[j, i]
                if factor != 0:
                    f_obj = M[j, :].tolist()[0]
                    f_piv = M[i, :].tolist()[0]
                    M[j, :] = M[j, :] - factor * M[i, :]
                    
                    tabla_aritmetica(f_obj, f_piv, factor, M[j, :].tolist()[0], 
                                     f"$R_{{{j+1}}} \\to R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M))
    
    if modo == "determinante":
        diag = [M[i,i] for i in range(n)]
        res_det = det_acumulado * np.prod(diag)
        st.write(f"### 🏁 Determinante = {sp.latex(det_acumulado)} × ({' × '.join([sp.latex(x) for x in diag])}) = **{sp.latex(res_det)}**")
    else:
        st.write("### 🏁 Resultado Final:")
        st.latex(sp.latex(M))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")

# Panel Superior: Entrada "Infinita" a prueba de errores
st.subheader("⌨️ Dibujar Matriz")
st.info("💡 Cada vez que escribas valores en la última fila o columna, la tabla crecerá sola. ¡A prueba de tontos!")

if 'matriz_dinamica' not in st.session_state:
    st.session_state.matriz_dinamica = pd.DataFrame([[""]], columns=[" "])

# Editor elástico
df_usuario = st.data_editor(
    st.session_state.matriz_dinamica,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="editor_reactivo"
)
st.session_state.matriz_dinamica = df_usuario

# Layout: Herramientas a la derecha
col_proc, col_opciones = st.columns([3, 1])

with col_opciones:
    st.markdown("### ⚙️ Acciones")
    accion = st.selectbox("Selecciona operación:", 
                          ["Gauss-Jordan", "Inversa", "Determinante"])
    
    procesar = st.button("🚀 CALCULAR", use_container_width=True, type="primary")

with col_proc:
    if procesar:
        try:
            # Limpiar datos y detectar m x n
            df_nans = df_usuario.replace(r'^\s*$', np.nan, regex=True)
            cuadro = df_nans.dropna(how='all').dropna(axis=1, how='all')
            
            # Convertir a Sympy
            datos = []
            for _, r in cuadro.iterrows():
                datos.append([sp.Rational(str(v)) if pd.notnull(v) else 0 for v in r])
            
            M_final = sp.Matrix(datos)
            
            if accion == "Gauss-Jordan":
                resolver_matriz(M_final, "gauss")
            elif accion == "Inversa":
                if M_final.shape[0] != M_final.shape[1]:
                    st.error("La matriz debe ser cuadrada.")
                else:
                    resolver_matriz(M_final.row_join(sp.eye(M_final.shape[0])), "inversa")
            elif accion == "Determinante":
                if M_final.shape[0] != M_final.shape[1]:
                    st.error("La matriz debe ser cuadrada.")
                else:
                    resolver_matriz(M_final, "determinante")
                    
        except Exception as e:
            st.error(f"Error en los datos: Revisa que no haya letras.")
