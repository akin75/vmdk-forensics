from argparse import ArgumentParser
from itertools import islice
from typing import Generator



def give_block_at_specified_pos(gen: Generator, pos: int):
    element = next(islice(gen, pos, pos + 1), None)
    if element is None:
        print("Pos does not exist")
    return element

def argparse():
    parser = ArgumentParser(description="Detect intermittent encryption and extract unencrypted blocks")