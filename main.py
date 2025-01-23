#import sys
import os
#import time
from datetime import datetime
import numpy as np
#from BlockDevice import BlockDevice
from multiprocessing import Pool, current_process, Lock
import logging
from utils import calculate_chi2, argparse, to_hex, calculate_shannon_entropy, to_bin

logger = logging.getLogger(__name__)
lock = Lock()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(processName)s - PID: %(process)d - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)

def read_chunks_of_vmdk(vmdk_file, block_size):
    filesize = os.path.getsize(vmdk_file)
    bytes_read = 0

    with open(vmdk_file, "rb") as f:

        f.seek(0)

        while bytes_read < filesize:

            remaining_bytes = filesize - bytes_read
            current_block_size = min(block_size, remaining_bytes)
            block = f.read(block_size)
            current_pos = f.tell()
            #print("READING")
            if not block:
                break
            yield block, current_pos

            bytes_read += current_block_size



def processing_section(args):
    #print("Process Starting")
    block, current_pos = args

    block_entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))

    with lock:
        if block_entropy > 7.90:
        # chunk_chisquare = calculate_chisquare(...)
        #print(f"Process: {current_process().name}, Entropy: {block_entropy:.5f}, Position: {current_pos} \n")
            logger.info(f" Entropy: {block_entropy:.5f}, Position: {current_pos}")

    #print("Shannon Entropy Calculation Ended")
    return block_entropy, current_pos, to_bin(block)


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
        results = pool.imap(processing_section, read_chunks_of_vmdk(vmdk_file2, block_size))
        pool.close()
        pool.join()

    #for i, (block_entropy, current_pos, block)  in enumerate(results):
    #    with open("output.txt", "a") as f:
    #        f.write(f"{block_entropy}\t{current_pos:.5f}\t{block}\n")
    #print("Finished Writing")


    print(f"Time taken: {(datetime.now() - start).total_seconds()} seconds")
