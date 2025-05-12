import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from scipy.io.wavfile import write as write_wav

st.set_page_config(layout="wide")
st.title("\U0001F50A Simulador Interactivo del Efecto Doppler (Ondas Sonoras)")

# Botón para reiniciar la animación
if st.button("Reiniciar animación"):
    st.session_state.frame_count = 0

# Sidebar sliders
st.sidebar.header("Parámetros del sistema")
f_emit_visual = st.sidebar.slider("Frecuencia de emisión (Hz) [visual]", 0.5, 10.0, 2.0, step=0.1)
v_source = st.sidebar.slider("Velocidad de la fuente (m/s)", -100, 100, 0, step=1)
v_sound = st.sidebar.slider("Velocidad del sonido (m/s)", 100, 500, 343, step=1)
observer_pos = st.sidebar.slider("Posición del observador (m)", -50, 150, 0, step=1)

# Factor de escalado para frecuencia de audio
audio_scale = 50  # Multiplicador para convertir Hz visual a Hz audible
f_emit_audio = f_emit_visual * audio_scale

# Contenedor para animación
graph_placeholder = st.empty()
audio_placeholder = st.empty()

# Inicializar frame_count si no existe
if "frame_count" not in st.session_state:
    st.session_state.frame_count = 0

# Bucle de animación
for _ in range(200):
    frame_count = st.session_state.frame_count
    t_now = frame_count * 0.05
    st.session_state.frame_count += 1
    source_pos = v_source * t_now

    # Emitir ondas anteriores
    emission_times = np.arange(0, t_now, 1 / f_emit_visual)
    waves = [(v_source * t, v_sound * (t_now - t)) for t in emission_times]

    # Calcular frecuencia percibida (real y escalada para audio)
    distance_to_source = source_pos - observer_pos
    v_rel = v_sound - v_source if distance_to_source > 0 else v_sound + v_source
    f_percibida_visual = f_emit_visual * v_sound / v_rel if v_rel > 0 else 0
    f_percibida_audio = f_emit_audio * v_sound / v_rel if v_rel > 0 else 0

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

    graph_placeholder.pyplot(fig)

    # Generar archivo de sonido dinámico según f_percibida_audio si es válida y audible
    if f_percibida_audio >= 20:
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        waveform = 0.5 * np.sin(2 * np.pi * f_percibida_audio * t)
        waveform_int = np.int16(waveform * 32767)
        wav_path = "/tmp/doppler_temp.wav"
        write_wav(wav_path, sample_rate, waveform_int)

        audio_placeholder.markdown(f"**Frecuencia percibida (escalada): {f_percibida_audio:.1f} Hz**")
        with open(wav_path, 'rb') as audio_file:
            audio_placeholder.audio(audio_file.read(), format='audio/wav')
    else:
        audio_placeholder.warning("Frecuencia percibida fuera del rango audible (mín. 20 Hz)")

    time.sleep(0.05)

st.caption("\U0001F9EE Esta simulación representa el Efecto Doppler con animación visual a escala y sonido generado dinámicamente a frecuencia audible proporcional.")
