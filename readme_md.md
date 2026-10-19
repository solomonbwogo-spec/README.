# End-to-End Simulation of a Digital Telemetry Communication Pipeline

**Authors:** Makalu Arnold and Bwogo Solomon  
**Project:** Practical 8 Mini-Project — Digital Telemetry Communication Simulation

---

## Executive Summary

This project presents a complete Python-based simulation of an end-to-end digital telemetry communication pipeline. It models every stage of the transmission chain, from analog signal generation to digital modulation, transmission over a noisy channel, demodulation, decoding, and analog reconstruction. 

System performance is evaluated across a sweep of Channel Signal-to-Noise Ratio (SNR) values using **Bit Error Rate (BER)** and **Mean Squared Error (MSE)** metrics, with analysis grounded in **Shannon’s Channel Capacity Theorem**.

---

## Pipeline Architecture

The communication chain consists of the following sequential processing blocks:

$$\text{Analog Source} \longrightarrow \text{Sampler \& Quantizer} \longrightarrow \text{PCM Encoder} \longrightarrow \text{NRZ Line Coder} \longrightarrow \text{BPSK Modulator} \longrightarrow \text{AWGN Channel} \longrightarrow \text{BPSK Demodulator} \longrightarrow \text{PCM Decoder} \longrightarrow \text{Signal Reconstructor}$$

### Block Breakdown

1. **Analog Source:** Generates a continuous sinusoidal message signal $m(t) = \sin(2\pi f_m t)$ at $f_m = 300\text{ Hz}$.
2. **Sampler & Quantizer:** Uniformly samples the signal at $F_s = 8000\text{ Hz}$ and quantizes continuous amplitude levels using $N = 8\text{-bit}$ resolution ($2^8 = 256$ discrete levels).
3. **PCM Encoder:** Converts quantized decimal indices into binary streams via bitwise shifting.
4. **NRZ Line Coder:** Formats binary bits into Non-Return-to-Zero symbol pulses.
5. **BPSK Modulator:** Maps binary bits ($0, 1$) to Binary Phase Shift Keying symbols ($\pm 1$).
6. **AWGN Channel:** Introduces Additive White Gaussian Noise modeled according to target channel SNR levels.
7. **BPSK Demodulator:** Performs threshold decision logic ($r \ge 0 \to 1, r < 0 \to 0$) to recover binary bits.
8. **PCM Decoder:** Reconstructs decimal index values from received bit groups using weight vectors.
9. **Signal Reconstructor:** Maps indices back to continuous voltage approximations to recover $m(t)$.

---

## Key System Parameters & Single-Run Baseline Results

### Configuration Parameters
* **Sampling Frequency ($F_s$):** $8000\text{ Hz}$
* **Message Frequency ($f_m$):** $300\text{ Hz}$
* **Signal Duration:** $0.05\text{ s}$ (400 samples)
* **PCM Resolution ($N$):** $8\text{ bits}$
* **Bit Rate ($R_b$):** $64,000\text{ bit/s}$ ($8000 \times 8$)
* **Default Channel SNR:** $8\text{ dB}$

### Metric Results at $8\text{ dB}$ SNR
| Metric | Simulated Value |
| :--- | :--- |
| **Total PCM Bits Transmitted** | $3200\text{ bits}$ |
| **Bit Errors** | $23$ |
| **Bit Error Rate (BER)** | $0.007188$ |
| **Quantization MSE** | $6.314 \times 10^{-6}$ |
| **Reconstruction MSE** | $0.018601$ |
| **Reconstruction SNR** | $14.294\text{ dB}$ |

---

## Performance Analysis Across Channel SNR Sweep

System performance was tested across a channel SNR sweep ranging from $-2\text{ dB}$ to $20\text{ dB}$:

* **Low SNR Region ($< 6\text{ dB}$):** Severe channel noise causes high BER. Corrupted MSBs (Most Significant Bits) in PCM words cause severe voltage spikes, resulting in high reconstruction MSE.
* **Transition Region ($8\text{ dB}$ to $12\text{ dB}$):** As channel SNR increases, BER drops rapidly, producing a steep drop in reconstruction MSE.
* **High SNR Region ($> 14\text{ dB}$):** Reconstruction MSE flattens out and hits the theoretical **Quantization-only Error Floor** ($\approx 6.31 \times 10^{-6}$). Channel noise becomes negligible, and distortion is purely governed by the $N=8\text{-bit}$ PCM quantization limit.

---

## Theoretical Discussion: Shannon's Capacity Limit

Shannon's Channel Capacity equation defines the upper theoretical bound on error-free bit rate:

$$C = B \log_2 \left(1 + \frac{S}{N}\right)$$

* **Channel Bottleneck:** The system transmits at a fixed source rate of $R_b = 64,000\text{ bit/s}$. When the Channel SNR drops below approximately $4\text{ dB}$, capacity falls below the required bit rate ($C < R_b$), making accurate recovery impossible without error correction.
* **Mitigation Strategy:** Operating below this boundary without Forward Error Correction (FEC) codes—such as Convolutional or LDPC codes—results in catastrophic signal failure.

---

## Prerequisites & Installation

To run this simulation, install the following required dependencies:

```bash
pip install numpy matplotlib
```

---

## Usage

Run the main Python script to execute the simulation, view terminal metrics, and save output visualization plots:

```bash
python main.py
```

Outputs generated in `/output`:
* Printed terminal performance metrics.
* Multi-panel waveform plot covering all 8 stages of transmission.
* Reconstruction MSE vs. Channel SNR curve with quantization floor overlay.