import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de página ancha
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

# --- ESTILO CSS PARA SIMULAR EXCEL ---
st.markdown("""
    <style>
    /* Hace que el editor de datos se vea más como una hoja de cálculo */
    .stDataEditor {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

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

st.title("🚀 Matrix Master 3000")
st.subheader("📊 Hoja de Trabajo Infinita")
st.write("Inserta tu matriz en cualquier lugar. El sistema detectará el bloque de datos automáticamente.")

# --- GENERACIÓN DE LIENZO "INFINITO" ---
# Creamos 26 columnas (A-Z) y 100 filas iniciales (pueden ser más)
columnas = [chr(65 + i) for i in range(26)]

if 'hoja_infinita' not in st.session_state:
    # Llenamos con strings vacíos para que el usuario pueda escribir de inmediato
    datos_vacion = [["" for _ in range(26)] for _ in range(100)]
    st.session_state.hoja_infinita = pd.DataFrame(datos_vacion, columns=columnas)

# Editor de datos configurado para ser un lienzo
df_usuario = st.data_editor(
    st.session_state.hoja_infinita,
    use_container_width=True,
    hide_index=False, # Muestra los números de fila como en Excel
    num_rows="fixed",  # Al ser 100, se siente infinito al hacer scroll
    key="canvas_excel"
)

# --- DETECCIÓN AUTOMÁTICA ---
if st.button("🚀 Resolver Matriz Detectada", use_container_width=True, type="primary"):
    try:
        # 1. Convertir todo a string, limpiar espacios y marcar vacíos como NaN
        df_limpio = df_usuario.applymap(lambda x: str(x).strip() if x else "").replace('', np.nan)
        
        # 2. EL RECORTE MÁGICO:
        # Buscamos el rectángulo más pequeño que contenga todos los datos.
        # Esto elimina todas las filas/columnas vacías que sobran en el lienzo de 100x26.
        cuadro_datos = df_limpio.dropna(how='all').dropna(axis=1, how='all')
        
        if cuadro_datos.empty:
            st.warning("⚠️ No se encontró ninguna matriz. Escribe algo en las celdas.")
        else:
            # 3. Transformar a Matriz Matemática
            filas_finales = []
            for _, fila_pandas in cuadro_datos.iterrows():
                # Celdas vacías dentro del rango detectado se vuelven 0
                fila_math = [sp.Rational(str(val)) if pd.notnull(val) else sp.Integer(0) for val in fila_pandas]
                filas_finales.append(fila_math)
            
            M_aug = sp.Matrix(filas_finales)
            
            # 4. Mostrar dimensiones detectadas
            st.success(f"✅ Matriz detectada: {M_aug.shape[0]}x{M_aug.shape[1]}")
            
            # 5. Ejecutar procedimiento
            resolver_gauss_jordan(M_aug)
            
            # --- RESULTADO ---
            st.markdown("---")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(M_aug.shape[1] - 1)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)
            if sols is not None:
                res_txt = ",".join([sp.latex(sols.get(v, v)) for v in vars_sym])
                st.latex(rf"S = \{{ {res_txt} \}}")
            else:
                st.error("El sistema no tiene solución.")

    except Exception as e:
        st.error(f"⚠️ Revisa tus datos. Asegúrate de usar solo números. ({e})")
