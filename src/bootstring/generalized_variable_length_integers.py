def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


def threshold(j, bias, base, tmin, tmax):
    return clamp(base * (j + 1) - bias, tmin, tmax)


def decode_variable_length_integer(
    encoded_integers: str,
    base_alphabet: str,
    bias: int,
    tmin: int,
    tmax: int,
) -> tuple[int, str]:
    """
    Read the next integer from a concatenated string of variable length integers.

    Args:
        encoded_integers (str): The string of concatenated variable length integers.
        base_alphabet (str): The base alphabet.
        bias (int): The bias.
        tmin (int): The minimum threshold.
        tmax (int): The maximum threshold.

    Returns:
        tuple[int, str]: The decoded integer and the remaining string.
    """

    # RFC 3492, section 3.3:
    # Decoding this representation is very
    # similar to decoding a conventional integer:  Start with a current
    # value of N = 0 and a weight w = 1.  Fetch the next digit d and
    # increase N by d * w.  If d is less than the current threshold (t)
    # then stop, otherwise increase w by a factor of (base - t), update t
    # for the next position, and repeat.
    j = 0
    w = 1
    delta = 0
    while True:
        next_digit = encoded_integers[j]
        d = base_alphabet.index(next_digit)
        delta += d * w
        t = threshold(j, bias, len(base_alphabet), tmin, tmax)
        if d < t:
            break
        w *= len(base_alphabet) - t
        j += 1
    return delta, encoded_integers[j + 1 :]


def encode_variable_length_integer(
    value: int,
    base_alphabet: str,
    bias: int,
    tmin: int,
    tmax: int,
) -> str:
    """
    Encode an integer as a variable length integer.

    Args:
        delta (int): The integer to encode.
        base_alphabet (str): The base alphabet.
        tmin (int): The minimum threshold.
        tmax (int): The maximum threshold.
        skew (int): The skew.
        damp (int): The damp.

    Returns:
        str: The encoded integer.
    """

    # RFC 3492, section 3.3:
    # Encoding this representation is similar to encoding a conventional
    # integer:  If N < t then output one digit for N and stop, otherwise
    # output the digit for t + ((N - t) mod (base - t)), then replace N
    # with (N - t) div (base - t), update t for the next position, and
    # repeat.

    base = len(base_alphabet)
    encoded = ""
    while True:
        t = threshold(len(encoded), bias, base, tmin, tmax)
        if value < t:
            encoded += base_alphabet[value]
            break
        encoded += base_alphabet[t + ((value - t) % (base - t))]
        value = (value - t) // (base - t)
    return encoded
