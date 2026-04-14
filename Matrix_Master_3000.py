import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# 1. Configuración de página
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILOS CSS PARA LA TABLA Y ARITMÉTICA ---
st.markdown("""
    <style>
    /* Cuadrícula de la Matriz Detectada */
    .matrix-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .matrix-table {
        border-collapse: collapse;
        background-color: white;
        color: #1f1f1f;
    }
    .matrix-table td {
        border: 2px solid #495057;
        padding: 15px;
        min-width: 60px;
        text-align: center;
        font-weight: bold;
        font-size: 1.3rem;
    }
    /* Estilo de las operaciones de renglón */
    .op-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .op-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .op-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    .header-row { background-color: #f8f9fa; font-weight: bold; }
    .res-row { background-color: #d4edda; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CÁLCULO ---
def mostrar_aritmetica(f_obj, f_piv, factor, f_res, titulo):
    with st.container():
        st.markdown(f"<div class='op-card'>", unsafe_allow_html=True)
        st.write(f"**🛠️ Operación:** {titulo}")
        
        # Generar tabla HTML de la operación
        cols_head = "".join([f"<td>C{i+1}</td>" for i in range(len(f_obj))])
        obj_row = "".join([f"<td>{sp.latex(x)}</td>" for x in f_obj])
        piv_row = "".join([f"<td>{sp.latex(-factor*x)}</td>" for x in f_piv])
        res_row = "".join([f"<td>{sp.latex(x)}</td>" for x in f_res])
        
        html = f"""
        <table class='op-table'>
            <tr class='header-row'><td>Concepto</td>{cols_head}</tr>
            <tr><td>R. Destino</td>{obj_row}</tr>
            <tr><td>Operación con Pivote</td>{piv_row}</tr>
            <tr class='res-row'><td>Nuevo Renglón</td>{res_row}</tr>
        </table>
        """
        st.write(html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def resolver_matriz(M, modo):
    n, cols = M.shape
    M_t = M.copy()
    det_factor = 1
    
    st.write("### 🏁 Inicio del Procedimiento")
    st.latex(sp.latex(M_t))

    for i in range(min(n, cols)):
        # 1. Pivoteo
        if M_t[i, i] == 0:
            for k in range(i + 1, n):
                if M_t[k, i] != 0:
                    M_t[i, :], M_t[k, :] = M_t[k, :], M_t[i, :]
                    det_factor *= -1
                    st.info(f"🔄 Intercambio: $R_{{{i+1}}} \\leftrightarrow R_{{{k+1}}}$")
                    st.latex(sp.latex(M_t))
                    break
        
        pivote = M_t[i, i]
        if pivote == 0: continue

        # 2. Normalización
        if modo != "Determinante" and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_t[i, :] = M_t[i, :] * inv
            st.write(f"🎯 **Normalización:** $R_{{{i+1}}} = R_{{{i+1}}} / {sp.latex(pivote)}$")
            st.latex(sp.latex(M_t))

        # 3. Eliminación
        for j in range(n):
            if i != j:
                if modo == "Determinante" and j < i: continue 
                factor = M_t[j, i]
                if factor != 0:
                    f_old = M_t[j, :].tolist()[0]
                    f_piv = M_t[i, :].tolist()[0]
                    M_t[j, :] = M_t[j, :] - factor * M_t[i, :]
                    
                    mostrar_aritmetica(f_old, f_piv, factor, M_t[j, :].tolist()[0], 
                                     f"$R_{{{j+1}}} = R_{{{j+1}}} - ({sp.latex(factor)})R_{{{i+1}}}$")
                    st.latex(sp.latex(M_t))

    if modo == "Determinante":
        diag = [M_t[x,x] for x in range(n)]
        resultado = det_factor * np.prod(diag)
        st.success(f"### 🏁 Determinante Final: {sp.latex(resultado)}")
    else:
        st.success("### 🏁 Matriz Resultante Final:")
        st.latex(sp.latex(M_t))

# --- INTERFAZ ---
st.title("🚀 Matrix Master 3000")
st.write("Ciencia de Datos - IPN ESCOM")

c1, c2 = st.columns([1.5, 1])

with c1:
    st.subheader("⌨️ Entrada de Matriz")
    st.markdown("_Escribe números. **Espacio** separa columnas, **Enter** separa filas._")
    
    entrada = st.text_area("Celdas:", height=120, placeholder="1 2 3\n4 5 6", key="input_matriz")
    
    if entrada:
        try:
            lineas = [l.split() for l in entrada.strip().split('\n') if l.strip()]
            if lineas:
                max_c = max(len(l) for l in lineas)
                # Dibujar tabla HTML sin índices de columna/fila
                html_matriz = "<div class='matrix-container'><table class='matrix-table'>"
                for f in lineas:
                    f_full = f + [""] * (max_c - len(f))
                    html_matriz += "<tr>" + "".join([f"<td>{x}</td>" for x in f_full]) + "</tr>"
                html_matriz += "</table></div>"
                
                st.write("### 📊 Matriz Detectada")
                st.write(html_matriz, unsafe_allow_html=True)
                
                M_ready = sp.Matrix([[sp.Rational(x) if x != "" else 0 for x in fila] for fila in [l + [""]*(max_c - len(l)) for l in lineas]])
            else: M_ready = None
        except:
            st.error("⚠️ Solo números por favor.")
            M_ready = None
    else: M_ready = None

with c2:
    st.subheader("⚙️ Opciones")
    opcion = st.selectbox("Acción:", ["Gauss-Jordan", "Inversa", "Determinante"])
    if st.button("🚀 CALCULAR", use_container_width=True, type="primary"):
        st.session_state.calculo = True

st.markdown("---")

# --- FLUJO FINAL ---
if st.session_state.get('calculo', False) and M_ready:
    resolver_matriz(M_ready, opcion)
