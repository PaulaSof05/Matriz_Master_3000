import streamlit as st
import pandas as pd
import sympy as sp
import random

# Configuración de pantalla completa
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

# --- ENTRADA DINÁMICA (Detección automática de m x n) ---
st.write("### ⌨️ Entrada de Datos: Matriz Aumentada")
st.info("Pega tu matriz aquí. Separa los números de una fila con espacios o comas, y usa un salto de línea para cada fila nueva. La última columna será tomada como el vector de resultados (b).")

# Área de texto para insertar la matriz de forma indefinida
raw_data = st.text_area("Inserta los datos de la matriz:", 
                        placeholder="Ejemplo para 3x3:\n1 2 3 9\n0 1 4 10\n5 6 0 1",
                        height=200)

# --- BOTÓN DE ACCIÓN ---
if st.button("🚀 Detectar y Resolver", use_container_width=True, type="primary"):
    if not raw_data.strip():
        st.warning("Por favor, ingresa algunos datos primero.")
    else:
        try:
            # Procesamiento de texto para detectar dimensiones
            filas_texto = raw_data.strip().split('\n')
            matriz_datos = []
            
            for fila in filas_texto:
                # Reemplazar comas por espacios y dividir
                valores = fila.replace(',', ' ').split()
                if valores:
                    matriz_datos.append([sp.Rational(v) for v in valores])
            
            # Validar que todas las filas tengan el mismo tamaño
            if not all(len(f) == len(matriz_datos[0]) for f in matriz_datos):
                st.error("Error: Todas las filas deben tener la misma cantidad de números.")
            else:
                M_aug = sp.Matrix(matriz_datos)
                n_eqs, n_tot = M_aug.shape
                n_vars = n_tot - 1
                
                st.success(f"✅ Matriz detectada: **{n_eqs} filas** x **{n_tot} columnas** ({n_vars} variables).")
                
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
                    st.markdown("**Nivel 1:**")
                    st.latex(rf"S = \{{ ({','.join([sp.latex(v) for v in vars_sym])}) : ({','.join([sp.latex(s) for s in lista_soluciones])}) \}}")
                    st.markdown("**Nivel 2:**")
                    st.latex(rf"S = \{{ {','.join([sp.latex(s) for s in lista_soluciones])} \}}")

        except Exception as e:
            st.error(f"⚠️ Error al procesar los datos. Asegúrate de usar solo números y que el formato sea correcto.")
