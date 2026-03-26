import itertools
import math
import os
import queue
import threading
import time
from datetime import timedelta

from constants import HASH_FUNCS
from hash_utils import count_brute_candidates


class CrackEngine:
    def __init__(self, target_hash: str, hash_type: str, callback=None):
        self.target = target_hash.strip().lower()
        self.hash_fn = HASH_FUNCS[hash_type]
        self.callback = callback
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self.attempts = 0
        self.start_time = None
        self.result = None

    def stop(self):
        self._stop.set()

    def is_running(self) -> bool:
        return not self._stop.is_set()

    def _emit(self, event, data=None):
        if self.callback:
            self.callback(event, data)

    def _check(self, word: str) -> bool:
        with self._lock:
            self.attempts += 1
        if self.hash_fn(word) == self.target:
            self.result = word
            self._emit("found", word)
            self.stop()
            return True
        return False

    def _stats_ticker(self, total: int):
        prev = 0
        while not self._stop.is_set():
            time.sleep(0.5)
            cur = self.attempts
            elapsed = time.time() - self.start_time
            speed = (cur - prev) * 2
            prev = cur
            pct = (cur / total * 100) if total else 0
            remaining = ((total - cur) / speed) if speed > 0 else float("inf")
            eta = str(timedelta(seconds=int(remaining))) if math.isfinite(remaining) else "∞"
            self._emit("stats", {
                "attempts": cur,
                "speed": speed,
                "elapsed": elapsed,
                "pct": pct,
                "eta": eta,
                "total": total,
            })

    def dictionary_attack(self, wordlist_path: str, threads: int = 4):
        if not os.path.exists(wordlist_path):
            self._emit("error", f"Wordlist negăsit: {wordlist_path}")
            return

        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]

        total = len(words) * 6
        self.start_time = time.time()
        self._emit("start", {"mode": "dictionary", "total": total})
        threading.Thread(target=self._stats_ticker, args=(total,), daemon=True).start()

        chunk_size = math.ceil(len(words) / threads)

        def worker(chunk):
            for word in chunk:
                if self._stop.is_set():
                    return
                for candidate in [word, word.capitalize(), word.upper(), word + "1", word + "123", word + "!"]:
                    if self._stop.is_set():
                        return
                    self._check(candidate)

        ts = [threading.Thread(target=worker, args=(words[i * chunk_size:(i + 1) * chunk_size],), daemon=True)
              for i in range(threads)]
        for t in ts: t.start()
        for t in ts: t.join()

        self._emit("done", self.result)

    def brute_force(self, charset: str, min_len: int, max_len: int, threads: int = 4):
        total = count_brute_candidates(charset, min_len, max_len)
        self.start_time = time.time()
        self._emit("start", {"mode": "brute-force", "total": total})
        threading.Thread(target=self._stats_ticker, args=(total,), daemon=True).start()

        wq = queue.Queue(maxsize=threads * 2000)

        def producer():
            for length in range(min_len, max_len + 1):
                for combo in itertools.product(charset, repeat=length):
                    if self._stop.is_set():
                        for _ in range(threads): wq.put(None)
                        return
                    wq.put("".join(combo))
            for _ in range(threads): wq.put(None)

        def consumer():
            while not self._stop.is_set():
                try:
                    word = wq.get(timeout=0.2)
                except queue.Empty:
                    continue
                if word is None:
                    return
                self._check(word)

        p = threading.Thread(target=producer, daemon=True)
        p.start()
        cs = [threading.Thread(target=consumer, daemon=True) for _ in range(threads)]
        for c in cs: c.start()
        p.join()
        for c in cs: c.join()

        self._emit("done", self.result)

    def combo_attack(self, wordlist_path: str, charset: str, suffix_max_len: int = 2, threads: int = 4):
        if not os.path.exists(wordlist_path):
            self._emit("error", f"Wordlist negăsit: {wordlist_path}")
            return

        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]

        suffixes = ["".join(c) for l in range(1, suffix_max_len + 1)
                    for c in itertools.product(charset, repeat=l)]

        total = len(words) * len(suffixes) * 2
        self.start_time = time.time()
        self._emit("start", {"mode": "combo", "total": total})
        threading.Thread(target=self._stats_ticker, args=(total,), daemon=True).start()

        wq = queue.Queue(maxsize=50_000)

        def producer():
            for word in words:
                for suffix in suffixes:
                    if self._stop.is_set():
                        for _ in range(threads): wq.put(None)
                        return
                    wq.put(word + suffix)
                    wq.put(suffix + word)
            for _ in range(threads): wq.put(None)

        def consumer():
            while not self._stop.is_set():
                try:
                    word = wq.get(timeout=0.2)
                except queue.Empty:
                    continue
                if word is None:
                    return
                self._check(word)

        p = threading.Thread(target=producer, daemon=True)
        p.start()
        cs = [threading.Thread(target=consumer, daemon=True) for _ in range(threads)]
        for c in cs: c.start()
        p.join()
        for c in cs: c.join()

        self._emit("done", self.result)
