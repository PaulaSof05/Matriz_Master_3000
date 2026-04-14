import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de pantalla ancha para máxima visibilidad de la hoja
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

# --- INTERFAZ DE HOJA INFINITA ---
st.subheader("📊 Lienzo de Trabajo (Estilo Excel)")
st.info("Escribe en cualquier celda. El sistema detectará automáticamente el tamaño de tu matriz.")

# Generamos encabezados A, B, C... Z
columnas_excel = [chr(65 + i) for i in range(26)] 

# Inicialización de la hoja "infinita" en el estado de sesión
if 'hoja_datos' not in st.session_state:
    # Creamos un lienzo de 100 filas por 26 columnas vacío
    lienzo_vacio = [["" for _ in range(26)] for _ in range(100)]
    st.session_state.hoja_datos = pd.DataFrame(lienzo_vacio, columns=columnas_excel)

# El editor de datos configurado como hoja de cálculo
df_usuario = st.data_editor(
    st.session_state.hoja_datos,
    use_container_width=True,
    num_rows="dynamic", # Permite añadir aún más filas si es necesario
    hide_index=False,   # Muestra los números de fila (1, 2, 3...)
    key="editor_excel"
)

# Guardar cambios para no perder datos al refrescar
st.session_state.hoja_datos = df_usuario

# --- PROCESAMIENTO CON DETECCIÓN AUTOMÁTICA ---
if st.button("🚀 Resolver Matriz Detectada", use_container_width=True, type="primary"):
    try:
        # 1. Limpiamos la hoja: quitamos espacios y convertimos celdas vacías en NaN
        df_limpio = df_usuario.replace(r'^\s*$', np.nan, regex=True)
        
        # 2. RECORTE INTELIGENTE:
        # Eliminamos todas las filas y columnas que estén COMPLETAMENTE vacías.
        # Esto nos deja solo con el "bloque" de datos que el usuario escribió.
        matriz_recortada = df_limpio.dropna(how='all').dropna(axis=1, how='all')
        
        if matriz_recortada.empty:
            st.warning("⚠️ No se detectaron datos en la hoja. Por favor, ingresa los números de tu matriz.")
        else:
            # 3. Convertir a matriz de Sympy
            datos_finales = []
            for _, fila_pandas in matriz_recortada.iterrows():
                # Si hay un hueco vacío dentro de la matriz, se asume como 0
                fila_math = [sp.Rational(str(val)) if pd.notnull(val) else sp.Integer(0) for val in fila_pandas]
                datos_finales.append(fila_math)
            
            M_aug = sp.Matrix(datos_finales)
            m, n_tot = M_aug.shape
            
            st.success(f"✅ **Detección Automática:** Matriz de {m}x{n_tot} ({m} ecuaciones, {n_tot-1} variables).")
            
            # 4. Resolver
            resolver_gauss_jordan(M_aug)
            
            # --- RESULTADOS ---
            st.markdown("---")
            st.subheader("💡 Solución Final")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_tot - 1)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)

            if sols is None:
                st.error(r"Sistema Inconsistente: $\{ \emptyset \}$")
            else:
                lista_s = [sols.get(v, v) for v in vars_sym]
                st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_s])}) \}}")

    except Exception as e:
        st.error(f"⚠️ Error: Asegúrate de usar solo números o fracciones (ej: 3/4). Detalle: {e}")
