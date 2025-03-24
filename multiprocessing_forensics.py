import os
import time
from datetime import datetime
import numpy as np
from multiprocessing import current_process, Lock, Process, Value, Manager
from utils import calculate_chi2, argparse, to_hex, calculate_shannon_entropy, to_bin, write_output, check_block_size_for_chi2
import sys
import matplotlib.pyplot as plt

def multi_processing_section(lock, vmdk_file, block_size, shared_offset, output_mod, entropy_values, block_offsets, file_output):

    # Determines the size of the VMDK file
    file_size = os.path.getsize(vmdk_file)
    # Variable to track the number of bytes read
    bytes_read = 0
    # Counter for the number of read blocks
    reading_counter = 0

    # Opens the VMDK file in read mode (“rb”) and an output file in attachment mode (“a”)
    with open(vmdk_file, "rb") as file, open(file_output, "a") as output_file:
        # Continuous loop for reading the file
        while True:

            # Take a short break after every 10th block read
            if reading_counter % 20 == 0 and reading_counter != 0:
                time.sleep(0.1)

            # Synchronizes access to shared resources with the lock
            with lock:

                # Calculates the remaining bytes that still need to be read
                remaining_bytes = file_size - bytes_read

                # Ends the loop when there are no more bytes left
                if remaining_bytes <= 0:
                    break

                # Determines the block size for the current read operation
                current_block_size = min(block_size, remaining_bytes)

                # Sets the file pointer to the location of the current offset
                file.seek(shared_offset.value)

                # Reads the block from the file
                block = file.read(current_block_size)

                # Ends the loop if the block is empty
                if not block:
                    break

                # ---------- Start Berechnung ----------

                # Calculates the Shannon entropy and Chi-Square of the block
                block_entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))
                chi2_statistic, p_value = check_block_size_for_chi2(block)

                entropy_values.append(block_entropy)
                block_offsets.append(shared_offset.value)

                if block_entropy > 7.9:
                    if p_value <= 0.05 or p_value >= 0.95 :
                        pass
                    else:
                        write_output(output_file, current_process().name, shared_offset.value, block, output_mod, entropy=block_entropy,chi2_statistic=chi2_statistic, p_value=p_value)
                else:
                    write_output(output_file, current_process().name, shared_offset.value, block, output_mod,
                                 entropy=block_entropy, chi2_statistic=chi2_statistic, p_value=p_value)
                # ---------- Ende Berechnung ----------

                #Updates the common offset by the size of the current block
                shared_offset.value += current_block_size
                # Increases the counter for the blocks read
                reading_counter += 1

            # Adds the bytes read to the total counter
            bytes_read += current_block_size

    print(f"Process: {current_process().name} has finished\n")


def plot_entropy(block_offsets, entropy_values):

    plt.figure(figsize=(10, 5))

    block_offsets = np.array(block_offsets)
    entropy_values = np.array(entropy_values)

    plt.plot(block_offsets, entropy_values, linestyle='-', color='b', label='Entropie')

    plt.xlabel("Speicherbereich (Offset in Bytes)")
    plt.ylabel("Entropie")
    plt.title("Verlauf der Entropie in der Datei")
    plt.grid(True)

    # X-Achse gleichmäßig skalieren
    plt.xticks(np.linspace(block_offsets.min(), block_offsets.max(), 3))

    plt.legend()
    plt.savefig("entropy_plot.png")




if __name__ == '__main__':
    # Creates a lock object for synchronisation between processes
    lock = Lock()

    # Reads the arguments from the command line
    args = argparse()

    # Saves the path to the file from the passed arguments
    file_path = args.input

    file_output = args.output

    # Defines the block size for reading the file
    block_size = args.block_size

    # Defines the number of processes to be started
    num_processes = args.processes

    output_mode = args.mode

    # Creates a common counter (Long) that is used by all processes
    counter = Value('l', 0)

    # Starts the time measurement to calculate the total duration of the programm
    start = datetime.now()

    with Manager() as manager:
        entropy_values = manager.list()
        block_offsets = manager.list()

        # Multiprocessing
        processes = []
        for i in range(num_processes):
            p = Process(target=multi_processing_section, args=(lock, file_path, block_size, counter, output_mode, entropy_values, block_offsets, file_output))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

        plot_entropy(list(block_offsets), list(entropy_values))

    #print(f"Time taken: {(datetime.now() - start).total_seconds()} seconds")
    sys.stdout.write(f"Time taken: {(datetime.now() - start).total_seconds()} seconds\n")

