import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de pantalla ancha para simular Excel
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

# --- LÓGICA DE EXCEL INFINITO ---
st.subheader("⌨️ Editor de Matriz (Estilo Excel)")
st.info("Escribe los números en las celdas. Puedes desplazarte y usar cualquier área de la hoja; el sistema detectará automáticamente tu matriz.")

# Creamos una hoja "infinita" inicial (ej. 50 filas x 26 columnas)
# Usamos letras para las columnas como en Excel (A, B, C...)
columnas_excel = [chr(65 + i) for i in range(26)] 

if 'hoja_infinita' not in st.session_state:
    # Inicializamos con strings vacíos
    data = [["" for _ in range(26)] for _ in range(50)]
    st.session_state.hoja_infinita = pd.DataFrame(data, columns=columnas_excel)

# El Data Editor permite la experiencia de Excel
# num_rows="dynamic" permite añadir más filas si 50 no fueran suficientes
df_usuario = st.data_editor(
    st.session_state.hoja_infinita,
    use_container_width=True,
    num_rows="dynamic", 
    hide_index=False, # Mostramos números de fila
    key="excel_editor"
)

# Guardar progreso
st.session_state.hoja_infinita = df_usuario

# --- PROCESAMIENTO INTELIGENTE ---
if st.button("🚀 Resolver Matriz Detectada", use_container_width=True, type="primary"):
    try:
        # 1. Limpieza radical: eliminar espacios y convertir vacíos en NaN
        df_limpio = df_usuario.replace(r'^\s*$', np.nan, regex=True)
        
        # 2. DETECCIÓN AUTOMÁTICA DEL ÁREA OCUPADA
        # Eliminamos filas y columnas que estén totalmente vacías
        # Esto "recorta" la hoja de cálculo al cuadro exacto donde el usuario escribió
        cuadro_datos = df_limpio.dropna(how='all').dropna(axis=1, how='all')
        
        if cuadro_datos.empty:
            st.warning("⚠️ No se detectaron datos. Escribe los números en la tabla superior.")
        else:
            # 3. Convertir el cuadro detectado a Sympy (Matriz Aumentada)
            matriz_final = []
            for _, fila_pandas in cuadro_datos.iterrows():
                # Si hay un hueco vacío en medio de los datos, lo tratamos como 0
                fila_math = [sp.Rational(str(val)) if pd.notnull(val) else sp.Integer(0) for val in fila_pandas]
                matriz_final.append(fila_math)
            
            M_aug = sp.Matrix(matriz_final)
            filas, columnas = M_aug.shape
            
            st.success(f"✅ **Matriz detectada:** {filas} ecuaciones con {columnas-1} incógnitas.")
            
            # 4. Ejecutar Gauss-Jordan
            resolver_gauss_jordan(M_aug)
            
            # --- RESULTADO FINAL ---
            st.markdown("---")
            st.subheader("💡 Solución")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(columnas - 1)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)

            if sols is None:
                st.error(r"Sistema Inconsistente: $\{ \emptyset \}$")
            else:
                lista_s = [sols.get(v, v) for v in vars_sym]
                st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_s])}) \}}")

    except Exception as e:
        st.error(f"⚠️ Error: Asegúrate de ingresar solo números o fracciones. (Detalle: {e})")
