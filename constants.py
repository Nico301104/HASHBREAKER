import hashlib
import string

CHARSETS = {
    "digits":       string.digits,
    "lowercase":    string.ascii_lowercase,
    "uppercase":    string.ascii_uppercase,
    "letters":      string.ascii_letters,
    "alphanumeric": string.ascii_letters + string.digits,
    "printable":    string.printable.strip(),
}

HASH_FUNCS = {
    "md5":    lambda s: hashlib.md5(s.encode()).hexdigest(),
    "sha1":   lambda s: hashlib.sha1(s.encode()).hexdigest(),
    "sha256": lambda s: hashlib.sha256(s.encode()).hexdigest(),
    "sha512": lambda s: hashlib.sha512(s.encode()).hexdigest(),
}

HASH_LENGTH_MAP = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}

ATTACK_MODES = ["dictionary", "brute-force", "combo"]
