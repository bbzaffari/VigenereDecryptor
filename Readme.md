# Vigenère Cipher Cryptanalysis

This project is a Python-based tool designed to perform cryptanalysis on text encrypted with the **Vigenère cipher**.

*A comprehensive explanation of the methodology can be found in the* [*accompanying IEEE report*](https://github.com/bbzaffari/VigenereDecryptor/blob/main/BrunoBZ_Vigenere.pdf), ***which was structured following the*** [***IEEE publication templates***](https://www.ieee.org/conferences/publishing/templates)

## Description

The code implements techniques to analyze and break the Vigenère cipher, a classical polyalphabetic substitution cipher. To deduce the key length and retrieve the original message, it uses:

- **Kasiski Examination** – to identify repeated sequences and estimate possible key lengths.
- **Index of Coincidence (IC)** – to measure the probability of letter repetition and refine the key length guess.
- **Chi-Square Test (χ²)** – to compare the frequency of letters in decrypted segments with the expected frequency of letters in Portuguese. This helps estimate the most likely key.

A separate file contains the expected frequency distribution of letters in Portuguese, which serves as the statistical basis for the chi-square comparison.

## Requirements

- Python 3.x

## How to Run

1. Open a terminal.
2. Navigate to the folder containing both the Python scripts and the encrypted text file (`ciphertext.txt`, or equivalent).
3. Run the program using:

   ```bash
   python VigenereDecipher.py
