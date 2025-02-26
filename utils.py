import os
from argparse import ArgumentParser
from scipy.stats import entropy, chi2, chisquare
import numpy as np
import logging

def calculate_shannon_entropy(chunk):
    # Handling 0 Bytes
    if chunk is None or len(chunk) == 0:
        logging.warning('Empty chunk')
        return 0

    # Zählen wie oft jedes Element(Byte) vorkommt.
    byte_count = np.bincount(chunk, minlength=256)

    # Array, mit der relativen Häufigkeit (Wahrscheinlichkeit) von jedem Byte.
    probabilities = byte_count / np.sum(byte_count)

    return entropy(probabilities, base=2)

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html#r81ecfb019d82-1
# Die ChiSquare Berechnung funktioniert auch nur mit den Observed Frequencies.
def calculate_chi2(chunk):
    if chunk is None or len(chunk) == 0:
        logging.warning('Empty chunk')

    f_obs = np.bincount(np.frombuffer(chunk, dtype=np.uint8), minlength=256)
    f_exp = np.full(256, len(chunk) / 256)
    # Gibt ein Objekt mit den Variablen = statistic (chi-squared statistic(Float-Wert)) und p-value (Der p-Wert des Tests(Float Wert))
    chi2_statistic, p_value = chisquare(f_obs, f_exp)
    
    return chi2_statistic, p_value

def to_hex(block):
    formatted_hex = ' '.join(['{:02x}'.format(b) for b in block])
    return formatted_hex

def to_bin(block):
    formatted_bin = ' '.join(f'{byte:08b}' for byte in block)
    return formatted_bin

def convert_to_nibbles(block):
    for byte in block:
        yield byte >> 4
        yield byte & 0x0F

def argparse():
    parser = ArgumentParser(description="Detect intermittent encryption and extract unencrypted blocks")

    parser.add_argument('-i', '--input', metavar='FILE', required=True, help='Vmdk file to process', type=str)

    #parser.add_argument('-o', '--output', metavar='FILE', required=True, help='File to store output', type=str)

    parser.add_argument('-block', '--block_size', metavar='SIZE', help='Block size to use', type=int, default=4096, dest="block_size")

    parser.add_argument('-p', '--processes', metavar='NUM', required=True, help='Number of processes to use', type=int)

    #parser.add_argument('-m','--mode', metavar='MODE', required=True, help='Output mode', type=int, default=0)

    args = parser.parse_args()

    # Check for VMDK file
    #if "vmdk" not in args.input.lower():
    #    parser.error('Input file must be vmdk')
    # Check if file exists
    #if not os.path.isfile(args.input):
    #    parser.error(f"Input file {args.input} does not exist")

    return args