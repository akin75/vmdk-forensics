from datetime import datetime
from multiprocessing import Pool
import os


# Generator, der Chunks aus der Datei liest
def chunk_generator(file_path, chunk_size):
    """Generator, der die Datei in Chunks aufteilt."""
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


# Funktion, die den Chunk verarbeitet (zum Beispiel die Länge des Chunks zurückgibt)
def process_chunk(chunk):
    # Hier könntest du komplexe Verarbeitung durchführen
    return chunk.decode("utf-8")


if __name__ == '__main__':
    file_path = '500MB_Test-flat.vmdk'  # Beispiel-Dateipfad
    chunk_size = 2048  # Größe eines Chunks in Bytes

    # Multiprocessing mit Pool
    start = datetime.now()
    with Pool(processes=8) as pool:
        # Generator mit file_path und chunk_size übergeben
        results = pool.imap(process_chunk, chunk_generator(file_path, chunk_size))
        for result in results:
            print(result)

    print(f"Time taken: {(datetime.now() - start).total_seconds()} Sekunden")