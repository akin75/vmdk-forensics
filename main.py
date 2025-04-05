import os
import time
from datetime import datetime
import numpy as np
from utils import calculate_chi2, argparse, to_hex, calculate_shannon_entropy, to_bin, write_output, check_block_size_for_chi2
import sys
import matplotlib.pyplot as plt
from tqdm import tqdm


def process_file_single(file_input, block_size, file_output, entropy_values, block_offsets):
    file_size = os.path.getsize(file_input)
    bytes_read = 0
    reading_counter = 0

    with open(file_input, "rb") as file, open(file_output, "wb") as output_file:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Processing") as progress:
            while True:

                remaining_bytes = file_size - bytes_read
                current_block_size = min(block_size, remaining_bytes)

                block = file.read(current_block_size)
                if not block:
                    break

                # ---------- Start Berechnung ----------
                block_entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))
                chi2_statistic, p_value = check_block_size_for_chi2(block)

                entropy_values.append(block_entropy)
                block_offsets.append(bytes_read)

                if block_entropy > 7.9:
                    if 0.05 < p_value < 0.95:
                        pass
                    else:
                        output_file.write(block)
                else:
                    output_file.write(block)
                # ---------- Ende Berechnung ----------

                bytes_read += current_block_size
                reading_counter += 1
                progress.update(current_block_size)

    print("[Done] Processing finished.\n")


def plot_entropy(block_offsets, entropy_values):
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
    plt.savefig("Entropy-plot.png")


if __name__ == '__main__':
    args = argparse()
    file_input = args.input
    file_output = args.output
    block_size = args.block_size

    start = datetime.now()

    entropy_values = []
    block_offsets = []

    process_file_single(file_input, block_size, file_output, entropy_values, block_offsets)

    plot_entropy(block_offsets, entropy_values)

    sys.stdout.write(f"Time taken: {(datetime.now() - start).total_seconds():.2f} seconds\n")
