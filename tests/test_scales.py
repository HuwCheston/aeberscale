#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for scales inside aeberscale/syllabus.py
"""

import pytest

from aeberscale.syllabus import (
    SCALE_SYLLABUS,
    Dorian,
    HarmonicMinor,
    Lydian,
    Major,
    Scale,
    WholeTone,
)


@pytest.mark.parametrize("scale", SCALE_SYLLABUS)
def test_attrs(scale):
    instant = scale(root="C")
    assert issubclass(type(instant), Scale)

    for prop in [
        "_note_numbers_nontransposed",
        "name",
        "family",
        "_notes_nontransposed",
        "notes",
        "note_numbers",
        "binary_distribution",
        "n_notes",
    ]:
        assert hasattr(instant, prop)
        assert getattr(instant, prop) is not None

    # test magic methods
    assert isinstance(repr(instant), str)
    assert isinstance(str(instant), str)
    assert isinstance(len(instant), int)
    assert len(instant) > 0


@pytest.mark.parametrize(
    "scale, expected",
    [
        (Major("D"), ["D", "E", "F#", "G", "A", "B", "C#"]),
        (
            Lydian("F"),
            [
                "F",
                "G",
                "A",
                "B",
                "C",
                "D",
                "E",
            ],
        ),
        (
            Dorian("E"),
            [
                "E",
                "F#",
                "G",
                "A",
                "B",
                "C#",
                "D",
            ],
        ),
        (HarmonicMinor("C"), ["C", "D", "D#", "F", "G", "G#", "B"]),
        (
            WholeTone("F"),
            [
                "F",
                "G",
                "A",
                "B",
                "C#",
                "D#",
            ],
        ),
    ],
)
def test_transposition_notes(scale, expected):
    assert scale.notes == expected


@pytest.mark.parametrize(
    "scale, inpt, expected",
    [
        (Major("D"), "D", 0),
        (Lydian("F"), "Ab", None),
        (Dorian("E"), "C#", 5),
        (HarmonicMinor("C"), 3, "F"),
        (WholeTone("F"), "G#", None),
        (WholeTone("F"), 7, None),
    ],
)
def test_getitem(scale, inpt, expected):
    assert scale[inpt] == expected


@pytest.mark.parametrize(
    "scale, expected",
    [
        (Major("D"), [None, 0, None, None, 0, None, None]),
        (Lydian("F"), [4, 5, None, 0, 5, None, 4]),
        (Dorian("E"), [None, 6, None, None, 6, None, None]),
        (HarmonicMinor("C"), [0, 1, 2, 3, 1, None, 0]),
        (WholeTone("F"), [None, None, 5, 0, None, None, None]),
    ],
)
def test_notes_to_diatonic_scale_steps(scale, expected):
    # why not
    lick = ["C", "D", "Eb", "F", "D", "Bb", "C"]
    assert scale.notes_to_diatonic_scale_steps(lick) == expected


def test_errors():
    with pytest.raises(ValueError, match="Expected `root` to be a string"):
        _ = Major(1)
    with pytest.raises(ValueError, match="Root note 123 is invalid"):
        _ = Major("123")

    sc = Major("D")
    with pytest.raises(ValueError, match="Note number must be below 12"):
        _ = sc[13]
    with pytest.raises(ValueError, match="Note number must be above 0"):
        _ = sc[-1]
    with pytest.raises(TypeError, match="Expected either str or int"):
        _ = sc[[1, 2, 3]]

    with pytest.raises(
        TypeError, match="Expected input to be either a list of strings"
    ):
        _ = sc.notes_to_diatonic_scale_steps("123")
