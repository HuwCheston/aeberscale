#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Evaluate aeberscale performance using transcribed piano + saxophone MIDI files
"""

import random
from pathlib import Path

import numpy as np
from pretty_midi import PrettyMIDI
from rapidfuzz.distance import Levenshtein
from tqdm import tqdm

from aeberscale import NOTE_NAMES, find_scale
from aeberscale.syllabus import (
    SCALE_SYLLABUS,
    Aeolian,
    Augmented,
    BebopHalfDiminished,
    Diminished8Tone,
    Dominant7th,
    Dorian,
    HarmonicMajor,
    HarmonicMinor,
    Hindu,
    Locrian,
    LocrianSharp2,
    Lydian,
    LydianAugmented,
    LydianDominant,
    Major,
    MajorPentatonic,
    MelodicMinor,
    MinorPentatonic,
    Phrygian,
    PhrygianMajor,
    Scale,
    WholeTone,
)

# Not all tracks are needed, e.g. tuning notes, warm up exercises
GROUND_TRUTH = {
    "1-02 Bb Major": Major("A#"),
    "1-03 Bb Lydian": Lydian("A#"),
    "1-04 Bb Harmonic Major": HarmonicMajor("A#"),
    "1-05 Bb Lydian Augmented": LydianAugmented("A#"),
    "1-06 Bb Augmented": Augmented("A#"),
    "1-08 Bb Major Pentatonic": MajorPentatonic("A#"),
    "1-11 Bb 7 Dominant 7th": Dominant7th("A#"),
    "1-12 Bb 7+4 Lydian Dominant": LydianDominant("A#"),
    "1-13 Bb 7 Hindu": Hindu("A#"),
    "1-14 Bb 7 Whole Tone": WholeTone("A#"),
    "1-15 Bb 7b9 Dim (Beg. w_ Half Step)": BebopHalfDiminished("A#"),
    "1-17 Bb 7+9 Dim Whole Tone": Diminished8Tone("A#"),
    "2-04 Bb- Dorian": Dorian("A#"),
    "2-05 Bb-a Melodic Minor": MelodicMinor("A#"),
    "2-07 Bb Minor Pentatonic": MinorPentatonic("A#"),
    "2-08 Bb Harmonic": HarmonicMinor("A#"),
    "2-09 Bb Phrygian": Phrygian("A#"),
    "2-10 Bb Major Phrygian": PhrygianMajor("A#"),
    "2-11 Bb Diminished": Diminished8Tone("A#"),
    "2-13 Bb Pure Minor": Aeolian("A#"),
    "2-15 Bb Half Diminished": Locrian("A#"),
    "2-16 Bb #2 Locrian #2": LocrianSharp2("A#"),
}

SAX_ROOT = Path("../data/midi/saxophone")
PIANO_ROOT = Path("../data/midi/piano")

# David Liebman playing soprano saxophone on these recordings I think
SAX_MIN_NOTE, SAX_MAX_NOTE = 45, 88
PIANO_MIN_NOTE, PIANO_MAX_NOTE = 21, 108

MIN_DURATION, MAX_DURATION = 0.1, 10.0
MAX_VELOCITY = 127

# number of bootstrap iterations per item
N_BOOTS = 1000

# Window parameters: set WINDOW_SIZE == None to disable windowing
WINDOW_SIZE = 5.0  # average JTD tempo == 194 BPM, this is duration of 4 bars of 4/4 (most common time signature)
HOP_SIZE = 5.0  # non-overlapping windows
MAX_NOTES = 64  # average number of notes contained across sliding window of 4 bars for all JTD tracks (63.98224943487665)


def window_notes(all_notes: list) -> list[list]:
    # If we don't have enough notes to create a window, just return
    if len(all_notes) < MAX_NOTES:
        return [all_notes]

    # First, get starting times for all windows
    end_sec = round(max(all_notes, key=lambda x: x.end).end)
    windows = np.arange(0, end_sec, HOP_SIZE)
    all_windows = []

    # Iterate over all starting times
    for window_start in windows:
        # Get notes contained in this window
        window_end = window_start + WINDOW_SIZE
        windowed_notes = [
            i for i in all_notes if i.start >= window_start and i.end <= window_end
        ]

        # Too many notes: truncate, keeping earliest notes only
        if len(windowed_notes) >= MAX_NOTES:
            windowed_notes = windowed_notes[:MAX_NOTES]

        # Not enough notes: grab notes from before the start of the window and keep appending until we have enough
        elif len(windowed_notes) < MAX_NOTES:
            outside_window = [i for i in all_notes if i.start < window_start]
            outside_sort = list(reversed(sorted(outside_window, key=lambda x: x.end)))
            extra_notes = outside_sort[: MAX_NOTES - len(windowed_notes)]
            windowed_notes = extra_notes + windowed_notes

        # Sort by onset time
        windowed_notes = sorted(windowed_notes, key=lambda x: x.start)

        # Little check that we have enough notes in the window
        if not len(windowed_notes) == MAX_NOTES:
            print(
                f"Not enough notes in window (expected {MAX_NOTES}, got {len(windowed_notes)})"
            )
            continue

        all_windows.append(windowed_notes)

    if len(all_windows) > 0:
        return all_windows
    else:
        return [all_notes]


def preprocess_midi(sax_path: Path, piano_path: Path) -> list:
    # load up all notes, remove any out of range/duration
    sax_midi = PrettyMIDI(str(sax_path))
    sax_notes = [
        n
        for n in sax_midi.instruments[0].notes
        if all(
            (
                SAX_MIN_NOTE <= n.pitch <= SAX_MAX_NOTE,
                MIN_DURATION <= n.duration <= MAX_DURATION,
                n.start >= 0.0,
                n.end >= 0.0,
                0 <= n.velocity <= MAX_VELOCITY,
            )
        )
    ]
    piano_midi = PrettyMIDI(str(piano_path))
    piano_notes = [
        n
        for n in piano_midi.instruments[0].notes
        if all(
            (
                PIANO_MIN_NOTE <= n.pitch <= PIANO_MAX_NOTE,
                MIN_DURATION <= n.duration <= MAX_DURATION,
                n.start >= 0.0,
                n.end >= 0.0,
                0 <= n.velocity <= MAX_VELOCITY,
            )
        )
    ]

    # combine both notes together and sort by onset time
    all_notes = sorted(sax_notes + piano_notes, key=lambda x: x.start)

    return all_notes


def score(expected_scale: Scale, actual_scale: Scale) -> float:
    # 1 == correct root, family, and scale (all correct)
    if all(
        (
            expected_scale.family == actual_scale.family,
            expected_scale.root == actual_scale.root,
            expected_scale.name == actual_scale.name,
        )
    ):
        return 1.0

    # 0.5 == correct family and root (i.e., Bb Lydian == Bb major)
    elif all(
        (
            expected_scale.family == actual_scale.family,
            expected_scale.root == actual_scale.root,
        )
    ):
        return 0.5

    # 0.2 == correct root (i.e., Bb Harmonic Minor == Bb Harmonic Major)
    elif all((expected_scale.root == actual_scale.root,)):
        return 0.25

    # 0.1 == correct family
    elif all((expected_scale.family == actual_scale.family,)):
        return 0.1

    else:
        return 0.0


def levenshtein_score(expected_scale: Scale, actual_scale: Scale) -> float:
    found_str = ",".join(str(i) for i in sorted(actual_scale.note_numbers))
    expected_str = ",".join(str(i) for i in sorted(expected_scale.note_numbers))
    return 1 - Levenshtein.normalized_distance(found_str, expected_str)


def jaccard_score(expected_scale: Scale, actual_scale: Scale) -> float:
    # convert note numbers to sets
    set1 = set(expected_scale.note_numbers)
    set2 = set(actual_scale.note_numbers)
    # intersection of two sets
    intersection = len(set1.intersection(set2))
    # unions of two sets
    union = len(set1.union(set2))
    return intersection / union


def main():
    res = []
    boot_res = []

    total_dur = 0
    total_notes = 0

    for desired_track, expected_scale in tqdm(
        GROUND_TRUTH.items(), desc="Processing tracks..."
    ):
        sax_path = SAX_ROOT / f"{desired_track}.mid"
        piano_path = PIANO_ROOT / f"{desired_track}.mid"

        # load up all notes, remove any out of range/duration
        all_notes = preprocess_midi(sax_path, piano_path)

        # increase counters
        total_dur += max(all_notes, key=lambda x: x.end).end
        total_notes += len(all_notes)

        # split into windows
        all_note_windows = (
            [all_notes] if WINDOW_SIZE is None else window_notes(all_notes)
        )

        # convert into format required for aeberscale
        for all_notes in all_note_windows:

            all_pitches = [n.pitch for n in all_notes]
            all_durs = [n.duration for n in all_notes]

            # find the scale
            found = find_scale(all_pitches, all_durs)

            # score the scale
            scale_score = jaccard_score(expected_scale, found)
            res.append(scale_score)

            # bootstrapping: choose a random scale for this window
            random_scale = random.choice(SCALE_SYLLABUS)
            random_root = random.choice(list(NOTE_NAMES.keys()))
            random_init = random_scale(root=random_root)

            # score this bootstrap iteration
            boot_res.append(jaccard_score(expected_scale, random_init))

    print("Total duration (s): ", total_dur)
    print("Total notes: ", total_notes)
    print("Final score and SD: ", np.mean(res), np.std(res))
    print("Baseline score and SD: ", np.mean(boot_res), np.std(boot_res))


if __name__ == "__main__":
    random.seed(42)
    main()
