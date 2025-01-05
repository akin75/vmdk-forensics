from argparse import ArgumentParser
from itertools import islice
from typing import Generator
from scipy.stats import entropy, chi2, chisquare
import numpy as np
import logging

def calculate_entropy(chunk):
    # Handling 0 Bytes
    if chunk is None or len(chunk) == 0:
        logging.warning('Empty chunk')
        return 0

    # Zählen wie oft jedes Element(Byte) vorkommt.
    byte_count = np.bincount(chunk, minlength=256)

    # Array, mit der relativen Häufigkeit (Wahrscheinlichkeit) von jedem Byte.
    probabilities = byte_count / np.sum(byte_count)

    return entropy(probabilities, base=2)

def calculate_chi2(chunk):
    if chunk is None or len(chunk) == 0:
        logging.warning('Empty chunk')

    chisquare(chunk)
    return 0

def to_hex(block):
    formatted_hex = ' '.join(['{:02x}'.format(b) for b in block])
    return formatted_hex

def give_block_at_specified_pos(gen: Generator, pos: int):
    element = next(islice(gen, pos, pos + 1), None)
    if element is None:
        print("Pos does not exist")
    return element

def argparse():
    parser = ArgumentParser(description="Detect intermittent encryption and extract unencrypted blocks")