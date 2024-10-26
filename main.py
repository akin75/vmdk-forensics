from typing import Generator
import pyvmdk
#import pytsk3
#import math
#import sys
#import argparse
#import time
from BlockDevice import BlockDevice
from itertools import islice
from multiprocessing import Pool
import utils



if __name__ == '__main__':
    # instantiating Blockdevice class -> open VMDK file.
    vmdk_file = BlockDevice(file_object="Metasploitable 2_1.vmdk")

    #pool = Pool(processes=4)
    # Construction of a Generator with given block_size -> in this case 64 (parameter)
    generator = vmdk_file.construct_blocks(64)
    # Generator wird zu groß und wird erschöpft. Ein guter Ansatz wäre, während dem iterieren schon das rechnen der Entropie zu implementieren.

    print(pyvmdk.get_version())
    # Prints the disk type -> MONOLITHIC FLAT
    vmdk_file.get_disk_type_of_vmdk()

    # Prints the first position
    print(f"Element: {next(islice(generator, 1, 1 + 1), None)}")
    print(f"Element at Position 1: {utils.give_block_at_specified_pos(gen=generator, pos=1)}")

    vmdk_file.close_handle()
    #pool.close()
    #pool.join()