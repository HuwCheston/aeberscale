#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for scales inside aeberscale/finder.py
"""


import pytest

from aeberscale.finder import find_scale, pearsonr


@pytest.mark.parametrize(
    "x,y,expected_error,error_message",
    [
        ([1, 2, 3], [1, 2], ValueError, "Lengths of X and Y are not equal"),
        ([1], [1], ValueError, "Need at least two values to compute correlation"),
        ([], [], ValueError, "Need at least two values to compute correlation"),
        ([1, 2, 3, 4], [1, 2], ValueError, "Lengths of X and Y are not equal"),
    ],
)
def test_pearsonr_raises_errors(x, y, expected_error, error_message):
    with pytest.raises(expected_error, match=error_message):
        pearsonr(x, y)


@pytest.mark.parametrize(
    "x,y,expected",
    [
        ([1, 2, 3, 4, 5], [2, 4, 6, 8, 10], 1.0),
        ([1, 2, 3, 4, 5], [10, 8, 6, 4, 2], -1.0),
        ([1, 2, 3, 4, 5], [5, 5, 5, 5, 5], None),
        ([5, 5, 5, 5, 5], [1, 2, 3, 4, 5], None),
        ([1, 2, 3], [1, 2, 3], 1.0),
        ([1, 2, 3], [3, 2, 1], -1.0),
        ([1, 2, 3, 4], [1, 3, 2, 4], 0.8),
        ([10, 20, 30], [15, 25, 35], 1.0),
        ([1.5, 2.5, 3.5], [3.0, 5.0, 7.0], 1.0),
    ],
)
def test_pearsonr_functionality(x, y, expected):
    result = pearsonr(x, y)
    if expected is None:
        assert result is None
    else:
        assert result == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize(
    "notes,durations,expected_error,error_message",
    [
        ([], [], ValueError, "Cannot find scale for passage with zero notes!"),
        ([1, 2, 3], [], ValueError, "Cannot find scale for passage with zero notes!"),
        ([], [1.0, 2.0], ValueError, "Cannot find scale for passage with zero notes!"),
        (
            [1, 2, 3],
            [1.0, 2.0],
            ValueError,
            "Must have exactly one duration for each note",
        ),
        (
            [1, 2],
            [1.0, 2.0, 3.0],
            ValueError,
            "Must have exactly one duration for each note",
        ),
        (
            [1, 2, None],
            [1.0, 2.0, 3.0],
            TypeError,
            "Notes must be either strings or integers",
        ),
        (
            [1, 2, [3]],
            [1.0, 2.0, 3.0],
            TypeError,
            "Notes must be either strings or integers",
        ),
    ],
)
def test_find_scale_raises_errors(notes, durations, expected_error, error_message):
    with pytest.raises(expected_error, match=error_message):
        find_scale(notes, durations)


@pytest.mark.parametrize(
    "notes,durations",
    [
        ([0, 2, 4, 5, 7, 9, 11], [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
        ([60, 62, 64, 65, 67], [1.0, 1.0, 1.0, 1.0, 1.0]),
        (["C", "D", "E", "F", "G"], [1.0, 1.0, 1.0, 1.0, 1.0]),
        (["c", "d", "e"], [2.0, 1.0, 1.0]),
        ([0, 4, 7], [1.0, 1.0, 1.0]),
        ([12, 14, 16], [1.0, 1.0, 1.0]),
        ([0], [1.0]),
        ([60, 60, 60], [0.5, 0.5, 1.0]),
    ],
)
def test_find_scale_functionality(notes, durations):
    result = find_scale(notes, durations)
    assert hasattr(result, "corr")
    assert hasattr(result, "binary_distribution")
    assert isinstance(result.corr, (float, type(None)))  # noqa
    assert len(result.binary_distribution) == 12
