#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aebersold Scale Syllabus - Extracted Scales

Scale names and notes extracted from the Scale Syllabus and converted to a base `Scale` instance.
"""

from typing import List, Union

from aeberscale.utils import NOTE_NAMES, NOTE_NUMBERS


class Scale:
    """
    Base instance for all scale subclasses. Must be instantiated with a given root note.
    """

    name: str = None
    family: str = None
    _notes_nontransposed: list[str] = None

    def __init__(self, root: str):
        if not isinstance(root, str):
            raise ValueError(f"Expected `root` to be a string, but got {type(root)}")
        elif not root.lower() in [n.lower() for n in NOTE_NAMES.keys()]:
            raise ValueError(
                f"Root note {root} is invalid (must be one of {', '.join(NOTE_NAMES.keys())}"
            )
        self.root = root
        self.root_number = NOTE_NAMES[root]

    @property
    def _note_numbers_nontransposed(self) -> List[str]:
        return [NOTE_NAMES[i] for i in self._notes_nontransposed]

    @property
    def notes(self) -> List[str]:
        return [NOTE_NUMBERS[i] for i in self.note_numbers]

    @property
    def note_numbers(self) -> List[int]:
        return [(i + self.root_number) % 12 for i in self._note_numbers_nontransposed]

    @property
    def binary_distribution(self) -> List[int]:
        return [1 if i in self.note_numbers else 0 for i in range(12)]

    @property
    def n_notes(self) -> int:
        return len(self._notes_nontransposed)

    def __getitem__(self, note_name_or_number: Union[int, str]) -> Union[str, int]:
        if isinstance(note_name_or_number, int):
            # sanity checking inputs
            if note_name_or_number > 12:
                raise ValueError(
                    f"Note number must be below 12, but got {note_name_or_number}"
                )
            elif note_name_or_number < -1:
                raise ValueError(
                    f"Note number must be above 0, but got {note_name_or_number}"
                )
            else:
                # return diatonic scale degree
                try:
                    return self.notes[note_name_or_number]
                # note not in scale, return None
                except IndexError:
                    return None

        elif isinstance(note_name_or_number, str):
            matches = [
                n
                for n, i in enumerate(self.notes)
                if NOTE_NAMES[i] == NOTE_NAMES[note_name_or_number]
            ]
            # no matches: note is not contained in scale, so return None
            if len(matches) == 0:
                return None
            # return matching note from scale
            else:
                return matches[0]

        else:
            raise ValueError(
                f"Expected either str or int, but got {type(note_name_or_number)}"
            )

    def __repr__(self) -> str:
        return self.root + " " + self.name

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self):
        return self.n_notes

    def notes_to_diatonic_scale_steps(self, notes: List[Union[str, int]]) -> List[int]:
        if all(isinstance(n, (str, int)) for n in notes):
            return [self[g] for g in notes]
        else:
            raise TypeError("Expected input to be either a list of strings or integers")


class Major(Scale):
    name = "major"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "A", "B"]


class MajorPentatonic(Scale):
    name = "major pentatonic"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "G", "A"]


class Lydian(Scale):
    name = "lydian"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "F#", "G", "A", "B"]


class BebopMajor(Scale):
    name = "bebop major"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "G#", "A", "B"]


class HarmonicMajor(Scale):
    name = "harmonic major"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "Ab", "B"]


class LydianAugmented(Scale):
    name = "lydian augmented"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "F#", "G#", "A", "B"]


class Augmented(Scale):
    name = "augmented"
    family = "major"
    _notes_nontransposed = ["C", "D#", "E", "G", "Ab", "B"]


class SixthModeHarmonicMinor(Scale):
    name = "sixth mode harmonic minor"
    family = "major"
    _notes_nontransposed = ["C", "D#", "E", "F#", "G", "A", "B"]


class Blues(Scale):
    name = "blues"
    family = "major"
    _notes_nontransposed = ["C", "Eb", "F", "F#", "G", "Bb"]


class Dominant7th(Scale):
    name = "dominant 7th"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "A", "Bb"]


class BebopDominant(Scale):
    name = "bebop dominant 7th"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "A", "Bb", "B"]


class SpanishJewish(Scale):
    name = "Spanish / Jewish"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "Db", "E", "F", "G", "Ab", "Bb"]


class LydianDominant(Scale):
    name = "lydian dominant 7th"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "D", "E", "F#", "G", "A", "Bb"]


class Hindu(Scale):
    name = "Hindu"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "Ab", "Bb"]


class WholeTone(Scale):
    name = "whole tone"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "D", "E", "F#", "G#", "Bb"]


class DiminishedDom7th(Scale):
    name = "diminished dominant 7th"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "Db", "D#", "E", "F#", "G", "A", "Bb"]


class DiminishedWholeTone(Scale):
    name = "diminished whole tone"
    family = "dominant_7th"
    _notes_nontransposed = ["C", "Db", "D#", "E", "F#", "G#", "Bb"]


class Dorian(Scale):
    name = "dorian"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "F", "G", "A", "Bb"]


class MinorPentatonic(Scale):
    name = "minor pentatonic"
    family = "minor"
    _notes_nontransposed = ["C", "Eb", "F", "G", "Bb"]


class BebopMinor(Scale):
    name = "bebop minor"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "E", "F", "G", "A", "Bb"]


class MelodicMinor(Scale):
    name = "melodic minor"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "F", "G", "A", "B"]


class BebopMinorNo2(Scale):
    name = "bebop minor 2"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "F", "G", "G#", "A", "B"]


class HarmonicMinor(Scale):
    name = "harmonic minor"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "F", "G", "Ab", "B"]


class DiminishedMinor(Scale):
    name = "diminished minor"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "F", "F#", "G#", "A", "B"]


class Phrygian(Scale):
    name = "phrygian"
    family = "minor"
    _notes_nontransposed = ["C", "Db", "Eb", "F", "G", "Ab", "Bb"]


class Aeolian(Scale):
    name = "aeolian"
    family = "minor"
    _notes_nontransposed = ["C", "D", "Eb", "F", "G", "Ab", "Bb"]


class Locrian(Scale):
    name = "locrian"
    family = "half_diminished"
    _notes_nontransposed = ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"]


class LocrianSharp2(Scale):
    name = "locrian sharp2"
    family = "half_diminished"
    _notes_nontransposed = ["C", "D", "Eb", "F", "Gb", "Ab", "Bb"]


class BebopHalfDiminished(Scale):
    name = "bebop half-diminished"
    family = "half_diminished"
    _notes_nontransposed = ["C", "Db", "Eb", "F", "Gb", "G", "Ab", "Bb"]


class Diminished8Tone(Scale):
    name = "diminished 8-tone"
    family = "diminished"
    _notes_nontransposed = ["C", "D", "Eb", "F", "Gb", "Ab", "A", "B"]


SCALE_SYLLABUS = [
    Major,
    MajorPentatonic,
    Lydian,
    BebopMajor,
    HarmonicMajor,
    LydianAugmented,
    Augmented,
    SixthModeHarmonicMinor,
    Blues,
    Dominant7th,
    BebopDominant,
    SpanishJewish,
    LydianDominant,
    Hindu,
    WholeTone,
    DiminishedDom7th,
    DiminishedWholeTone,
    Dorian,
    MinorPentatonic,
    BebopMinor,
    MelodicMinor,
    BebopMinorNo2,
    HarmonicMinor,
    DiminishedMinor,
    Phrygian,
    Aeolian,
    Locrian,
    LocrianSharp2,
    BebopHalfDiminished,
    Diminished8Tone,
]
