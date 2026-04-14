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

# --- LIENZO INFINITO SIN NOMBRES ---
st.subheader("⌨️ Cuadrícula de Trabajo Limpia")
st.info("Escribe tu matriz en cualquier parte de la cuadrícula blanca. No hay límites ni etiquetas.")

# Inicializamos una hoja grande (50x50 por ejemplo)
if 'hoja_limpia' not in st.session_state:
    # Creamos un DataFrame sin nombres de columnas específicos
    datos = [["" for _ in range(50)] for _ in range(50)]
    st.session_state.hoja_limpia = pd.DataFrame(datos)

# Editor de datos configurado para ocultar TODO
df_usuario = st.data_editor(
    st.session_state.hoja_limpia,
    use_container_width=True,
    hide_index=True,          # OCULTA los números de fila (1, 2, 3...)
    column_config={
        str(i): st.column_config.Column(label="", width="small") for i in range(50)
    },                        # OCULTA los nombres de columnas (A, B, C...)
    num_rows="dynamic",       # Permite seguir bajando infinitamente
    key="canvas_limpio"
)

# Guardar estado
st.session_state.hoja_limpia = df_usuario

# --- DETECCIÓN Y PROCESAMIENTO ---
if st.button("🚀 Resolver Matriz", use_container_width=True, type="primary"):
    try:
        # Convertir a texto y limpiar
        df_limpio = df_usuario.applymap(lambda x: str(x).strip() if x else "").replace('', np.nan)
        
        # El "Recorte Mágico" para encontrar el bloque de datos del usuario
        cuadro = df_limpio.dropna(how='all').dropna(axis=1, how='all')
        
        if cuadro.empty:
            st.warning("⚠️ La cuadrícula está vacía.")
        else:
            matriz_final = []
            for _, fila_pd in cuadro.iterrows():
                # Huecos internos se asumen como 0
                fila_math = [sp.Rational(str(v)) if pd.notnull(v) else sp.Integer(0) for v in fila_pd]
                matriz_final.append(fila_math)
            
            M_aug = sp.Matrix(matriz_final)
            st.success(f"✅ Matriz detectada de {M_aug.shape[0]}x{M_aug.shape[1]}")
            
            # Procedimiento
            resolver_gauss_jordan(M_aug)
            
            # Resultado final
            st.markdown("---")
            vars_sym = [sp.symbols(f'x_{i+1}') for i in range(M_aug.shape[1] - 1)]
            sols = sp.solve_linear_system(M_aug, *vars_sym)
            if sols is not None:
                res_txt = ",".join([sp.latex(sols.get(v, v)) for v in vars_sym])
                st.latex(rf"S = \{{ ({res_txt}) \}}")
            else:
                st.error("Sistema sin solución.")

    except Exception as e:
        st.error(f"⚠️ Error: Ingresa solo números. ({e})")
