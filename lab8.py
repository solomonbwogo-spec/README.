from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

# 1. SIMULATION PARAMETERS
FS = 8000
FM = 300
DURATION = 0.05
N_BITS = 8
CHANNEL_SNR_DB = 8
SNR_SWEEP_DB = np.arange(-2, 21, 2)
SEED = 7

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)


# 2. QUANTIZATION
def quantize(x, n_bits=8):
    levels = 2 ** n_bits
    step = 2.0 / levels

    indices = np.floor((x + 1.0) / step).astype(int)
    indices = np.clip(indices, 0, levels - 1)

    quantized = -1.0 + (indices + 0.5) * step
    return indices, quantized


# 3. PCM ENCODING: DECIMAL TO BINARY
def encode_pcm(indices, n_bits=8):
    shifts = np.arange(n_bits - 1, -1, -1)
    return (
        (indices[:, None] >> shifts) & 1
    ).astype(np.uint8).ravel()


# 4. PCM DECODING: BINARY TO DECIMAL
def decode_pcm(bits, n_bits=8):
    groups = np.asarray(bits).reshape(-1, n_bits)
    weights = 2 ** np.arange(n_bits - 1, -1, -1)
    return groups @ weights


# 5. NRZ LINE CODING
def nrz_encode(bits):
    return np.repeat(np.asarray(bits, dtype=float), 4)


# 6. BPSK MODULATION
def bpsk_modulate(bits):
    return 2.0 * np.asarray(bits, dtype=float) - 1.0


# 7. AWGN CHANNEL
def awgn(signal, snr_db, rng):
    power = np.mean(signal ** 2)
    noise_power = power / (10 ** (snr_db / 10))

    noise = rng.normal(
        0, np.sqrt(noise_power), size=signal.shape
    )
    return signal + noise


# 8. BPSK DEMODULATION
def bpsk_demodulate(received):
    return (received >= 0).astype(np.uint8)


# 9. MEAN SQUARED ERROR
def mse(original, reconstructed):
    return float(np.mean((original - reconstructed) ** 2))


def main():
    rng = np.random.default_rng(SEED)

    # STEP 1: Generate the message signal
    t = np.arange(0, DURATION, 1 / FS)
    message = np.sin(2 * np.pi * FM * t)

    # STEP 2: Sample and quantize
    sampled = message.copy()
    indices, quantized = quantize(sampled, N_BITS)

    # STEP 3: Convert quantized samples into PCM bits
    bits = encode_pcm(indices, N_BITS)

    # STEP 4: NRZ line coding
    nrz = nrz_encode(bits)

    # STEP 5: BPSK modulation
    tx = bpsk_modulate(bits)

    # STEP 6: Transmit through AWGN channel
    rx = awgn(tx, CHANNEL_SNR_DB, rng)

    # STEP 7: Demodulate received symbols
    received_bits = bpsk_demodulate(rx)

    # STEP 8: Decode PCM bits
    decoded_indices = decode_pcm(received_bits, N_BITS)

    # STEP 9: Reconstruct the message
    step = 2.0 / (2 ** N_BITS)
    reconstructed = -1.0 + (decoded_indices + 0.5) * step

    # STEP 10: Calculate performance
    bit_errors = np.sum(bits != received_bits)
    ber = bit_errors / len(bits)

    quantization_mse = mse(message, quantized)
    reconstruction_mse = mse(message, reconstructed)

    reconstruction_snr = 10 * np.log10(
        np.mean(message ** 2) / max(reconstruction_mse, 1e-15)
    )

    # STEP 11: Plot all main stages
    fig, ax = plt.subplots(4, 2, figsize=(13, 13))
    ax = ax.ravel()

    ax[0].plot(t, message)
    ax[0].set_title("Original message")

    ax[1].stem(t, sampled, basefmt=" ")
    ax[1].set_title("Sampled signal")

    ax[2].step(t, quantized, where="mid")
    ax[2].set_title("Quantized signal")

    ax[3].step(np.arange(64), bits[:64], where="post")
    ax[3].set_title("First 64 PCM bits")

    ax[4].plot(nrz[:128], drawstyle="steps-post")
    ax[4].set_title("NRZ line coding")

    ax[5].stem(np.arange(64), tx[:64], basefmt=" ")
    ax[5].set_title("Transmitted BPSK symbols")

    ax[6].stem(np.arange(64), rx[:64], basefmt=" ")
    ax[6].set_title("Received BPSK symbols")

    ax[7].plot(t, message, label="Original")
    ax[7].plot(t, reconstructed, "--", label="Reconstructed")
    ax[7].set_title("Original vs reconstructed")
    ax[7].legend()

    for a in ax:
        a.grid(True, alpha=0.3)
        a.set_xlabel("Time / sample index")

    fig.tight_layout()
    fig.savefig(OUT / "communication_chain_stages.png", dpi=160)
    plt.close(fig)

    # STEP 12: Investigate different channel SNR values
    results = []

    for snr_db in SNR_SWEEP_DB:
        test_rng = np.random.default_rng(SEED + int(snr_db) + 100)

        noisy = awgn(tx, float(snr_db), test_rng)
        detected_bits = bpsk_demodulate(noisy)
        decoded = decode_pcm(detected_bits, N_BITS)

        recovered = -1.0 + (decoded + 0.5) * step

        results.append({
            "SNR_dB": float(snr_db),
            "BER": float(np.mean(bits != detected_bits)),
            "MSE": mse(message, recovered)
        })

    # Plot SNR against reconstruction MSE
    plt.figure(figsize=(8, 5))

    plt.semilogy(
        [r["SNR_dB"] for r in results],
        [max(r["MSE"], 1e-12) for r in results],
        "o-", label="Reconstruction MSE"
    )

    plt.axhline(
        quantization_mse, linestyle="--",
        label="Quantization-only MSE"
    )

    plt.xlabel("Channel SNR (dB)")
    plt.ylabel("Mean squared error")
    plt.title("Channel SNR versus reconstruction MSE")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "snr_vs_reconstruction_mse.png", dpi=160)
    plt.close()

    # Save numerical SNR sweep results
    with open(OUT / "snr_sweep.csv", "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["SNR_dB", "BER", "MSE"]
        )
        writer.writeheader()
        writer.writerows(results)

    # Display final results
    print("\n--- SIMULATION RESULTS ---")
    print("Sampling frequency:", FS, "Hz")
    print("Message frequency:", FM, "Hz")
    print("Number of samples:", len(message))
    print("PCM bits:", len(bits))
    print("PCM bit rate:", FS * N_BITS, "bit/s")
    print("Channel SNR:", CHANNEL_SNR_DB, "dB")
    print("Bit errors:", int(bit_errors))
    print("BER:", round(ber, 6))
    print("Quantization MSE:", quantization_mse)
    print("Reconstruction MSE:", reconstruction_mse)
    print("Reconstruction SNR:", round(reconstruction_snr, 3), "dB")
    print("Plots and CSV saved in:", OUT)


if __name__ == "__main__":
    main()