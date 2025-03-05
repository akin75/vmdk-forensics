import os
import time
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from multiprocessing import Lock, Process, Value
from utils import calculate_chi2, calculate_shannon_entropy, write_output

# Globale Variablen für Visualisierung
entropy_values = []
chi2_values = []
blocks_processed = []
lock = Lock()

# Streamlit UI
st.set_page_config(layout="wide", page_title="Ransomware Analyse")

st.title("📊 Ransomware Analyse mit Entropie & Chi²-Statistik")

# Datei-Upload über Streamlit
uploaded_file = st.sidebar.file_uploader("Wähle eine Datei", type=None)

# Benutzerdefinierter Dateiname für hohe Entropie
output_filename = st.sidebar.text_input("Dateiname für hohe Entropie-Blöcke", "high_entropy_blocks.txt")

# Blockgröße und Anzahl der Prozesse festlegen
block_size = st.sidebar.slider("Blockgröße (Bytes)", min_value=512, max_value=4096, value=1024, step=512)
num_processes = st.sidebar.slider("Anzahl der Prozesse", min_value=1, max_value=8, value=4)

# Fortschrittsbalken
progress_bar = st.progress(0)
status_text = st.empty()

# Echtzeit-Graphen vorbereiten
chart_entropy = st.empty()
chart_chi2 = st.empty()

def visualize():
    """ Zeichnet die aktuellen Werte in Streamlit """
    if blocks_processed:
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))

        # 1. Entropie-Verlauf
        ax[0].plot(blocks_processed, entropy_values, color='blue', marker='o', linestyle='-')
        ax[0].set_title("Entropie-Verlauf")
        ax[0].set_xlabel("Block-Index")
        ax[0].set_ylabel("Entropie")
        ax[0].grid(True)

        # 2. Chi²-Verlauf
        ax[1].plot(blocks_processed, chi2_values, color='red', marker='s', linestyle='-')
        ax[1].set_title("Chi-Quadrat-Werte")
        ax[1].set_xlabel("Block-Index")
        ax[1].set_ylabel("Chi²-Statistik")
        ax[1].grid(True)

        # Aktualisieren der Streamlit Diagramme
        chart_entropy.pyplot(fig)
        chart_chi2.pyplot(fig)
        plt.close(fig)

def process_block(lock, file_path, block_size, shared_offset, total_size, output_filename):
    """ Liest Blöcke, berechnet Entropie & Chi² und speichert Werte """
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file, open(output_filename, "w") as output_file:
        while True:

            if len(blocks_processed) % 20 == 0 and len(blocks_processed) != 0:
                time.sleep(0.1)

            with lock:
                if shared_offset.value >= file_size:
                    break
                file.seek(shared_offset.value)
                block = file.read(min(block_size, file_size - shared_offset.value))
                current_offset = shared_offset.value
                shared_offset.value += len(block)

            if not block:
                break

            # Berechnung der Werte
            entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))
            chi2_statistic, p_value = calculate_chi2(block)

            # Werte speichern (Thread-sicher)
            with lock:
                entropy_values.append(entropy)
                chi2_values.append(chi2_statistic)
                blocks_processed.append(len(blocks_processed) + 1)

                # Falls Entropie > 7.90 oder p-Wert > 0.05, in Datei schreiben
                if entropy > 7.90:
                    output_file.write(f"Offset: {current_offset}, Entropie: {entropy}, Chi²: {chi2_statistic}, p-Wert: {p_value}\n")
                    if p_value > 0.05:
                        output_file.write(
                            f"Offset: {current_offset}, Entropie: {entropy}, Chi²: {chi2_statistic}, p-Wert: {p_value}\n")

            # Fortschritt aktualisieren
            progress_bar.progress(shared_offset.value / total_size)
            status_text.text(f"Fortschritt: {shared_offset.value}/{total_size} Bytes")

            visualize()  # Echtzeit-Visualisierung

# Hauptfunktion für Multiprocessing
if uploaded_file:
    file_path = uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    total_size = os.path.getsize(file_path)
    shared_offset = Value('l', 0)

    st.sidebar.success(f"Analysiere: {file_path} ({total_size} Bytes)")

    processes = []
    for _ in range(num_processes):
        p = Process(target=process_block, args=(lock, file_path, block_size, shared_offset, total_size, output_filename))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    st.sidebar.success("Analyse abgeschlossen! ✅")
