from __future__ import annotations

from collections.abc import Sequence
import bootstring
from bootstring.generalized_variable_length_integers import (
    decode_variable_length_integer,
)


def split_literal_portion_and_deltas_string(
    encoded: str, delimeter: str = "-"
) -> tuple[str, str]:
    """
    Split an encoded string into its literal portion and its deltas string.

    Args:
        encoded (str): The encoded string.

    Returns:
        tuple[str, str]: The literal portion and the deltas string.
    """

    # RFC3492, section 3.1:
    # The delimiter is a particular basic
    # code point, which never appears in the remainder of the basic string.
    # The decoder can therefore find the end of the literal portion (if
    # there is one) by scanning for the last delimiter.
    if delimeter in encoded:
        delim_index = encoded.rindex(delimeter)  # The last instance of the delimeter.
        literal_portion = encoded[
            :delim_index
        ]  # Up to but not including the delimeter.
        deltas_string = encoded[delim_index + 1 :]  # After the delimeter.
        return literal_portion, deltas_string
    return "", encoded  # No delimeter, so the entire string is the deltas string.


def decode(
    encoded: str,
    basic_code_points: Sequence[int] = range(0, 128),
    delimeter: str = "-",
    base_alphabet: str = "abcdefghijklmnopqrstuvwxyz0123456789",
    tmin: int = 1,
    tmax: int = 26,
    skew: int = 38,
    damp: int = 700,
    initial_bias: int = 72,
    initial_n: int = 128,
) -> str:
    """
    Decode a bootstring encoded string.

    Args:
        encoded (str): The encoded string.
        delimeter (str, optional): The delimeter. Defaults to "-".
        base_alphabet (str, optional): The base alphabet. Defaults to "abcdefghijklmnopqrstuvwxyz0123456789".
        tmin (int, optional): The minimum threshold. Defaults to 1.
        tmax (int, optional): The maximum threshold. Defaults to 26.
        skew (int, optional): The skew. Defaults to 38.
        damp (int, optional): The damp. Defaults to 700.
        initial_bias (int, optional): The initial bias. Defaults to 72.
        initial_n (int, optional): The initial n. Defaults to 128.

    Returns:
        str: The decoded string.

    Raises:
        ValueError: If the encoded string is invalid.
    """

    literal, deltas_string = split_literal_portion_and_deltas_string(encoded, delimeter)

    if any(ord(c) not in basic_code_points for c in literal):
        raise ValueError(
            "Invalid bootstring. Literal portion contains non-basic code points."
        )

    extended_string = literal  # Start off with the literal portion.
    bias = initial_bias

    n, i = initial_n, 0
    first_iteration = True
    while deltas_string:
        # Read the next integer from the deltas string.
        delta, deltas_string = decode_variable_length_integer(
            deltas_string, base_alphabet, bias, tmin, tmax
        )

        # Advance `delta` steps in the state machine where
        # <n, i> => <n, i + 1> if i + 1 < len(extended_string)
        # <n, i> => <n + 1, 0> if i + 1 >= len(extended_string)

        # We must advance one more step in the state machine if we
        # are not in the first iteration to complete the last
        # iteration's work.
        steps = delta + (0 if first_iteration else 1)
        n += (i + steps) // (len(extended_string) + 1)
        i = (i + steps) % (len(extended_string) + 1)

        code_point = chr(n)
        if code_point in basic_code_points:
            raise ValueError("Invalid bootstring. Basic code point in extended string.")

        # Insert the code point into the extended string at position `i`.
        extended_string = extended_string[:i] + code_point + extended_string[i:]

        bias = bootstring.adapt_bias(
            delta,
            damp if first_iteration else 2,
            len(extended_string),
            len(base_alphabet),
            tmin,
            tmax,
            skew,
        )

        first_iteration = False
    return extended_string
