import pyvmdk
import pytsk3
import math
import sys
import argparse
import time

blocks = []

vmdk_handle = pyvmdk.handle()
vmdk_handle.open("Metasploitable 2_1.vmdk", mode="r")
vmdk_handle.open_extent_data_files()

def print_hi(name):
    print(f'Hi, {name}')  # Press Strg+F8 to toggle the breakpoint.
    print("FIRST")

def construct_blocks(byte_chunk):
    # VMDK is being read in given byte_chunks
    # Byte_chunks will be appended to the list
    # Return the list of the byte_chunks
    while True:
        block = vmdk_handle.read(byte_chunk)
        if not block:
            break
        blocks.append(block)
    return blocks


def read_block(data_block):
    block_read = vmdk_handle.read(data_block)
    print(f"Decoded block: {block_read.decode('utf-8')}")
    blocks.append(block_read.decode('utf-8'))
    print(f"Block size: {len(block_read)}")
    print(blocks)
    return blocks

def main():
    print_hi('Akin')
    print(pyvmdk.get_version())
    byte_array = construct_blocks(64)
    print(byte_array)
    print(f"Get Media size: {vmdk_handle.get_media_size()}")
    print(f"Count of elements: {len(byte_array)}")
    print(byte_array[1])
    #print(f"Reading blocks: {read_block(4096)}")
    #print("------------------------------------")
    #print(f"Reading blocks: {read_block(64)}")



if __name__ == '__main__':
    print("Before main()")
    main()
    print("After main()")
    vmdk_handle.close()




















# ---------------------------------------------------------------------------------------------------------------------#
    # Testing Methods
    #print(vmdk_handle.open_extent_data_files())
    #print(f"Get disk type: {vmdk_handle.get_disk_type()}") # DISK TYPE : 6 = MONOLITHIC FLAT
    #if vmdk_handle.get_disk_type() == pyvmdk.disk_types.MONOLITHIC_FLAT:
    #    print("It's Monolithic Flat!")
    #print(f"Get Media size: {vmdk_handle.get_media_size()}") # Gives back total bytes of file
    #print(f"Get content Identifier: {vmdk_handle.get_content_identifier()}") # Unique Identifier
    #hex_cid = "06c5e46d"
    #hex_number = int(hex_cid, 16)
    #print(f"Content Identifier: {hex_number}")
    #if hex_number == vmdk_handle.get_content_identifier():
    #    print(f"It is equal! {hex_number} == {vmdk_handle.get_content_identifier()}")
    #print(f"Number of Extents: {vmdk_handle.get_number_of_extents()}")
    #print(f"Get offset {vmdk_handle.get_offset()}")

    #print(vmdk_handle.read(8192))
    #with open("output.raw", "wb") as f:
    #    f.write(vmdk_handle.read(8192))




