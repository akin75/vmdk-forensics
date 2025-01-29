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

    # Gibt ein Objekt mit den Variablen = statistic (chi-squared statistic(Float-Wert)) und p-value (Der p-Wert des Tests(Float Wert))
    chi2_statistic, p_value = chisquare(chunk)
    
    return chi2_statistic, p_value

def to_hex(block):
    formatted_hex = ' '.join(['{:02x}'.format(b) for b in block])
    return formatted_hex

def to_bin(block):
    formatted_bin = ' '.join(f'{byte:08b}' for byte in block)
    return formatted_bin

def argparse():
    parser = ArgumentParser(description="Detect intermittent encryption and extract unencrypted blocks")
    parser.add_argument('file', metavar='file', help='files to process', type=str)
    parser.add_argument('block_size', metavar='blocksize', help='block size to use', type=int, default=4096)
    parser.add_argument('num_processes', metavar='numprocesses', help='number of processes', type=int)
    #parser.add_argument('output-file', metavar='outputfile', help='file to store output', type=str)
    parser.add_argument('outputmode', metavar='outputmode', help='chunk size', type=int, default=0)
    args = parser.parse_args()
    return args