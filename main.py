#import sys
#import argparse
import os
#import time
from datetime import datetime
from scipy.stats import entropy
import numpy as np
#from BlockDevice import BlockDevice
from multiprocessing import Pool, current_process, Lock, Manager
import logging
#import utils



logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(processName)s - PID: %(process)d - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)

def calculate_entropy(chunk):
    # Handling 0 Bytes
    if chunk is None or len(chunk) == 0:
        logging.warning('Empty chunk')
        return 0

    # Zählen wie oft jedes Element(Byte) vorkommt.
    byte_count = np.bincount(chunk, minlength=256)

    # Array, mit der relativen Häufigkeit (Wahrscheinlichkeit) von jedem Byte.
    probabilities = byte_count / np.sum(byte_count)

    return entropy(probabilities, base=2)


def read_chunks_of_vmdk(vmdk_file, num_process, chunk_size, lock, process_number):

    with open(vmdk_file, "rb") as f:
        file_size = f.seek(0, 2)
        section_size = file_size // num_process
        start_offset = process_number * section_size

        f.seek(start_offset) # Starting to read at the beginning

        bytes_read = 0 # temporary storage of bytes

        while bytes_read < section_size:
            remaining_bytes = section_size - bytes_read
            current_chunk_size = min(chunk_size, remaining_bytes)
            chunk = f.read(current_chunk_size)

            if not chunk:
                break

            chunk_entropy = calculate_entropy(np.frombuffer(chunk, dtype=np.uint8))
            #yield chunk
            if chunk_entropy > 7.2:
                with lock:
                    logging.info(f"Entropy: {chunk_entropy:.5f} - Read Bytes: {chunk} \n ")
            else:
                with lock:
                    with open("datastream.txt", "a") as f2:
                        f2.write(f"Process: {process_number}\n, Entropy: {chunk_entropy:.5f}\n, Chunk: {chunk.hex()}\n;")
            bytes_read += current_chunk_size

        print("FINISH!")

    return


if __name__ == '__main__':
    #logger = logging.getLogger(__name__)
    #vmdk_file = BlockDevice(file_object="100MB_Test.vmdk.akira")
    vmdk_file2 = "100MB_Test-flat.vmdk.akira"
    chunk_size = 4096
    num_processes = 6
    file_size_test = os.path.getsize(vmdk_file2)
    start = datetime.now()

    with Manager() as manager:
        lock = manager.Lock()
        with Pool(processes=num_processes) as pool:
            results = pool.starmap(read_chunks_of_vmdk, [(vmdk_file2, num_processes, chunk_size, lock, i) for i in range(num_processes)])

    print(f"File Size of vmdk_file2: {file_size_test}")
    print(f"Time taken: {(datetime.now() - start).total_seconds()} seconds")
