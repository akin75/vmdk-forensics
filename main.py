#import sys
#import argparse
import os
#import time
from datetime import datetime
import numpy as np
#from BlockDevice import BlockDevice
from multiprocessing import Pool, current_process
import logging
from utils import calculate_entropy, calculate_chi2, argparse


logger = logging.getLogger(__name__)
#logging.basicConfig(
#    level=logging.DEBUG,
#    format='%(asctime)s - %(processName)s - PID: %(process)d - %(levelname)s - %(message)s',
#    handlers=[logging.StreamHandler()],
#)

def read_chunks_of_vmdk(vmdk_file, block_size):
    print("ICH BIN HIER")
    filesize = os.path.getsize(vmdk_file)
    bytes_read = 0

    with open(vmdk_file, "rb") as f:

        f.seek(0)

        while bytes_read < filesize:

            remaining_bytes = filesize - bytes_read
            current_block_size = min(block_size, remaining_bytes)
            block = f.read(block_size)
            current_pos = f.tell()

            if not block:
                break
            yield block, current_pos

            bytes_read += current_block_size



def processing_section(args):

    block, current_pos = args

    block_entropy = calculate_entropy(np.frombuffer(block, dtype=np.uint8))

    if block_entropy > 7.90:
        # chunk_chisquare = calculate_chisquare(...)
        print(f"Process: {current_process().name}, Entropy: {block_entropy:.5f}, Position: {current_pos}\n")


    #return block_entropy, current_pos, block


if __name__ == '__main__':
    #logger = logging.getLogger(__name__)
    #vmdk_file = BlockDevice(file_object="100MB_Test.vmdk.akira")
    #"100MB_Test-flat.vmdk.akira"
    args = argparse()
    vmdk_file2 = args.file
    block_size = args.block_size
    num_processes = args.num_processes
    start = datetime.now()

    with Pool(processes=num_processes) as pool:
        results = pool.imap(processing_section, read_chunks_of_vmdk(vmdk_file2, block_size), chunksize=10)
        pool.close()
        pool.join()
    #for i, (block_entropy, current_pos, block)  in enumerate(results):
    #    print(f"Position: {i}, Entropy: {block_entropy}, Current Position: {current_pos}, Chunk: {utils.to_hex(block)}\n")

    print(f"Time taken: {(datetime.now() - start).total_seconds()} seconds")
