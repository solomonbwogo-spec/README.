import numpy as np


def quantize(x, n_bits=8):
    """
    Uniformly quantizes a continuous signal bounded between [-1.0, 1.0].

    Parameters:
        x (array_like): Input continuous/analog signal array.
        n_bits (int): Bit depth resolution (e.g., 8-bit = 256 quantization levels).

    Returns:
        indices (ndarray): Integer indices corresponding to quantization levels.
        quantized (ndarray): Reconstructed discrete amplitude values.
    """
    levels = 2 ** n_bits
    step = 2.0 / levels

    # Map input signal values into discrete level indices
    indices = np.floor((x + 1.0) / step).astype(int)
    indices = np.clip(indices, 0, levels - 1)

    # Reconstruct amplitude values centered within each quantization step
    quantized = -1.0 + (indices + 0.5) * step

    return indices, quantized


# --- Example Usage ---
if __name__ == "__main__":
    t = np.linspace(0, 1, 10)
    analog_signal = np.sin(2 * np.pi * t)

    indices, quantized_signal = quantize(analog_signal, n_bits=8)
    print("Quantized Indices:", indices)
    print("Quantized Values:", quantized_signal)