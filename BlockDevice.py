import pyvmdk

class BlockDevice:
    # When initialized open vmdk file
    vmdk_handle = pyvmdk.handle()

    def __init__(self, file_object: str):
        self.list_of_blocks = []
        self.file_object = file_object # "Metasploitable 2_1.vmdk"
        vmdk_handle = self.vmdk_handle
        vmdk_handle.open(file_object, "r")
        vmdk_handle.open_extent_data_files()

    def get_disk_type_and_size_of_vmdk(self):
        print(f"Media Size: {self.vmdk_handle.get_media_size()}")
        print(f"Disk Type: {self.vmdk_handle.get_disk_type()}")
        if  self.vmdk_handle.get_disk_type() == 1:
            print("FLAT_2GB_EXTENT")
        elif self.vmdk_handle.get_disk_type() == 2:
            print("SPARSE_2GB_EXTENT")
        elif self.vmdk_handle.get_disk_type() == 3:
            print("CUSTOM")
        elif self.vmdk_handle.get_disk_type() == 4:
            print("DEVICE")
        elif self.vmdk_handle.get_disk_type() == 5:
            print("DEVICE_PARITIONED")
        elif self.vmdk_handle.get_disk_type() == 6:
            print("MONOLITHIC_FLAT")
        elif self.vmdk_handle.get_disk_type() == 7:
            print("MONOLITHIC_SPARSE")
        elif self.vmdk_handle.get_disk_type() == 8:
            print("STREAM_OPTIMIZED")
        elif self.vmdk_handle.get_disk_type() == 9:
            print("VMFS_FLAT")
        elif self.vmdk_handle.get_disk_type() == 10:
            print("VMFS_FLAT_PRE_ALLOCATED")
        elif self.vmdk_handle.get_disk_type() == 11:
            print("VMFS_FLAT_ZEROED")
        elif self.vmdk_handle.get_disk_type() == 12:
            print("VMFS_RAW")
        elif self.vmdk_handle.get_disk_type() == 13:
            print("VMFS_RDM")
        elif self.vmdk_handle.get_disk_type() == 14:
            print("VMFS_RDMP")
        elif self.vmdk_handle.get_disk_type() == 15:
            print("VMFS_SPARSE")
        elif self.vmdk_handle.get_disk_type() == 16:
            print("VMFS_SPARSE_THIN")


    def construct_blocks(self, block_size: int):
        """
                This function reads the vmdk by given block_size and constructs a list of blocks.
                :param block_size: size of chunks
                :yield -> Generator of blocks
                """
        # VMDK is being read in given byte_chunks
        # Byte_chunks will be appended to the list
        # Return the list of the byte_chunks
        while True:
            block = self.vmdk_handle.read(block_size)
            if not block:
                break
            yield block

    def close_handle(self):
        self.vmdk_handle.close()

    def get_size(self):
        return self.vmdk_handle.get_media_size()

    def vmdk_seek(self, start_offset):
        return self.vmdk_handle.seek(start_offset)

    def vmdk_tell(self):
        return self.vmdk_handle.tell()

    def vmdk_read(self, chunk_size):
        return self.vmdk_handle.read(chunk_size)