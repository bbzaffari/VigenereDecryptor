from collections import defaultdict, Counter
import math
from pathlib import Path
from typing import Dict, List, Tuple, Sequence, Any, Iterable
import string
import time

def load_ciphertext(path: str) -> str:
    text = Path(path).read_text(encoding='ascii')
    # 1) Keep only alphabetic characters
    filtered = (c for c in text if c.isalpha())
    # 2) Convert everything to uppercase
    return ''.join(filtered).upper()

def extract_ngram_positions(text: str, n: int = 3, threshold: int = 2) -> Dict[str, List[int]]:
    """
    Maps each repeated n-gram to its list of positions (sliding window),
    filtering only those with more than 'threshold' occurrences.
    """
    positions: Dict[str, List[int]] = defaultdict(list)
    for i in range(len(text) - n + 1):
        ngram = text[i:i+n]
        positions[ngram].append(i)
    return {ng: pos for ng, pos in positions.items() if len(pos) >= threshold}

def compute_pairwise_distances(positions: Dict[str, List[int]]) -> Dict[str, List[int]]:
    """
    For each repeated n-gram, compute all pairwise distances between its positions.
    """
    distances: Dict[str, List[int]] = defaultdict(list)
    for ng, pos_list in positions.items():
        for i in range(len(pos_list) - 1):
            for j in range(i+1, len(pos_list)):
                distances[ng].append(pos_list[j] - pos_list[i])
    return distances

def get_divisors(n: int) -> List[int]:
    """
    Returns all divisors of n (>=2), including n itself.
    """
    divs = set()
    limit = int(math.isqrt(n))
    for i in range(2, limit+1):
        if n % i == 0:
            divs.add(i)
            divs.add(n // i)
    divs.add(n)
    return sorted(divs)

def kasiski_test(text: str, n: int = 3, top_k: int = 10, threshold: int = 2) -> List[Tuple[int, int]]:
    positions = extract_ngram_positions(text, n, threshold) 
    distances = compute_pairwise_distances(positions)

    list_a = []

    for ng, dist in distances.items():
        factor_list = []
        for d in dist:
            factor_list.extend(get_divisors(d))
        top_divisors = Counter(factor_list).most_common(top_k)
        for key, _ in top_divisors:
            list_a.append(key)

    counter_b = Counter(list_a)
    top = counter_b.most_common(top_k)
    print(f"Top {top_k} most frequent key lengths for n-gram size {n}:")
    for i, (length, count) in enumerate(top, start=1):
        print(f"{i}. Key length {length}: {count} occurrences")
    return top

def list_to_dict(pairs: Sequence[Tuple[Any, Any]]) -> Dict[Any, Any]:
    """
    Converts a sequence of (key, value) pairs into a dictionary.
    If keys are duplicated, the last one overwrites the others.
    """
    return dict(pairs)

def sum_dicts(dicts: Iterable[Dict[int, int]]) -> Dict[int, int]:
    """
    Given a list of {key: numeric_value} dicts, sums values by key.
    """
    result: Dict[int, int] = {}
    for d in dicts:
        for key, freq in d.items():
            result[key] = result.get(key, 0) + freq
    return result

def index_of_coincidence(text: str) -> float:
    """
    Computes the Index of Coincidence (IC) of a given A–Z text.
    IC = [∑ f_i (f_i – 1)] / [N (N – 1)], where f_i is the frequency of letter i,
    and N is the total length of the text.
    """
    N = len(text)
    if N <= 1:
        return 0.0
    freq = Counter(text)
    numerator = sum(f * (f - 1) for f in freq.values())
    return numerator / (N * (N - 1))

def average_ic_for_key_length(text: str, key_length: int) -> float:
    """
    Splits the text into `key_length` groups and computes the average IC.
    Each group contains every k-th character starting from a different offset.
    """
    groups = group(text, key_length)
    ics = [index_of_coincidence(g) for g in groups]
    return sum(ics) / key_length

def group(text: str, key_length: int) -> List[str]:
    return [''.join(text[i::key_length]) for i in range(key_length)]

freq_pt = {
    'A':14.7154, 'B':0.9926, 'C':3.8775, 'D':4.7958, 'E':12.7879,
    'F':0.9868, 'G':1.1435, 'H':1.4840, 'I':6.1426, 'J':0.2787,
    'K':0.0044, 'L':3.3069, 'M':4.8531, 'N':4.7498, 'O':10.5498,
    'P':2.6743, 'Q':1.2897, 'R':6.3127, 'S':7.5612, 'T':4.2199,
    'U':4.7630, 'V':1.6736, 'W':0.0011, 'X':0.2845, 'Y':0.0686,
    'Z':0.4824
}

def chi_squared(obs_counts, total_len, shift):
    """
    Computes the chi-squared statistic for a given Caesar shift in a group.
    """
    χ2 = 0.0
    for L, E_perc in freq_pt.items():
        shifted_letter = chr(((ord(L) - ord('A') + shift) % 26) + ord('A'))
        observed = obs_counts.get(shifted_letter, 0)
        O = observed / total_len * 100
        χ2 += (O - E_perc) ** 2 / (E_perc or 1)
    return χ2

def decrypt_vigenere(text: str, key: str) -> str:
    result = []
    ki = 0
    for c in text:
        if 'A' <= c <= 'Z':
            shift = ord(key[ki % len(key)]) - ord('A')
            dec = (ord(c) - ord('A') - shift) % 26 + ord('A')
            result.append(chr(dec))
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

#=========================================================================================
if __name__ == "__main__":
    start = time.perf_counter()

    text = load_ciphertext('cipher.txt')
    top = 3
    tests = [(3, 6), (4, 5), (5, 3), (6, 2), (7, 2)]  # (n-gram size, min occurrences)

    print("\nKasiski Test")
    list_dicts: List[Dict[int, int]] = []
    for n, threshold in tests:
        result = kasiski_test(text, n=n, top_k=top, threshold=threshold)
        d = list_to_dict(result)
        list_dicts.append(d)
        print("=" * 6)

    sums = sum_dicts(list_dicts)
    count = Counter(sums)

    print("Most likely key lengths (higher frequency → more probable):")
    possible_keys_length = []
    i = 1
    for length, freq in count.most_common(3):
        if length > 2:
            possible_keys_length.append(length)
            print(f"{i}. Key length {length}: {freq} occurrences")
            i += 1

    print("\nIndex of Coincidence")
    greatest = (0, 0)
    for k in possible_keys_length:
        ic_avg = average_ic_for_key_length(text, k)
        print(f"Avg. IC for key length {k}: {ic_avg:.4f}")
        if ic_avg > greatest[1]:
            greatest = (k, ic_avg)
    print(f"Most probable key length: {greatest[0]}")
    print("-" * 6)

    key = []
    for i in range(greatest[0]):
        group_i = text[i::greatest[0]]
        counts = Counter(group_i)
        n = len(group_i)

        best_k, best_score = 0, float('inf')
        for k in range(26):
            score = chi_squared(counts, n, k)
            if score < best_score:
                best_k, best_score = k, score
        key.append(chr(best_k + ord('A')))

    estimated_key = ''.join(key)
    print("Estimated key:", estimated_key)
    
    end = time.perf_counter()
    print(f"\n⏱ Total execution time: {end - start:.4f} seconds\n")
    print(decrypt_vigenere(text[:500], estimated_key))
