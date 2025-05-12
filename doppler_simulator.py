import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide")
st.title("\U0001F50A Simulador Interactivo del Efecto Doppler (Ondas Sonoras)")

# Botón para reiniciar la animación
if st.button("Reiniciar animación"):
    st.session_state.frame_count = 0

# Sidebar sliders
st.sidebar.header("Parámetros del sistema")
f_emit = st.sidebar.slider("Frecuencia de emisión (Hz)", 0.5, 10.0, 2.0, step=0.1)
v_source = st.sidebar.slider("Velocidad de la fuente (m/s)", -100, 100, 0, step=1)
v_sound = st.sidebar.slider("Velocidad del sonido (m/s)", 100, 500, 343, step=1)
observer_pos = st.sidebar.slider("Posición del observador (m)", -50, 150, 0, step=1)

# Simulación interactiva
frame_count = st.session_state.get("frame_count", 0)
t_now = frame_count * 0.05
st.session_state.frame_count = frame_count + 1
source_pos = v_source * t_now

# Emitir ondas anteriores
dt = 0.05
emission_times = np.arange(0, t_now, 1 / f_emit)
waves = [(v_source * t, v_sound * (t_now - t)) for t in emission_times]

# Calcular frecuencia percibida
distance_to_source = source_pos - observer_pos
v_rel = v_sound - v_source if distance_to_source > 0 else v_sound + v_source
f_percibida = f_emit * v_sound / v_rel if v_rel > 0 else 0

# Gráfico de ondas circulares
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_title("Ondas circulares emitidas por una fuente en movimiento")
ax.set_xlim(-50, 150)
ax.set_ylim(-100, 100)
ax.set_aspect('equal')
ax.grid(True)

for source_x, radius in waves:
    circle = plt.Circle((source_x, 0), radius, fill=False, color='purple', linewidth=1)
    ax.add_artist(circle)

ax.plot(source_pos, 0, 'ro', markersize=10, label="Fuente de sonido")
ax.plot(observer_pos, 0, 'go', markersize=10, label="Observador")
ax.legend()

st.pyplot(fig)

st.caption("\U0001F9EE Esta simulación representa el Efecto Doppler con animación visual actualizada dinámicamente.")
