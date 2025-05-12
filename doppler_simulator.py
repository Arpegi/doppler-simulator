import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide")
st.title("\U0001F50A Simulador Interactivo del Efecto Doppler (Ondas Sonoras)")

# Sidebar sliders
st.sidebar.header("Parámetros del sistema")
f_emit = st.sidebar.slider("Frecuencia de emisión (Hz)", 0.5, 10.0, 2.0, step=0.1)
v_source = st.sidebar.slider("Velocidad de la fuente (m/s)", -100, 100, 0, step=1)
v_sound = st.sidebar.slider("Velocidad del sonido (m/s)", 100, 500, 343, step=1)

# Simulación
dt = 0.05
num_frames = 50
t_wave = np.linspace(0, 0.02, 1000)

wavefronts = []
emission_times = []
snapshots = []

placeholder = st.empty()

for frame in range(num_frames):
    t_now = frame * dt
    source_pos = v_source * t_now

    if len(emission_times) == 0 or t_now - emission_times[-1] >= 1 / f_emit:
        emission_times.append(t_now)
        wavefronts.append(source_pos)

    snapshot = {
        "time": t_now,
        "source_pos": source_pos,
        "wavefronts": [
            {"pos": pos, "radius": v_sound * (t_now - t_emit)}
            for pos, t_emit in zip(wavefronts, emission_times)
        ]
    }
    snapshots.append(snapshot)

    snap = snapshot

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [2, 1]})
    ax1.set_title("Ondas circulares emitidas por una fuente en movimiento")
    ax1.set_xlim(-50, 150)
    ax1.set_ylim(-100, 100)
    ax1.set_aspect('equal')
    ax1.grid(True)

    for wave in snap["wavefronts"]:
        circle = plt.Circle((wave["pos"], 0), wave["radius"], fill=False, color='purple', linewidth=1)
        ax1.add_artist(circle)

    ax1.plot(snap["source_pos"], 0, 'ro', label="Fuente de sonido")
    ax1.legend()

    v_rel = v_sound - v_source
    if v_rel <= 0:
        f_percibida = 0
        y_wave = np.zeros_like(t_wave)
    else:
        f_percibida = f_emit * v_sound / v_rel
        y_wave = np.sin(2 * np.pi * f_percibida * t_wave)

    ax2.plot(t_wave, y_wave, color='blue')
    ax2.set_ylim(-1.5, 1.5)
    ax2.set_title(f"Onda Percibida - Frecuencia: {f_percibida:.1f} Hz")
    ax2.set_xlabel("Tiempo (s)")
    ax2.set_ylabel("Amplitud")
    ax2.grid(True)

    placeholder.pyplot(fig)
    time.sleep(0.1)

st.caption("\U0001F9EE Esta simulación representa el Efecto Doppler para una fuente de sonido en movimiento y un observador en reposo.")
