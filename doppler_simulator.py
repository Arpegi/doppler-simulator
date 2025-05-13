import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from scipy.io.wavfile import write as write_wav

st.set_page_config(layout="wide")
st.title("\U0001F50A Simulador Interactivo del Efecto Doppler (Ondas Sonoras)")

with st.expander("📘 Explicación del experimento y fórmulas"):
    st.markdown("""
    ### Objetivo
    Este simulador tiene como propósito visualizar e interpretar el **efecto Doppler** aplicado a las ondas sonoras.
    
    El efecto Doppler describe cómo cambia la frecuencia percibida de una onda cuando existe movimiento relativo entre la fuente que emite la onda y el observador.

    ---
    ### Fundamento físico
    Cuando una fuente sonora se mueve respecto al observador:

    - Si **la fuente se acerca**, las ondas se comprimen → frecuencia percibida aumenta.
    - Si **la fuente se aleja**, las ondas se expanden → frecuencia percibida disminuye.

    ---
    ### Fórmula del efecto Doppler (observador en reposo):
    \[
    f_\text{percibida} = f_\text{emitida} \cdot \frac{v_\text{sonido}}{v_\text{sonido} \pm v_\text{fuente}}
    \]
    
    - Si la fuente **se aleja**, se usa el signo **+**.
    - Si la fuente **se acerca**, se usa el signo **−**.

    Donde:
    - \( f_\text{emitida} \): Frecuencia original de la fuente
    - \( v_\text{sonido} \): Velocidad del sonido en el medio (aire)
    - \( v_\text{fuente} \): Velocidad de la fuente sonora
    
    ---
    ### Implementación en la app
    - La animación muestra ondas circulares que se expanden desde la posición de la fuente móvil.
    - El usuario puede modificar:
        - Frecuencia emitida (visual)
        - Velocidad de la fuente
        - Posición del observador
        - Velocidad del sonido
    - El sistema calcula la frecuencia percibida y **genera un archivo de audio** con esa frecuencia **escalada** para ser audible.
    - El **volumen del sonido depende de la distancia** entre la fuente y el observador, simulando realismo sonoro.

    ---
    ### Conversión de escala
    Como la frecuencia visual está en el rango 0.5–10 Hz (para observar bien las ondas), se multiplica por un factor (\( \times 50 \)) para generar una frecuencia audible:

    \[
    f_\text{audio} = f_\text{visual} \times 50
    \]
    
    Este valor se usa en una onda senoidal digital para reproducir el sonido con la librería `scipy.io.wavfile`.
    
    ---
    ### Consideraciones finales
    - Este simulador permite **explorar el efecto Doppler de forma interactiva**, con representación visual y auditiva.
    - Los parámetros permiten reproducir fenómenos como **el cruce de una fuente rápida** y la variación en la **intensidad y tono percibido**.

    """)

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

    # Volumen amplificado bruscamente cerca del observador
    max_distance = 150
    proximity_factor = 1 / (1 + abs(distance_to_source) / 5)  # más brusco
    proximity_factor = min(max(proximity_factor, 0.05), 1.0)

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

    # Generar archivo de sonido dinámico con volumen ajustado por proximidad
    if f_percibida_audio >= 20:
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        waveform = proximity_factor * np.sin(2 * np.pi * f_percibida_audio * t)
        waveform_int = np.int16(waveform * 32767)
        wav_path = "/tmp/doppler_temp.wav"
        write_wav(wav_path, sample_rate, waveform_int)

        audio_placeholder.markdown(f"**Frecuencia percibida (escalada): {f_percibida_audio:.1f} Hz**  |  **Volumen (cruce): {proximity_factor:.2f}**")
        with open(wav_path, 'rb') as audio_file:
            audio_placeholder.audio(audio_file.read(), format='audio/wav')
    else:
        audio_placeholder.warning("Frecuencia percibida fuera del rango audible (mín. 20 Hz)")

    time.sleep(0.05)

st.caption("\U0001F9EE Esta simulación representa el Efecto Doppler con animación visual y sonido proporcional a la frecuencia y amplificación al acercarse al observador.")
