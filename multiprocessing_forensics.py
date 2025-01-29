import os
import time
from datetime import datetime
import numpy as np
from multiprocessing import current_process, Lock, Process, Value
import logging
from utils import calculate_chi2, argparse, to_hex, calculate_shannon_entropy, to_bin

def multi_processing_section(lock, logger, vmdk_file, block_size, shared_offset, output_mod):

    # Determines the size of the VMDK file
    file_size = os.path.getsize(vmdk_file)
    # Variable to track the number of bytes read
    bytes_read = 0
    # Counter for the number of read blocks
    reading_counter = 0

    # Opens the VMDK file in read mode (“rb”) and an output file in attachment mode (“a”)
    with open(vmdk_file, "rb") as file, open("output.txt", "a") as output_file:
        # Continuous loop for reading the file
        while True:

            # Take a short break after every 10th block read
            if reading_counter % 10 == 0 and reading_counter != 0:
                print(f"{current_process().name}: Now sleeping!\n")
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

                # Calculates the Shannon entropy of the block
                block_entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))

                # if the entropy is greater than 7.9, then the block will be logged onto the console
                if block_entropy > 7.9:
                    #print(f"Process - {current_process().name}, Counter - {reading_counter}, Offset - {shared_offset.value}, Entropy - {block_entropy}\n")
                    logger.warning(f"Process: {current_process().name}, Counter: {reading_counter},read from offset: {shared_offset.value} : {block_entropy} Entropy \n")
                #logger.info(f"Process: {process_id}, Counter: {counter.value},read from offset: {pos} : {block} bytes \n")
                #print(f"Process: {current_process().name}, read from offset: {pos} : {block} \n")
                #    block_chi2_statistic, p_value = calculate_chi2(np.frombuffer(block, dtype=np.uint8))
                #    if p_value > 0.05 :
                #        pass
                #    elif p_value < 0.05 :
                #        pass
                else:
                    if output_mod == 0:
                        output_file.write(f"{current_process().name}: Offset-{shared_offset.value}, Block: {block}\n")
                    elif output_mod == 1:
                        output_file.write(f"{current_process().name}: Offset-{shared_offset.value}, Block: {to_hex(block)}\n")
                    elif output_mod == 2:
                        output_file.write(f"{current_process().name}: Offset-{shared_offset.value}, Block: {to_bin(block)}\n")


                # ---------- Ende Berechnung ----------

                #Updates the common offset by the size of the current block
                shared_offset.value += current_block_size
                # Increases the counter for the blocks read
                reading_counter += 1

            # Adds the bytes read to the total counter
            bytes_read += current_block_size

    print(f"Process: {current_process().name} has finished\n")






if __name__ == '__main__':
    # Creates a logger for the current module
    logger = logging.getLogger(__name__)

    # Creates a lock object for synchronisation between processes
    lock = Lock()

    # Reads the arguments from the command line
    args = argparse()

    # Saves the path to the file from the passed arguments
    file_path = args.file

    # Defines the block size for reading the file
    block_size = args.block_size

    # Defines the number of processes to be started
    num_processes = args.num_processes

    output_mode = args.outputmode

    # Creates a common counter (integer) that is used by all processes
    counter = Value('i', 0)

    # Starts the time measurement to calculate the total duration of the programme
    start = datetime.now()

    # Multiprocessing
    processes = []
    for i in range(num_processes):
        p = Process(target=multi_processing_section, args=(lock, logger, file_path, block_size, counter, output_mode))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

    print(f"Time taken: {(datetime.now() - start).total_seconds()} seconds")