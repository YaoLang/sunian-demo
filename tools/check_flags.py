def ending_for(helped: bool, honest: bool, closer: bool) -> str:
    score = int(helped) + int(honest) + int(closer)
    return "a" if score >= 2 else "b"
