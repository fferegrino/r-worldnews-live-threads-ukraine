import hashlib


def hash_string(w):
    h = hashlib.md5(w.encode("utf-8"))
    return h.hexdigest()[:7]
