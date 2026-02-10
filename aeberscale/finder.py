#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Estimate jazz scale using a modified version of the Krumhansl-Schmuckler algorithm, using the scales defined in the
Jamey Aebersold scale syllabus.

The process is as follows:

- Collect all notes in FULL piano roll of past 10 seconds
    - Gives distribution: weight by sum of all durations
    - E.g., note E held for 5 seconds across all onsets, so Y axis is 5 for E
- Binary scale distribution of JA scales: 0 if not in scale, 1 if in scale
- Transpose this histogram 12 times
 - Get a vector each time, correlate with actual distribution (unscaled)
- Choose maximum correlation coefficient FOR EACH scale
- Choose maximum coefficient OVER ALL scales
"""

import math
from typing import List, Optional, Type, Union

from aeberscale.syllabus import SCALE_SYLLABUS, Scale
from aeberscale.utils import NOTE_NAMES, NOTE_NUMBERS


def pearsonr(x: List[Union[float, int]], y: List[Union[float, int]]) -> Optional[float]:
    """
    Calculate Pearson Correlation Coefficient from two lists of values
    """
    if not len(x) == len(y):
        raise ValueError("Lengths of X and Y are not equal")
    if len(x) < 2:
        raise ValueError("Need at least two values to compute correlation")

    # no need to check len(y) < 2, implicit in the above
    avg_x = float(sum(x)) / len(x)
    avg_y = float(sum(y)) / len(y)

    # instantiate all variables
    xdiff2, ydiff2, diffprod = 0, 0, 0

    for idx in range(len(x)):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff * ydiff
        xdiff2 += xdiff * xdiff
        ydiff2 += ydiff * ydiff

    # catch potential division by zero errors in case of zero variance
    if xdiff2 == 0 or ydiff2 == 0:
        return None

    return diffprod / math.sqrt(xdiff2 * ydiff2)


def find_scale(notes: List[Union[str, int]], durations: List[float]) -> Type[Scale]:
    if len(notes) == 0 or len(durations) == 0:
        raise ValueError("Cannot find scale for passage with zero notes!")

    elif len(notes) != len(durations):
        raise ValueError(
            f"Must have exactly one duration for each note "
            f"(got {len(notes)} notes, {len(durations)} durations)."
        )

    if not all(isinstance(n, (str, int)) for n in notes):
        raise TypeError("Notes must be either strings or integers")

    # String inputs: need to coerce to numbers
    elif all(isinstance(n, str) for n in notes):
        notes = [NOTE_NAMES[n.title()] for n in notes]

    # Apply modulo operator to all note numbers
    notes_mod = [n % 12 for n in notes]

    # Sum durations for all notes to get distribution for current passage
    res = {i: 0 for i in range(12)}
    for n, d in zip(notes_mod, durations):
        res[n] += d
    current_dist = list(res.values())

    all_scale_res = []
    for scale in SCALE_SYLLABUS:
        scale_res = []

        for root_note in NOTE_NUMBERS.values():
            # create the scale and grab its binary note distribution
            scale_inst = scale(root=root_note)
            bin_dist = scale_inst.binary_distribution

            # compute the correlation with the current results
            corr_out = pearsonr(bin_dist, current_dist)

            # set as attribute
            setattr(scale_inst, "corr", corr_out)
            scale_res.append(scale_inst)

        # store the maximum correlation for this scale type
        all_scale_res.append(max(scale_res, key=lambda x: x.corr))

    # get the overall best match and return the Scale instance
    return max(all_scale_res, key=lambda x: x.corr)
