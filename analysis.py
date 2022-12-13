import sys
import tkinter
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import librosa
import scipy.signal

matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import mir_eval.display
from models.performance_record import Performance_record
from models.transcriber import detectOnsets, loudnessAnalysis

def timing_display(y, sr):

    onset_samples, onset_times, times, onsetEnvelope, silence = detectOnsets(y=y, sr=sr)
    # onsetTimingLabels:
    #   Allow us to identify each onset as 'Early, 'On-time', or 'Late'
    # timingThreshold:
    #   A threshold in frames of when a note falls out of time or off-tempo
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
        if i <= beats[idx] - timingThreshold:
            onsetTimingLabels.append('Early')
        elif i >= beats[idx] + timingThreshold:
            onsetTimingLabels.append('Late')
        else:
            onsetTimingLabels.append('On-time')
    #
    return onsetEnvelope, newOnsets, onsetTimingLabels, times, beats

def draw_single_performance_feedback(parent, performance_record):

    y, sr = librosa.load(performance_record.get_filename() + ".wav")
    # Pre-process the audio (Remove silence from start and end of recording)
    # trimmed, trimIndex = librosa.effects.trim(y=y, top_db=20)
    # y = y[trimIndex[0]:trimIndex[1]]

    # Get relevant data from the record
    intervals = []
    frequencies = []
    inter_onsets_y = []
    inter_onsets_x = []
    min_ioi = sys.maxsize
    max_ioi = 0
    for idx, note in enumerate(performance_record.note_list):
        # Build piano roll
        intervals.append((note.get_onset_seconds(), note.get_offset_seconds()))
        frequencies.append(note.get_avg_frequency())

        # Calculate inter-onset intervals
        if (idx == 0):
            current_onset = performance_record.note_list[idx].get_onset_seconds()
        if idx != len(performance_record.note_list) - 1:
            next_onset = performance_record.note_list[idx + 1].get_onset_seconds()
            inter_onsets_y.append(next_onset - current_onset)
            inter_onsets_x.append(note.get_name())
            print("Onsets: ", current_onset, ", ", next_onset)
            current_onset = next_onset
        else:
            inter_onsets_y.append(note.get_duration_seconds())
            inter_onsets_x.append(note.get_name())
        if inter_onsets_y[idx] < min_ioi:
            min_ioi = inter_onsets_y[idx]
        elif inter_onsets_y[idx] > max_ioi:
            max_ioi = inter_onsets_y[idx]



    # Estimate tempo and provide note timing feedback
    onset_envelope, newOnsets, onsetTimingLabels, times, beats = timing_display(y, sr)
    # print(times)
    fig, ax = plt.subplots(nrows=3, figsize=(10, 6))

    # Plot the piano roll
    print("Frequencies:")
    print(frequencies)
    ax[0].set_title("Piano Roll")
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel("Pitch")
    mir_eval.display.piano_roll(intervals=intervals, pitches=frequencies, ax=ax[0], label='Transcribed Notes', alpha=0.5)
    plt.grid('on')
    mir_eval.display.ticker_notes(ax=ax[0])

    # Calculate the loudness of the performance
    loudness, loudness_times = loudnessAnalysis(y, sr)

    # Select the peaks from the loudness curve
    peaks, properties = scipy.signal.find_peaks(loudness[0])
    min_peak = min(loudness[0][peaks])
    max_peak = max(loudness[0][peaks])

    # Calculate a line of best fit using te peaks
    res = scipy.stats.linregress(peaks, loudness[0][peaks])
    print('{0:.10f}'.format(res.slope))

    # Plot the inter-onset intervals
    ax[1].set_title("Inter Onset Intervals")
    ax[1].set_xlabel("Note names")
    ax[1].set_ylabel("Time (s)")
    ax[1].bar(inter_onsets_x, inter_onsets_y)
    ax[1].grid(True)
    ax[1].set_yticks(np.arange(0, max_ioi, min_ioi))

    # Plot the onsets alone and envelope
    # ax[1].plot(times, librosa.util.normalize(onset_envelope))
    # ax[1].vlines(times[beats], 0, 1, color='r', alpha=0.9, linestyle='--', label='Onsets')

    # Plot the loudness of the performance as well
    # ax[2].semilogy(loudness_times, loudness[0], label="Loudness")
    ax[2].set_title("Loudness")
    ax[2].set_xlabel("Time (s)")
    ax[2].set_ylabel("dbA (log10)")
    ax[2].plot(loudness[0], alpha=0.4)
    ax[2].plot(peaks, loudness[0][peaks], 'o', alpha=0.4)
    ax[2].plot(peaks, res.intercept + res.slope*peaks, '--k')
    ax[2].set_ylim([min_peak, max_peak])

    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, parent)
    toolbar.update()

def multi_performance_feedback(parent, performances):

    # Retrieve relevant data
    note_dict = {}

    frequencies = []
    loudness = []
    for performance in performances:
        for note in performance.note_list:
            note_dict.setdefault(note.name, []).append(note.loudness)
            frequencies.append(note.get_avg_frequency())
            loudness.append(note.get_avg_loudness())
            print(note.loudness)

    fig, ax = plt.subplots(nrows=2, figsize=(10, 6))

    # Plot 1:
    #   Loudness vs Pitch scatter plot
    ax[0].set_title("Average loudness per Note")
    ax[0].set_xlabel("dbA (log10)")
    ax[0].set_ylabel("Frequency (Hz)")
    ax[0].scatter(loudness, frequencies, marker='o', alpha=0.5)
    ax[0].set_xscale('log')


    # Plot 2:
    #   Loudness over time per pitch
    ax[1].set_title("Loudness curve per pitch")
    ax[1].set_ylabel("dbA (log10)")
    ax[1].set_xlabel("Time (frames)")
    note_names = []
    for key, value in note_dict.items():
        note_names.append(key)
        for note in value:
            ax[1].plot(note, alpha=0.3)

    def pitch_loudness(label):
        ax[1].clear()
        data = note_dict[label]
        for value in data:
            ax[1].plot(value, alpha=0.3)
        plt.tight_layout()
        canvas.draw()

    rax = plt.axes([0.82, 0.25, 0.1, 0.2])
    rax.patch.set_alpha(0.5)
    rad_btn = matplotlib.widgets.RadioButtons(rax, note_names)
    rad_btn.on_clicked(pitch_loudness)

    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, parent)
    toolbar.update()

