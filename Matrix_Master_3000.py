import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de página ancha para simular el lienzo de Excel
st.set_page_config(page_title="Matrix Master 3000 - Spreadsheet Mode", layout="wide")

# --- ALGORITMO GAUSS-JORDAN ---
def resolver_gauss_jordan(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    
    for i in range(min(n_eqs, n_cols - 1)):
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        
        if pivote != 0 and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
    return M_aug

# --- INTERFAZ ESTILO EXCEL ---
st.title("🚀 Matrix Master 3000")
st.subheader("📊 Hoja de Cálculo de Matrices")
st.markdown("""
    *Escribe tus datos en cualquier lugar de la cuadrícula. No importa el tamaño, el sistema detectará el área con números automáticamente.*
""")

# 1. Crear la cuadrícula "Infinita" (A-Z columnas)
columnas_excel = [chr(65 + i) for i in range(26)] 

if 'hoja_excel' not in st.session_state:
    # Inicializamos una hoja limpia de 100 filas
    datos_iniciales = [["" for _ in range(26)] for _ in range(100)]
    st.session_state.hoja_excel = pd.DataFrame(datos_iniciales, columns=columnas_excel)

# 2. El Editor con estética de Excel
# Configuramos el ancho de columnas para que parezca cuadrícula
df_editado = st.data_editor(
    st.session_state.hoja_excel,
    use_container_width=True,
    num_rows="dynamic", # Permite añadir más filas al final
    hide_index=False,   # Muestra los números de fila (1, 2, 3...)
    key="excel_sheet"
)

# Guardar estado
st.session_state.hoja_excel = df_editado

# --- BOTÓN DE PROCESAMIENTO ---
if st.button("🚀 Resolver desde la Hoja", use_container_width=True, type="primary"):
    try:
        # Lógica de detección: buscamos el "rectángulo" de datos
        df_temp = df_editado.replace(r'^\s*$', np.nan, regex=True)
        # Eliminamos el aire (filas y columnas vacías alrededor)
        cuadro = df_temp.dropna(how='all').dropna(axis=1, how='all')
        
        if cuadro.empty:
            st.warning("⚠️ La hoja está vacía. Ingresa los datos de tu matriz.")
        else:
            # Convertir el cuadro detectado a Sympy
            matriz_datos = []
            for _, fila_pd in cuadro.iterrows():
                # Huecos internos se asumen como 0
                fila_val = [sp.Rational(str(v)) if pd.notnull(v) else sp.Integer(0) for v in fila_pd]
                matriz_datos.append(fila_val)
            
            M_aug = sp.Matrix(matriz_datos)
            m, n_tot = M_aug.shape
            
            st.success(f"✅ Se detectó una matriz de {m}x{n_tot}")
            
            # Resolver
            resolver_gauss_jordan(M_aug)
            
            # --- RESULTADOS ---
            st.markdown("---")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_tot - 1)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)

            if sols is None:
                st.error("Sistema Inconsistente.")
            else:
                lista_s = [sols.get(v, v) for v in vars_sym]
                st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_s])}) \}}")

    except Exception as e:
        st.error(f"⚠️ Revisa el formato de los números. (Error: {e})")
