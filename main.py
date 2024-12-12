#import pyvmdk
#import sys
#import argparse
import os
#import time
from datetime import datetime
#from pickletools import uint8
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
    #
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

            with lock:
                logging.info(f"Entropie: {chunk_entropy:.5f} - Read Bytes: {chunk} \n ")
            #print(f"Prozess: {multiprocessing.current_process().name}" , f" PID: {multiprocessing.current_process().pid}" , f" Read Bytes:  {chunk} \n")
            bytes_read += current_chunk_size
    return

# A function to do the tasks with Multiprocessing
def multiprocessing_section():
    pass





if __name__ == '__main__':
    #lock = logging.getLogger(__name__)
    #vmdk_file = BlockDevice(file_object="Metasploitable 2_1.vmdk")
    vmdk_file2 = "D:\\Akira\\100MB\\100MB_Test-flat.vmdk.akira"
    chunk_size = 4096
    num_processes = 8
    file_size_test = os.path.getsize(vmdk_file2)
    start = datetime.now()

    #with Manager() as manager:
    #    lock = manager.Lock()
    #    with Pool(processes=num_processes) as pool:
    #        results = pool.starmap(read_chunks_of_vmdk, [(vmdk_file2, num_processes, chunk_size, lock, i) for i in range(num_processes)])
    print(f"File Size of vmdk_file2: {file_size_test}")
    print(f"Time taken: {(datetime.now() - start).total_seconds()} Sekunden")
    chunk_entropy = calculate_entropy(np.frombuffer(b"y\x8fF\xb6\x01^7P\xb2\xffc\xd7\xdd\xf6\x00\x898\xb2\xdbg\xf7\xa7\xceC{\xecC\x96\xc9\xa1\xde\xba~\xb7\x1b\x89\xa9-F\xa8\xd1|Z/\xeb'U\xcc\x02{y\xa9\xb1f\xad(\t\xdb\xf2\x9e\xfc\xa1d=", dtype=np.uint8))
    print(f"Chunk Entropy: {chunk_entropy:.5f}")
    print(f"Rounded Chunk: {round(chunk_entropy, 5)}")
    if chunk_entropy == 5.71875:
        print(f"Entropy Matches: {chunk_entropy:.5f} == 5.71875")

    #test_chunk = np.array(b"y\x8fF\xb6\x01^7P\xb2\xffc\xd7\xdd\xf6\x00\x898\xb2\xdbg\xf7\xa7\xceC{\xecC\x96\xc9\xa1\xde\xba~\xb7\x1b\x89\xa9-F\xa8\xd1|Z/\xeb'U\xcc\x02{y\xa9\xb1f\xad(\t\xdb\xf2\x9e\xfc\xa1d=", dtype=np.uint8)
    #print(f"Test chunk: {test_chunk}")

    #for start_offset, actual_block_size in split_file_into_sections(vmdk_file, block_size, num_processes):
    #    print(f"Start Offset: {start_offset}, Block Size: {actual_block_size}")

    #sections = split_file_into_sections(vmdk_file, block_size, num_processes)
    #for i, (start_offset, actual_block_size) in enumerate(sections, start=1):
    #    print(f"Index: {i}, Start Offset: {start_offset}, Block Size: {actual_block_size}")

    #sections_test = split_file_into_sections(vmdk_file, block_size, num_processes)
    #process_blocks_test = process_section(vmdk_file, sections_test, block_size)
    #for chunk in process_blocks_test:
    #    print(f"THIS IS CHUNK {chunk}")

    #print(pyvmdk.get_version())
    # Prints the disk type -> MONOLITHIC FLAT
    #vmdk_file.get_get_disk_type_and_size_of_vmdk()

    # Prints the first position
    #print(f"Element: {next(islice(generator, 1, 1 + 1), None)}")
    #print(f"Element at Position 1: {utils.give_block_at_specified_pos(gen=generator, pos=1)}")

    #pool.close()
    #pool.join()

