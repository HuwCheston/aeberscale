#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Transcribe the recordings from the Jamey Aebersold scale syllabus to MIDI using basic-pitch and Kong's AMT model
"""

import os
from pathlib import Path

import librosa
import soundfile as sf
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.inference import Model, predict
from piano_transcription_inference import PianoTranscription
from piano_transcription_inference import sample_rate as kong_sr

SAMPLE_RATE = 44100  # confirmed from FFprobe of apple music recordings
DEVICE = "cpu"
OFFSET = 7  # removes Jamey's speaking
AUDIO_FILEPATH = Path("../data/audio")
SAX_MIDI_FILEPATH = Path("../data/midi/saxophone")
PIANO_MIDI_FILEPATH = Path("../data/midi/piano")


def main():
    audio_ins = list(AUDIO_FILEPATH.rglob("**/*.m4a"))
    if len(audio_ins) == 0:
        raise ValueError(
            "No audio files found. Ensure you've downloaded these and extracted to aeberscale/evaluation/data/audio"
        )

    basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)

    for audio_in in audio_ins:
        # Load up audio, split channels
        #  Kong audio needs different sample rate
        y, _ = librosa.load(audio_in, mono=False, sr=SAMPLE_RATE, offset=OFFSET)
        y_sax = y[0, :]
        y_piano = librosa.resample(y[1, :], orig_sr=SAMPLE_RATE, target_sr=kong_sr)

        # Transcribe the piano with Kong model
        piano_loc = str(audio_in.with_suffix(".mid")).replace("audio", "midi/piano")
        transcriptor = PianoTranscription(device=DEVICE, checkpoint_path=None)
        transcriptor.transcribe(y_piano, piano_loc)

        # Transcribe the sax with Basic Pitch
        #  Need to dump temp audio
        sax_loc = str(audio_in.with_suffix(".mid")).replace("audio", "midi/saxophone")
        sf.write("tmp_sax.wav", y_sax, SAMPLE_RATE)
        _, midi_data, __ = predict(
            "tmp_sax.wav",
            basic_pitch_model,
        )
        midi_data.write(sax_loc)

        os.remove("tmp_sax.wav")


if __name__ == "__main__":
    main()
