import numpy as np


def nrz_encode(bits, samples_per_bit=4):
    """
    Applies Non-Return-to-Zero (NRZ) line coding by extending each bit pulse.

    Parameters:
        bits (array_like): Input array of binary bits (0s and 1s).
        samples_per_bit (int): Number of time samples to represent a single bit duration.

    Returns:
        ndarray: NRZ pulse-coded signal stream.
    """
    return np.repeat(np.asarray(bits, dtype=float), samples_per_bit)


# --- Example Usage ---
if __name__ == "__main__":
    pcm_bits = [1, 0, 1, 1, 0]

    nrz_signal = nrz_encode(pcm_bits, samples_per_bit=4)
    print("PCM Bits:", pcm_bits)
    print("NRZ Encoded Signal:", nrz_signal)