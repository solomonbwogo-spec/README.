import numpy as np


def bpsk_modulate(bits):
    """
    Performs Binary Phase Shift Keying (BPSK) modulation.
    Maps binary bit values {0, 1} to bipolar phase symbols {-1.0, +1.0}.

    Parameters:
        bits (array_like): Input array of binary bits (0s and 1s).

    Returns:
        ndarray: Transmitted BPSK symbol array.
    """
    return 2.0 * np.asarray(bits, dtype=float) - 1.0


# --- Example Usage ---
if __name__ == "__main__":
    pcm_bits = [0, 1, 1, 0, 1]

    tx_symbols = bpsk_modulate(pcm_bits)
    print("PCM Bits:", pcm_bits)
    print("BPSK Modulated Symbols:", tx_symbols)