# Credits: https://stackoverflow.com/a/1630350
def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False

def contains(a, pos, b):
    ai = pos
    bi = 0
    if len(b) > len(a) - pos:
        return False
    while bi < len(b):
        if a[ai] != b[bi]:
            return False
        ai += 1
        bi += 1
    return True

def split_safe(s: str, delim: str) -> [str]:
    tokens = []
    i = 0
    last = 0
    inside = 0
    while i < len(s):
        c = s[i]
        if i == len(s)-1:
            tokens.append(s[last:i+1])
        if c == '<' or c == '[' or c == '{' or c == '(':
            inside += 1
            i += 1
            continue
        if c == '>' or c == ']' or c == '}' or c == ')':
            inside -= 1
            i += 1
            continue
        if inside > 0:
            i += 1
            continue
        if contains(s, i, delim):
            tokens.append(s[last:i])
            i += 2
            last = i
        i += 1
    return tokens
