import streamlit as st
import pandas as pd
import sympy as sp
import numpy as np

# Configuración de pantalla ancha
st.set_page_config(page_title="Matrix Master 3000", layout="wide")

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
st.markdown("---")

# --- LA HOJA DINÁMICA ---
st.subheader("⌨️ Cuadrícula de Datos")
st.info("Haz doble clic en una celda para empezar. El sistema expandirá la tabla automáticamente conforme agregues datos.")

# Inicialización: Empezamos con un DataFrame de 1x1 totalmente vacío
# Esto obliga al usuario a definir su propio m*n solo escribiendo
if 'df_dinamico' not in st.session_state:
    st.session_state.df_dinamico = pd.DataFrame([[""]], columns=["1"])

# Editor con TODAS las capacidades dinámicas activadas
df_usuario = st.data_editor(
    st.session_state.df_dinamico,
    use_container_width=True,
    num_rows="dynamic",     # Filas infinitas (botón +)
    hide_index=False,
    column_config={
        str(i): st.column_config.TextColumn(width="small") for i in range(1, 100)
    },
    key="grid_infinito"
)

# Guardar estado
st.session_state.df_dinamico = df_usuario

# --- DETECCIÓN Y PROCESAMIENTO ---
if st.button("🚀 Resolver Matriz", use_container_width=True, type="primary"):
    try:
        # Reemplazar vacíos por NaN para recortar
        df_limpio = df_usuario.replace(r'^\s*$', np.nan, regex=True)
        
        # El sistema recorta el aire alrededor de lo que el usuario escribió
        cuadro = df_limpio.dropna(how='all').dropna(axis=1, how='all')
        
        if cuadro.empty:
            st.warning("⚠️ Escribe algo en la tabla primero.")
        else:
            matriz_final = []
            for _, fila_pd in cuadro.iterrows():
                # Celdas vacías internas se vuelven 0 para no romper la matemática
                fila_math = [sp.Rational(str(v)) if pd.notnull(v) else sp.Integer(0) for v in fila_pd]
                matriz_final.append(fila_math)
            
            M_aug = sp.Matrix(matriz_final)
            st.success(f"✅ Matriz detectada de {M_aug.shape[0]}x{M_aug.shape[1]}")
            
            resolver_gauss_jordan(M_aug)
            
            # Resultado Final
            st.markdown("---")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(M_aug.shape[1] - 1)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)
            if sols:
                lista_s = [sols.get(v, v) for v in vars_sym]
                st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_s])}) \}}")
            else:
                st.error("Sistema sin solución.")

    except Exception as e:
        st.error(f"⚠️ Revisa tus datos. (Error: {e})")
