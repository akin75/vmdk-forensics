import os
from argparse import ArgumentParser
from scipy.stats import entropy, chi2, chisquare
import numpy as np
import logging

def calculate_shannon_entropy(block):
    # Handling 0 Bytes
    if block is None or len(block) == 0:
        logging.warning('Empty block')
        return 0

    # Zählen wie oft jedes Element(Byte) vorkommt.
    byte_count = np.bincount(block, minlength=256)

    # Array, mit der relativen Häufigkeit (Wahrscheinlichkeit) von jedem Byte.
    probabilities = byte_count / np.sum(byte_count)

    return entropy(probabilities, base=2)

def calculate_chi2(block):
    if block is None or len(block) == 0:
        logging.warning('Empty block')
        return 0

    f_obs = np.bincount(np.frombuffer(block, dtype=np.uint8), minlength=256)
    f_exp = np.full(256, len(block) / 256)
    # Gibt ein Objekt mit den Variablen = statistic (chi-squared statistic(Float-Wert)) und p-value (Der p-Wert des Tests(Float Wert))
    chi2_statistic, p_value = chisquare(f_obs, f_exp)
    
    return chi2_statistic, p_value

def calculate_nibbles_chi2(block):

    if block is None or len(block) == 0:
        logging.warning('Empty block')
        return 0

    nibbles = np.array(convert_to_nibbles(block), dtype=np.uint8)

    f_obs = np.bincount(nibbles, minlength=16)
    #f_exp = np.full(16, len(chunk) / 16)

    chi2_statistic, p_value = chisquare(f_obs)

    return chi2_statistic, p_value


def convert_to_nibbles(block):
    return [nibble for byte in block for nibble in (byte >> 4, byte & 0x0F)]

def check_block_size_for_chi2(block):
    if len(block) > 1300:
        chi2_statistic, p_value = calculate_chi2(block)
    else:
        chi2_statistic, p_value = calculate_nibbles_chi2(block)

    return chi2_statistic, p_value


def argparse():
    parser = ArgumentParser(description="Detect intermittent encryption and extract encrypted blocks")

    parser.add_argument('-i', '--input', metavar='FILE', required=True, help='Vmdk file to process', type=str)

    parser.add_argument('-o', '--output', metavar='FILE', required=True, help='File to store output', type=str)

    parser.add_argument('-block', '--block_size', metavar='SIZE', help='Block size to use', type=int, default=4096, dest="block_size")

    args = parser.parse_args()

    return args