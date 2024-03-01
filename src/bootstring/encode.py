from __future__ import annotations

from collections.abc import Sequence
import bootstring
from bootstring.generalized_variable_length_integers import (
    encode_variable_length_integer,
)


def basic_code_point_segregation(
    raw: str, basic_code_points: Sequence[int], delimeter: str
) -> str:
    """
    Segregate the basic code points from the input string and append a delimeter, if necessary.

    Args:
        raw (str): The input string.
        basic_code_points (Sequence[int]): The basic code points.
        delimeter (str): The delimeter.

    Returns:
        str: The literal portion of the input string, followed by the delimeter, if necessary.
    """

    # RFC3492, section 3.1:
    # All basic code points appearing in the extended string are
    # represented literally at the beginning of the basic string, in their
    # original order, followed by a delimiter if (and only if) the number
    # of basic code points is nonzero.  The delimiter is a particular basic
    # code point, which never appears in the remainder of the basic string.
    # The decoder can therefore find the end of the literal portion (if
    # there is one) by scanning for the last delimiter.
    segregated_string = "".join(
        filter(
            lambda c: ord(c) in basic_code_points,
            raw,
        )
    )
    return segregated_string + (delimeter if segregated_string else "")


def encode(
    raw: str,
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
    Encode a string using the bootstring encoding.

    Args:
        raw (str): The input string.
        basic_code_points (Sequence[int], optional): The basic code points. Defaults to range(0, 128).
        delimeter (str, optional): The delimeter. Defaults to "-".
        base_alphabet (str, optional): The base alphabet. Defaults to "abcdefghijklmnopqrstuvwxyz0123456789".
        tmin (int, optional): The minimum threshold. Defaults to 1.
        tmax (int, optional): The maximum threshold. Defaults to 26.
        skew (int, optional): The skew. Defaults to 38.
        damp (int, optional): The damp. Defaults to 700.
        initial_bias (int, optional): The initial bias. Defaults to 72.
        initial_n (int, optional): The initial n. Defaults to 128.

    Returns:
        str: The encoded string.

    Raises:
        ValueError: If the parameters for the bootstring algorithm are invalid.
    """

    # if the input contains a non-basic code point < n then fail
    if any(ord(c) < initial_n and ord(c) not in basic_code_points for c in raw):
        raise ValueError(
            "The input string contains code points that are not in the basic code points and cannot be encoded."
        )

    encoded = basic_code_point_segregation(raw, basic_code_points, delimeter)
    encoded_count = max(len(encoded) - 1, 0)

    delta = 0
    n = initial_n
    bias = initial_bias
    first_iteration = True

    # We encode the code points in ascending order, so that we can always
    # use a positive delta relative to the previous code point to encode the
    # next code point value. For this, we always aim to encode "the next lowest"
    # code point, starting from n. Then, we simpy advance our "state machine" to
    # the next code point, and repeat the process until we have encoded all code points.
    while encoded_count < len(raw):
        # let m = the minimum {non-basic} code point >= n in the input
        m = ord(
            min(
                filter(
                    lambda c: ord(c) >= n and ord(c) not in basic_code_points,
                    raw,
                ),
            )
        )
        # we need to add "(m - n)" to n to reach the next code point, and
        # the state machine increments n every time it "wraps around", which
        # happens every `encoded_count + 1` iterations, so we need to add
        # `(m - n) * (encoded_count + 1)` to delta.
        delta += (m - n) * (encoded_count + 1)
        n = m
        for c in raw:
            if ord(c) < n or ord(c) in basic_code_points:
                # this code point is already in the "decoded" string (from the perspective of the decoder)
                # so we will need to advance the state machine by one iteration
                delta += 1
            if ord(c) == n:
                # we have reached our target code point
                encoded += encode_variable_length_integer(
                    delta, base_alphabet, bias, tmin, tmax
                )

                encoded_count += 1
                bias = bootstring.adapt_bias(
                    delta,
                    damp if first_iteration else 2,
                    encoded_count,
                    len(base_alphabet),
                    tmin,
                    tmax,
                    skew,
                )
                delta = 0
                first_iteration = False
        delta += 1
        n += 1
    return encoded
