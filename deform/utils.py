"""Utils."""


def text_(s, encoding="latin-1", errors="strict"):
    """If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return s  # pragma: no cover


def bytes_(s, encoding="latin-1", errors="strict"):
    """If ``s`` is an instance of ``text_type``, return
    ``s.encode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, str):  # pragma: no cover
        return s.encode(encoding, errors)
    return s  # pragma: no cover
