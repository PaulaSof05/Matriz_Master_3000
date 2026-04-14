import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de pantalla
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ALGORITMO GAUSS-JORDAN (CORE) ---
def resolver_gauss_jordan(M_aug):
    n_eqs, n_cols = M_aug.shape
    st.write("### 🤖 Procedimiento: Gauss-Jordan")
    st.latex(sp.latex(M_aug))
    
    for i in range(min(n_eqs, n_cols - 1)):
        # 1. Búsqueda de Pivote (Equipo 4)
        pivote = M_aug[i, i]
        if pivote == 0:
            for j in range(i + 1, n_eqs):
                if M_aug[j, i] != 0:
                    M_aug[i, :], M_aug[j, :] = M_aug[j, :], M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {i+1} }} \\leftrightarrow R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
                    pivote = M_aug[i, i]
                    break
        
        # 2. Hacer el pivote 1 (Equipo 3)
        if pivote != 0 and pivote != 1:
            inv = sp.Rational(1, pivote)
            M_aug[i, :] = M_aug[i, :] * inv
            st.write(f"**Operación:** $({sp.latex(inv)}) R_{{ {i+1} }} \\to R_{{ {i+1} }}$")
            st.latex(sp.latex(M_aug))
        
        # 3. Hacer ceros en la columna (Equipos 1 y 2)
        for j in range(n_eqs):
            if i != j:
                factor = M_aug[j, i]
                if factor != 0:
                    M_aug[j, :] = M_aug[j, :] - factor * M_aug[i, :]
                    st.write(f"**Operación:** $R_{{ {j+1} }} - ({sp.latex(factor)})R_{{ {i+1} }} \\to R_{{ {j+1} }}$")
                    st.latex(sp.latex(M_aug))
    return M_aug

# --- TÍTULO ---
st.title("🚀 Matrix Master 3000")
st.markdown("---")

# --- INTERFAZ TIPO EXCEL (Infinita y Dinámica) ---
st.write("### ⌨️ Editor de Matriz Aumentada")
st.info("💡 **Tips:** Haz doble clic en una celda para editar. Usa el botón **(+)** al final de las filas o columnas para expandir la tabla. El sistema detectará el tamaño automáticamente.")

# Inicializamos una tabla vacía de 3x4 en el estado de sesión si no existe
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = pd.DataFrame(
        [["" for _ in range(4)] for _ in range(3)],
        columns=[f"C{i+1}" for i in range(4)]
    )

# Editor de datos con permisos para agregar filas y columnas
df_editado = st.data_editor(
    st.session_state.excel_data,
    num_rows="dynamic",      # Permite agregar filas infinitas
    use_container_width=True,
    hide_index=False,
    column_config={f"C{i+1}": st.column_config.TextColumn(width="small") for i in range(50)} 
)

# Guardar en session_state
st.session_state.excel_data = df_editado

# --- PROCESAMIENTO Y DETECCIÓN ---
if st.button("🚀 Resolver Matriz Detectada", use_container_width=True, type="primary"):
    try:
        # 1. Limpiar datos: Convertir a strings, quitar espacios y filtrar filas/columnas vacías
        # Reemplazamos celdas vacías por None para poder dropearlas
        df_limpio = df_editado.replace(r'^\s*$', np.nan, regex=True).dropna(how='all').dropna(axis=1, how='all')
        
        if df_limpio.empty:
            st.warning("La tabla está vacía. Por favor, ingresa los coeficientes.")
        else:
            # 2. Convertir a matriz de Sympy
            matriz_datos = []
            for _, row in df_limpio.iterrows():
                # Si una celda individual está vacía en medio de datos, la tratamos como 0
                fila = [sp.Rational(str(val)) if pd.notnull(val) else sp.Integer(0) for val in row]
                matriz_datos.append(fila)
            
            M_aug = sp.Matrix(matriz_datos)
            n_eqs, n_tot = M_aug.shape
            n_vars = n_tot - 1
            
            st.success(f"✅ Sistema detectado: **{n_eqs} ecuaciones** con **{n_vars} variables**.")
            
            # Ejecución del algoritmo
            resolver_gauss_jordan(M_aug)
            
            # --- RESULTADOS ---
            st.markdown("---")
            st.subheader("💡 Solución")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)

            if sols is None:
                st.error(r"Sistema Inconsistente: $\{ \emptyset \}$")
            else:
                lista_soluciones = [sols.get(v, v) for v in vars_sym]
                st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_soluciones])}) \}}")

    except Exception as e:
        st.error(f"⚠️ Error: Asegúrate de que todas las celdas contengan números o fracciones válidas.")
