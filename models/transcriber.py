# import essentia.algorithms
import librosa
import librosa.display
import numpy
# import mir_eval.display
# import numpy
# import scipy
import numpy as np
# import seaborn as sns
import matplotlib.pyplot as plt
# import sounddevice as sd
# import music21 as m21
# import midiutil
# import pretty_midi
# import fluidsynth
# import pkg_resources
# import midi2audio
# import essentia
# import essentia.standard

from models.note import Note
# from utils import utils
# from plotPitch import colorline
# import midiAlign

# TO-DO: Peaks not marked as onsets should also be labelled as 'weak onsets'
def detectOnsets(y, sr, filename = None, instrument = "Piano"):
    if (instrument == "Piano") :
        onsetEnvelope = librosa.onset.onset_strength(y=y,
                                                     sr=sr,
                                                     n_mels=512,
                                                     n_fft=4096,
                                                     hop_length=512)
        onset_samples = librosa.onset.onset_detect(onset_envelope=onsetEnvelope,
                                                   sr=sr,
                                                   units='samples',
                                                   backtrack=False,
                                                   delta=0.1,
                                                   normalize=True,
                                                   pre_max=1, post_max=1, pre_avg=3, post_avg=5, wait=5)
    elif (instrument == "Trumpet"):
        onsetEnvelope = librosa.onset.onset_strength(y=y,
                                                     sr=sr,
                                                     n_mels=512,
                                                     n_fft=8192,
                                                     hop_length=512)
        onset_samples = librosa.onset.onset_detect(onset_envelope=onsetEnvelope,
                                                   sr=sr,
                                                   units='samples',
                                                   backtrack=False)


    times = librosa.times_like(onsetEnvelope, sr=sr)
    onset_samples = librosa.onset.onset_detect(onset_envelope=onsetEnvelope,
                                               sr=sr,
                                               units='samples',
                                               backtrack=False,
                                               delta=0.1,
                                               pre_max=1, post_max=1, pre_avg=3, post_avg=5, wait=5)
    onset_times = librosa.samples_to_frames(onset_samples)

    # For offsets we will use proceeding onsets and silent segments
    silence = np.concatenate(librosa.effects.split(y=y, top_db=40))
    silence = librosa.samples_to_frames(silence)

    # if filename != None:
    #     utils.save_onsets(onset_times, filename)

    return onset_samples, onset_times, times, onsetEnvelope, silence


def segmentationRetry(silence, onsets, f0, times, sr, loudness, newOnsets, timingLabels):

    noteList = []
    idealOnsetIndex = 0
    noteStart = 0
    voicedEnd = 0
    inVoicedSegment = False
    j = 0 # Index for iterating over the silence array
    #
    # print("Loudness: ", (loudness[0]))
    # print("f0: ", (f0))

    print("Silence:")
    print(silence)
    for i in range(len(onsets)):

        # First we can grab the timing label for the given onset

        # Within a voiced segment, onsets[i] is treated as the note offset
        if inVoicedSegment:
            # Case 1: "Offset" occurs after the voiced segment ends
            # Identifies the point at which a rest may be present (break between voiced sections)
            if (onsets[i] >= voicedEnd):
                # If the current onset occurs after the end of a voiced segment,
                #   we save the old note with a subsequent rest and record that we are no longer in a voiced segment
                # Adding the note
                noteFrequency = f0[noteStart:voicedEnd]
                noteTime = times[noteStart:voicedEnd]
                duration = times[voicedEnd] - times[noteStart]
                noteLoudness = loudness[noteStart:voicedEnd]
                # print(noteLoudness)
                newNote = Note(frequencyCurve=noteFrequency, onset=noteStart, offset=voicedEnd, duration=duration,
                               time=noteTime, sampleRate=sr, loudness=noteLoudness, idealOnset=newOnsets[idealOnsetIndex], timingLabel=timingLabels[idealOnsetIndex])
                noteList.append(newNote)

                # Adding the rest which follows
                # For midi representation the rests do not matter, but are vital for musicXML representation
                noteFrequency = f0[voicedEnd:silence[j]]
                noteTime = times[voicedEnd:silence[j]]
                duration = times[silence[j]] - times[voicedEnd]
                newNote = Note(frequencyCurve=noteFrequency, onset=voicedEnd, offset=silence[j], duration=duration,
                               time=noteTime, sampleRate=sr, loudness=[], idealOnset=newOnsets[idealOnsetIndex], timingLabel=timingLabels[idealOnsetIndex])
                noteList.append(newNote)
                inVoicedSegment = False
            elif onsets[i] < voicedEnd:
                # Onsets occurring before the end of the current voiced segment will have the same offset as the next
                #   notes onset (legato notes)
                noteFrequency = f0[noteStart:onsets[i]]
                # However, if the current note contains non-integer values for the frequency
                # we can assume the previous note had a sharp offset and is not actually
                # a note.
                if not numpy.isnan(noteFrequency).all():
                    noteTime = times[noteStart:onsets[i]]
                    duration = times[onsets[i]] - times[noteStart]
                    noteLoudness = loudness[noteStart:onsets[i]]
                    # print(noteLoudness)
                    newNote = Note(frequencyCurve=noteFrequency, onset=noteStart, offset=onsets[i], duration=duration,
                                   time=noteTime, sampleRate=sr, loudness=noteLoudness, idealOnset=newOnsets[idealOnsetIndex], timingLabel=timingLabels[idealOnsetIndex])
                    noteList.append(newNote)
                # Check if we're up to the last onset
                if (i < len(onsets) - 1):
                    noteStart = onsets[i]
                    idealOnsetIndex = i
                else:
                    noteFrequency = f0[onsets[i]:voicedEnd]
                    noteTime = times[onsets[i]:voicedEnd]
                    duration = times[voicedEnd] - times[onsets[i]]
                    noteLoudness = loudness[onsets[i]:voicedEnd]
                    # print(noteLoudness)
                    newNote = Note(frequencyCurve=noteFrequency, onset=onsets[i], offset=voicedEnd, duration=duration,
                                   time=noteTime, sampleRate=sr, loudness=noteLoudness, idealOnset=newOnsets[idealOnsetIndex], timingLabel=timingLabels[idealOnsetIndex])
                    noteList.append(newNote)
        if not (inVoicedSegment):
            # Move onto the next voiced segment. Segmentation always starts here.
            if j < len(silence):
                if onsets[i] >= silence[j]: # Obsolete: This check assumes "silence" may be detecting notes
                    inVoicedSegment = True
                    idealOnsetIndex = i
                    noteStart = onsets[i]
                    if (j < len(silence)):
                        voicedEnd = silence[j + 1]
                        j += 2
                    else:
                        voicedEnd = times[len(times) - 1]
                    if (i == (len(onsets) - 1)):
                        noteFrequency = f0[noteStart:voicedEnd]
                        noteTime = times[noteStart:voicedEnd]
                        duration = times[voicedEnd] - times[noteStart]
                        noteLoudness = loudness[noteStart:voicedEnd]
                        # print(noteLoudness)
                        newNote = Note(frequencyCurve=noteFrequency, onset=noteStart, offset=voicedEnd,
                                       duration=duration, time=noteTime, sampleRate=sr, loudness=noteLoudness, idealOnset=newOnsets[idealOnsetIndex], timingLabel=timingLabels[idealOnsetIndex])
                        noteList.append(newNote)

    return noteList
    # return segmentedFrequency, segmentedTimes, noteDurations


def pitchAnalysis(notes):
    # - Calculate deviation of the frequency for each note
    # - Set the accidental attribute for the note objects to maintain an average deviation
    #       The cents deviation is already set when assigning names to each note object
    #       All that's left is to analyse the available notes and 'display' something
    cents_dict = {note.name: note.cents for note in notes}

    plt.bar(range(len(cents_dict)), list(cents_dict.values()), align='center')
    plt.xticks(range(len(cents_dict)), list(cents_dict.keys()))
    plt.show()

def loudnessAnalysis(y, sr):
    # Loudness is a strange measure of intensity and changes based on listeners perception
    # https://www.audiolabs-erlangen.de/resources/MIR/FMP/C1/C1S3_Dynamics.html
    # First focus on calculating a power to decibels plot, however understand that this is just an absolute measure
    # and will not be influenced by a logarithmic equal loudness weighting. This will need to be applied later to
    # normalize for notes of different frequencies.
    # win_len_sec = 0.1
    # power_ref = 10**(-12)

    n_fft = 2048

    # win_len = round(win_len_sec * sr)
    # win = np.ones(win_len) / win_len
    # power_db = 10 * np.log10(np.convolve(y**2, win, mode='same') / power_ref)

    # Get STFT
    s = librosa.stft(y, n_fft=n_fft, hop_length=512, center=False)

    # Convert spectrogram to dB
    amp_db = np.abs(librosa.amplitude_to_db(s))

    # We then weight the amplitude with a perceptual weighting which more closely resembles how humans perceive loudness
    # https://en.wikipedia.org/wiki/A-weighting#Function_realisation_of_some_common_weightings

    # Perceptual A-weighting
    frequencies = librosa.fft_frequencies(n_fft=n_fft, sr=sr)
    s = librosa.perceptual_weighting(S=s**2, frequencies=frequencies, kind='A')
    a_weighting = librosa.A_weighting(frequencies)
    a_weighting = np.expand_dims(a_weighting, axis=1)

    amp_db = amp_db + a_weighting

    rms = librosa.feature.rms(S=s)

    loudness = librosa.feature.rms(S=librosa.db_to_amplitude(amp_db))
    times = librosa.times_like(loudness)

    return loudness, times

def rhythmAnalysis(y, sr, onsetEnvelope, onset_times):
    # onsetTimingLabels:
    #   Allow us to identify each onset as 'Early, 'On-time', or 'Late'
    # timingThreshold:
    #   A threshold in frames of when a note falls out of time or off-tempo
    print("Rhythm Analysis:")
    tempo, beats = librosa.beat.beat_track(y=y,
                                           sr=sr,
                                           onset_envelope=onsetEnvelope,
                                           hop_length=512)
    newOnsets = []
    onsetTimingLabels = []
    timingThreshold = 0.3
    for i in onset_times:
        idx = (np.abs(beats - i)).argmin()
        newOnsets.append(beats[idx])
        print(i, beats[idx])
        print(librosa.frames_to_time(i), librosa.frames_to_time(beats[idx]))
        if i >= beats[idx] + timingThreshold:
            onsetTimingLabels.append('Late')
        elif i <= beats[idx] - timingThreshold:
            onsetTimingLabels.append('Early')
        else:
            onsetTimingLabels.append('On-time')

    # Estimate duration of each played note
    # roundedNoteDurations = []
    # durationAccuracy = 0.5
    # for i in range(len(noteDurations)):
    #     noteTempo = 60 / noteDurations[i] # Estimate "bpm" for the note
    #     r = (tempo/noteTempo) % durationAccuracy
    #     # roundedNoteDurations.append(round(r))
    #     if r <= (0.5*durationAccuracy):
    #         roundedNoteDurations.append(tempo/noteTempo - r)
    #     else:
    #         roundedNoteDurations.append(tempo / noteTempo + durationAccuracy - r)

    # print(tempo)
    # print(noteDurations)
    # print(roundedNoteDurations)
    return newOnsets, onsetTimingLabels

# Primary function of 'extractFeatures' is to perform note segmentation, estimate tempo,
def extractFeatures(filename):

    y, sr = librosa.load(filename)

    # Pre-process the audio (Remove silence from start and end of recording)
    trimmed, trimIndex = librosa.effects.trim(y=y, top_db=20)
    y = y[trimIndex[0]:trimIndex[1]]

    # Detect onsets within the recording
    onsets, onset_times, times, onsetEnvelope, silence = detectOnsets(y, sr)

    # Estimate the tempo from the onsetEnvelope used
    tempo, beats = librosa.beat.beat_track(onset_envelope=onsetEnvelope, sr=sr)

    # Calculating frequency curve with pYin
    f0, voiced_flag, voiced_probs = librosa.pyin(y,
                                                 fmin=librosa.midi_to_hz(12.0),
                                                 fmax=librosa.midi_to_hz(120.0),
                                                 fill_na=np.nan,
                                                 no_trough_prob=0)

    # Analyse loudness/intensity of performance and individual notes
    loudness = loudnessAnalysis(y=y, sr=sr)

    # Analyse the timing of each note with respect to the average tempo
    newOnsets, onsetTimingLabels = rhythmAnalysis(y, sr, onsetEnvelope, onset_times)

    # Segment the frequency curve into individual notes
    # Frequency, onsets, durations, loudness
    notes = segmentationRetry(silence=silence,
                              onsets=onset_times,
                              f0=f0,
                              times=times,
                              sr=sr,
                              loudness=loudness[0][0],
                              newOnsets=newOnsets,
                              timingLabels=onsetTimingLabels)

    # Clean edges of the frequency curves for notes
    # print("Transcribed notes: ")
    for note in notes:
        note.clean_frequency()
        # print(note.get_midi_note())

    # D = np.abs(librosa.stft(y))
    # fig, ax = plt.subplots(nrows=2, sharex=True, figsize=(15, 10))
    # librosa.display.specshow(librosa.amplitude_to_db(D, ref=np.max), x_axis='time', y_axis='log', ax=ax[0])
    # ax[0].set(title='Power spectrogram')
    # ax[0].label_outer()
    # ax[0].plot(times, f0, label='f0', color='cyan', linewidth=3)


    # for note in notes:
    #     ax[0].plot(note.get_time(), note.get_frequencyCurve())
    # ax[0].vlines(times[onset_times], 0, D.max(), color='r', alpha=0.9, linestyle='--', label='Onsets')
    #
    # plt.show()

    # Piano roll display for the stored notes
    # intervals = []
    # frequencies = []
    # for note in notes:
    #     intervals.append((note.get_onset_seconds(), note.get_offset_seconds()))
    #     frequencies.append(note.get_avg_frequency())
    # mir_eval.display.piano_roll(intervals=intervals, pitches=frequencies)
    print("Tempo: ", tempo)
    return notes, tempo

# Additional function provided to return the relevant variables for algorithm validation
def extractFeatures_validation(filename):
    y, sr = librosa.load(filename)

    # Detect onsets within the recording
    onsets, onset_times, times, onsetEnvelope, silence = detectOnsets(y, sr)

    # Calculating frequency curve with pYin
    # f0, voiced_flag, voiced_probs = librosa.pyin(y,
    #                                              fmin=librosa.midi_to_hz(12.0),
    #                                              fmax=librosa.midi_to_hz(120.0),
    #                                              fill_na=np.nan,
    #                                              no_trough_prob=0)

    # Analyse loudness/intensity of performance and individual notes
    # loudness = loudnessAnalysis(y=y, sr=sr)

    # Segment the frequency curve into individual notes
    # Frequency, onsets, durations, loudness
    # notes = segmentationRetry(silence=silence,
    #                           onsets=onset_times,
    #                           f0=f0,
    #                           times=times,
    #                           sr=sr,
    #                           loudness=loudness[0][0])

    # Clean edges of the frequency curves for notes
    # for note in notes:
    #     note.clean_frequency()

    return librosa.samples_to_time(onsets)