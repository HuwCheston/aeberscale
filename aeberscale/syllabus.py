#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Aebersold Scale Syllabus - Extracted Scales

Scale names and notes extracted from the Scale Syllabus and converted to a base `Scale` instance.
"""

from typing import List, Optional, Type, Union

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
        """
        Return the name of the notes in the scale, transposed to the root
        """
        return [NOTE_NUMBERS[i] for i in self.note_numbers]

    @property
    def note_numbers(self) -> List[int]:
        """
        Return the pitch class numbers of the notes in the scale AFTER transposition to target note
        """
        return [(i + self.root_number) % 12 for i in self._note_numbers_nontransposed]

    @property
    def binary_distribution(self) -> List[int]:
        """
        Return a binary distribution X with length == 12.

        Distribution is calculated where i == 1 if note_numbers[i] else i == 0 for i in [0, 1, ..., 11]
        """
        return [1 if i in self.note_numbers else 0 for i in range(12)]

    @property
    def n_notes(self) -> int:
        """
        Return the number of notes within the scale
        """
        return len(self._notes_nontransposed)

    def __getitem__(
        self, note_name_or_number: Union[int, str]
    ) -> Optional[Union[str, int]]:
        """
        Get either diatonic scale step or note name.

        Given a string (e.g., 'C', 'D'), return the diatonic scale step (e.g., 0, 1). Given an integer, return the name
        of the note. In both cases, if the scale step/note is not in the scale, will return None.
        """
        if isinstance(note_name_or_number, int):
            # sanity checking inputs
            if note_name_or_number > 12:
                raise ValueError(
                    f"Note number must be below 12, but got {note_name_or_number}"
                )
            elif note_name_or_number <= -1:
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
            raise TypeError(
                f"Expected either str or int, but got {type(note_name_or_number)}"
            )

    def __repr__(self) -> str:
        return self.root + " " + self.name

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return self.n_notes

    def notes_to_diatonic_scale_steps(self, notes: List[Union[str, int]]) -> List[int]:
        """
        Given a list of note names, calculate the diatonic scale steps with reference to this Scale.

        Notes that do not appear within the scale will be returned as None.

        Returns:
            List of integers representing the diatonic scale steps

        Example:
            >>> Major("C").notes_to_diatonic_scale_steps(["C", "D", "E", "F#"])
            [0, 1, 2, None]
        """
        if isinstance(notes, (list, tuple, set)) and all(
            isinstance(n, (str, int)) for n in notes
        ):
            return [self[g] for g in notes]
        else:
            raise TypeError("Expected input to be either a list of strings or integers")

    @classmethod
    def _get_interval_pattern(cls) -> tuple:
        """
        Calculate the interval pattern (semitone distances) for this scale.

        Returns:
            Tuple of intervals between consecutive notes.
            For example, Major scale returns (2, 2, 1, 2, 2, 2, 1)
        """
        if cls._notes_nontransposed is None:
            return tuple()

        note_numbers = [NOTE_NAMES[n] for n in cls._notes_nontransposed]
        intervals = []
        for i in range(len(note_numbers)):
            next_idx = (i + 1) % len(note_numbers)
            interval = (note_numbers[next_idx] - note_numbers[i]) % 12
            intervals.append(interval)
        return tuple(intervals)

    @classmethod
    def _get_all_rotations(cls, interval_pattern: tuple) -> list:
        """
        Get all rotations of an interval pattern.

        Args:
            interval_pattern: Tuple of intervals

        Returns:
            List of all possible rotations of the pattern
        """
        rotations = []
        for i in range(len(interval_pattern)):
            rotations.append(interval_pattern[i:] + interval_pattern[:i])
        return rotations

    @classmethod
    def _get_all_scale_subclasses(cls) -> list:
        """
        Recursively get all subclasses of Scale.
        We need to walk up to the base Scale class first, then get all its subclasses.

        Returns:
            List of all Scale subclass types
        """
        # Find the base Scale class
        base = cls
        while base.__bases__ and base.__bases__[0].__name__ != "object":  # noqa
            if base.__bases__[0].__name__ == "Scale":  # noqa
                base = base.__bases__[0]
                break
            base = base.__bases__[0]

        # Now recursively get all subclasses from the base
        all_subclasses = []

        def get_subclasses_recursive(klass):
            for subclass in klass.__subclasses__():
                if subclass not in all_subclasses:
                    all_subclasses.append(subclass)
                    get_subclasses_recursive(subclass)

        get_subclasses_recursive(base)
        return all_subclasses

    # noinspection PyProtectedMember
    @classmethod
    def get_rotationally_equivalent_scales(cls) -> List[Type["Scale"]]:
        """
        Return all scale classes that are rotationally equivalent to this one.

        Two scales are rotationally equivalent if one is a mode (rotation) of the other.
        For example, Major scale is rotationally equivalent to Dorian, Phrygian, Lydian,
        Mixolydian (Dominant7th), Aeolian, and Locrian.

        Returns:
            List of Scale class types (not instances) that are rotationally equivalent.

        Example:
            >>> Major.get_rotationally_equivalent_scales()
            [<class 'Lydian'>, <class 'Dominant7th'>, <class 'Dorian'>, ...]
        """
        if cls._notes_nontransposed is None:
            return []

        my_intervals = cls._get_interval_pattern()
        my_rotations = cls._get_all_rotations(my_intervals)

        # Get all Scale subclasses
        all_scales = cls._get_all_scale_subclasses()

        equivalent = []
        for scale_class in all_scales:
            # Skip self
            if scale_class == cls:
                continue

            # Skip scales without notes defined
            if scale_class._notes_nontransposed is None:
                continue

            # Check if this scale's interval pattern matches any rotation
            scale_intervals = scale_class._get_interval_pattern()
            if scale_intervals in my_rotations:
                equivalent.append(scale_class)

        return equivalent

    @classmethod
    def get_mode_relationship(cls, other_scale: Type["Scale"]) -> dict:
        """
        Describe the modal relationship between this scale and another.

        Args:
            other_scale: Another Scale class to compare with

        Returns:
            Dictionary with keys:
                - 'is_equivalent': bool - Whether scales are rotationally equivalent
                - 'mode_number': int - Which mode of this scale the other represents (1-based)
                - 'transposition_semitones': int - How many semitones to transpose

        Example:
            >>> Major.get_mode_relationship(Dorian)
            {'is_equivalent': True, 'mode_number': 2, 'transposition_semitones': 10}

            This means Dorian is the 2nd mode of Major, transposed 10 semitones
            (or down a major 2nd from the root)
        """
        if cls._notes_nontransposed is None or other_scale._notes_nontransposed is None:
            return {
                "is_equivalent": False,
                "mode_number": None,
                "transposition_semitones": None,
            }

        my_intervals = cls._get_interval_pattern()
        other_intervals = other_scale._get_interval_pattern()
        my_rotations = cls._get_all_rotations(my_intervals)

        for i, rotation in enumerate(my_rotations):
            if rotation == other_intervals:
                # Calculate transposition
                my_notes = cls._notes_nontransposed
                other_notes = other_scale._notes_nontransposed
                semitone_diff = (
                    NOTE_NAMES[other_notes[0]] - NOTE_NAMES[my_notes[i]]
                ) % 12

                return {
                    "is_equivalent": True,
                    "mode_number": i + 1,
                    "transposition_semitones": semitone_diff,
                }

        return {
            "is_equivalent": False,
            "mode_number": None,
            "transposition_semitones": None,
        }

    def get_rotationally_equivalent_instances(self) -> List["Scale"]:
        """
        Return instantiated scales that are rotationally equivalent with their proper modal roots.

        For each mode of this scale, returns an instance with the root note that would make
        it use the same notes as this scale instance.

        Returns:
            List of Scale instances with appropriate roots to share the same notes.

        Example:
            >>> c_major = Major("C")
            >>> c_major.get_rotationally_equivalent_instances()
            [Lydian("F"), Dominant7th("G"), Dorian("D"), Phrygian("E"), Aeolian("A"), Locrian("B")]

            All these scales use the same notes as C Major, but start on different degrees.
        """
        equivalent_classes = self.get_rotationally_equivalent_scales()
        equivalent_instances = []

        # Handle other scale classes
        for scale_class in equivalent_classes:
            # Get the modal relationship
            relationship = self.__class__.get_mode_relationship(scale_class)

            if relationship["is_equivalent"]:
                mode_number = relationship["mode_number"]
                # The root of the equivalent scale should be the Nth note of this scale
                # (where N is the mode number, 1-indexed)
                modal_root = self.notes[mode_number - 1]
                equivalent_instances.append(scale_class(modal_root))

        # Check if this scale is rotationally equivalent to itself (symmetrical scales)
        my_intervals = self.__class__._get_interval_pattern()
        my_rotations = self.__class__._get_all_rotations(my_intervals)

        # If any rotation (other than the first) equals the original pattern,
        # this scale is self-equivalent
        for i, rotation in enumerate(
            my_rotations[1:], start=1
        ):  # Skip first (identity)
            if rotation == my_intervals:
                # Add an instance of the same scale class starting on the i-th note
                modal_root = self.notes[i]
                equivalent_instances.append(self.__class__(modal_root))

        return equivalent_instances

    @classmethod
    def is_rotationally_equivalent_to(cls, other_scale: Type["Scale"]) -> bool:
        """
        Check if this scale is rotationally equivalent to another scale.

        Args:
            other_scale: Another Scale class

        Returns:
            True if the scales are rotationally equivalent, False otherwise

        Example:
            >>> Major.is_rotationally_equivalent_to(Dorian)
            True
            >>> Major.is_rotationally_equivalent_to(HarmonicMinor)
            False
        """
        return other_scale in cls.get_rotationally_equivalent_scales()


class Major(Scale):
    """
    Basic major scale, sometimes also called the Ionian mode
    """

    name = "major"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "F", "G", "A", "B"]
    equivalent_to = []


class MajorPentatonic(Scale):
    name = "major pentatonic"
    family = "major"
    _notes_nontransposed = ["C", "D", "E", "G", "A"]


class Lydian(Scale):
    """
    Fourth mode of the major scale
    """

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
    """
    Third mode of the melodic minor scale, sometimes also called Lydian #5
    """

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
    """
    Fifth mode of the major scale, sometimes also called the Mixolydian mode
    """

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


class PhrygianMajor(Scale):
    name = "phrygian major"
    family = "minor"
    _notes_nontransposed = ["C", "Db", "E", "F", "G", "Ab", "Bb"]


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
    PhrygianMajor,
]
