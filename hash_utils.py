from constants import HASH_LENGTH_MAP


def detect_hash_type(hash_str: str) -> str:
    return HASH_LENGTH_MAP.get(len(hash_str.strip()), "unknown")


def count_brute_candidates(charset: str, min_len: int, max_len: int) -> int:
    n = len(charset)
    return sum(n ** l for l in range(min_len, max_len + 1))


def validate_hash(hash_str: str) -> tuple[bool, str]:
    h = hash_str.strip().lower()
    if not h:
        return False, "Hash-ul nu poate fi gol."
    if not all(c in "0123456789abcdef" for c in h):
        return False, "Hash-ul conține caractere invalide."
    htype = detect_hash_type(h)
    if htype == "unknown":
        return False, f"Lungime nerecunoscută ({len(h)} chars). Suportat: 32/40/64/128."
    return True, htype
