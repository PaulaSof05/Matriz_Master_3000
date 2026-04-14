import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .op-table { width: 100%; border-collapse: collapse; font-family: 'Courier New', monospace; margin: 20px 0; background-color: #f8f9fa; }
    .op-table td { border: 1px solid #dee2e6; padding: 12px; text-align: center; }
    .row-label { background-color: #e9ecef; font-weight: bold; width: 150px; }
    .row-res { background-color: #d4edda; font-weight: bold; border-top: 2px solid #28a745; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE ARITMÉTICA VISUAL ---
def mostrar_aritmetica(f_obj, f_piv, factor, f_res, titulo):
    st.write(f"#### ➕ Desglose Aritmético: {titulo}")
    
    # Construcción de la tabla HTML
    html = f"<table class='op-table'>"
    html += f"<tr><td class='row-label'>Renglón Destino</td>" + "".join([f"<td>{sp.latex(x)}</td>" for x in f_obj]) + "</tr>"
    html += f"<tr><td class='row-label'>$-({sp.latex(factor)}) \\times R_{{piv}}$</td>" + "".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv]) + "</tr>"
    html += f"<tr class='row-res'><td class='row-label'>Resultado</td>" + "".join([f"<td>{sp.latex(x)}</td>" for x in f_res]) + "</tr>"
    html += "</table>"
    st.write(html, unsafe_allow_html=True)

# --- MOTOR GAUSS-JORDAN ---
def ejecutar_metodo(M, modo="gauss"):
    n, cols = M.shape
    M_t = M.copy()
    det_signo = 1
    
    st.write(f"### ⚙️ Procesando: {modo.upper()}")
    st.latex(sp.latex(M_t))

    for i in range(min(n, cols)):
        # Pivoteo (Equipo 4)
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_signo *= -1
                    st.info(f"🔄 Intercambio: $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_t))
                    break
        
        piv = M_t[i, i]
        if piv == 0: continue

        # Normalización (Hacer 1 el pivote - Equipo 3)
        if modo != "determinante" and piv != 1:
            m_inv = sp.Rational(1, piv)
            M_t[i, :] = M_t[i, :] * m_inv
            st.write(f"🎯 Normalizar pivote: $R_{{{i+1}}} \\to R_{{{i+1}}} / {sp.latex(piv)}$")
            st.latex(sp.latex(M_t))

        # Eliminación (Equipos 1 y 2)
        for j in range(n):
            if i != j:
                if modo == "determinante" and j < i: continue # Triangular para det
                
                factor = M_t[j, i]
                if factor != 0:
                    f_old = M_t[j, :].tolist()[0]
                    f_piv = M_t[i, :].tolist()[0]
                    M_t[j, :] = M_t[j, :] - factor * M_t[i, :]
                    
                    mostrar_aritmetica(f_old, f_piv, factor, M_t[j, :].tolist()[0], 
                                      f"$R_{{{j+1}}} = R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M_t))

    if modo == "determinante":
        diag = [M_t[x,x] for x in range(n)]
        res = det_signo * np.prod(diag)
        st.success(f"### 🏁 Determinante: {sp.latex(det_signo)} × ({' × '.join([sp.latex(d) for d in diag])}) = **{sp.latex(res)}**")
    else:
        st.success("### 🏁 Matriz Resultante:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")

col_input, col_tools = st.columns([2, 1])

with col_input:
    st.subheader("⌨️ Constructor de Matriz")
    st.markdown("_Escribe números. **Espacio** = Siguiente columna, **Enter** = Siguiente fila._")
    
    # El usuario escribe aquí. Al ser un solo input, el foco nunca se pierde.
    raw = st.text_area("Entrada rápida:", height=100, placeholder="1 2 3\n4 5 6", key="input_celda")
    
    # Convertimos el texto a una tabla visual instantáneamente
    try:
        filas = [f.split() for f in raw.strip().split('\n') if f.strip()]
        if filas:
            max_c = max(len(f) for f in filas)
            matriz_limpia = [f + ["0"]*(max_c - len(f)) for f in filas]
            
            # Dibujamos la tabla "a prueba de tontos"
            st.write("**Tabla Detectada:**")
            st.table(pd.DataFrame(matriz_limpia))
            
            M_ready = sp.Matrix([[sp.Rational(x) for x in f] for f in matriz_limpia])
        else:
            M_ready = None
    except:
        st.error("⚠️ Formato inválido. Solo números y espacios.")
        M_ready = None

with col_tools:
    st.subheader("⚙️ Opciones")
    metodo = st.selectbox("Operación:", ["Gauss-Jordan", "Matriz Inversa", "Determinante (Gauss)"])
    if st.button("🚀 CALCULAR", use_container_width=True, type="primary"):
        st.session_state.ejecutar = True
    else:
        if 'ejecutar' not in st.session_state: st.session_state.ejecutar = False

st.markdown("---")

# --- RESULTADOS ---
if st.session_state.ejecutar and M_ready is not None:
    n, m = M_ready.shape
    if metodo == "Gauss-Jordan":
        ejecutar_metodo(M_ready, "gauss")
    elif metodo == "Matriz Inversa":
        if n != m: st.error("Debe ser cuadrada.")
        else: ejecutar_metodo(M_ready.row_join(sp.eye(n)), "inversa")
    elif metodo == "Determinante (Gauss)":
        if n != m: st.error("Debe ser cuadrada.")
        else: ejecutar_metodo(M_ready, "determinante")
