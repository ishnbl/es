"""Population statistics for the validated, nonempty numeric lists in this app."""

from __future__ import division

import math


def mean(values):
    return math.fsum(values) / len(values)


def median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def pvariance(values):
    average = mean(values)
    return math.fsum((value - average) ** 2 for value in values) / len(values)


def pstdev(values):
    return math.sqrt(pvariance(values))
