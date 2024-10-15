class BlockDevice:

    Byte_Size = 512

    def __init__(self, block, file_object):
        self.block = block
        self.file_object = file_object
        self.file = open(self.file_object, "rb")

block_device = BlockDevice(1, "Metasploitable 2_1-flat.vmdk")