import multiprocessing
from fileinput import filename
from typing import Generator
import pyvmdk
#import pytsk3
#import math
#import sys
#import argparse
import os
import time
from datetime import datetime
from BlockDevice import BlockDevice
from itertools import islice
from multiprocessing import Pool, current_process, Lock
import logging
import utils

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(processName)s - PID: %(process)d - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
    filename="outputLogs.log"
)


def process_chunks(vmdk_file, num_process, chunk_size, process_number):
    lock = multiprocessing.Lock()
    with open(vmdk_file, "rb") as f:
        file_size = f.seek(0, 2)
        section_size = file_size // num_process
        block_count = file_size // chunk_size
        blocks_per_process = block_count // num_process
        start_offset = process_number * section_size

        f.seek(start_offset) # Starting to read at the beginning

        bytes_read = 0 # temporary storage of bytes

        while bytes_read < section_size:
            remaining_bytes = section_size - bytes_read
            current_chunk_size = min(chunk_size, remaining_bytes)
            chunk = f.read(current_chunk_size)
            if not chunk:
                break
            with lock:
                logging.info(f" -- Read Bytes: {chunk} \n ")
            #print(f"Prozess: {multiprocessing.current_process().name}" , f" PID: {multiprocessing.current_process().pid}" , f" Read Bytes:  {chunk} \n")
            bytes_read += current_chunk_size
    return




if __name__ == '__main__':
    # instantiating Blockdevice class -> open VMDK file.
    vmdk_file = BlockDevice(file_object="Metasploitable 2_1.vmdk")
    vmdk_file2 = "500MB_Test-flat.vmdk"
    chunk_size = 2048
    num_processes = 8
    file_size_test = os.path.getsize(vmdk_file2)
    start = datetime.now()
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_chunks, [(vmdk_file2, num_processes, chunk_size, i) for i in range(num_processes)])
    print(f"File Size of vmdk_file2: {file_size_test}")
    print(f"Time taken: {(datetime.now() - start).total_seconds()} Sekunden")

    #for start_offset, actual_block_size in split_file_into_sections(vmdk_file, block_size, num_processes):
    #    print(f"Start Offset: {start_offset}, Block Size: {actual_block_size}")

    #sections = split_file_into_sections(vmdk_file, block_size, num_processes)
    #for i, (start_offset, actual_block_size) in enumerate(sections, start=1):
    #    print(f"Index: {i}, Start Offset: {start_offset}, Block Size: {actual_block_size}")

    #sections_test = split_file_into_sections(vmdk_file, block_size, num_processes)
    #process_blocks_test = process_section(vmdk_file, sections_test, block_size)
    #for chunk in process_blocks_test:
    #    print(f"THIS IS CHUNK {chunk}")

    print("Cpu count: ", os.cpu_count())

    #print(pyvmdk.get_version())
    # Prints the disk type -> MONOLITHIC FLAT
    #vmdk_file.get_get_disk_type_and_size_of_vmdk()

    # Prints the first position
    #print(f"Element: {next(islice(generator, 1, 1 + 1), None)}")
    #print(f"Element at Position 1: {utils.give_block_at_specified_pos(gen=generator, pos=1)}")

    #pool.close()
    #pool.join()
    file_size = vmdk_file.get_size()
    print(f"File size: {file_size}")
    print(file_size // 64)
    block_count = file_size // 64
    print(f"{file_size} // 64 blocks = ", file_size // 64)
    print(f"{block_count} // 4 processes = ", block_count // 4)
    print(f"This is f: ", file_size_test)
    vmdk_file.close_handle()
