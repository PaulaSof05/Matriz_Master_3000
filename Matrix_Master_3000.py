import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de pantalla
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ALGORITMO GAUSS-JORDAN ---
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

# --- INTERFAZ TIPO EXCEL INFINITO ---
st.write("### ⌨️ Editor de Matriz Indefinido")
st.info("💡 **Detección Automática:** Puedes añadir filas y columnas libremente. El sistema detectará el área donde escribiste y calculará las dimensiones por ti.")

# Inicializamos una tabla vacía en el estado de sesión (pequeña para empezar)
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = pd.DataFrame(
        [["" for _ in range(10)] for _ in range(10)], # Empezamos con 10x10 pero es expandible
        columns=[f"{i+1}" for i in range(10)]
    )

# Editor de datos con columnas y filas dinámicas
df_editado = st.data_editor(
    st.session_state.excel_data,
    num_rows="dynamic",      # Permite al usuario añadir filas infinitas con el botón (+)
    use_container_width=True,
    hide_index=False,
)

# Guardar cambios
st.session_state.excel_data = df_editado

# --- BOTÓN DE PROCESAMIENTO ---
if st.button("🚀 Resolver Matriz Detectada", use_container_width=True, type="primary"):
    try:
        # Lógica para detectar solo la zona con datos (el "cuadro" real)
        # 1. Convertimos todo a string y limpiamos espacios. Celdas vacías -> NaN
        df_temp = df_editado.applymap(lambda x: str(x).strip() if x is not None else "")
        df_temp = df_temp.replace(r'^\s*$', np.nan, regex=True)
        
        # 2. Cortamos filas y columnas que estén COMPLETAMENTE vacías al final y al inicio
        # Esto permite que el usuario escriba donde sea y el sistema encuentre la matriz
        df_limpio = df_temp.dropna(how='all').dropna(axis=1, how='all')
        
        if df_limpio.empty:
            st.warning("⚠️ No se detectaron datos en la tabla. Por favor, ingresa los coeficientes.")
        else:
            # 3. Convertir a matriz de Sympy
            matriz_datos = []
            for _, row in df_limpio.iterrows():
                # Tratamos celdas NaN individuales dentro de la matriz como 0
                fila = [sp.Rational(str(val)) if pd.notnull(val) else sp.Integer(0) for val in row]
                matriz_datos.append(fila)
            
            M_aug = sp.Matrix(matriz_datos)
            n_eqs, n_tot = M_aug.shape
            n_vars = n_tot - 1
            
            st.success(f"✅ Se detectó una matriz de **{n_eqs}x{n_tot}** ({n_vars} variables).")
            
            # Ejecutar algoritmo
            resolver_gauss_jordan(M_aug)
            
            # --- RESULTADOS ---
            st.markdown("---")
            st.subheader("💡 Solución del Sistema")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)

            if sols is None:
                st.error(r"El sistema es Inconsistente: $\{ \emptyset \}$")
            else:
                lista_soluciones = [sols.get(v, v) for v in vars_sym]
                st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_soluciones])}) \}}")

    except Exception as e:
        st.error(f"⚠️ Error: Hubo un problema procesando los números. Revisa que no haya letras en la matriz.")
