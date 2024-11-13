import multiprocessing


def process_chunk(prozess_nummer, anzahl_prozesse, file_path, chunk_size):
    with open(file_path, "rb") as f:
        # Berechne den Startpunkt für den Prozess
        file_size = f.seek(0, 2)  # Dateigröße ermitteln
        section_size = file_size // anzahl_prozesse  # Größe des Abschnitts für jeden Prozess
        start_offset = prozess_nummer * section_size

        # Zum Startpunkt der Sektion gehen
        f.seek(start_offset)

        # Daten in kleinen Chunks innerhalb des zugewiesenen Bereichs lesen
        bytes_read = 0
        while bytes_read < section_size:
            remaining_bytes = section_size - bytes_read
            current_chunk_size = min(chunk_size, remaining_bytes)
            chunk = f.read(current_chunk_size)

            if not chunk:
                break  # Ende der Datei erreicht

            # Verarbeite den Chunk (hier z.B. nur ausgeben)
            print(f"Prozess {multiprocessing.current_process().name}: "
                  f"Offset {start_offset + bytes_read}, Gelesene Bytes: {len(chunk)}")

            bytes_read += len(chunk)
    return


# Datei-Pfad und Chunk-Größe
file_path = "deine_datei.dat"
chunk_size = 1024  # Beispielgröße für kleinere Leseschritte in Bytes
num_processes = 4  # Anzahl der Prozesse

# Starte die Prozesse
with multiprocessing.Pool(processes=num_processes) as pool:
    pool.starmap(process_chunk, [(i, num_processes, file_path, chunk_size) for i in range(num_processes)])