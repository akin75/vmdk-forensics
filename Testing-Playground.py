from multiprocessing import Process, Queue
import os

def file_reader(file_path, start, end, queue):
    """Generator, der die Datei abschnittsweise liest und nur relevante Bytes in die Queue stellt."""
    with open(file_path, "rb") as f:
        f.seek(start)
        while f.tell() < end:
            chunk = f.read(1)
            if not chunk:
                break
            if chunk != b'\x00':  # Nur Bytes ungleich Null in die Queue stellen
                queue.put(chunk)
    queue.put(None)  # Signalisiert das Ende der Daten für diesen Abschnitt

def main_worker(queue):
    """Liest die Queue und verarbeitet die empfangenen Daten."""
    while True:
        chunk = queue.get()
        if chunk is None:  # Ende des Abschnitts erreicht
            break
        print(chunk)  # Hier wird jedes relevante Byte (ungleich b'\x00') ausgegeben

if __name__ == '__main__':
    file_path = "Carve1.bin"
    file_size = os.path.getsize(file_path)  # Tatsächliche Dateigröße abrufen
    num_workers = 4
    chunk_size = file_size // num_workers

    # Start- und Endpositionen für jeden Prozess vorbereiten
    queues = [Queue() for _ in range(num_workers)]
    processes = []

    # Startet für jeden Abschnitt ein Lese- und ein Hauptprozess
    for i in range(num_workers):
        start = i * chunk_size
        end = (i + 1) * chunk_size
        p_reader = Process(target=file_reader, args=(file_path, start, end, queues[i]))
        p_worker = Process(target=main_worker, args=(queues[i],))
        p_reader.start()
        p_worker.start()
        processes.extend([p_reader, p_worker])

    # Auf alle Prozesse warten
    for p in processes:
        p.join()