from __future__ import annotations

from .encode import encode
from .decode import decode


def adapt_bias(
    delta: int, scalar: int, length: int, base: int, tmin: int, tmax: int, skew: int
) -> int:
    # After each delta is encoded or decoded, bias is set for the next
    # delta as follows:
    #
    # 1. Delta is scaled in order to avoid overflow in the next step:
    delta = delta // scalar

    # 2. Delta is increased to compensate for the fact that the next delta
    #    will be inserting into a longer string:
    delta += delta // length

    # 3. Delta is repeatedly divided until it falls within a threshold, to
    #    predict the minimum number of digits needed to represent the next
    number_of_divisions = 0
    while delta > ((base - tmin) * tmax) // 2:
        delta //= base - tmin
        number_of_divisions += 1

    # 4. The bias is set:
    bias = (base * number_of_divisions) + (
        ((base - tmin + 1) * delta) // (delta + skew)
    )

    return bias
