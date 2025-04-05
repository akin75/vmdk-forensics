import os
from datetime import datetime
import numpy as np
from multiprocessing import Pool, current_process, Value, Lock, Manager
import matplotlib.pyplot as plt

from utils import calculate_shannon_entropy, check_block_size_for_chi2, argparse, to_bin

lock = Lock()
counter = Value('l', 0)

def read_chunks_of_vmdk(vmdk_file, block_size):
    filesize = os.path.getsize(vmdk_file)
    bytes_read = 0

    with open(vmdk_file, "rb") as f:
        while bytes_read < filesize:
            remaining_bytes = filesize - bytes_read
            current_block_size = min(block_size, remaining_bytes)
            block = f.read(current_block_size)
            current_pos = bytes_read

            if not block:
                break

            yield (block, current_pos)
            bytes_read += current_block_size


def processing_section(args):
    block, offset = args
    entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))
    chi2_statistic, p_value = check_block_size_for_chi2(block)

    return (offset, entropy, chi2_statistic, p_value, block)


def plot_entropy(block_offsets, entropy_values):
    if not block_offsets or not entropy_values:
        return

    plt.figure(figsize=(10, 5))
    block_offsets = np.array(block_offsets)
    entropy_values = np.array(entropy_values)

    plt.plot(block_offsets, entropy_values, linestyle='-', color='b', label='Entropie')
    plt.xlabel("Speicherbereich (Offset in Bytes)")
    plt.ylabel("Entropie")
    plt.title("Verlauf der Entropie in der Datei")
    plt.grid(True)
    plt.xticks(np.linspace(block_offsets.min(), block_offsets.max(), 3))
    plt.legend()
    plt.tight_layout()
    plt.savefig("Entropy-Akira-10GB.png")

if __name__ == '__main__':
    args = argparse()
    vmdk_file = args.input
    block_size = args.block_size
    num_processes = args.processes
    output_file = args.output

    start = datetime.now()

    # Manager-Listen zum Sammeln der Werte für das Plot
    with Manager() as manager:
        entropy_values = manager.list()
        block_offsets = manager.list()
        blocks_to_write = manager.list()

        with Pool(processes=num_processes) as pool:
            results = pool.imap(processing_section, read_chunks_of_vmdk(vmdk_file, block_size), chunksize=10)
            for offset, entropy, chi2_stat, p_value, block in results:
                entropy_values.append(entropy)
                block_offsets.append(offset)

                # Speicherbedingung für Ausgabe
                if entropy > 7.9:
                    if 0.05 < p_value < 0.95:
                        continue
                    else:
                        blocks_to_write.append((offset, block))
                else:
                    blocks_to_write.append((offset, block))

            pool.close()
            pool.join()

        # Sortiere Blöcke nach Offset und schreibe in Datei
        with open(output_file, "wb") as out:
            for offset, block in sorted(blocks_to_write):
                out.write(block)

        # Entropie-Plot erzeugen
        plot_entropy(list(block_offsets), list(entropy_values))

        duration = (datetime.now() - start).total_seconds()
        print(f"⏱️ Verarbeitung abgeschlossen in {duration:.2f} Sekunden")
