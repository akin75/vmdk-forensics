import os
import time
from datetime import datetime
import numpy as np
from utils import calculate_chi2, argparse, calculate_shannon_entropy, check_block_size_for_chi2
import sys
import matplotlib.pyplot as plt
from tqdm import tqdm

# Function to process a binary file in blocks and analyze each block
def processing_section(file_input, block_size, file_output, entropy_values, block_offsets):
    file_size = os.path.getsize(file_input)  # Get total file size
    bytes_read = 0  # Initialize the counter for how many bytes have been read

    # Open the input file for reading and output file for writing
    with open(file_input, "rb") as file, open(file_output, "wb") as output_file:
        # Create a progress bar for the file processing
        with tqdm(total=file_size, unit='B', unit_scale=True, desc="Processing") as progress:
            while True:
                # Determine how many bytes to read in this iteration
                remaining_bytes = file_size - bytes_read
                current_block_size = min(block_size, remaining_bytes)

                # Read the current block
                block = file.read(current_block_size)
                if not block:
                    break  # Exit if there's nothing left to read

                # ----------- Start of Analysis -----------
                # Convert block to numpy array and calculate entropy
                block_entropy = calculate_shannon_entropy(np.frombuffer(block, dtype=np.uint8))
                # Run chi-squared test to check randomness
                chi2_statistic, p_value = check_block_size_for_chi2(block)

                # Store entropy and the offset (position in file)
                entropy_values.append(block_entropy)
                block_offsets.append(bytes_read)

                # Decide whether to write the block to output file based on entropy and chi2 p-value
                if block_entropy > 7.9:
                    if 0.05 < p_value < 0.95:
                        pass  # Likely random data – skip writing (or handle differently if needed)
                    else:
                        output_file.write(block)  # Possibly non-random – write block
                else:
                    output_file.write(block)  # Low entropy – write block
                # ----------- End of Analysis -----------

                bytes_read += current_block_size  # Update how many bytes were read
                progress.update(current_block_size)  # Update progress bar

    print("[Done] Processing finished.\n")

# Function to plot entropy values against their position in the file
def plot_entropy(block_offsets, entropy_values):
    plt.figure(figsize=(10, 5))

    block_offsets = np.array(block_offsets)
    entropy_values = np.array(entropy_values)

    # Plot entropy over file offsets
    plt.plot(block_offsets, entropy_values, linestyle='-', color='b', label='Entropie')

    plt.xlabel("File Offset (in Bytes)")
    plt.ylabel("Entropy")
    plt.title("Entropy Trend Across File")
    plt.grid(True)
    plt.xticks(np.linspace(block_offsets.min(), block_offsets.max(), 3))
    plt.legend()
    plt.savefig("Entropy-plot.png")  # Save plot as PNG image

# Main entry point
if __name__ == '__main__':
    args = argparse()  # Parse command line arguments
    file_input = args.input # Input file
    file_output = args.output # Output file
    block_size = args.block_size  # The number of bytes to read and process at a time from the input file

    start = datetime.now()  # Start timing

    entropy_values = []  # List to store entropy values per block
    block_offsets = []   # List to store offset of each block

    # Process the file and analyze block-wise entropy
    processing_section(file_input, block_size, file_output, entropy_values, block_offsets)

    # Create a plot from the entropy data
    plot_entropy(block_offsets, entropy_values)

    # Print total processing time
    sys.stdout.write(f"Time taken: {(datetime.now() - start).total_seconds():.2f} seconds\n")
