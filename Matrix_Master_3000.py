import streamlit as st
import pandas as pd
import sympy as sp

# Configuración de pantalla completa y limpia
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

# --- INTERFAZ ABSOLUTAMENTE INDEFINIDA ---
st.subheader("⌨️ Entrada de Matriz Libre")
st.info("Copia y pega tus datos desde Excel o escríbelos. No necesitas definir el tamaño; el sistema lo detectará solo.")

# El secreto: Un text_area que acepta cualquier cantidad de datos
# Al ser un área de texto, el usuario puede pegar una matriz de 2x2 o de 100x100 sin restricciones.
input_data = st.text_area(
    "Pega aquí la matriz aumentada (incluyendo el vector b):",
    height=250,
    placeholder="1 0 2 9\n0 1 -1 4\n3 2 0 1",
    help="Usa espacios o tabuladores entre números y saltos de línea para las filas."
)

# --- PROCESAMIENTO DINÁMICO ---
if st.button("🚀 Procesar y Resolver", use_container_width=True, type="primary"):
    if not input_data.strip():
        st.error("⚠️ La entrada está vacía. Por favor ingresa datos.")
    else:
        try:
            # 1. Convertir el texto en una lista de listas (Matriz)
            filas = input_data.strip().split('\n')
            matriz_cruda = []
            for f in filas:
                # Detectamos espacios o tabs como separadores
                valores = f.replace(',', ' ').split()
                if valores:
                    matriz_cruda.append([sp.Rational(v) for v in valores])
            
            # 2. Validar consistencia de columnas
            if not all(len(f) == len(matriz_cruda[0]) for f in matriz_cruda):
                st.error("❌ Error: No todas las filas tienen el mismo número de columnas. Revisa tus datos.")
            else:
                M_aug = sp.Matrix(matriz_cruda)
                m, n_total = M_aug.shape
                n_vars = n_total - 1
                
                # Mostrar al usuario qué fue lo que la máquina detectó
                st.success(f"✅ **Detección exitosa:** Matriz de {m}x{n_total} ({n_vars} incógnitas).")
                
                # 3. Visualización previa en formato tabla para que el usuario esté seguro
                with st.expander("Ver tabla detectada", expanded=False):
                    df_preview = pd.DataFrame(matriz_cruda).astype(str)
                    st.table(df_preview)

                # 4. Resolver
                resolver_gauss_jordan(M_aug)
                
                # --- RESULTADOS FINALES ---
                st.markdown("---")
                st.subheader("💡 Resultado Final")
                vars_sym = [sp.symbols(f'x_{i+1}') for i in range(n_vars)]
                sols = sp.solve_linear_system(M_aug, *vars_sym)

                if sols is None:
                    st.error(r"Sistema Inconsistente: $\{ \emptyset \}$")
                else:
                    lista_soluciones = [sols.get(v, v) for v in vars_sym]
                    st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_soluciones])}) \}}")

        except Exception as e:
            st.error(f"⚠️ Error de formato: Asegúrate de ingresar solo números o fracciones. (Detalle: {e})")
