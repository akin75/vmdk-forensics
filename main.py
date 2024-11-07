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
from multiprocessing import Pool
import utils

def split_file_into_sections(file_object: BlockDevice, block_size: int, num_processes: int):
    file_size = file_object.get_size()
    block_count = file_size // block_size
    blocks_per_process = block_count // num_processes
    start_offset = 0

    for process_index in range(num_processes):
        if process_index == num_processes - 1:
            # Last process gets the rest of the remaining Bytes
            actual_block_size = file_size - start_offset
        else:
            # Blocks per process multiplied by the blocksize returns the actual size 10 MB -> 2.5 MB each for 4 processes
            actual_block_size = blocks_per_process * block_size

        yield start_offset, actual_block_size

        start_offset += actual_block_size

def process_section(file_object: BlockDevice, args, chunk_size: int):
    # Startpunkt start_offset seek(); actual_blocksize wird unterteilt
    print(f"THIS IS ARGS: {args}")
    for arg in args:
        start_offset, actual_block_size = arg
        print(f"{start_offset}: {actual_block_size}")
    file_size = file_object.vmdk_seek(start_offset)
    bytes_read = 0 # Temp Storage of read bytes

    # Loop
    while bytes_read < actual_block_size:
        remaining_bytes = actual_block_size - bytes_read
        current_chunk_size = min(chunk_size, remaining_bytes)
        block = file_object.vmdk_read(current_chunk_size)
        if remaining_bytes == 64:
            print("THIS IS THE END")
        if not block:
            break
        yield block
        bytes_read += current_chunk_size
        print(remaining_bytes)
    print("we are at the end")




if __name__ == '__main__':
    # instantiating Blockdevice class -> open VMDK file.
    vmdk_file = BlockDevice(file_object="Metasploitable 2_1.vmdk")
    chunk_size = 64
    num_processes = 4
    file_size_test = os.path.getsize("Metasploitable 2_1-flat.vmdk")

    with Pool(processes=num_processes) as p:
        sections = split_file_into_sections(vmdk_file, chunk_size, num_processes)
        results = p.starmap(process_section, (sections, chunk_size)) # TypeError: cannot pickle 'generator' object
        print(results)

    #for start_offset, actual_block_size in split_file_into_sections(vmdk_file, block_size, num_processes):
    #    print(f"Start Offset: {start_offset}, Block Size: {actual_block_size}")

    #sections = split_file_into_sections(vmdk_file, block_size, num_processes)
    #for i, (start_offset, actual_block_size) in enumerate(sections, start=1):
    #    print(f"Index: {i}, Start Offset: {start_offset}, Block Size: {actual_block_size}")

    #sections_test = split_file_into_sections(vmdk_file, block_size, num_processes)
    #process_blocks_test = process_section(vmdk_file, sections_test, block_size)
    #for chunk in process_blocks_test:
    #    print(f"THIS IS CHUNK {chunk}")


    # Construction of a Generator with given block_size -> in this case 64 (parameter)
    start = datetime.now()
    generator = vmdk_file.construct_blocks(64)
    # Generator wird zu groß und wird erschöpft. Ein guter Ansatz wäre, während dem iterieren schon das rechnen der Entropie zu implementieren.
    with open("output.txt", "w") as f:
        for i,element in enumerate(generator):
            #print(f"Element: {element} at position {i}\n")
            f.write(f"Element: {element} at position {i}\n")
    print(f"Time taken: {(datetime.now() - start).total_seconds()} Sekunden")
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
