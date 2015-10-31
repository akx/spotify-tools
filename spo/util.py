# -- encoding: UTF-8 --
import unicodedata


def levenshtein(a, b):
    """Calculates the Levenshtein distance between a and b."""
    # Via hetland.org/coding/python/levenshtein.py
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current[j] = min(add, delete, change)

    return current[n]


def flatten(s):
    return unicodedata.normalize("NFKD", s.lower()).encode("ASCII", "ignore")


def flattened_levenshtein(a, b):
    return levenshtein(flatten(a), flatten(b))


def batch(value, count):
    tmp = []
    for item in value:
        if len(tmp) == count:
            yield tmp
            tmp = []
        tmp.append(item)
    if tmp:
        yield tmp
