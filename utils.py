from argparse import ArgumentParser
from itertools import islice
from typing import Generator
from scipy.stats import entropy
import numpy as np

def calculate_entropy(byte_data):
    """Berechnet die Shannon-Entropie einer Byte-Verteilung."""
    byte_counts = np.bincount(byte_data, minlength=256)  # Häufigkeiten der Byte-Werte (0–255)
    probabilities = byte_counts / len(byte_data)        # Normierung zu Wahrscheinlichkeiten
    probabilities = probabilities[probabilities > 0]   # Null-Wahrscheinlichkeiten entfernen
    return entropy(probabilities, base=2)       # Shannon-Entropie (Basis 2)



def give_block_at_specified_pos(gen: Generator, pos: int):
    element = next(islice(gen, pos, pos + 1), None)
    if element is None:
        print("Pos does not exist")
    return element

def argparse():
    parser = ArgumentParser(description="Detect intermittent encryption and extract unencrypted blocks")