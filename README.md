# AeberScale

AeberScale is a scale finding algorithm that modifies the famous [Krumhansl-Schmuckler key-finding algorithm](https://github.com/Corentin-Lcs/music-key-finder) for jazz music. In particular, rather than using solely major or minor key profiles, we adapt the scales from the (equally famous!) [Jamey Aebersold Scale Syllabus](https://www.jazzbooks.com/mm5/download/FREE-scale-syllabus.pdf). This syllabus is perhaps best known to musicians for its inclusion in copies of the Charlie Parker Omnibook (check the back page!).

## Usage

AeberScale is an extremely simple package that has no external dependencies. It relies on you providing it a set of pitch classes and their corresponding durations. It is up to you how you extract this information, so you might find it handy to use a package like `pretty-midi` or `music21`, depending on what sort of input you are using.

Once you have this information, you can use `aeberscale.find_key` to estimate the key:

```
from pretty_midi import PrettyMIDI
from aeberscale import find_scale

# Extract notes and durations from MIDI file
pm = PrettyMIDI("path/to/a/midi/file")
nots = [p.pitch for p in pm.instruments[0].notes]
durs = [p.duration for p in pm.instruments[0].notes]

# grab the scale with aeberscale
out = find_scale(nots, durs)
print(out)
>>> "F major"
```

Note that the returned object from `find_scale` is an instance of a subclass `aeberscale.Scale`. This provides some useful helper properties and methods:

```
print(out.notes)
>>> ["F", "G", "A", "A#", "C", "D", "E"]

print(out.note_numbers)
>>> [5, 7, 9, 10, 0, 2, 4]

print(out.family)
>>> "major"
```

You can also easily convert from note names or chromatic scale steps to diatonic scale steps (useful in, e.g., $n$-gram extraction and computation). Notes that are not contained within the current key will be returned as `None`:
```
ss = ["C", "D", "Eb", "F", "D", "Bb", "C"]
dia = out.notes_to_diatonic_scale_steps(ss)

print(dia)
>>> [5, 6, None, 0, 6, 4, 5]
```

## Installation

Easy:

`pip install aeberscale`

To run the tests:

```
git clone https://github.com/HuwCheston/aeberscale.git
cd aeberscale
pytest tests
```

## Algorithm

The process is as follows:

- For provided notes, obtain a histogram of summed pitch-class durations (e.g., note 5 held for X seconds, note 6 held for Y...)
- For all scales in the Jamey Aebersold syllabus and all possible root notes, obtain a binary distribution (key profile)
  - Where 1 == PC contained in scale, 0 == not (and PC \in {0, 1, 2, ..., 11})
- Compute the maximum possible correlation coefficient between the provided input and all scale/root note combinations

For more information on the Krumhansl-Schmuckler algorithm, check out [this paper](https://davidtemperley.com/wp-content/uploads/2015/11/temperley-mp99.pdf). Note that the only difference between the original implementation and AeberScale is that we use a binary distribution for the key profiles, rather than obtaining these through perceptual experiments.
