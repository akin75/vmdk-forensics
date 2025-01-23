import os
import time
from datetime import datetime
import numpy as np
from multiprocessing import current_process, Lock, Process, Value
import logging
from utils import calculate_chi2, argparse, to_hex, calculate_shannon_entropy, to_bin

def multi_processing_section(lock, logger, vmdk_file, block_size, shared_offset):

    file_size = os.path.getsize(vmdk_file)
    bytes_read = 0
    reading_counter = 0

    with open(vmdk_file, "rb") as file:
        while True:

            if reading_counter % 10 == 0 and reading_counter != 0:
                print(f"{current_process().name}: Now sleeping!\n")
                time.sleep(0.1)

            with lock:
                remaining_bytes = file_size - bytes_read
                if remaining_bytes <= 0:
                    break

                current_block_size = min(block_size, remaining_bytes)
                file.seek(shared_offset.value)
                block = file.read(current_block_size)
                if not block:
                    break

                # ---------- Berechnungen ----------
                block_entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))

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
                #else:
                #    with open("output.txt", "a") as output_file:
                #        output_file.write(f"{current_process().name}: Counter-{reading_counter}, Offset-{shared_offset.value}, Block: {block} \n")

                # ---------- Ende Berechnung ----------

                shared_offset.value += current_block_size
                reading_counter += 1

            bytes_read += current_block_size

    print(f"Process: {current_process().name} has finished\n")






if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    lock = Lock()
    args = argparse()
    file_path = args.file
    block_size = args.block_size
    num_processes = args.num_processes

    counter = Value('i', 0)

    start = datetime.now()

    # Multiprocessing
    processes = []
    for i in range(num_processes):
        p = Process(target=multi_processing_section, args=(lock, logger, file_path, block_size, counter))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

    print(f"Time taken: {(datetime.now() - start).total_seconds()} seconds")